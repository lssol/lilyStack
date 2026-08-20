# 🛠️ Smart Nursery Installation & Setup Guide

This guide walks you through physical room babyproofing, sensor placement, network isolation, and software configuration for Lily's nursery.

---

## 📐 Step 1: Physical Room Layout & Babyproofing

```
+-------------------------------------------------------------+
|                                                             |
|   [ Nursery Window ] (Zigbee Contact Sensor)                |
|                                                             |
|   +-------------------+                                     |
|   |                   |      [ mmWave Radar ]               |
|   |    Lily's Crib    |      (Corner Wall-Mount @ 2m)       |
|   |                   |                                     |
|   +-------------------+                                     |
|     * Temp/Humidity LCD                                     |
|       (Wall @ 1m height)                                    |
|                                                             |
|   =======================================================   |
|   🚫 3-FOOT (1-METER) CORD SAFETY ZONE AROUND CRIB RAILS   |
|   =======================================================   |
|                                                             |
|   [ Changing Table ]                  [ Glider Chair ]      |
|   - IKEA Air Quality Sensor           - Floor Lamp (Red RGB)|
|   - Diaper Log NFC Tag                - 4-Button Controller |
|                                       - Feeding NFC Tag     |
|                                                             |
|   [ Nursery Door ]                                          |
|   (Contact Sensor)                                          |
+-------------------------------------------------------------+
```

### 1.1 The 3-Foot (1-Meter) Cord Safety Perimeter
> [!CAUTION]
> **Strangulation Hazard Prevention**: 
> * Never hang cameras, audio monitors, or sensor wires directly over or inside the crib.
> * Every single power cable in the nursery must be encased in rigid wall-mounted raceways or secured firmly behind heavy furniture.
> * Anchor all heavy furniture (dressers, bookshelves, changing tables) to wall studs with anti-tip brackets.

### 1.2 Optimal Sensor & Camera Placement
* **Camera (Local RTSP)**: Mount in the top corner of the room (approx. 2.2m / 7.2ft height) angled down toward the crib. Ensure the camera has a clear line of sight while remaining completely unreachable from the crib.
* **Temperature & Humidity Sensor**: Mount on the wall at mattress height (approx. 1 meter off the floor), on an **interior wall**. Avoid placing it directly next to windows, heating vents, or in direct sunlight.
* **mmWave Presence Sensor**: Mount at 1.8m–2.0m height in an upper corner angled 45° downward toward the crib mattress. In the configuration app, set the detection zone boundary strictly around the crib to ignore curtains or ceiling fans.
* **Air Quality Sensor**: Place on the changing table or dresser shelf where adult breathing and room airflow are well-represented.

---

## 🔒 Step 2: Network & Security Architecture

To guarantee 100% privacy, the nursery camera must never communicate with external cloud servers.

```mermaid
graph LR
    subgraph "Router / Firewall"
        VLAN_IOT["IoT VLAN (Subnet 192.168.30.0/24)"]
        WAN["🌍 Internet (WAN)"]
    end

    CAM["📹 Nursery RTSP Camera"] -->|192.168.30.50| VLAN_IOT
    VLAN_IOT -.->|🚫 BLOCKED: Outbound WAN Rule| WAN
    VLAN_IOT -->|Local RTSP Port 554| HA["🏠 Home Assistant (192.168.10.10)"]
    HA -->|Encrypted WebRTC| PARENT["📱 Parent Phones & Tablet"]
```

### 2.1 Router / Firewall Rule Configuration
1. Assign the camera to your **IoT VLAN** or set a static DHCP reservation.
2. In your router settings (UniFi, OPNsense, pfSense, or Asus/TP-Link parental controls), create an **Outbound Firewall Rule**:
   * **Source**: `192.168.30.50` (Camera IP)
   * **Destination**: `Any (WAN / 0.0.0.0/0)`
   * **Action**: `REJECT / DROP`
3. **Verify**: Open the camera's cloud manufacturer app (Reolink/Tapo) on 4G cellular data (disconnected from Wi-Fi). The camera should report **Offline / Unreachable**, while still streaming smoothly in Home Assistant on your local network.

### 2.2 Low-Latency Streaming with `go2rtc`
In Home Assistant, install the **go2rtc** add-on or integration. Add the local RTSP feed in `go2rtc.yaml`:

```yaml
streams:
  lily_crib:
    - rtsp://admin:YourSecurePassword123@192.168.30.50:554/h264Preview_01_main
    - "ffmpeg:lily_crib#audio=opus#video=copy"
```
*Benefits*: Reduces streaming latency from 4–6 seconds (standard HLS) to **under 200 milliseconds** via WebRTC.

---

