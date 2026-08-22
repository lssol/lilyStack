# 🖥️ CHUWI UBox Mini PC: Comprehensive Hardware, Linux & Proxmox Reference

> Complete technical teardown, port standards, BIOS configuration, Linux/Proxmox quirks, and optimization guide for the **CHUWI UBox (AMD Ryzen 5 6600H)** as BabyStack's central server.

---

## 📊 1. Full Hardware Specifications & Teardown

```
+---------------------------------------------------------------------------------------+
|                                CHUWI UBOX MINI PC (R5 6600H)                          |
+-------------------+-------------------------------------------------------------------+
| Component         | Detailed Technical Specification                                  |
+-------------------+-------------------------------------------------------------------+
| Processor (CPU)   | AMD Ryzen 5 6600H (Zen 3+, 6nm TSMC)                              |
|                   | • 6 Cores / 12 Threads (Base 3.3 GHz, Boost up to 4.5 GHz)        |
|                   | • 16 MB L3 Cache, 3 MB L2 Cache                                   |
|                   | • TDP: 45W default (Configurable 35W–54W in BIOS)                 |
+-------------------+-------------------------------------------------------------------+
| Graphics (iGPU)   | AMD Radeon 660M (RDNA 2 Architecture)                             |
|                   | • 6 Compute Units (CUs) @ 1900 MHz                                |
|                   | • VCN 3.1 Hardware Decode: H.264, HEVC (10-bit), VP9, AV1 (4K/8K) |
|                   | • VA-API / Vulkan / ROCm accelerated media decoding               |
+-------------------+-------------------------------------------------------------------+
| Memory (RAM)      | 16 GB DDR5 4800 MHz (SO-DIMM)                                     |
|                   | • 2x DDR5 SO-DIMM slots (Supports up to 64 GB: 2x 32GB)           |
|                   | • Dual-channel bandwidth support                                  |
+-------------------+-------------------------------------------------------------------+
| Storage (NVMe)    | 512 GB PCIe M.2 2280 NVMe SSD                                     |
|                   | • 2x M.2 2280 PCIe NVMe slots (Supports up to 2x 2TB)              |
|                   | • Tool-free magnetic top lid for fast drive access                |
+-------------------+-------------------------------------------------------------------+
| Wireless & BT     | Wi-Fi 6 / 6E (802.11ax) + Bluetooth 5.2 / 5.3 (M.2 2230 swappable)|
+-------------------+-------------------------------------------------------------------+
| Networking (LAN)  | Dual RJ45 Ethernet Ports (2.5 GbE / 1 GbE Realtek RTL8125/RTL8111)|
+-------------------+-------------------------------------------------------------------+
| Power Supply      | 19V / 4.74A (90W–95W) DC Barrel Adapter                           |
+-------------------+-------------------------------------------------------------------+
| Dimensions/Weight | ~128 × 128 × 48 mm | 650g                                         |
+-------------------+-------------------------------------------------------------------+
```

---

## 🔌 2. Complete Port Layout & Supported Standards

```
Front Panel:
[ 🔘 Power ]  [ 🎧 3.5mm Audio ]  [ ⚡ USB4 Type-C (40Gbps/PD/DP) ]  [ 🔵 USB 3.2 Gen2 ]  [ 🔵 USB 3.2 Gen2 ]

Rear Panel:
[ 🔌 DC-In 19V ]  [ 🌐 LAN 1 (2.5G) ]  [ 🌐 LAN 2 (2.5G/1G) ]  [ 🖥️ DP 1.4 ]  [ 📺 HDMI 2.1 ]  [ 🔵 USB 3.2 Gen2 ]  [ ⚫ USB 2.0 ]
```

### Detailed Port Standards:
1. **Front USB4 Type-C**:
   * **Data Speed**: Up to 40 Gbps.
   * **Display Output**: DisplayPort 1.4 Alt-Mode (Supports up to **4K @ 240Hz** or **8K @ 60Hz**).
   * **Power Delivery (PD)**: Supports bidirectional USB-PD (can be powered via high-wattage 100W PD charger).
2. **Video Outputs (Triple 4K Display Capable)**:
   * **1x HDMI 2.1 TMDS**: Up to 4K @ 144Hz.
   * **1x DisplayPort 1.4**: Up to 4K @ 144Hz.
   * **1x USB-C Alt Mode**: Up to 4K @ 240Hz.
3. **USB-A Ports**:
   * **3x USB 3.2 Gen 2 (10 Gbps)**: 2 on front, 1 on rear (fast external SSD backups).
   * **1x USB 2.0 (480 Mbps)**: 1 on rear (best for legacy peripherals or USB coordinator isolation).
4. **Networking**:
   * **2x RJ45 Gigabit/2.5G Ethernet Ports**: Enables physical isolation between your main home network and the IoT/BabyStack isolated subnet without requiring a managed switch.
5. **Audio**:
   * **1x 3.5mm combo jack** (stereo output + microphone input).

---

## 🛠️ 3. Upgrade Potential & Internal Access

