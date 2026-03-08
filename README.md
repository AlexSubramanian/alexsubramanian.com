# Implementation Plan for Self-Hosted Portfolio and Documentation Site  
*This plan will be updated as phases are completed.*  
**Created**: March 2026  
**Status:** Phase 4 in progress

---

## Project Goals

Host a personal website at alexsubramanian.com to support job applications and showcase technical skills. The site will include a resume, project documentation (including the homelab itself), and any future portfolio pieces. It should be self-hosted on the existing Proxmox infrastructure with a future AWS failover path.

---

## Stack Decisions

### Static Site Generator: Hugo
- **Why Hugo:** Written in Go (aligns with current skills), generates pure static HTML, excellent documentation themes, fast builds, single binary with no runtime dependencies
- **Frontend learning path:** Hugo's templating system introduces HTML/CSS/JS incrementally rather than requiring a full framework like React up front
- **Theme candidates:** Hugo Book or Doks — clean, documentation-oriented, professional

### Web Server: Caddy
- **Why Caddy:** Automatic HTTPS via Let's Encrypt (or Cloudflare origin certs), built-in rate limiting, simple configuration, written in Go
- **Alternative considered:** Nginx — more complex config, no auto-TLS, overkill for static files

### DNS and CDN: Cloudflare (Free Tier)
- **Why Cloudflare:** Free CDN caching, DDoS/bot protection, hides home IP via proxy mode, DNS management
- **Domain registrar:** Porkbun (domain purchased, nameservers will point to Cloudflare)

### CI/CD: GitHub Actions
- **Workflow:** Push to `main` → GitHub Actions builds Hugo site → deploys to VM via SSH/rsync
- **Repo:** `alexsubramanian.com` (public, separate from homelab repo)

### Bot and Scraper Protection (Layered)
1. **Cloudflare (free tier):** Filters malicious bots and caches static assets at edge before traffic hits home
2. **Caddy rate limiting:** Limits requests per IP at the web server level
3. **robots.txt:** Discourages well-behaved scrapers from aggressive crawling
4. **fail2ban:** Watches Caddy access logs and bans abusive IPs via iptables
5. **Static site advantage:** No database to overwhelm, no dynamic endpoints to exploit

---

## Repository Strategy

**Personal site:** New public repo at `https://github.com/AlexSubramanian/alexsubramanian.com`
- Contains Hugo source, Caddyfile, GitHub Actions workflow, and site content
- Standalone portfolio piece visible on GitHub profile

**Homelab repo:** Stays public at `https://github.com/AlexSubramanian/homelab`
- Arr-stack documentation is not unprofessional — it demonstrates real infrastructure skills (Docker, NFS, Proxmox, networking)
- Keep it focused on infrastructure; avoid including credentials or anything questionable
- The personal site can link to the homelab repo as a project showcase

---

## Hardware Assessment

Current allocation with web server VM added:

| VM | vCPU | RAM | Notes |
|----|------|-----|-------|
| Home Assistant (100) | 2 | 6GB | |
| Arr Stack (102) | 4 | 6GB | |
| Plex (103) | 4 | 8GB | |
| Web Server (104) | 1 | 1GB | New |
| **Total** | **11** | **21GB** | |

**Capacity:** 11GB RAM remaining, CPU overprovisioning at 1.8x (manageable). Web server uses negligible resources since it serves only static files.

**Minecraft consideration:** A Minecraft server would need 2-4GB RAM and 2 cores. That would push total to 13 vCPU / 25GB RAM — tight but workable for a small server (<8 players). If RAM pressure appears or Plex transcoding stutters, consider offloading to a dedicated N100-based mini PC (~$150).

---

## Implementation Phases

### Phase 1: DNS and Cloudflare Setup
**Goal:** Point domain to Cloudflare, configure DNS

Steps:
1. Create a Cloudflare account (free tier)
2. Add alexsubramanian.com to Cloudflare
3. In Porkbun, change nameservers to the ones Cloudflare provides
4. In Cloudflare DNS, create an A record pointing to home public IP (proxy mode / orange cloud enabled)
5. Create a CNAME record for `www` → `alexsubramanian.com`
6. Enable "Always Use HTTPS" and "Automatic HTTPS Rewrites" in Cloudflare SSL/TLS settings
7. Set SSL/TLS mode to "Full (Strict)" — Caddy will use a Cloudflare origin certificate
8. Generate a Cloudflare origin certificate (valid 15 years) for use by Caddy

