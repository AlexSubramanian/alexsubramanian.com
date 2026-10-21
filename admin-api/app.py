"""admin-api -- the control plane behind alexsubramanian.com/admin.

Sits on the web VM, fans out to the homelab agent on each Docker host, and holds
every credential involved so none of them ever reaches a browser.

Two principles shape most of the code here:

1. An unreachable host is its own state, never a clean one. Every silent-success
   bug found while building the agent was a failed lookup rendered as good news
   -- an empty service list becoming "nothing to update", an unreachable
   registry becoming "up to date". A host that cannot be contacted, a stale
   cache, and a failed registry check each surface explicitly, and the overview
   carries an `attention` list so the page cannot accidentally show a tick.

2. Nothing authenticating anything is sent downstream. Agent tokens and the
   Tautulli API key live only in this process.
"""

from __future__ import annotations

import asyncio
import hmac
import os
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

AGENT_PORT = int(os.environ.get("HOMELAB_AGENT_PORT", "9180"))

# Hard-coded like the rest of this homelab's topology (see the prometheus scrape
# config and the repo README); overridable for testing.
HOSTS: dict[str, dict[str, str]] = {
    "arr-stack":  {"ip": os.environ.get("AGENT_IP_ARR_STACK",  "192.168.1.75"),
                   "token": os.environ.get("HOMELAB_AGENT_TOKEN_ARR_STACK", "")},
    "plex":       {"ip": os.environ.get("AGENT_IP_PLEX",       "192.168.1.103"),
                   "token": os.environ.get("HOMELAB_AGENT_TOKEN_PLEX", "")},
    "monitoring": {"ip": os.environ.get("AGENT_IP_MONITORING", "192.168.1.228"),
                   "token": os.environ.get("HOMELAB_AGENT_TOKEN_MONITORING", "")},
}

# A fan-out must not hang the page on one dead host. These are short on purpose;
# /status is served from the agent's cache so it answers in milliseconds.
FANOUT_TIMEOUT = float(os.environ.get("ADMIN_FANOUT_TIMEOUT", "6"))
# A forced re-check shells out to docker once per container on the far side.
CHECK_TIMEOUT = float(os.environ.get("ADMIN_CHECK_TIMEOUT", "240"))

# Cloudflare Access (phase 3). Until these are set, the only way in is the LAN
# token below.
ACCESS_TEAM_DOMAIN = os.environ.get("ADMIN_ACCESS_TEAM_DOMAIN", "").strip()
ACCESS_AUD = os.environ.get("ADMIN_ACCESS_AUD", "").strip()
ACCESS_ALLOWED_EMAILS = {
    e.strip().lower() for e in os.environ.get("ADMIN_ACCESS_EMAILS", "").split(",") if e.strip()
}

# A bearer token for reaching this API from inside the LAN, without going
# through Cloudflare. Useful for scripts and for testing before Access exists.
# It is only usable from the LAN: Caddy does not route to this service until
# phase 3, and when it does the edge requires an Access session first.
LAN_TOKEN = os.environ.get("ADMIN_API_LAN_TOKEN", "")

TAUTULLI_URL = os.environ.get("TAUTULLI_URL", "http://192.168.1.103:8181")
TAUTULLI_API_KEY = os.environ.get("TAUTULLI_API_KEY", "")

_jwk_client: jwt.PyJWKClient | None = None
if ACCESS_TEAM_DOMAIN:
    _jwk_client = jwt.PyJWKClient(
        f"https://{ACCESS_TEAM_DOMAIN}/cdn-cgi/access/certs", cache_keys=True
    )

app = FastAPI(title="homelab admin-api", docs_url=None, redoc_url=None, openapi_url=None)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Auth --------------------------------------------------------------------


def _verify_access_jwt(token: str) -> dict[str, Any]:
    if not (_jwk_client and ACCESS_AUD):
        raise HTTPException(503, "Cloudflare Access is not configured on this server")
    try:
        key = _jwk_client.get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token, key, algorithms=["RS256"],
            audience=ACCESS_AUD, issuer=f"https://{ACCESS_TEAM_DOMAIN}",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(403, f"invalid Access token: {exc}") from exc

    # An Access app can be widened by accident in the dashboard; pinning the
    # allowed identities here means that alone isn't enough to get in.
    if ACCESS_ALLOWED_EMAILS:
        email = str(claims.get("email", "")).lower()
        if email not in ACCESS_ALLOWED_EMAILS:
            raise HTTPException(403, "identity not permitted")
    return claims


