# admin-api

The control plane behind `alexsubramanian.com/admin`. Runs on VM 104, fans out
to the [homelab agent](https://github.com/AlexSubramanian/homelab) on each
Docker host, and holds every credential involved so none of them reaches a
browser.

## Why it exists separately from the agents

The agents can each describe and update exactly one stack. This turns that into
one view, holds the tokens, and is where authentication happens. It is also the
only component of the system that is ever reachable from the internet.

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET  | `/healthz` | Liveness and which auth mechanisms are configured. No auth. |
| GET  | `/api/overview` | All three hosts, concurrently, plus an `attention` list. |
| POST | `/api/hosts/{host}/check` | Force a registry re-check on one host. |
| POST | `/api/hosts/{host}/update` | `{"prune": false}` → `202 {"job_id": ...}` |
| POST | `/api/hosts/{host}/rollback` | `{"clear": false}` → `202 {"job_id": ...}` |
| GET  | `/api/hosts/{host}/history` | Rollback points on that host. |
| GET  | `/api/hosts/{host}/jobs/{id}?offset=N` | Job state and log tail. |
| GET  | `/api/plex/activity` | Now-playing from Tautulli. |

## An unreachable host is never a clean one

Every silent-success bug found while building this system was a failed lookup
rendered as good news: an empty compose service list became "nothing to
update"; an unreachable registry became "up to date". A fan-out is the next
place that can happen, so it is handled explicitly.

Each host carries `reachable`, a distinct `error`, and a `summary.unknown`
flag; the top-level summary carries `hosts_unreachable` and `any_unknown`; and
`attention` is a plain list of things a human should look at — unreachable
hosts, failed registry checks, stale caches, and active rollback pins.

`updates_available: 0` is therefore never sufficient on its own. The page must
read `any_unknown` and `attention` before showing anything reassuring.

## Authentication

Two mechanisms, and it **fails closed** if neither is configured — a request
then gets 503 explaining that, rather than being served.

1. **Cloudflare Access** (phase 3). The `Cf-Access-Jwt-Assertion` header is
   verified against the team's JWKS with `aud` and `iss` pinned.
   `ADMIN_ACCESS_EMAILS` additionally pins the permitted identities, so
   accidentally widening the Access policy in the dashboard is not by itself
   enough to get in.
2. **A LAN bearer token** for scripts and for testing before Access exists.
   This is not a way around Access: Caddy does not route to this service at
   all, so the token only works from inside the LAN.

## Deployment

Built by the site's GitHub Actions workflow as a second image and picked up by
the existing Watchtower. It publishes **no ports** — Caddy reaches it over the
compose network as `admin-api:8000`.

That route does not exist yet, and deliberately won't until Cloudflare Access
is configured in front of it. There is no window in which this API is
reachable from the internet without an Access session.

### Environment

| Variable | Purpose |
|----------|---------|
| `HOMELAB_AGENT_TOKEN_ARR_STACK` / `_PLEX` / `_MONITORING` | Agent bearer tokens; source of truth is `/etc/homelab-agent/env` on each host |
| `ADMIN_ACCESS_TEAM_DOMAIN` | e.g. `yourteam.cloudflareaccess.com` |
| `ADMIN_ACCESS_AUD` | Access application AUD tag |
| `ADMIN_ACCESS_EMAILS` | Comma-separated allow-list |
| `ADMIN_API_LAN_TOKEN` | LAN-only bearer token |
| `TAUTULLI_API_KEY` | For `/api/plex/activity` |