## ⚙️ Step 3: Home Assistant & Zigbee Setup

### 3.1 Zigbee Coordinator Optimization
* Plug your Zigbee USB coordinator (Sonoff ZBDongle-E or SkyConnect) into the Home Assistant host using a **1-meter (3ft) USB 2.0 extension cable**.
* *Why?* USB 3.0 ports emit broadband RF noise in the 2.4 GHz spectrum that severely degrades Zigbee signals. The extension cable physically isolates the antenna.
* Set your Zigbee channel to **Channel 25** (which sits in the guard-band between common Wi-Fi Channels 1, 6, and 11).

### 3.2 Pairing IKEA Zigbee Devices (ZHA / Zigbee2MQTT)
Pair all mains-powered devices (IKEA TRÅDFRI bulbs, INSPELNING/TRETAKT plugs) **first** so they form your mesh router backbone before pairing battery sensors:

1. **IKEA Smart Plugs & Bulbs (Routers)**: 
   * Plugs: Press and hold the small reset pinhole button on top for 5 seconds until the LED pulses.
   * Bulbs: Toggle the physical wall switch On/Off 6 times until the bulb pulses brightness.
2. **IKEA PARASOLL Contact & VALLHORN Motion**:
   * Insert rechargeable **IKEA LADDA AAA** battery.
   * Press the pairing button inside the battery compartment 4 times rapidly. The red LED will pulse and Home Assistant ZHA will instantly discover it.
3. **IKEA SOMRIG Shortcut Button**:
   * Press the pairing button next to the battery 4 times within 5 seconds.
4. **IKEA VINDSTYRKA Air Quality**:
   * Press the small pairing button on the back 4 times rapidly.
5. **IKEA SYMFONISK Speaker**:
   * Plug into power and connect to Wi-Fi via the Sonos app once. Home Assistant will auto-discover it as a media player entity.

### 3.3 Baby Buddy Backend Installation
You can run Baby Buddy either as an official Home Assistant Add-on or via Docker Compose.

**Via Home Assistant Add-on Store:**
1. Open Home Assistant → **Settings** → **Add-ons** → **Add-on Store**.
2. Add the repository: `https://github.com/babybuddy/babybuddy` (or search community add-ons).
3. Click **Install**, set your timezone (e.g., `Europe/Paris` or `America/New_York`), and click **Start**.
4. Open the Web UI, create Lily's baby profile with her birthdate, and generate an **API Key** under User Profile.

**Via HACS Integration:**
1. Open **HACS** → Search for **Baby Buddy**.
2. Install the integration and restart Home Assistant.
3. Go to **Settings** → **Devices & Services** → **Add Integration** → **Baby Buddy**.
4. Enter `http://127.0.0.1:8000` (or your Baby Buddy container IP) and paste the API Key.
5. All of Lily's sensors (`sensor.lily_last_feed`, `sensor.lily_last_diaper_change`, `sensor.lily_last_sleep`) are now automatically available in Home Assistant.

---

## 🏷️ Step 4: Configuring 1-Tap NFC & Physical Buttons

### 4.1 NFC Sticker Programming (iOS / Android)
NFC stickers allow instantaneous, zero-screen logging at 3 AM:

1. Stick **NFC Tag 1** directly onto the corner of the changing pad.
2. Stick **NFC Tag 2** on the left arm of the glider chair ("Nursing Left").
3. Stick **NFC Tag 3** on the right arm of the glider chair ("Nursing Right").

**Configuring in Home Assistant Companion App:**
1. Open HA App on parent phone → **Settings** → **Tags** → **Add Tag**.
2. Name the tag: `Lily Changing Table NFC`.
3. Tap phone against the sticker to write the unique ID.
4. When scanned, Home Assistant triggers the automation to record a Diaper Change in Baby Buddy and send a gentle haptic confirmation to your phone.

### 4.2 Glider 4-Button Zigbee Controller Mapping
Program your physical Zigbee remote (e.g., IKEA SOMRIG or Aqara Wireless Switch) with the following parent-friendly scheme:

| Button Action | Function | Behavior |
| :--- | :--- | :--- |
| **Button 1 (Single Press)** | *Night Feed Scene* | Smoothly ramps floor lamp to 8% Deep Red (650nm) over 3 seconds. |
| **Button 1 (Double Press)** | *Diaper Change Boost* | Ramps light to 25% Warm Amber (2200K) for higher visibility during diaper changes. |
| **Button 2 (Single Press)** | *White Noise Toggle* | Turns on/off the sound machine plug. |
| **Button 2 (Long Press)** | *All Off / Sleep Mode* | Fades lights to 0% over 5 seconds and resets room to quiet sleep mode. |
