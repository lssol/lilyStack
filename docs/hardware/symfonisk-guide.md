# 🔊 IKEA SYMFONISK Bookshelf (Sonos) Hardware & Integration Guide

The **IKEA SYMFONISK Bookshelf Speaker** is co-engineered with **Sonos**, combining genuine Sonos acoustic drivers, Class-D digital amplifiers, and the Sonos S2 operating platform within an IKEA minimalist chassis.

In **BabyStack**, the SYMFONISK is the central acoustic element for Lily's nursery: playing continuous, high-fidelity **offline brown noise** to mask sudden household sounds and soothing lullabies without relying on cloud streaming.

---

## 📋 Acquired Hardware Specifications

| Specification | Hardware Detail |
| :--- | :--- |
| **Acoustic Design** | Custom Sonos-tuned 1x tweeter + 1x mid-woofer |
| **Amplification** | Two Class-D digital amplifiers individually tuned to speaker drivers |
| **Connectivity** | Wi-Fi (802.11 b/g/n, 2.4 GHz) + 10/100 Mbps RJ45 Ethernet port |
| **Audio Streaming** | Apple AirPlay 2, Spotify Connect, Sonos S2, DLNA / UPnP, local HTTP streams |
| **Power Supply** | Built-in 100–240V AC 50/60Hz internal power supply (removable standard C7 power cord) |
| **Dimensions & Weight** | 10 cm (W) x 15 cm (D) x 31 cm (H) — Weight: 2.16 kg |
| **Mounting** | Horizontal or vertical bookshelf placement, optional wall bracket |

---

## 🛡️ Pediatric Acoustic Safety Directives

According to the American Academy of Pediatrics (AAP) and pediatric audiologists:
1. **Distance**: Place the speaker at least **2 meters (6.5 feet)** away from Lily's crib.
2. **Volume Cap**: Sound level at the infant's ear level must **never exceed 60 dBA** (recommended target: **50–55 dBA**).
3. **Brown Noise vs White/Pink Noise**: Brown noise features a deeper, softer low-frequency roll-off ($-6\text{ dB/octave}$), mimicking the womb sound environment without harsh high frequencies.

---

## 🏠 Home Assistant Integration & Local Offline Playback

The SYMFONISK speaker is natively auto-discovered by Home Assistant via the official **Sonos Integration**.

### 1. Local Offline Brown Noise Loop (Zero Internet Dependency)
To prevent streaming dropouts when the external internet fluctuates, store a continuous 60-minute seamless brown noise `.flac` or `.mp3` file directly on your **CHUWI UBox** server inside `/config/www/audio/brown_noise_continuous.flac`.

Home Assistant exposes this local file via its local webserver:
`http://homeassistant.local:8123/local/audio/brown_noise_continuous.flac`

### 2. Home Assistant Automation Blueprint (Volume Guard & 1-Click Toggle)

```yaml
# configs/home-assistant/automations.yaml snippet
- id: 'nursery_symfonisk_brown_noise'
  alias: "Nursery: Toggle Safe Brown Noise on SYMFONISK"
  description: "Plays local brown noise capped at 25% volume (~52 dBA) when glider button is clicked"
  trigger:
    - platform: event
      event_type: zha_event
      event_data:
        command: "button_2_single" # IKEA Remote on Glider
  action:
    - choose:
        - conditions:
            - condition: state
              entity_id: media_player.nursery_symfonisk
              state: 'playing'
          sequence:
            - service: media_player.media_pause
              target:
                entity_id: media_player.nursery_symfonisk
      default:
        # Enforce safe volume ceiling (25% = ~52 dB at 2 meters)
        - service: media_player.volume_set
          target:
            entity_id: media_player.nursery_symfonisk
          data:
            volume_level: 0.25
        # Loop continuous local brown noise
        - service: media_player.play_media
          target:
            entity_id: media_player.nursery_symfonisk
          data:
            media_content_type: music
            media_content_id: "http://127.0.0.1:8123/local/audio/brown_noise_continuous.flac"
        - service: sonos.set_sleep_timer
          target:
            entity_id: media_player.nursery_symfonisk
          data:
            sleep_time: "02:00:00" # Auto-off after 2 hours (optional)
```

---

## 🛠️ Physical Placement Tips in Nursery

1. **Bookshelf / Dresser**: Place vertically or horizontally on a sturdy shelf away from climbing reach.
2. **Cord Routing**: Run the power cable inside an **IKEA MONTERA** cable trunking channel, firmly anchored to the wall.
3. **Status LED**: In the Sonos App, toggle **Status Light -> OFF** so the small white LED does not disturb nighttime sleep.