* **Tool-Free Magnetic Top Cover**: The upper panel lifts off magnetically without screws, allowing 10-second access to RAM and M.2 storage.
* **RAM Expansion**: Comes with 16GB DDR5. Supports standard **DDR5 4800MHz / 5600MHz SO-DIMM** modules up to **64 GB (2x 32GB)**.
  > [!TIP]
  > If your unit arrives with 1x 16GB stick (single-channel), adding a second matching 16GB DDR5 SO-DIMM stick enables **dual-channel memory**, providing a ~25–30% boost to the Radeon 660M iGPU transcoding throughput.
* **Dual M.2 NVMe Slots**:
  * **Slot 1**: 512 GB NVMe SSD (pre-installed, boots OS / Proxmox).
  * **Slot 2**: Free M.2 2280 PCIe NVMe slot (can drop in a 1TB/2TB SSD for Frigate NVR 24/7 video recording buffer or a ZFS mirror pool).
* **Wi-Fi Module**: Standard M.2 2230 form factor; can be upgraded to an Intel AX210 / BE200 if needed.

---

## ⚡ 4. Power Consumption & Thermal Behavior

| System State | Power Draw (at Wall) | Fan Noise Profile |
| :--- | :--- | :--- |
| **Idle (Home Assistant OS / Proxmox)** | **8W – 12W** | Near-silent / Inaudible (< 25 dB) |
| **Moderate Load (WebRTC transcoding + Baby Buddy)** | **18W – 28W** | Gentle hum (~30 dB) |
| **Full Stress / Max Compute (Frigate AI + Compilation)** | **55W – 68W** | Audible fan airflow (~38–42 dB) |

---

##  BIOS & Firmware Configuration Guide

### 1. Unlocking the "Hidden" Advanced BIOS Menu
Chuwi mini PCs ship with a simplified AMI BIOS interface by default.
* **Shortcut to Unlock**:
  1. Power on the PC and press **`DEL`** repeatedly to enter BIOS.
  2. Press **`Alt + F5`** (or in some firmware versions, **`Fn + Alt + F5`**).
  3. The BIOS will refresh, exposing hidden **Advanced**, **AMD CBS**, **AMD PBS**, and **Power** configuration tabs.

### 2. Mandatory BIOS Settings for 24/7 Server Deployment
1. **Disable Secure Boot**:
   * `Security` → `Secure Boot` → Set to **`Disabled`** (Required for Proxmox VE / HAOS bootloaders).
2. **Enable Virtualization (AMD SVM & IOMMU)**:
   * `Advanced` → `CPU Configuration` → **`SVM Mode: Enabled`**.
   * `Advanced` → `AMD CBS` → `NBIO Common Options` → **`IOMMU: Enabled`**.
3. **Automatic Restart on Power Outage (Auto-Power-On)**:
   * `Advanced` / `Chipset` → `State After G3` (or `Restore on AC Power Loss`) → Set to **`Power On`**.
   * *Why?* Guarantees that if a blackout occurs in the middle of the night, the nursery monitoring system boots right back up automatically as soon as mains power returns.
4. **Quiet Fan & TDP Tuning**:
   * `AMD CBS` → `NBIO Options` → `System Configuration / TDP` → Set to **`35W (Quiet/Balanced)`**.
   * Reduces thermal spikes and fan pulsing while maintaining 95%+ of CPU performance.

---

## 🐧 6. Linux, Proxmox & Home Assistant Compatibility Matrix

```
+-------------------------------------------------------------------------+
|                    OS COMPATIBILITY & TWEAKS MATRIX                     |
+-----------------------+------------+------------------------------------+
| Operating System      | Status     | Notes & Recommended Settings       |
+-----------------------+------------+------------------------------------+
| Proxmox VE 8.x        | ⭐ Ideal   | Linux 6.5/6.8 kernel. Native RDNA2 |
| (Debian 12 Bookworm)  |            | amdgpu and RTL8125 2.5G support.   |
| --------------------- | ---------- | ---------------------------------- |
| Bare-Metal HAOS x86   | ✅ Verified| Flash generic-x86-64 image directly|
|                       |            | to NVMe via Ubuntu Live USB.       |
| --------------------- | ---------- | ---------------------------------- |
| Ubuntu Server 24.04   | ✅ Native  | Full hardware support out-of-box.  |
+-----------------------+------------+------------------------------------+
```

### Known Linux Quirks & Fixes:

#### 1. Hardware Video Transcoding (VA-API with Radeon 660M)
The Ryzen 5 6600H includes AMD's **VCN 3.1** hardware video engine. To pass it to Proxmox LXC containers (for go2rtc, Frigate, or Jellyfin):
```bash
# Verify render node in Proxmox host
ls -l /dev/dri/renderD128

# Add to your Proxmox LXC container configuration (/etc/pve/lxc/<CTID>.conf):
lxc.cgroup2.devices.allow: c 226:128 rwm
lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file
```

#### 2. PCIe ASPM & Network Link Stability
If using high-bandwidth 2.5GbE transfers on Linux kernel <6.5, prevent Realtek sleep drops by adding the following to `/etc/default/grub`:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet amdgpu.sg_display=0 pcie_aspm=off"
```
Then run `update-grub`.

#### 3. Zigbee RF Isolation Reminder
Even though the UBox is compact, **never plug a USB 3.0 Zigbee dongle directly into the rear USB ports**. The dual RJ45 ports allow using the **SMLIGHT SLZB-MR2U network coordinator**, eliminating RF interference entirely.
