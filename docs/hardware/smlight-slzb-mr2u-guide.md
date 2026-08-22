# 📡 SMLIGHT SLZB-MR2U: Dual-Radio Zigbee & Thread Coordinator Reference Guide

> Complete hardware teardown, network architecture, Home Assistant integration (ZHA/Zigbee2MQTT + Matter/Thread), RF channel coexistence planning, and SLZB-OS configuration guide for the **SMLIGHT SLZB-MR2U**.

---

## 📊 1. Full Hardware Specifications & Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                 SMLIGHT SLZB-MR2U DUAL-RADIO COORDINATOR                          |
+----------------------+----------------------------------------------------------------------------+
| Component            | Detailed Technical Specification                                           |
+----------------------+----------------------------------------------------------------------------+
| Radio SoC 1 (Zigbee) | Texas Instruments CC2652P (ARM Cortex-M4F @ 48 MHz)                       |
|                      | • Output Power: +20 dBm hardware power amplifier (PA)                      |
|                      | • Firmware: Z-Stack 3.x coordinator firmware (Zigbee 3.0 / Zigbee2MQTT)    |
|                      | • Capacity: Up to 200+ direct Zigbee children & unlimited via routers      |
+----------------------+----------------------------------------------------------------------------+
| Radio SoC 2 (Thread) | Silicon Labs EFR32MG21 (ARM Cortex-M33 @ 80 MHz)                          |
|                      | • Output Power: +20 dBm hardware power amplifier (PA)                      |
|                      | • Firmware: OpenThread RCP (Radio Co-Processor) for Matter over Thread    |
|                      | • Capacity: Full OpenThread Border Router (OTBR) integration               |
+----------------------+----------------------------------------------------------------------------+
| Core Host Controller | Espressif ESP32-S3 (Dual-Core Xtensa LX7 @ 240 MHz)                        |
|                      | • Flash: 16 MB SPI Flash                                                   |
|                      | • PSRAM: 8 MB Octal PSRAM                                                  |
|                      | • Dedicated Buffer RAM: 2.5 MB ("U" series enhanced packet buffer)         |
|                      | • OS: SLZB-OS with responsive Web UI, WebSocket, and REST API              |
+----------------------+----------------------------------------------------------------------------+
| Networking           | W5500 SPI Hardwired Ethernet (10/100 Mbps)                                  |
|                      | • Fallback: Wi-Fi 802.11 b/g/n (2.4 GHz)                                   |
+----------------------+----------------------------------------------------------------------------+
| Power Supply         | Dual Power Support with Optoelectronic Isolation:                          |
|                      | 1. IEEE 802.3af PoE (Active Power over Ethernet, 36V–57V)                  |
|                      | 2. USB Type-C 5V @ 1A                                                      |
+----------------------+----------------------------------------------------------------------------+
| Antennas             | 2x External +5 dBi SMA Rotatable Omnidirectional High-Gain Antennas       |
|                      | • Antenna 1: Dedicated to TI CC2652P (Zigbee)                              |
|                      | • Antenna 2: Dedicated to Silabs EFR32MG21 (Thread)                        |
+----------------------+----------------------------------------------------------------------------+
| Passthrough Features | USB-over-IP (TCP/IP serial forwarder for secondary USB dongles)            |
| Status Indicators    | Multi-color status LEDs (Power, Ethernet, Zigbee TX/RX, Thread TX/RX)      |
| Dimensions / Weight  | ~160 × 24 × 22 mm (excluding antennas) | ~95g                             |
+----------------------+----------------------------------------------------------------------------+
```

---

## 🎯 2. Why the SLZB-MR2U Makes 100% Sense for BabyStack

The decision to choose the **SMLIGHT SLZB-MR2U** from Domadoo.fr is the optimal architectural choice for the following reasons:

### 1. Dual Independent Silicon vs Flawed Single-Chip "Multiprotocol"
* **The Single-Chip Problem**: First-generation combo dongles (like SkyConnect or Sonoff Dongle-E running Silicon Labs Multi-PAN RCP firmware) force a single 2.4 GHz radio to rapidly time-slice between Zigbee packets and Thread packets. In practice, this causes:
  * High latency spikes under sensor traffic.
  * Dropped Zigbee pairing events.
  * Frequent coordinator crashes requiring daemon restarts (Nabu Casa even paused recommending Multi-PAN).
* **The Dual Silicon Solution**: The SLZB-MR2U houses **two separate, dedicated chips**:
  * **TI CC2652P** runs purely Zigbee 3.0.
  * **Silabs EFR32MG21** runs purely OpenThread / Matter.
  * Both operate simultaneously at full +20 dBm TX power without stealing bandwidth or interrupting each other.

```
       +-------------------------------------------------------------+
       |                      SMLIGHT SLZB-MR2U                      |
       |                                                             |
       |  +--------------------+             +--------------------+  |
       |  |  TI CC2652P SoC    |             | Silabs EFR32MG21   |  |
       |  | (Pure Zigbee 3.0)  |             | (Pure Thread/Matter|  |
       |  +---------+----------+             +---------+----------+  |
       |            |                                  |             |
       |    Antenna 1 (+5dBi)                  Antenna 2 (+5dBi)     |
       |            |                                  |             |
       |       [Zigbee Mesh]                    [Thread Mesh]        |
       |   (IKEA PARASOLL, VALLHORN,         (IKEA KAJPLATS bulbs,   |
       |    SOMRIG, VINDSTYRKA, etc.)         Eve Matter sensors)    |
       +------------+----------------------------------+-------------+
                    |                                  |
                    +----------------+-----------------+
                                     |
                          [ ESP32-S3 Host Controller ]
                                     |
                         [ W5500 PoE Ethernet Port ]
                                     |
                                (CAT6 Cable)
                                     |
                     [ Home Assistant (Proxmox/CHUWI) ]
                     - Zigbee2MQTT / ZHA (Port 8253)
                     - OpenThread Border Router (Port 8081)
```

---

### 2. Elimination of USB 3.0 High-Frequency EMI Interference
* The CHUWI UBox mini PC runs high-speed **USB 3.2 Gen 2 (10 Gbps)** ports and is connected to an external **4TB USB HDD**.
* USB 3.0 data lines radiate broadband RF noise centered around **2.4 GHz to 2.5 GHz**, which can drown out weak Zigbee/Thread battery sensor signals within a 1–2 meter radius.
* **The Ethernet Fix**: Using the SLZB-MR2U over Ethernet allows you to place the coordinator anywhere in the home (e.g., centrally in the hallway, near the nursery, or on the ceiling via PoE) with **zero USB interference** and without running long, fragile USB extension cables.

---

### 3. Stability in Virtualized Environments (Proxmox VE)
* Direct USB passthrough in Proxmox VE can occasionally drop or re-enumerate with different device paths (`/dev/ttyUSB0` vs `/dev/ttyUSB1`) upon host reboot.
* With the SLZB-MR2U connected over IP (`socket://192.168.1.50:8253`), the connection is a reliable TCP socket. If the Proxmox VM reboots or migrates, it immediately re-establishes the TCP stream without touching host USB drivers.

---

### 4. The "U" (Upgraded) Series Advantage
* **2.5 MB Buffer Memory**: Dramatically reduces buffer overruns when dozens of sensors broadcast simultaneously (e.g., during sudden nursery motion or rapid climate changes).
* **USB-over-IP Passthrough**: The rear USB port on the SLZB-MR2U can forward additional serial peripherals (such as a 433MHz radio or Z-Wave stick) over the network directly into Home Assistant.

---

## 📡 3. Coexistence & RF Frequency Planning

To ensure complete interference-free operation between **Zigbee**, **Thread**, and **Home Wi-Fi (2.4 GHz)**, configure your channels according to this frequency plan:

```
2.4GHz Spectrum Coexistence Plan:

Wi-Fi Channel 1 (2412 MHz): [=========== Wi-Fi ===========]
Thread Channel 15 (2425 MHz):         [--- Thread ---]

Wi-Fi Channel 6 (2437 MHz):           [=========== Wi-Fi ===========]

Zigbee Channel 25 (2475 MHz):                                           [--- Zigbee ---]
Wi-Fi Channel 11 (2462 MHz):                                  [=========== Wi-Fi ===========]
```

### Recommended Channel Settings:
1. **Home Wi-Fi 2.4 GHz**: Lock router to **Channel 1** (or Channels 1 & 6).
2. **SLZB-MR2U Zigbee (TI CC2652P)**: Set Zigbee2MQTT / ZHA to **Channel 25** (2475 MHz).
   * *Why Channel 25?* It sits in the clear gap above Wi-Fi Channel 11 and does not collide with Wi-Fi Channels 1 or 6.
3. **SLZB-MR2U Thread (Silabs EFR32MG21)**: Set OpenThread to **Channel 15** (2425 MHz).
   * Sits cleanly between Wi-Fi Channel 1 and Wi-Fi Channel 6 side lobes.

---

## ⚙️ 4. Step-by-Step Configuration Runbook

### Step 1: Physical Placement & Power
1. Screw the two +5 dBi omnidirectional antennas securely into Antenna Ports 1 and 2.
2. Plug an Ethernet cable into the RJ45 port connected to your PoE switch (or standard switch with USB-C 5V power supplied).
3. The power and link LEDs will illuminate. The device obtains an IP address via DHCP.

### Step 2: Accessing SLZB-OS Web Management
1. In your web browser, navigate to:
   ```
   http://slzb-mr2u.local/
   # Or find the assigned IP (e.g., http://192.168.1.50) via your router client list
   ```
2. Set a static IP reservation in your router for the device's MAC address.
3. In SLZB-OS:
   * Navigate to **General Settings** → Set Device Name (e.g., `BabyStack-Coordinator`).
   * Navigate to **Radio 1 (CC2652P)** → Set Mode to **Zigbee to Ethernet (TCP)** → Port `8253`.
   * Navigate to **Radio 2 (EFR32MG21)** → Set Mode to **OpenThread RCP (TCP)** → Port `8081`.

---

### Step 3: Integrating Zigbee with Home Assistant

#### Option A: Zigbee2MQTT (Recommended for IKEA Hardware)
In your `docker-compose.yml` or Zigbee2MQTT Add-on configuration:

```yaml
serial:
  port: tcp://192.168.1.50:8253
  adapter: zstack
advanced:
  channel: 25
  pan_id: 0x1a62
  ext_pan_id: [0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd, 0xdd]
```

#### Option B: ZHA (Zigbee Home Automation Built-in)
1. Go to **Settings** → **Devices & Services** → **Add Integration** → **Zigbee Home Automation (ZHA)**.
2. Select **Radio type**: `TI CC2652 / CC1352 / CC2538 (zstack)`.
3. Serial port settings:
   * **Serial Device Path**: `socket://192.168.1.50:8253`
   * **Port speed**: `115200`
   * **Data flow control**: `software`

---

### Step 4: Integrating Thread / Matter (OpenThread Border Router)
1. In Home Assistant, install the **OpenThread Border Router (OTBR)** Add-on.
2. In the OTBR Add-on configuration, set the device path to Radio 2's TCP stream:
   ```yaml
   device: tcp://192.168.1.50:8081
   baudrate: 460800
   flow_control: false
   ```
3. Start the Add-on. Home Assistant will discover the Thread network and allow commissioning **Matter-over-Thread** devices (such as IKEA KAJPLATS bulbs and Eve sensors) directly from your smartphone via the Home Assistant Companion App.

---

## 🔄 5. Web OTA Firmware Management

SLZB-OS includes built-in 1-click web flashing for all components without needing external programmers:
1. **ESP32-S3 Core Firmware**: Updates the SLZB-OS interface, Ethernet drivers, and USB-over-IP stack.
2. **TI CC2652P Firmware**: Updates the Zigbee coordinator Z-Stack firmware (from Koenkk repository) directly from the browser.
3. **Silabs EFR32MG21 Firmware**: Updates the Silicon Labs OpenThread RCP firmware via the web interface.

> [!TIP]
> Always create a backup of your Zigbee network (`coordinator_backup.json`) via the Zigbee2MQTT or ZHA interface before performing firmware updates on the TI CC2652P radio.
