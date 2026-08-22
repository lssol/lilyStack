# Acquired Hardware Inventory & Rules

## Instructions
- Always reference and prioritize the user's acquired equipment.
- Automatically research and record complete hardware specifications, ports, standards, upgrade potential, OS quirks, and tweaks whenever new hardware is purchased.

## Acquired Equipment

### 1. Central Compute & Home Assistant Hub
* **Device**: **CHUWI UBox Mini PC**
* **Processor**: AMD Ryzen 5 6600H (6 Cores / 12 Threads, Base 3.3 GHz, Boost 4.5 GHz, Zen 3+, 6nm TSMC)
* **Graphics**: AMD Radeon 660M (RDNA 2, 6 CUs @ 1900 MHz, VCN 3.1 4K/8K AV1/HEVC hardware decoding)
* **Memory**: 16 GB DDR5 4800 MHz (2x SO-DIMM slots, upgradeable to 64 GB)
* **Storage**: 512 GB PCIe NVMe SSD (2x M.2 2280 slots, upgradeable to 2x 2TB, magnetic tool-free lid)
* **Ports**:
  * 1x USB4 Type-C (40 Gbps, DisplayPort 1.4 Alt-Mode 4K@240Hz, Power Delivery)
  * 3x USB 3.2 Gen 2 Type-A (10 Gbps)
  * 1x USB 2.0 Type-A
  * 1x HDMI 2.1 TMDS (4K@144Hz)
  * 1x DisplayPort 1.4 (4K@144Hz)
  * 2x RJ45 Gigabit/2.5G Ethernet Ports (Realtek RTL8125/RTL8111)
  * 1x 3.5mm Headphone/Microphone Audio Jack
* **Power & Thermals**: 19V / 4.74A (90W DC), Idle: 8W–12W, Max: ~65W, 650g
* **Critical BIOS Tweaks**:
  * Unhide advanced menus: Press **`Alt + F5`** in BIOS.
  * Virtualization: Enable **`SVM Mode`** and **`IOMMU`**.
  * Outage Recovery: Enable **`State After G3: Power On`**.
  * Noise control: Set TDP to **`35W Quiet/Balanced`**.
* **Documentation**: See [`docs/hardware/chuwi-ubox-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/chuwi-ubox-guide.md).

### 2. External Storage & NAS
* **Device**: **4TB External USB HDD**
* **Connection**: Attached via rear USB 3.2 Gen 2 (10 Gbps) port.
* **Purpose**: Network storage (Samba/NFS), Jellyfin media library, and local photo backup pool.

### 3. Dual-Radio Zigbee & Thread Network Coordinator
* **Device**: **SMLIGHT SLZB-MR2U** (Purchased via Domadoo.fr)
* **SoC 1 (Zigbee 3.0)**: Texas Instruments CC2652P (+20 dBm PA, Z-Stack 3.x coordinator firmware)
* **SoC 2 (Thread / Matter)**: Silicon Labs EFR32MG21 (+20 dBm PA, OpenThread Border Router - OTBR)
* **Host Microcontroller**: ESP32-S3 (Dual-Core 240 MHz, 16 MB Flash, 8 MB PSRAM, 2.5 MB high-speed RAM buffer)
* **Network & Connectivity**:
  * 10/100 Mbps RJ45 Ethernet (W5500 SPI)
  * Wi-Fi (802.11 b/g/n fallback)
  * USB-C 2.0 (Data, Passthrough, & Power)
  * USB-over-IP passthrough (allows attaching secondary USB dongles across the network)
* **Power**: IEEE 802.3af PoE (Active Power over Ethernet) + USB-C (optoelectronic isolation allows dual connection)
* **Antennas**: 2x +5 dBi external rotatable SMA high-gain omnidirectional antennas
* **Operating OS & Management**: SLZB-OS web interface, 1-click web OTA firmware updater for ESP32, TI CC2652P, and Silabs EFR32MG21.
* **Key Architecture Benefit**: Separates Zigbee and Thread onto independent physical silicon, eliminating single-chip multi-PAN latency and packet drops. Connected via Ethernet PoE to avoid USB 3.0 EMI interference from the CHUWI UBox mini PC and external hard drives.
* **Documentation**: See [`docs/hardware/smlight-slzb-mr2u-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/smlight-slzb-mr2u-guide.md).

### 4. Smart Nursery Audio & Sound
* **Device**: **IKEA SYMFONISK Bookshelf Speaker** (Gen 2 - Sonos Platform)
* **Acoustics**: Custom Sonos woofer & tweeter + dual Class-D digital amplifiers
* **Integration**: Auto-discovered by Home Assistant native Sonos integration
* **Usage**: Plays uncompressed continuous brown noise loop locally hosted on HA/UBox. Nighttime volume capped at 25% (~50-55 dBA).
* **Documentation**: See [`docs/hardware/symfonisk-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/symfonisk-guide.md).

### 5. Local Smart Nursery Camera
* **Device**: **TP-Link Tapo Camera**
* **Streams**: Dual RTSP streams (`/stream1` High-Res recording + `/stream2` Low-Res AI detect)
* **Local Control**: Local camera account created on device; 100% WAN blockable at router firewall
* **Integration**: Frigate NVR + go2rtc for sub-200ms WebRTC live streaming in Home Assistant
* **Documentation**: See [`docs/hardware/tapo-camera-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/tapo-camera-guide.md).

---

## 🚀 Server Workload & Service Scope
The CHUWI UBox host is dedicated to running:
1. **Home Automation & Smart Nursery**: Home Assistant OS + Baby Buddy PostgreSQL + go2rtc + ESPHome.
2. **OpenCode Dev Server**: Remote development environment (`devbox`).
3. **NAS & File Sharing**: Samba/NFS server sharing the 4TB USB HDD.
4. **Media Stack**: Gluetun VPN + Radarr + Sonarr + Bazarr + qBittorrent + Jellyfin (VA-API hardware transcoding).
5. **Frigate NVR**: AI object/motion detection using Tapo `/stream2` and recording `/stream1` to 4TB HDD.
6. **Photo Sync**: Immich (deferred/optional).
