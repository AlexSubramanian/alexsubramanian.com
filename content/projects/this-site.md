---
title: "alexsubramanian.com"
date: 2026-03-07
weight: 2
---

# alexsubramanian.com

This website — self-hosted on my homelab, built with Hugo, and deployed via Docker containers.

## Source

[github.com/AlexSubramanian/alexsubramanian.com](https://github.com/AlexSubramanian/alexsubramanian.com)

## Stack

- **Hugo** — Static site generator (Blowfish theme)
- **Caddy** — Web server with TLS and security headers
- **Docker** — Multi-stage build packages Hugo output + Caddy into a single image
- **GitHub Actions** — Builds and pushes the Docker image to ghcr.io on every push
- **Watchtower** — Auto-pulls new images on the server
- **Cloudflare** — DNS, CDN, DDoS protection, origin certificate

## How It Works

Every push to `main` triggers a GitHub Actions workflow that builds a Docker image and pushes it to GitHub Container Registry. On the server, Watchtower detects the new image and restarts the container automatically. No SSH keys or exposed deployment ports needed.

For the full writeup, see [Hosting This Site](/docs/hosting-this-site/).
