---
title: "Homelab"
date: 2026-03-07
weight: 1
---

# Homelab Infrastructure

## Overview

My homelab runs on a Proxmox virtualization server hosting multiple VMs for different services. The infrastructure is documented in my [homelab GitHub repository](https://github.com/AlexSubramanian/homelab).

## The Rack

This is where the site you're reading right now is running — a StarTech 25U rack in my basement.

![Homelab rack](/images/homelab-rack.jpg)

## Hardware

- Proxmox VE host (HP EliteDesk 800 G4)
- Raspberry Pi 4B + Samsung T7 SSD (monitoring & UPS management)
- CyberPower CP1500PFCRM2U rack UPS
- UniFi networking (UDM SE, switches, patch panel)
- Network storage (UNAS Pro, 24TB RAID 5)

## Virtual Machines

| VM | Purpose | vCPU | RAM |
|----|---------|------|-----|
| [Home Assistant](/projects/home-assistant/) (100) | Home automation | 2 | 6GB |
| Arr Stack (102) | Media automation | 4 | 6GB |
| Plex (103) | Media server | 4 | 8GB |
| [Web Server](/projects/this-site/) (104) | This website | 1 | 1GB |

## Monitoring

The infrastructure is monitored with a Prometheus + Grafana stack running on a dedicated Raspberry Pi 4B, separate from the Proxmox host and VMs it monitors. The Pi boots from a Samsung T7 SSD and also runs a NUT server for UPS monitoring of the CyberPower CP1500PFCRM2U. Blackbox exporter performs HTTP health checks against every service, and node-exporter agents on each host report system-level metrics.

### Service Status & Uptime

![Grafana service status dashboard](/images/grafana-service-status.png)

Blackbox probes each service endpoint every 30 seconds. The uptime history panel shows availability over time — green bars mean the service responded with a 2xx status code.

### Resource Utilization

![Grafana resource metrics dashboard](/images/grafana-metrics.png)

Per-host gauges for CPU and memory utilization, plus network throughput across all VMs and the monitoring Pi.

## Key Technologies

- **Proxmox VE** — Type 1 hypervisor for VM management
- **Docker** — Container orchestration across all hosts
- **Raspberry Pi 4B** — Dedicated monitoring and UPS management
- **NFS** — Shared media storage from UNAS Pro
- **Unifi** — Network management (UDM SE)
- **Prometheus + Grafana** — Metrics collection, dashboards, and service health monitoring
- **Blackbox Exporter** — HTTP endpoint probing for uptime tracking
- **NUT** — Network UPS Tools for UPS monitoring

For full details, see the [homelab repo on GitHub](https://github.com/AlexSubramanian/homelab).
