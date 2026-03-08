---
title: "Hosting This Site"
weight: 1
---

# Hosting This Site

This page documents the full stack behind alexsubramanian.com — from DNS to deployment.

## Architecture Overview

```text
User → Cloudflare (CDN/DNS) → Caddy (HTTPS) → Hugo static files
                                    ↑
                        GitHub Actions (CI/CD)
                                    ↑
                          Push to main branch
```

## Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| DNS / CDN | Cloudflare (Free) | DNS, caching, DDoS protection, hides origin IP |
| Web Server | Caddy | Static file serving, automatic HTTPS, security headers |
| Site Generator | Hugo | Builds static HTML from Markdown content |
| Hosting | Proxmox VM (Debian) | 1 vCPU, 1GB RAM lightweight VM |
| CI/CD | GitHub Actions | Automated build and deploy on push to main |
| Version Control | GitHub | Public repo for source and content |

## DNS and Cloudflare

The domain is registered through Porkbun with nameservers pointed to Cloudflare. Cloudflare provides:

- Proxy mode (orange cloud) to hide the home IP address
- Free CDN caching for static assets
- SSL/TLS in Full (Strict) mode with a Cloudflare origin certificate
- DDoS and bot protection

## Web Server

Caddy runs on a dedicated Debian VM (VM 104) in Proxmox with:

- Cloudflare origin certificate for TLS
- Security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Rate limiting per IP
- Gzip compression

## CI/CD Pipeline

*This section will be updated once the GitHub Actions pipeline is configured (Phase 6).*

## Security Layers

1. **Cloudflare** — Filters malicious traffic at the edge
2. **Caddy rate limiting** — Per-IP request limits
3. **robots.txt** — Discourages aggressive crawlers
4. **fail2ban** — Bans abusive IPs based on Caddy access logs
5. **Static site** — No database or dynamic endpoints to exploit