**Verification:** `dig alexsubramanian.com` resolves to Cloudflare IPs (not home IP)

### Phase 2: Create the Web Server VM (104)
**Goal:** Lightweight Debian VM with Hugo and Caddy installed

Steps:
1. Create VM in Proxmox GUI:
   - VM ID: 104, Name: `web-server`
   - OS: Debian 13 (Trixie)
   - Machine: q35, BIOS: SeaBIOS
   - Disk: 16GB on local-lvm (cache: write back, discard: on)
   - CPU: 1 socket, 1 core, type: host
   - Memory: 1024 MB
   - Network: vmbr0, VirtIO
2. Install Debian (SSH server + standard utilities only)
3. Post-install configuration:
   ```bash
   # login as root to install sudo, elevate user permissions to allow sudo first
   su -
   apt update && apt upgrade -y
   apt install sudo
   usermod -aG sudo alex
   exit
   sudo apt install -y curl wget nano qemu-guest-agent fail2ban git
   sudo systemctl enable qemu-guest-agent && sudo systemctl start qemu-guest-agent
   ```
4. Install Hugo (extended edition):
   ```bash
   sudo apt install hugo
   hugo version
   ```
5. Install Caddy:
   ```bash
   # https://caddyserver.com/docs/install#debian-ubuntu-raspbian
   sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   chmod o+r /etc/apt/sources.list.d/caddy-stable.list
   sudo apt update
   sudo apt install caddy
   ```

**Verification:** SSH to 192.168.1.104, `hugo version` and `caddy version` both work

### Phase 3: Router Port Forwarding and Firewall
**Goal:** Route external web traffic to VM 104 only

Steps:
1. In UDM SE, create port forwarding rules:
   - Port 80 (TCP) → 192.168.1.104:80
   - Port 443 (TCP) → 192.168.1.104:443
2. Create a firewall rule that restricts incoming WAN traffic on ports 80/443 to destination 192.168.1.104 only
3. Verify no other VMs are reachable from outside

**Verification:** From an external network (e.g., phone on cellular), `curl -I http://[home-public-ip]` reaches the web server VM

### Phase 4: Hugo Site Scaffolding
**Goal:** Initialize the Hugo site with a professional theme and basic content structure within the existing repository.

Steps:
1. Clone this repo on a development machine (or the VM) and move into the directory:
   ```bash
   git clone https://github.com/AlexSubramanian/alexsubramanian.com.git
   cd alexsubramanian.com
   ```
2. Scaffold the site (using `--force` to bypass the existing README and `.git` data):
   ```bash
   hugo new site . --force
   # Add chosen theme as a git submodule
   git submodule add https://github.com/alex-shpak/hugo-book.git themes/hugo-book
   ```
3. Configure `hugo.toml` with site title, base URL, theme (`theme = 'hugo-book'`), and menu structure.
4. Create initial content structure:
   ```text
   content/
   ├── _index.md              # Landing / about page
   ├── resume/
   │   └── _index.md          # Resume page (also offer PDF download)
   ├── projects/
   │   ├── _index.md          # Projects overview
   │   └── homelab.md         # Homelab documentation
   └── docs/
       ├── _index.md          # Documentation section
       └── hosting-this-site.md  # Meta-doc about the site setup itself
   ```
5. Build and test locally: 
   ```bash
   hugo server -D
   ```
6. Commit and push the new scaffolding to GitHub:
   ```bash
   git add .
   git commit -m "Initialize Hugo scaffolding and add hugo-book theme"
   git push origin main
   ```

### Phase 5: Caddy Configuration
**Goal:** Serve the Hugo site over HTTPS with security hardening

Steps:
1. Place the Cloudflare origin certificate and key on the VM:
   ```bash
   mkdir -p /opt/caddy/certs
   # Copy origin cert and key from Cloudflare dashboard
   ```
2. Create the Caddyfile at `/opt/caddy/Caddyfile`:
   ```
   alexsubramanian.com {
       root * /var/www/alexsubramanian.com/public
       file_server
       encode gzip

       tls /opt/caddy/certs/origin.pem /opt/caddy/certs/origin-key.pem

       header {
           X-Content-Type-Options nosniff
           X-Frame-Options DENY
           Referrer-Policy strict-origin-when-cross-origin
           -Server
       }

       # Rate limiting
       rate_limit {
           zone static_zone {
               key {remote_host}
               events 100
               window 1m
           }
       }
   }

   www.alexsubramanian.com {
       redir https://alexsubramanian.com{uri} permanent
   }
   ```
