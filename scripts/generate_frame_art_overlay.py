#!/usr/bin/env python3
"""
🌸 BabyStack: Samsung The Frame Art Overlay Generator
Renders live Home Assistant nursery telemetry onto 4K artwork while maintaining
100% native Samsung Frame "Art Mode" (low power, matte finish, auto-dimming).

Requirements:
    pip install pillow requests
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
HA_URL = os.getenv("HA_URL", "http://192.168.10.10:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "YOUR_LONG_LIVED_ACCESS_TOKEN")
BASE_ART_PATH = os.getenv("BASE_ART_PATH", "/config/media/art/monet_water_lilies.jpg")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/config/www/frame_art_nursery.jpg")
CANVAS_SIZE = (3840, 2160) # 4K 16:9 native Samsung Frame resolution

def get_ha_state(entity_id: str) -> str:
    """Fetch live entity state from Home Assistant REST API."""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=headers, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("state", "N/A")
    except Exception as e:
        print(f"Error fetching {entity_id}: {e}")
    return "N/A"

def generate_frame_canvas():
    # 1. Fetch live telemetry from Home Assistant & Baby Buddy
    temp = get_ha_state("sensor.nursery_temperature")
    sleep_state = get_ha_state("binary_sensor.nursery_crib_presence")
    last_feed = get_ha_state("sensor.lily_last_feeding")
    sound_db = get_ha_state("sensor.nursery_ambient_sound_level")

    sleep_label = "Sleeping 💤" if sleep_state == "on" else "Awake ☀️"

    status_text = f"🌸 Lily: {sleep_label}   |   🌡️ {temp}°C   |   🔊 {sound_db} dB   |   🍼 Last Fed: {last_feed}"

    # 2. Open or create base artwork image
    if os.path.exists(BASE_ART_PATH):
        img = Image.open(BASE_ART_PATH).convert("RGBA")
        img = img.resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    else:
        # Fallback to dark elegant canvas
        img = Image.new("RGBA", CANVAS_SIZE, (28, 30, 34, 255))

    # 3. Create a subtle, frosted museum-plaque overlay at the bottom
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Frosted bar dimensions
    bar_height = 80
    bar_top = CANVAS_SIZE[1] - bar_height - 60
    bar_bottom = CANVAS_SIZE[1] - 60
    margin = 80

    # Draw rounded pill / plaque
    draw.rounded_rectangle(
        [(margin, bar_top), (CANVAS_SIZE[0] - margin, bar_bottom)],
        radius=20,
        fill=(15, 18, 22, 160) # Semi-transparent elegant dark charcoal
    )

    # 4. Draw Typography
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Draw centered text with subtle drop shadow
    draw.text((margin + 40, bar_top + 20), status_text, fill=(245, 245, 245, 230), font=font)

    # 5. Composite and save
    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(OUTPUT_PATH, "JPEG", quality=95)
    print(f"✅ Generated 4K Art Canvas at {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_frame_canvas()