async def require_admin(request: Request) -> dict[str, Any]:
    """Accept a Cloudflare Access assertion, or the LAN token.

    Fails closed: with neither mechanism configured, nothing is authorised.
    """
    assertion = request.headers.get("Cf-Access-Jwt-Assertion")
    if assertion:
        claims = _verify_access_jwt(assertion)
        return {"via": "cloudflare-access", "email": claims.get("email")}

    auth = request.headers.get("Authorization", "")
    if LAN_TOKEN and auth.startswith("Bearer "):
        if hmac.compare_digest(auth[len("Bearer "):], LAN_TOKEN):
            return {"via": "lan-token", "email": None}

    if not (ACCESS_AUD or LAN_TOKEN):
        raise HTTPException(
            503,
            "admin-api has no authentication configured; refusing all requests. "
            "Set ADMIN_ACCESS_AUD + ADMIN_ACCESS_TEAM_DOMAIN, or ADMIN_API_LAN_TOKEN.",
        )
    raise HTTPException(401, "unauthorized")


# --- Agent plumbing ----------------------------------------------------------


def _host_or_404(host: str) -> dict[str, str]:
    cfg = HOSTS.get(host)
    if not cfg:
        raise HTTPException(404, f"unknown host {host!r}")
    if not cfg["token"]:
        raise HTTPException(503, f"no agent token configured for {host!r}")
    return cfg


async def _agent(
    client: httpx.AsyncClient, host: str, path: str,
    method: str = "GET", json_body: dict | None = None, timeout: float | None = None,
) -> httpx.Response:
    cfg = _host_or_404(host)
    return await client.request(
        method, f"http://{cfg['ip']}:{AGENT_PORT}{path}",
        headers={"Authorization": f"Bearer {cfg['token']}"},
        json=json_body, timeout=timeout or FANOUT_TIMEOUT,
    )


def _summarise(status_payload: dict[str, Any] | None) -> dict[str, Any]:
    """Collapse one agent's status into counts the page can render at a glance.

    `unknown` is the important field: it means this host's numbers cannot be
    trusted, which must look different from "zero updates".
    """
    if not status_payload or not status_payload.get("ok"):
        return {"containers": 0, "updates": 0, "pinned": 0,
                "remote_failures": 0, "unknown": True}
    s = status_payload.get("status") or {}
    containers = s.get("containers") or []
    return {
        "containers": len(containers),
        "updates": sum(1 for c in containers if c.get("update_available")),
        "pinned": sum(1 for c in containers if c.get("pinned")),
        "remote_failures": int(s.get("remote_failures") or 0),
        "unknown": bool(status_payload.get("stale")) or not containers
                   or int(s.get("remote_failures") or 0) > 0,
    }


async def _one_host(client: httpx.AsyncClient, host: str) -> dict[str, Any]:
    out: dict[str, Any] = {"host": host, "service": host, "reachable": False,
                           "error": None, "agent": None, "status": None}
    try:
        health, status = await asyncio.gather(
            _agent(client, host, "/healthz"),
            _agent(client, host, "/status"),
        )
        health.raise_for_status()
        status.raise_for_status()
        out["reachable"] = True
        out["agent"] = health.json()
        out["status"] = status.json()
    except httpx.HTTPStatusError as exc:
        out["error"] = f"agent returned HTTP {exc.response.status_code}"
    except httpx.TimeoutException:
        out["error"] = f"agent did not respond within {FANOUT_TIMEOUT}s"
    except httpx.HTTPError as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    out["summary"] = _summarise(out["status"])
    return out


# --- Routes ------------------------------------------------------------------


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    """Unauthenticated, for Caddy and for telling 'API down' from 'auth wrong'."""
    return {
        "ok": True,
        "hosts": sorted(HOSTS),
        "auth": {
            "cloudflare_access": bool(ACCESS_AUD and ACCESS_TEAM_DOMAIN),
            "lan_token": bool(LAN_TOKEN),
        },
    }


