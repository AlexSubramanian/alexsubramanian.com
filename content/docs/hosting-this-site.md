---
title: "Hosting This Site"
date: 2026-03-07
weight: 1
---

# Hosting This Site

This page documents the full stack behind alexsubramanian.com — from DNS to deployment.

## Architecture Overview

```text
User → Cloudflare (CDN/DNS) → Docker (Caddy + Hugo static files)
                                    ↑
                        Watchtower (auto-pull)
                                    ↑
                          ghcr.io container registry
                                    ↑
                        GitHub Actions (build + push)
                                    ↑
                          Push to main branch
```

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| DNS / CDN | Cloudflare (Free) | DNS, caching, DDoS protection, hides origin IP |
| Web Server | Caddy (in Docker) | Static file serving, HTTPS, security headers |
| Site Generator | Hugo (in Docker) | Builds static HTML from Markdown at image build time |
| Hosting | Proxmox VM (Debian) | 1 vCPU, 1GB RAM lightweight VM running Docker |
| CI/CD | GitHub Actions + Watchtower | Build image, push to ghcr.io, auto-pull on server |
| Version Control | GitHub | Public repo for source and content |

## DNS and Cloudflare

The domain is registered through Porkbun with nameservers pointed to Cloudflare. Cloudflare provides:

- Proxy mode (orange cloud) to hide the home IP address
- Free CDN caching for static assets
- SSL/TLS in Full (Strict) mode with a Cloudflare origin certificate
- DDoS and bot protection

## Containerized Deployment

The site runs as a single Docker container that bundles both Hugo's static output and the Caddy web server. A multi-stage Dockerfile builds the site with Hugo, then copies the output into a Caddy image. The Cloudflare origin certificate is mounted from the host at runtime.

Caddy is configured with:

- Cloudflare origin certificate for TLS
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Gzip compression
- JSON access logging for fail2ban

## CI/CD Pipeline

On push to `main`, GitHub Actions builds the Docker image and pushes it to GitHub Container Registry (`ghcr.io`). On the server, Watchtower polls for new images and automatically restarts the container. No SSH keys or exposed deployment ports are needed.

## Security Layers

1. **Cloudflare** — Filters malicious traffic and rate limits at the edge
2. **robots.txt** — Discourages aggressive crawlers
3. **fail2ban** — Bans abusive IPs based on Caddy access logs
4. **Static site** — No database or dynamic endpoints to exploit
