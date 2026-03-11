---
title: "Home Assistant"
date: 2026-03-11
weight: 2
---

# Home Assistant

## Overview

My smart home runs on [Home Assistant](https://www.home-assistant.io/) OS, deployed as a VM on my Proxmox hypervisor. It controls lighting, climate, security, garage access, and media across the house — all locally, with no reliance on cloud services for core automation.

## Infrastructure

| | |
|-|-|
| **Platform** | Home Assistant OS 17.1 on Proxmox VM (2 vCPU, 6GB RAM) |
| **Z-Wave** | Nabu Casa Connect ZWA-2 USB coordinator |
| **Zigbee** | SLZB-06 PoE coordinator |
| **Hue** | Philips Hue Bridge (BSB002) — 30+ color bulbs, strips, and dimmer switches |
| **MQTT** | Mosquitto broker for ESPHome and IoT device communication |
| **Voice** | Home Assistant Voice PE with Google Gemini 2.5 Flash (STT, TTS, conversation) |

## Protocols & Why They Matter

One of the more interesting challenges in home automation is managing a multi-protocol environment. Different device categories have different strengths:

- **Z-Wave** — Used for the front door lock (Kwikset HC620), thermostat (Honeywell T6 Pro), and smart plugs (Zooz ZEN04). Z-Wave's mesh networking and mandatory encryption make it ideal for security-critical devices.
- **Zigbee / Hue** — Handles all lighting through a Philips Hue Bridge. 30+ color bulbs and lightstrips across every room, plus 6 Hue dimmer switches for physical control.
- **ESPHome** — Custom firmware on ESP32 devices for the garage door opener ([ratgdo](https://paulwieland.github.io/ratgdo/)) and a few Apollo MSR-2 mmWave presence sensors to trigger lighting automations based on human presence
- **Matter / Thread** — Supported and ready as the ecosystem matures.
- **WiFi** — Deako smart switches, Meross devices, and Google Cast speakers.

## Devices

### Security & Access
- **Kwikset HC620** — Z-Wave smart lock on the front door
- **ratgdo** — ESPHome-based garage door controller, replacing the proprietary myQ cloud service with fully local control
- **UniFi Protect** — G4 Doorbell Pro PoE, G6 Bullet (backyard), and G6 Instant cameras. Footage is stored on the HDD in my UDM SE — no cloud subscription needed. Feeds are accessible through the UniFi Protect app and integrated into Home Assistant for event-driven automations.

### Climate
- **Honeywell T6 Pro** — Z-Wave programmable thermostat with full local control through Home Assistant

### Presence Detection
- **Apollo MSR-2 mmWave sensors** — Three ESPHome-powered sensors using millimeter-wave radar for room-level occupancy detection. Unlike PIR sensors, these detect stationary occupants (sitting, sleeping) and report presence zones, distance, and CO2 readings

### Lighting
- **30+ Philips Hue color bulbs and lightstrips** — Full RGBW control across every room (kitchen, living room, bedroom, office, loft, dining room, gym, garage, deck, and more)
- **6 Hue dimmer switches** — Physical wall controls for each zone

### Media & Voice
- **Home Assistant Voice PE** — Local wake word detection with Google Gemini 2.5 Flash powering conversation, speech-to-text, and text-to-speech

### Smart Plugs
- **Zooz ZEN04** — Z-Wave smart plugs for seasonal lighting (holiday garland, Christmas tree)

## Dashboard

The Home Assistant frontend is customized with [HACS](https://hacs.xyz/) community components:

- **Mushroom cards** — Clean, modern UI components
- **mini-graph-card** — Sparkline-style sensor history graphs
- **Hue-Like Light Card** — Visual light control that mimics the Hue app
- **Mini Media Player** — Compact media controls for Sonos and Cast devices

## What's Next

- Building out automations — presence-based lighting using the mmWave sensors, climate schedules, and notification workflows
- Adding more ESPHome sensor nodes
- Exploring local AI voice pipelines to reduce cloud dependency
