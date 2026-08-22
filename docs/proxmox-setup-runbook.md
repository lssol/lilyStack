# 🚀 Turnkey Proxmox VE 8 Setup Runbook: CHUWI UBox Mini PC

> Complete, step-by-step unboxing-to-production deployment guide formatted in your exact rollout order:
> 1. **Stage 1**: `devbox` Sandbox + RDP (macOS & Windows) + Dev Toolchain
> 2. **Stage 2**: 4TB Storage Mount & Gluetun VPN Media Stack (ARR + Jellyfin)
> 3. **Stage 3**: Smart Nursery (Home Assistant OS VM + Frigate NVR + Tapo + Baby Buddy)

---

## 🏗️ Virtualization Architecture Overview

```mermaid
graph TD
    subgraph "Proxmox VE 8 Host (CHUWI UBox: Ryzen 5 6600H / 16GB DDR5 / 512GB NVMe)"
        PVE["🖥️ Proxmox Kernel 6.8 Host (192.168.1.100:8006)"]
        USB4TB["💽 4TB USB 3.2 HDD (/mnt/storage4tb)"]
        GPU["🎮 AMD Radeon 660M (/dev/dri/renderD128)"]

        subgraph "Stage 1: Development Sandbox (7.0 GB RAM)"
            CT101["💻 LXC 101: devbox (XFCE GUI + XRDP + Docker + OpenCode)"]
        end

        subgraph "Stage 2: Storage & Media Automation (4.0 GB RAM)"
            CT102["📁 LXC 102: Samba / NFS NAS (512 MB RAM)"]
            CT103["🛡️ LXC 103: Gluetun VPN + ARR + qBittorrent (2.0 GB RAM)"]
            CT104["🍿 LXC 104: Jellyfin Media Server (1.5 GB RAM + GPU)"]
        end

        subgraph "Stage 3: Smart Nursery & Home Automation (3.0 GB RAM)"
            VM100["🏠 VM 100: Home Assistant OS (2.5 GB RAM / 2 vCPUs)"]
            CT106["👶 LXC 106: Baby Buddy + PostgreSQL (512 MB RAM)"]
            FRIGATE["🛡️ Frigate NVR (OpenVINO AI on Ryzen 6600H CPU)"]
        end
    end

    %% Storage & Hardware binds
    PVE --> USB4TB
    USB4TB -.->|Bind Mount| CT102
    USB4TB -.->|Bind Mount| CT103
    USB4TB -.->|Bind Mount| CT104
    GPU -.->|VA-API Pass| CT104
    VM100 --- FRIGATE
```

---

## 📋 Pre-Flight: Unboxing, BIOS & Proxmox VE 8 Install

### 1. BIOS Configuration (2 minutes)
1. Flash **Proxmox VE 8.x ISO** to a USB drive using BalenaEtcher / Ventoy.
2. Plug into CHUWI UBox, power on, and press **`DEL`** repeatedly.
3. Press **`Alt + F5`** (or `Fn + Alt + F5`) to unlock hidden tabs:
   * `Security` → `Secure Boot` → **`Disabled`**
   * `Advanced` → `CPU Configuration` → **`SVM Mode: Enabled`**
   * `Advanced` → `AMD CBS` → `NBIO Common Options` → **`IOMMU: Enabled`**
   * `Advanced` / `Chipset` → `State After G3` → **`Power On`** (Auto-restart on blackout)
   * `AMD CBS` → `NBIO Options` → `System Configuration / TDP` → **`35W`** (Silent fan mode)
4. Press **`F10`** to save and reboot.

### 2. Proxmox VE 8 OS Installation (5 minutes)
1. Boot installer, select internal **512GB NVMe SSD**, set timezone (`Europe/Paris`), password, and static IP (e.g. `192.168.1.100`).
2. Log into Web GUI: **`https://192.168.1.100:8006`**.
### 3. Enable ZRAM & Tailscale Subnet Router (Global Remote Access 🌍)
In the Proxmox host shell:

```bash
# 1. Enable ZRAM (Compressed RAM swap for heavy OpenCode builds)
apt update && apt install -y zram-tools && echo "PERCENT=50" >> /etc/default/zramswap && systemctl restart zramswap

# 2. Install Tailscale on the Proxmox Host
curl -fsSL https://tailscale.com/install.sh | sh

# 3. Enable IP Forwarding (Allows Tailscale to route to all containers & VMs)
echo 'net.ipv4.ip_forward = 1' | tee -a /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | tee -a /etc/sysctl.d/99-tailscale.conf
sysctl -p /etc/sysctl.d/99-tailscale.conf

# 4. Start Tailscale advertising your entire local network subnet
tailscale up --advertise-routes=192.168.1.0/24 --hostname=babystack-pve
```

