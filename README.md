# alexsubramanian.com

Self-hosted portfolio and documentation site running on Proxmox homelab infrastructure.

**URL:** [https://alexsubramanian.com](https://alexsubramanian.com)

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Static site generator | [Hugo](https://gohugo.io/) | Single binary, fast builds, Go templating |
| Theme | [Blowfish](https://github.com/nunocoracao/blowfish) | Profile layout, dark mode, ocean color scheme |
| Web server | [Caddy](https://caddyserver.com/) | Automatic HTTPS, security headers, reverse proxy |
| DNS / CDN | [Cloudflare](https://www.cloudflare.com/) (free tier) | CDN caching, DDoS protection, hides home IP |
| DDNS | [cloudflare-ddns](https://github.com/favonia/cloudflare-ddns) | Updates Cloudflare A record every 6 hours |
| CI/CD | GitHub Actions → GHCR → Watchtower | Push-to-deploy with event-driven container updates |
| Domain registrar | Porkbun | Nameservers pointed to Cloudflare |
| Host | Proxmox VM (104) | 1 vCPU, 1GB RAM, Debian 13 |

---

## Architecture

```
Push to main
    │
    ▼
GitHub Actions
    ├── Builds multi-stage Docker image (LibreOffice PDF conversion → Hugo build → Caddy)
    ├── Pushes to ghcr.io/alexsubramanian/alexsubramanian.com:latest
    ├── Triggers Watchtower via HTTP API through Caddy reverse proxy
    └── Purges Cloudflare cache

    ▼
VM 104 (web-server)
    ├── site        → Caddy serving static files + reverse proxy to Watchtower
    ├── watchtower   → Pulls new images, restarts site container
    └── cloudflare-ddns → Keeps DNS A record updated with home IP
```

---

## Site Structure

```
alexsubramanian.com/
├── /                          # Profile / about page
├── /resume/                   # Resume (HTML + PDF download)
├── /projects/                 # Project showcase
│   ├── /projects/homelab/     # Homelab infrastructure writeup
│   └── /projects/this-site/   # How this site is built and hosted
└── /docs/                     # Technical documentation
    └── /docs/hosting-this-site/   # Detailed hosting walkthrough
```

---

## Docker Build

The Dockerfile uses a multi-stage build:

1. **pdf-converter** — Alpine with LibreOffice converts `content/resume/*.docx` to PDF
2. **builder** — Hugo builds the site with `--minify`, including the generated PDF in `static/files/`
3. **runtime** — Caddy serves the built static files with the Caddyfile config

---

## Deployment

Deployment is fully automated and event-driven:

1. Push to `main` triggers the GitHub Actions workflow
2. The workflow builds and pushes a Docker image to GHCR
3. The workflow sends an HTTP POST to Watchtower (proxied through Caddy at `/v1/update`)
4. Watchtower pulls the new image and restarts the site container
5. The workflow waits 15 seconds, then purges the entire Cloudflare cache

Watchtower also polls every 24 hours as a fallback.

### Required Secrets (GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `WATCHTOWER_TOKEN` | Bearer token for Watchtower HTTP API |
| `CLOUDFLARE_ZONE_ID` | Cloudflare zone for cache purge |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API token with cache purge permissions |

### Required Environment Variables (Server `.env`)

| Variable | Purpose |
|----------|---------|
| `CLOUDFLARE_DDNS_API_TOKEN` | Cloudflare API token for DDNS updates |
| `WATCHTOWER_TOKEN` | Bearer token for Watchtower HTTP API |

---

## Local Development

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/AlexSubramanian/alexsubramanian.com.git
cd alexsubramanian.com

# Run Hugo dev server
hugo server -D

# Or build with Docker
docker build -t alexsubramanian-site .
docker run -p 8080:80 alexsubramanian-site
```

---

## Server Setup

On VM 104:

```bash
# Log in to GHCR
echo "<token>" | docker login ghcr.io -u AlexSubramanian --password-stdin

# Create cert directory and add Cloudflare origin certs
sudo mkdir -p /opt/caddy/certs
# Copy cert.pem and key.pem from Cloudflare dashboard

# Create .env with required variables
cp .env.example .env  # then fill in values

# Start all services
docker compose up -d
```

---

## Security

- Cloudflare proxy mode hides home IP
- Only ports 80/443 forwarded to VM 104
- Caddy security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Server` header stripped
- fail2ban monitors Caddy access logs for abusive IPs
- SSH key-only auth on the VM
- No secrets in the repo (`.env` and `static/files/resume.pdf` are gitignored)
- Static site — no database or dynamic endpoints to exploit