3. Configure Caddy to use the custom Caddyfile and restart
4. Set up fail2ban with a Caddy jail for repeated 4xx/5xx errors

**Verification:** `curl -I https://alexsubramanian.com` returns 200 with correct security headers

### Phase 6: CI/CD Pipeline
**Goal:** Automated build and deploy on push to main

Steps:
1. On the web server VM, create a deploy user with restricted SSH access:
   ```bash
   useradd -m -s /bin/bash deploy
   mkdir -p /home/deploy/.ssh
   # Add GitHub Actions public key to authorized_keys
   # Grant deploy user write access to /var/www/alexsubramanian.com/
   ```
2. In the GitHub repo, create `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy Site
   on:
     push:
       branches: [main]

   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             submodules: true

         - name: Setup Hugo
           uses: peaceiris/actions-hugo@v3
           with:
             hugo-version: 'latest'
             extended: true

         - name: Build
           run: hugo --minify

         - name: Deploy
           uses: burnett01/rsync-deployments@7.0.2
           with:
             switches: -avz --delete
             path: public/
             remote_path: /var/www/alexsubramanian.com/public/
             remote_host: alexsubramanian.com
             remote_user: deploy
             remote_key: ${{ secrets.DEPLOY_SSH_KEY }}
   ```
3. Add the SSH private key as a GitHub Actions secret (`DEPLOY_SSH_KEY`)

**Verification:** Push a content change to `main`, confirm site updates within ~1 minute

### Phase 7: Content
**Goal:** Write the initial pages that make the site useful for job applications

Priority content:
1. **Landing page:** Brief professional intro, links to resume and projects
2. **Resume page:** Full resume in HTML (rendered by Hugo) plus a downloadable PDF
3. **"Hosting This Site" doc:** Meta-documentation covering the full stack — Proxmox VM, Hugo, Caddy, Cloudflare, CI/CD pipeline. This is the kind of writeup that impresses hiring managers.
4. **Homelab project page:** Overview of the Proxmox infrastructure, linking to the public homelab repo

Future content ideas:
- Go or Python project writeups
- Technical blog posts
- Any contributions to open source

### Phase 8: AWS Fallback (Future)
**Goal:** Static site failover so the site stays up if the home server goes down

Steps:
1. Create an S3 bucket configured for static website hosting
2. Set up a CloudFront distribution in front of the S3 bucket
3. Extend the GitHub Actions workflow to deploy to both the VM (rsync) and S3 (aws s3 sync)
4. In Cloudflare, configure a health check on the origin (home server)
5. Set up a failover DNS record: if the health check fails, Cloudflare routes to the CloudFront distribution
6. Document the entire setup as another page on the site

**Note:** This phase is not urgent — Cloudflare's caching already provides some resilience since cached pages are served from the edge even if the origin is briefly down. The AWS fallback is a nice-to-have that also demonstrates cloud skills.

---

## Site Structure (Planned)

```
alexsubramanian.com/
├── /                          # Landing / about page
├── /resume/                   # Resume (HTML + PDF download)
├── /projects/                 # Project showcase
│   ├── /projects/homelab/     # Homelab infrastructure writeup
│   └── /projects/[future]/    # Additional projects over time
└── /docs/                     # Technical documentation
    ├── /docs/hosting-this-site/   # How this site is hosted
    └── /docs/[future]/            # Additional docs over time
```

---

## Security Checklist

- [ ] Cloudflare proxy mode enabled (home IP hidden)
- [ ] Only ports 80/443 forwarded, only to VM 104
- [ ] Firewall rules prevent external access to any other VM
- [ ] Caddy security headers configured (nosniff, DENY framing, etc.)
- [ ] Rate limiting enabled in Caddy
- [ ] fail2ban watching Caddy logs
- [ ] robots.txt configured
- [ ] SSH key-only auth on VM 104 (password auth disabled)
- [ ] Deploy user has minimal permissions (write to web root only)
- [ ] No secrets or credentials in the public repo

---

