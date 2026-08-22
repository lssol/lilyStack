# 📹 TP-Link Tapo Camera: Complete Integration, RTSP & Frigate Guide

> Hardware specifications, local RTSP stream configuration, Home Assistant integration, and Frigate NVR setup for the **TP-Link Tapo Camera**.

---

## 📊 1. Hardware Specifications & Streaming Architecture

```
+---------------------------------------------------------------------------------------+
|                               TP-LINK TAPO CAMERA OVERVIEW                            |
+-------------------+-------------------------------------------------------------------+
| Feature           | Specification & Standards                                         |
+-------------------+-------------------------------------------------------------------+
| Streaming Protocol| RTSP (Real Time Streaming Protocol), ONVIF Profile S              |
| Video Codecs      | H.264 / H.265                                                     |
| Main Stream       | RTSP Port 554: `/stream1` (High Resolution: 1080p / 2K / 4K)       |
| Sub Stream        | RTSP Port 554: `/stream2` (Low Resolution: 640×360 for AI Detect) |
| Audio             | Two-way audio (G.711 / AAC / PCM)                                 |
| Connection Limits | Max 2 simultaneous direct RTSP connections (go2rtc solves this)   |
| Privacy Mode      | Physical / software privacy shutter supported                     |
+-------------------+-------------------------------------------------------------------+
```

---

## ⚙️ 2. Step 1: Enable Local RTSP in the Tapo App

To access your camera without cloud dependencies:

1. Open the **Tapo App** on your smartphone.
2. Tap your camera → **Settings (Gear Icon)** → **Advanced Settings**.
3. Select **Camera Account**.
4. Create a dedicated local username and password (e.g. Username: `lilybaby`, Password: `YourStrongPassword123`).
   > [!IMPORTANT]
   > This is a separate, local-only account created on the camera itself. Do **not** use your TP-Link cloud account email.
5. In your Wi-Fi router, assign a **Static DHCP Reservation** for the camera IP (e.g. `192.168.30.50` or `192.168.1.50`).

---

## 🏗️ 3. Where Does Frigate Live?

You have two clean options in your Proxmox setup:

```mermaid
graph TD
    subgraph "Option A: Home Assistant OS VM (Simplest)"
        HA_VM["🏠 VM 100: Home Assistant OS"]
        FRIGATE_ADDON["🛡️ Frigate Add-on (Official HAOS Store)"]
        HA_VM --- FRIGATE_ADDON
    end

    subgraph "Option B: Dedicated Proxmox LXC (Maximum Isolation)"
        FRIGATE_LXC["🛡️ CT 107: Dedicated Frigate LXC / Docker"]
        HA_VM2["🏠 VM 100: Home Assistant OS"]
        FRIGATE_LXC <-->|MQTT / Webhooks| HA_VM2
    end

    TAPO["📹 Tapo Camera (RTSP /stream1 & /stream2)"] --> FRIGATE_ADDON
    TAPO --> FRIGATE_LXC
```

### Option A: As a Home Assistant OS Add-on (Recommended for simplicity)
* **How it works**: Go to Home Assistant → **Settings** → **Add-ons** → Install **Frigate NVR**.
* **Pros**: 1-click updates, seamless single-dashboard access inside the Home Assistant sidebar.
* **Cons**: Consumes RAM inside the HAOS VM.

### Option B: As a Dedicated Proxmox LXC Container
* **How it works**: Deploy a standalone Docker LXC container running Frigate, with direct bind-mount to `/mnt/storage4tb/data/media/recordings` on your 4TB HDD and GPU hardware acceleration (`/dev/dri/renderD128`).
* **Pros**: If Frigate crashes or processes heavy AI detection, Home Assistant is 100% unaffected.

---

## ⚡ 4. Complete `frigate.yml` Configuration for Tapo

```yaml
mqtt:
  enabled: true
  host: 192.168.1.100 # IP of your Home Assistant Mosquitto MQTT broker
  user: mqtt_user
  password: mqtt_password

# Use go2rtc as the stream multiplexer to solve Tapo's 2-connection limit
go2rtc:
  streams:
    nursery_cam:
      - rtsp://lilybaby:YourStrongPassword123@192.168.1.50:554/stream1 # High-Res Recording
    nursery_cam_sub:
      - rtsp://lilybaby:YourStrongPassword123@192.168.1.50:554/stream2 # Low-Res AI Detect

# Hardware Acceleration with AMD Radeon 660M
ffmpeg:
  hwaccel_args: preset-vaapi

cameras:
  nursery_cam:
    ffmpeg:
      inputs:
        # 1. Recording role from High-Res stream
        - path: rtsp://127.0.0.1:8554/nursery_cam
          roles:
            - record
        # 2. Detection role from Low-Res stream (saves 80% CPU!)
        - path: rtsp://127.0.0.1:8554/nursery_cam_sub
          roles:
            - detect
    detect:
      enabled: true
      width: 640
      height: 360
      fps: 5
    record:
      enabled: true
      retain:
        days: 7
        mode: motion
      events:
        retain:
          default: 14
          mode: active_objects

# Detect humans / motion in crib
objects:
  track:
    - person
```

---

## 🔒 5. Zero-Cloud Privacy Lockdown

Once configured:
1. In your router firewall, block the Tapo camera's IP (`192.168.1.50`) from accessing the Internet (WAN Outbound: `DROP`).
2. Frigate and Home Assistant will continue streaming locally via RTSP with **zero latency** and **100% privacy**.