@app.get("/api/overview")
async def overview(_: dict = Depends(require_admin)) -> JSONResponse:
    started = time.monotonic()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(_one_host(client, h) for h in HOSTS))

    attention: list[str] = []
    for r in results:
        if not r["reachable"]:
            attention.append(f"{r['host']}: unreachable — {r['error']}")
            continue
        s, st = r["summary"], r["status"]
        if st and not st.get("ok"):
            attention.append(f"{r['host']}: agent could not read the stack — {st.get('error')}")
        if s["remote_failures"]:
            attention.append(
                f"{r['host']}: registry check failed for {s['remote_failures']} image(s); "
                "their update state is unknown, not up to date")
        if st and st.get("stale"):
            attention.append(f"{r['host']}: status is stale ({st.get('age_seconds')}s old)")
        if s["pinned"]:
            attention.append(f"{r['host']}: {s['pinned']} service(s) pinned by a rollback")

    payload = {
        "fetched_at": now_iso(),
        "duration_ms": int((time.monotonic() - started) * 1000),
        "hosts": results,
        "summary": {
            "hosts_total": len(results),
            "hosts_unreachable": sum(1 for r in results if not r["reachable"]),
            "updates_available": sum(r["summary"]["updates"] for r in results),
            "any_unknown": any(r["summary"]["unknown"] for r in results),
        },
        "attention": attention,
    }
    return JSONResponse(payload, headers={"Cache-Control": "no-store"})


@app.post("/api/hosts/{host}/check")
async def force_check(host: str, _: dict = Depends(require_admin)) -> Response:
    async with httpx.AsyncClient() as client:
        r = await _agent(client, host, "/check", "POST", timeout=CHECK_TIMEOUT)
    return JSONResponse(r.json(), status_code=r.status_code, headers={"Cache-Control": "no-store"})


@app.post("/api/hosts/{host}/update")
async def start_update(host: str, request: Request, _: dict = Depends(require_admin)) -> Response:
    body = await _json_body(request)
    # Only a known flag is forwarded; nothing from the request reaches a command
    # line on the far side either (see the agent's argv construction).
    async with httpx.AsyncClient() as client:
        r = await _agent(client, host, "/update", "POST",
                         {"prune": body.get("prune") is True})
    return JSONResponse(r.json(), status_code=r.status_code)


@app.post("/api/hosts/{host}/rollback")
async def start_rollback(host: str, request: Request, _: dict = Depends(require_admin)) -> Response:
    body = await _json_body(request)
    async with httpx.AsyncClient() as client:
        r = await _agent(client, host, "/rollback", "POST",
                         {"clear": body.get("clear") is True})
    return JSONResponse(r.json(), status_code=r.status_code)


@app.get("/api/hosts/{host}/history")
async def history(host: str, _: dict = Depends(require_admin)) -> Response:
    async with httpx.AsyncClient() as client:
        r = await _agent(client, host, "/history")
    return JSONResponse(r.json(), status_code=r.status_code)


@app.get("/api/hosts/{host}/jobs/{job_id}")
async def job(host: str, job_id: str, offset: int = 0,
              _: dict = Depends(require_admin)) -> Response:
    async with httpx.AsyncClient() as client:
        r = await _agent(client, host, f"/jobs/{job_id}?offset={max(offset, 0)}")
    return JSONResponse(r.json(), status_code=r.status_code,
                        headers={"Cache-Control": "no-store"})


@app.get("/api/plex/activity")
async def plex_activity(_: dict = Depends(require_admin)) -> JSONResponse:
    """Now-playing from Tautulli.

    The page needs this for its own sake, and phase 4 needs the stream count to
    warn before restarting the plex stack. The API key stays here.
    """
    if not TAUTULLI_API_KEY:
        return JSONResponse({"ok": False, "error": "TAUTULLI_API_KEY not set"}, 503)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{TAUTULLI_URL}/api/v2", timeout=FANOUT_TIMEOUT,
                                 params={"apikey": TAUTULLI_API_KEY, "cmd": "get_activity"})
            r.raise_for_status()
            data = r.json()["response"]["data"]
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        return JSONResponse({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, 502)

    sessions = [
        {
            "user": s.get("friendly_name"),
            "title": s.get("full_title"),
            "state": s.get("state"),
            "transcode": s.get("transcode_decision"),
            "progress_percent": s.get("progress_percent"),
        }
        for s in data.get("sessions", [])
    ]
    return JSONResponse(
        {"ok": True, "stream_count": int(data.get("stream_count") or 0), "sessions": sessions},
        headers={"Cache-Control": "no-store"},
    )


async def _json_body(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except (ValueError, TypeError):
        return {}
    return body if isinstance(body, dict) else {}
