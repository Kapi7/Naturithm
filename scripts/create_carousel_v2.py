"""Create Running Carousel V2 — with Imagen-generated illustrations.

8 slides with watercolor running illustrations + text overlays.
"""

import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from google import genai
from google.genai import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/kapi7/Naturithm/credentials.json'

client = genai.Client(
    vertexai=True,
    project='naturitm',
    location='us-central1',
)

OUT_BASE = Path("/Users/kapi7/Naturithm/output")
W, H = 1080, 1350
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
DARK_BG = (42, 38, 34)

STYLE_PREFIX = (
    "Warm earth-tone illustration, soft natural feel, "
    "muted palette of browns, greens, and warm golds, "
    "no text on image, square composition, "
)

# Background images for each slide
CAROUSEL_IMAGES = [
    ("bg_01_hook",
     "Person lacing up running shoes on a trail at sunrise, "
     "close-up of hands and shoes, warm golden light, nature setting"),
    ("bg_02_problem",
     "Person sitting on couch looking tired and sluggish, "
     "warm interior, soft afternoon light, contemplative mood"),
    ("bg_03_science",
     "Abstract illustration of a human heart with flowing energy lines, "
     "warm colors, anatomical but artistic, gentle glow"),
    ("bg_04_body",
     "Runner in motion on a forest trail, motion blur, golden morning light, "
     "dynamic energy, earth tones, natural setting"),
    ("bg_05_high",
     "Person finishing a run with arms slightly raised, peaceful expression, "
     "endorphin glow, sunrise behind them, natural landscape"),
    ("bg_06_born",
     "Human footprint in soft earth or sand, barefoot, natural terrain, "
     "primal simplicity, warm earth tones"),
    ("bg_07_start",
     "Simple trail path leading into warm morning light, inviting, "
     "beginning of a journey, earth tones, peaceful"),
    ("bg_08_cta",
     "Warm sunrise over an open field or trail, expansive horizon, "
     "golden light, inspiring, peaceful, earth tones"),
]

# Slide text content
SLIDES = [
    {"title": "Your body was made\nto run.", "subtitle": "Here's what happens when you do.", "style": "hook"},
    {"title": "We sit all day.\nWe feel low.", "subtitle": "Something is missing.", "style": "problem"},
    {"title": "Within 20 minutes\nof running:", "subtitle": "Your heart rate enters\nthe growth zone.\nSerotonin and dopamine spike.", "style": "science"},
    {"title": "Your body doesn't\nneed a gym.", "subtitle": "It needs what it was\ndesigned to do.", "style": "body"},
    {"title": "Runner's high\nis real.", "subtitle": "Not a metaphor.\nA chemical event in\nyour brain.", "style": "high"},
    {"title": "We were born\nto move.", "subtitle": "Every cell in your body\nknows this.", "style": "born"},
    {"title": "Start with\n15 minutes.", "subtitle": "Walk if you need to.\nJust move.", "style": "start"},
    {"title": "Follow @oria_naturithm", "subtitle": "for more ways your body\nalready has the answers.", "style": "cta"},
]


def get_font(size, bold=False, italic=False):
    if bold and italic:
        try:
            return ImageFont.truetype("/System/Library/Fonts/Palatino.ttc", size, index=3)
        except:
            return ImageFont.truetype("/System/Library/Fonts/Palatino.ttc", size, index=1)
    elif bold:
        return ImageFont.truetype("/System/Library/Fonts/Palatino.ttc", size, index=1)
    elif italic:
        return ImageFont.truetype("/System/Library/Fonts/Palatino.ttc", size, index=2)
    return ImageFont.truetype("/System/Library/Fonts/Palatino.ttc", size, index=0)


def generate_bg_image(prompt, output_path):
    """Generate background illustration with Imagen."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        print(f"    Already exists: {output_path.name}")
        return True

    full_prompt = STYLE_PREFIX + prompt
    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="4:3",
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation="ALLOW_ADULT",
            ),
        )
        if response.generated_images:
            output_path.write_bytes(response.generated_images[0].image.image_bytes)
            print(f"    Done: {output_path.name}")
            return True
        print("    No image generated")
        return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


def create_slide(slide_data, bg_path, slide_num, total, output_path):
    """Create a carousel slide with background image + text overlay."""
    if bg_path and bg_path.exists():
        bg = Image.open(bg_path).convert('RGB')
        bg = bg.resize((W, H), Image.LANCZOS)
        # Darken for text readability
        from PIL import ImageEnhance
        bg = ImageEnhance.Brightness(bg).enhance(0.5)
    else:
        bg = Image.new('RGB', (W, H), DARK_BG)

    draw = ImageDraw.Draw(bg)

    # Slide indicator dots
    dot_y = 60
    dot_spacing = 18
    start_x = W // 2 - (total * dot_spacing) // 2
    for i in range(total):
        x = start_x + i * dot_spacing
        color = SAND if i == slide_num else (100, 90, 80)
        draw.ellipse([x, dot_y, x + 8, dot_y + 8], fill=color)

    # Watermark
    wm_font = get_font(24)
    draw.text((40, H - 60), "oria", font=wm_font, fill=(*SAND, 180))

    # Title
    font_title = get_font(52, bold=True)
    font_sub = get_font(34, italic=True)

    title = slide_data["title"]
    subtitle = slide_data.get("subtitle", "")

    # Draw title centered
    y = H // 2 - 150
    for line in title.split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2
        # Shadow
        for dx, dy in [(0, 2), (2, 0), (0, -1), (-1, 0)]:
            draw.text((x+dx, y+dy), line, font=font_title, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font_title, fill=WHITE)
        y += th + 12

    y += 30

    # Subtitle in sand
    for line in subtitle.split('\n'):
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2
        for dx, dy in [(0, 2), (2, 0)]:
            draw.text((x+dx, y+dy), line, font=font_sub, fill=(0, 0, 0, 150))
        draw.text((x, y), line, font=font_sub, fill=SAND)
        y += th + 8

    bg.save(str(output_path), quality=95)
    print(f"  Slide {slide_num + 1}: {output_path.name}")


if __name__ == "__main__":
    out_dir = OUT_BASE / "carousel_running"
    bg_dir = out_dir / "backgrounds"
    out_dir.mkdir(parents=True, exist_ok=True)
    bg_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  Generating Running Carousel V2 (with images)")
    print(f"{'='*50}")

    # Step 1: Generate background images
    print("\n  Generating background images...")
    bg_paths = {}
    for img_name, prompt in CAROUSEL_IMAGES:
        path = bg_dir / f"{img_name}.png"
        generate_bg_image(prompt, path)
        bg_paths[img_name] = path
        time.sleep(15)

    # Step 2: Compose slides
    print("\n  Composing slides...")
    for i, slide in enumerate(SLIDES):
        bg_name = CAROUSEL_IMAGES[i][0]
        bg_path = bg_paths.get(bg_name)
        if bg_path and not bg_path.exists():
            bg_path = None
        out_path = out_dir / f"slide_{i+1:02d}_{slide['style']}.png"
        create_slide(slide, bg_path, i, len(SLIDES), out_path)

    print(f"\n  Done! {len(SLIDES)} slides in {out_dir}")
