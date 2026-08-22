# 🤖 BabyStack Project Instructions & Rules

## 📦 Acquired Hardware Inventory & Tracking Protocol

### 1. Persistent Tracking Rule (Always Active)
* **Always Record Purchases & Full Hardware Details**: Whenever the user mentions having bought, ordered, or acquired a new device, component, sensor, or tool:
  1. Immediately conduct online research (YouTube, forums, spec sheets) to gather all hardware details (ports, standards, upgrade potential, Linux/Proxmox/Home Assistant quirks, reviews, BIOS tweaks).
  2. Record the item with full details into the **Acquired Hardware Table** below, in `GEMINI.md`, in `.agents/rules/hardware_inventory.md`, in [`docs/shopping-list.md`](file:///c:/Users/sacha/src/babystack/docs/shopping-list.md), and in a dedicated guide under [`docs/hardware/`](file:///c:/Users/sacha/src/babystack/docs/hardware/).
* **Context & Recommendation Filtering**: Never recommend buying an item the user already owns unless explicitly requested. Always tailor installation guides, automation code, Docker/OS setup, and troubleshooting directly to the user's exact acquired hardware specifications.

---

### 2. Acquired Hardware Table

| Component | Device / Model | Key Specifications & Standards | OS / Compatibility Notes | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Compute & HA Hub** | **CHUWI UBox Mini PC** | **CPU**: AMD Ryzen 5 6600H (6C/12T, up to 4.5 GHz, Zen 3+, 6nm)<br>• **RAM**: 16 GB DDR5 4800MHz (2x SO-DIMM up to 64GB)<br>• **Storage**: 512 GB PCIe NVMe SSD (2x M.2 2280 slots up to 2x 2TB, magnetic lid)<br>• **GPU**: AMD Radeon 660M (RDNA 2, VCN 3.1 4K/8K AV1/HEVC hardware decode)<br>• **Ports**: 1x USB4 Type-C (40Gbps/PD/DP), 3x USB 3.2 Gen2 (10Gbps), 1x USB 2.0, 1x HDMI 2.1, 1x DP 1.4, 1x 3.5mm audio<br>• **Network**: Dual RJ45 Ethernet (2.5GbE / 1GbE Realtek), Wi-Fi 6, BT 5.2<br>• **Power/Weight**: 19V DC 90W (8W–12W idle), 650g | • **Proxmox VE 8 / HAOS**: Excellent compatibility (Linux kernel 6.5+).<br>• **BIOS Unlock**: Press `Alt + F5` in BIOS for hidden AMD CBS/SVM/IOMMU menus.<br>• **Auto-Power-On**: Enable `State After G3: Power On`.<br>• **TDP Tuning**: 35W quiet mode in BIOS for silent cooling.<br>• See: [`docs/hardware/chuwi-ubox-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/chuwi-ubox-guide.md) | **Bought / Acquired ✅** |
| **Mass Storage / NAS** | **4TB External USB HDD** | Connected via USB 3.2 Gen 2 (10 Gbps) port on CHUWI UBox for Samba/NFS NAS storage, media library, and local photo backups. | • Formatted as ext4/btrfs/ZFS for Linux/Proxmox sharing. | **Acquired / Owned ✅** |
| **Zigbee & Thread Coordinator** | **SMLIGHT SLZB-MR2U** | **SoC 1 (Zigbee)**: TI CC2652P (+20dBm, Z-Stack 3.x)<br>• **SoC 2 (Thread/Matter)**: Silabs EFR32MG21 (+20dBm, OTBR)<br>• **Core MCU**: ESP32-S3 (240MHz, 16MB Flash, 8MB PSRAM, 2.5MB buffer)<br>• **Network**: 10/100 Ethernet (W5500), Wi-Fi, USB-C<br>• **Power**: IEEE 802.3af PoE & USB-C (opto-isolated)<br>• **Antennas**: 2x +5dBi external SMA antennas<br>• **Features**: Dual independent radios, USB-over-IP passthrough, SLZB-OS Web UI / OTA | • **Home Assistant**: TCP socket to ZHA/Zigbee2MQTT (port 8253) + OTBR add-on.<br>• **RF Isolation**: Ethernet/PoE eliminates USB 3.0 EMI interference from UBox & external HDD.<br>• See: [`docs/hardware/smlight-slzb-mr2u-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/smlight-slzb-mr2u-guide.md) | **Confirmed Purchase ✅ (Domadoo)** |
| **Smart Nursery Audio & Sound** | **IKEA SYMFONISK Bookshelf Speaker** | **Acoustics**: Sonos custom-tuned drivers & Class-D digital amplifiers<br>• **Connectivity**: Wi-Fi (802.11b/g/n, 2.4 GHz), 10/100 Mbps Ethernet port<br>• **Protocols**: Apple AirPlay 2, Spotify Connect, Sonos S2 platform<br>• **Dimensions/Power**: 10 x 15 x 31 cm, 2.16 kg, integrated 100–240V AC power supply | • **Home Assistant**: Auto-discovered via native Sonos integration.<br>• **Local Offline Audio**: Plays uncompressed continuous brown noise loop locally hosted on CHUWI UBox / HA without internet dependency.<br>• **Volume Safety**: Automated volume clamp at 25% (~50-55 dBA) during night hours.<br>• See: [`docs/hardware/symfonisk-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/symfonisk-guide.md) | **Acquired / Owned ✅** |
| **Local Smart Nursery Video** | **TP-Link Tapo Camera** | **Streaming**: Dual RTSP streams (`/stream1` High-Res HD/2K/4K + `/stream2` Low-Res 640x360)<br>• **Protocols**: RTSP, ONVIF Profile S, local camera account<br>• **Audio**: Two-way audio support via go2rtc / WebRTC<br>• **Night Vision**: 850nm / 940nm IR LEDs with physical privacy mode | • **Frigate / Home Assistant**: Local RTSP stream via `go2rtc` (avoids 2-stream connection limit).<br>• **Privacy**: 100% WAN blockable at router once local account is created.<br>• See: [`docs/hardware/tapo-camera-guide.md`](file:///c:/Users/sacha/src/babystack/docs/hardware/tapo-camera-guide.md) | **Acquired / Owned ✅** |

---

### 3. Architecture & Multi-Service Host Directives
The CHUWI UBox Mini PC serves as an all-in-one Virtualization / Container Host (Proxmox VE 8 or Docker):
1. **Smart Nursery & Home Automation**: Home Assistant OS VM + Baby Buddy PostgreSQL + ESPHome + go2rtc.
2. **OpenCode Dev Server**: Remote development environment / coding server.
3. **NAS & Storage**: Network-attached storage (Samba / NFS) hosting the 4TB USB HDD.
4. **Media & Automation Stack**: Gluetun VPN container routing traffic for Radarr, Sonarr, Bazarr, and qBittorrent + Jellyfin (leveraging Radeon 660M hardware VA-API video transcoding).
5. **Photo Synchronization**: Automated photo backup & sync (Immich / PhotoPrism / Nextcloud).
6. **Network & RF Setup**: Pair with the network-based **SMLIGHT SLZB-MR2U Dual-Radio Coordinator** via Ethernet PoE/LAN so the mini PC can be placed anywhere in the home without USB 3.0 RF interference on Zigbee/Thread.
