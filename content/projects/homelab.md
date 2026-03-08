---
title: "Homelab"
weight: 1
---

# Homelab Infrastructure

## Overview

My homelab runs on a Proxmox virtualization server hosting multiple VMs for different services. The infrastructure is documented in my [homelab GitHub repository](https://github.com/AlexSubramanian/homelab).

## Hardware

- Proxmox VE host
- Multiple VMs for isolated services

## Virtual Machines

| VM | Purpose | vCPU | RAM |
|----|---------|------|-----|
| Home Assistant (100) | Home automation | 2 | 6GB |
| Arr Stack (102) | Media automation | 4 | 6GB |
| Plex (103) | Media server | 4 | 8GB |
| Web Server (104) | This website | 1 | 1GB |

## Key Technologies

- **Proxmox VE** — Type 1 hypervisor for VM management
- **Docker** — Container orchestration for the Arr stack
- **NFS** — Shared storage between VMs
- **Unifi** — Network management (UDM SE)

For full details, see the [homelab repo on GitHub](https://github.com/AlexSubramanian/homelab).