* **1-Click Route Approval**:
  1. Open [login.tailscale.com/admin/machines](https://login.tailscale.com/admin/machines) on your phone/laptop.
  2. Find **`babystack-pve`** → Click **`...`** → **Edit route settings** → Check **`192.168.1.0/24`** → Save.
* **Result**: You now have seamless, encrypted access to **everything** (`devbox` RDP, Home Assistant, Proxmox GUI `:8006`, Jellyfin, Samba NAS) using their exact local IPs from anywhere in the world without opening a single router port!

---

# 🚀 STAGE 1: `devbox` Sandbox & RDP Setup (Priority #1)

Your high-performance Linux workstation with 7GB RAM and 6 CPU cores, accessible via Remote Desktop (RDP) from macOS and Windows.

### Step 1.1: Create `devbox` LXC Container (In Proxmox Host Shell)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/docker.sh)"
```
* **Interactive Prompts**:
  * CT ID: **`101`**
  * Hostname: **`devbox`**
  * Disk Size: **`60`** (GB on fast NVMe)
  * CPU Cores: **`6`**
  * RAM: **`7168`** (7.0 GB)
  * Bridge: `vmbr0` (Static IP: e.g. `192.168.1.101/24`, Gateway: `192.168.1.1`)

---

### Step 1.2: Install XFCE Desktop, XRDP & Development Toolchain
Enter the `devbox` container shell:
```bash
pct enter 101
```
Paste this complete workstation setup script:
```bash
# 1. Update & Install Desktop + XRDP + Build Tools
apt update && apt upgrade -y
apt install -y xfce4 xfce4-goodies xrdp xorgxrdp dbus-x11 sudo git curl wget htop build-essential

# 2. Configure XRDP session & certificates
echo "xfce4-session" > ~/.xsession
adduser xrdp ssl-cert

# 3. Prevent annoying polkit color-management popups on RDP login
cat <<EOF > /etc/polkit-1/localauthority/50-local.d/45-allow-colord.pkla
[Allow Colord all Users]
Identity=unix-user:*
Action=org.freedesktop.color-manager.create-device;org.freedesktop.color-manager.create-profile;org.freedesktop.color-manager.delete-device;org.freedesktop.color-manager.delete-profile;org.freedesktop.color-manager.modify-device;org.freedesktop.color-manager.modify-profile
ResultAny=no
ResultInactive=no
ResultActive=yes
EOF

# 4. Create your developer user
adduser devuser
usermod -aG sudo,docker devuser
echo "xfce4-session" > /home/devuser/.xsession
chown devuser:devuser /home/devuser/.xsession

# 5. Enable & start XRDP
systemctl enable xrdp && systemctl restart xrdp
```

---

### Step 1.3: Connecting to `devbox` via RDP

#### 🍏 From macOS (Using "Windows App" / Microsoft Remote Desktop):
1. Open **Windows App** (or **Microsoft Remote Desktop** from Mac App Store).
2. Click **`+`** → **Add PC**:
   * **PC name**: `192.168.1.101`
   * **User account**: Click "Add User Account" → Username: `devuser`, Password: `YourPassword`.
   * **Friendly name**: `BabyStack DevBox`
3. Under the **Display** tab:
   * Check **"Fit session to window"** and **"Optimize for Retina displays"**.
4. Double-click the connection card → You now have a full 60fps graphical Linux desktop with shared clipboard and audio!

#### 🪟 From Windows:
1. Press `Win + R`, type **`mstsc`** (Remote Desktop Connection), hit Enter.
2. Computer: `192.168.1.101`.
3. Log in with `devuser` and password.

#### 🌍 Accessing `devbox` RDP from Anywhere (via Tailscale):
Because your Proxmox host is configured as a **Tailscale Subnet Router** (from Pre-Flight Step 3):
1. Simply turn on the **Tailscale app** on your Mac, Windows laptop, or iPhone while away from home.
2. Open Remote Desktop (`mstsc` / macOS Windows App) and connect to **`192.168.1.101`** exactly as if you were sitting on your living room couch!
3. All local IPs (`192.168.1.xxx`) work transparently everywhere without any port forwarding.

---

# 🛡️ STAGE 2: 4TB Storage & Gluetun Media Stack (Priority #2)

### Step 2.1: Mount 4TB External USB HDD (In Proxmox Host Shell)
```bash
# Format as ext4 (if new)
mkfs.ext4 -L STORAGE4TB /dev/sdb1

# Auto-mount at /mnt/storage4tb
mkdir -p /mnt/storage4tb
echo "UUID=$(blkid -s UUID -o value /dev/sdb1) /mnt/storage4tb ext4 defaults,nofail 0 2" >> /etc/fstab
mount -a

# Create folder structure
mkdir -p /mnt/storage4tb/data/{media/movies,media/tv,torrents/downloading,torrents/completed,nas-shares/personal,nas-shares/family}
mkdir -p /mnt/storage4tb/backups/{homeassistant,babybuddy,proxmox}
chmod -R 777 /mnt/storage4tb/data
```

---

### Step 2.2: Deploy Samba NAS (LXC 102)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/samba.sh)"
```
* CT ID: `102`, RAM: `512 MB`, Cores: `1`.
* Add 4TB bind mount to `/etc/pve/lxc/102.conf`:
  ```ini
  mp0: /mnt/storage4tb/data/nas-shares,mp=/shares
  ```

---

### Step 2.3: Deploy Gluetun VPN + ARR Stack (LXC 103)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/docker.sh)"
```
* CT ID: `103`, Hostname: `media-arr`, RAM: `2048 MB`, Cores: `2`.
* Bind mount storage in `/etc/pve/lxc/103.conf`:
  ```ini
  mp0: /mnt/storage4tb/data/media,mp=/data/media
  mp1: /mnt/storage4tb/data/torrents,mp=/data/torrents
  ```
* Inside LXC 103, launch the stack using [`configs/docker/docker-compose.homelab.yml`](file:///c:/Users/sacha/src/babystack/configs/docker/docker-compose.homelab.yml).

---

### Step 2.4: Deploy Jellyfin with AMD Radeon 660M GPU Hardware Transcoding (LXC 104)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/jellyfin.sh)"
```
* CT ID: `104`, RAM: `1536 MB`, Cores: `2`.
* Pass AMD GPU to `/etc/pve/lxc/104.conf`:
  ```ini
  lxc.cgroup2.devices.allow: c 226:128 rwm
  lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file
  mp0: /mnt/storage4tb/data/media,mp=/media
  ```
* In Jellyfin Admin Dashboard → Playback → Enable **VA-API** (`/dev/dri/renderD128`).

---

# 🍼 STAGE 3: Smart Nursery & Home Assistant (Priority #3)

### Step 3.1: Deploy Home Assistant OS (VM 100)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/vm/haos-vm.sh)"
```
* RAM: `2560 MB`, Cores: `2 vCPUs`, Disk: `40 GB`.

---

### Step 3.2: Configure Frigate NVR & Tapo Camera (Easiest HA Add-on Method)

1. **In Tapo Mobile App**: Create Local Camera Account (`Settings → Advanced → Camera Account` → `lilybaby` / `Password123`).
2. **In Home Assistant**:
   * Install **Mosquitto broker** from Add-on Store → Start.
   * Go to **Settings → System → Storage → Add Network Storage** → Point to Samba LXC 102 (`192.168.1.102:/shares/storage`) as `Media` usage.
   * Add Frigate repository: `https://github.com/blakeblackshear/frigate-hass-addons` → Install **Frigate (Full Access)**.
3. **Create `/config/frigate.yaml`**:
   ```yaml
   mqtt:
     enabled: true
     host: 127.0.0.1
     user: mqtt_user
     password: mqtt_password

   # OpenVINO AI detection on Ryzen 6600H CPU (~8ms inference)
   detectors:
     ov:
       type: openvino
       device: CPU

   # go2rtc stream multiplexer
   go2rtc:
     streams:
       nursery_cam:
         - rtsp://lilybaby:Password123@192.168.1.50:554/stream1 # High-Res Recording
       nursery_cam_sub:
         - rtsp://lilybaby:Password123@192.168.1.50:554/stream2 # Low-Res Detection

   ffmpeg:
     hwaccel_args: preset-vaapi

   cameras:
     nursery_cam:
       ffmpeg:
         inputs:
           - path: rtsp://127.0.0.1:8554/nursery_cam
             roles: [record]
           - path: rtsp://127.0.0.1:8554/nursery_cam_sub
             roles: [detect]
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
       objects:
         track: [person]
   ```
4. Start Frigate and add **Frigate Card** in HACS for live WebRTC feeds with 2-way talk on your nursery dashboard.

---

### Step 3.3: Deploy Baby Buddy PostgreSQL (LXC 106)
```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/docker.sh)"
```
* CT ID: `106`, RAM: `512 MB`, Cores: `1`.
* Deploy Baby Buddy using [`configs/docker/docker-compose.babybuddy.yml`](file:///c:/Users/sacha/src/babystack/configs/docker/docker-compose.babybuddy.yml).
