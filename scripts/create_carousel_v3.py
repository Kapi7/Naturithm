"""Running Carousel V3 — original rich text + Imagen backgrounds.

Merges the detailed original slide text with generated illustration backgrounds.
"""

import os
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

OUT = Path("/Users/kapi7/Naturithm/output/carousel_running")
BG_DIR = OUT / "backgrounds"
W, H = 1080, 1350
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
DARK = (35, 30, 25)
EARTH_BG = (62, 55, 48)


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


def draw_text_centered(draw, text, y, font, fill=WHITE, max_width=900):
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        words = paragraph.split()
        current = ''
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
    for line in lines:
        if not line:
            y += 20
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2
        # Shadow for readability on image backgrounds
        for dx, dy in [(0, 2), (2, 0), (0, -1), (-1, 0)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, 180))
        draw.text((x, y), line, font=font, fill=fill)
        y += th + 12
    return y


def draw_text_left(draw, text, x, y, font, fill=WHITE, max_width=850):
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        words = paragraph.split()
        current = ''
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
    for line in lines:
        if not line:
            y += 20
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        th = bbox[3] - bbox[1]
        for dx, dy in [(0, 2), (2, 0)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), line, font=font, fill=fill)
        y += th + 12
    return y


BG_NAMES = [
    "bg_01_hook", "bg_02_problem", "bg_03_science", "bg_04_body",
    "bg_05_high", "bg_06_born", "bg_07_start", "bg_08_cta",
]

def load_bg(slide_num):
    """Load Imagen background by name, crop border artifacts, darken for text readability."""
    if slide_num < len(BG_NAMES):
        bg_path = BG_DIR / f"{BG_NAMES[slide_num]}.png"
        if bg_path.exists():
            bg = Image.open(bg_path).convert('RGB')
            # Crop 4% from each edge to remove Imagen border artifacts
            bw, bh = bg.size
            crop_x = int(bw * 0.04)
            crop_y = int(bh * 0.04)
            bg = bg.crop((crop_x, crop_y, bw - crop_x, bh - crop_y))
            bg = bg.resize((W, H), Image.LANCZOS)
            bg = ImageEnhance.Brightness(bg).enhance(0.45)
            return bg
    return Image.new('RGB', (W, H), EARTH_BG)


def add_watermark(draw):
    font = get_font(24)
    for dx, dy in [(0, 1), (1, 0)]:
        draw.text((40+dx, 40+dy), "oria", font=font, fill=(0, 0, 0, 120))
    draw.text((40, 40), "oria", font=font, fill=(*SAND, 180))


def add_slide_indicator(draw, current, total=8):
    dot_y = H - 50
    dot_spacing = 20
    total_w = (total - 1) * dot_spacing
    start_x = (W - total_w) // 2
    for i in range(total):
        x = start_x + i * dot_spacing
        r = 4 if i == current else 3
        color = WHITE if i == current else (150, 140, 130)
        draw.ellipse([x-r, dot_y-r, x+r, dot_y+r], fill=color)


def slide_1():
    img = load_bg(0)
    draw = ImageDraw.Draw(img)
    font_big = get_font(72, bold=True)
    font_sub = get_font(36, italic=True)
    y = draw_text_centered(draw, "You're running\ntoo fast.", H//2 - 120, font_big, WHITE)
    y += 40
    draw_text_centered(draw, "Or not running at all.\nBoth are the same mistake.", y, font_sub, SAND)
    add_watermark(draw)
    add_slide_indicator(draw, 0)
    font_sm = get_font(20)
    for dx, dy in [(0, 1), (1, 0)]:
        draw.text((W - 160+dx, H - 50+dy), "swipe →", font=font_sm, fill=(0, 0, 0, 120))
    draw.text((W - 160, H - 50), "swipe →", font=font_sm, fill=(*SAND, 200))
    img.save(OUT / "slide_01_hook.png", quality=95)


def slide_2():
    img = load_bg(1)
    draw = ImageDraw.Draw(img)
    font_title = get_font(28, bold=True)
    font_body = get_font(34)
    font_accent = get_font(34, italic=True)
    y = 180
    draw_text_left(draw, "THE PROBLEM", 100, y, font_title, SAND)
    y += 80
    y = draw_text_left(draw, "80% of beginner runners quit\nbecause they start too fast.", 100, y, font_body, WHITE, max_width=850)
    y += 40
    y = draw_text_left(draw, "Your ego says: run until it hurts.", 100, y, font_body, WHITE)
    y += 10
    y = draw_text_left(draw, "Your body says: please stop.", 100, y, font_accent, SAND)
    y += 40
    draw_text_left(draw, "So you stop.\nAnd you never come back.", 100, y, font_body, WHITE)
    add_watermark(draw)
    add_slide_indicator(draw, 1)
    img.save(OUT / "slide_02_problem.png", quality=95)


def slide_3():
    img = load_bg(2)
    draw = ImageDraw.Draw(img)
    font_title = get_font(26, bold=True)
    font_body = get_font(28)
    font_accent = get_font(30, bold=True)
    font_small = get_font(22)
    y = 120
    draw_text_left(draw, "THE SCIENCE", 100, y, font_title, SAND)
    y += 55
    draw_text_left(draw, "Zone 2: 60-70% of max heart rate", 100, y, font_accent, WHITE)
    y += 50
    # Heart rate zone bar
    zone_colors = [(80, 180, 80), (120, 200, 80), (200, 200, 60), (220, 140, 50), (200, 60, 60)]
    zone_labels = ["Z1", "Z2", "Z3", "Z4", "Z5"]
    bar_x, bar_w = 100, 850
    bar_h = 45
    zone_w = bar_w // 5
    for i, (color, label) in enumerate(zip(zone_colors, zone_labels)):
        x = bar_x + i * zone_w
        draw.rectangle([x, y, x + zone_w, y + bar_h], fill=color)
        bbox = draw.textbbox((0, 0), label, font=font_small)
        lw = bbox[2] - bbox[0]
        draw.text((x + (zone_w - lw) // 2, y + 10), label, font=font_small, fill=DARK)
    z2_x = bar_x + zone_w
    draw.rectangle([z2_x - 3, y - 3, z2_x + zone_w + 3, y + bar_h + 3], outline=WHITE, width=3)
    y += bar_h + 40
    y = draw_text_left(draw, "The test is simple:", 100, y, font_body, WHITE)
    y += 15
    y = draw_text_left(draw, "Can you hold a conversation\nwhile running?", 100, y, font_body, WHITE)
    y += 25
    y = draw_text_left(draw, "Yes → you're in the zone.", 100, y, font_accent, (120, 200, 80))
    y += 8
    y = draw_text_left(draw, "No → slow down.", 100, y, font_accent, (220, 140, 50))
    y += 30
    draw_text_left(draw, "Elite marathon runners train here\n80% of the time. You should too.", 100, y, font_body, SAND)
    add_watermark(draw)
    add_slide_indicator(draw, 2)
    img.save(OUT / "slide_03_science.png", quality=95)


def slide_4():
    img = load_bg(3)
    draw = ImageDraw.Draw(img)
    font_title = get_font(26, bold=True)
    font_body = get_font(28)
    font_accent = get_font(26, italic=True)
    y = 120
    draw_text_left(draw, "WHAT SLOW RUNNING BUILDS", 100, y, font_title, SAND)
    y += 70
    benefits = [
        ("Stronger heart", "pumps more blood per beat"),
        ("More mitochondria", "your cells' energy factories"),
        ("Better fat burning", "metabolic flexibility"),
        ("Sharper focus", "prefrontal cortex activation"),
        ("Stronger bones", "tendons & ligaments too"),
    ]
    for title, desc in benefits:
        draw.ellipse([100, y+2, 140, y+42], fill=SAND)
        for dx, dy in [(0, 1), (1, 0)]:
            draw.text((160+dx, y+dy), title, font=font_body, fill=(0, 0, 0, 150))
        draw.text((160, y), title, font=font_body, fill=WHITE)
        draw.text((160, y + 36), desc, font=font_accent, fill=(200, 190, 175))
        y += 82
    y += 25
    draw_text_left(draw, "All of this happens at EASY pace.", 100, y, get_font(30, bold=True), WHITE)
    y += 50
    draw_text_left(draw, "None of it requires suffering.", 100, y, get_font(30, italic=True), SAND)
    add_watermark(draw)
    add_slide_indicator(draw, 3)
    img.save(OUT / "slide_04_body.png", quality=95)


def slide_5():
    img = load_bg(4)
    draw = ImageDraw.Draw(img)
    font_big = get_font(52, bold=True)
    font_body = get_font(32)
    font_accent = get_font(34, italic=True)
    font_title = get_font(28, bold=True)
    y = 180
    draw_text_left(draw, "THE RUNNER'S HIGH", 100, y, font_title, SAND)
    y += 80
    y = draw_text_centered(draw, "Your body makes its\nown bliss molecule.", y, font_big, WHITE)
    y += 50
    y = draw_text_left(draw, "After 30+ minutes of easy running,\nyour brain releases anandamide —\nan endocannabinoid.", 100, y, font_body, WHITE)
    y += 40
    # Highlight box
    draw.rectangle([80, y, W-80, y+120], outline=SAND, width=2)
    y_inner = y + 20
    draw_text_centered(draw, "'Ananda' means bliss in Sanskrit.", y_inner, font_accent, SAND)
    y_inner += 50
    draw_text_centered(draw, "This isn't motivation talk. This is biochemistry.", y_inner, font_body, WHITE)
    add_watermark(draw)
    add_slide_indicator(draw, 4)
    img.save(OUT / "slide_05_high.png", quality=95)


def slide_6():
    img = load_bg(5)
    draw = ImageDraw.Draw(img)
    font_big = get_font(42, bold=True)
    font_body = get_font(28)
    font_accent = get_font(30, italic=True)
    font_title = get_font(26, bold=True)
    y = 130
    draw_text_left(draw, "BORN TO RUN", 100, y, font_title, SAND)
    y += 65
    y = draw_text_centered(draw, "2 million years of\nevolution designed\nyou for this.", y, font_big, WHITE)
    y += 40
    features = [
        "Your Achilles tendon.",
        "Your arched foot.",
        "Your ability to sweat instead of pant.",
    ]
    for feat in features:
        for dx, dy in [(0, 1), (1, 0)]:
            draw.text((130+dx, y+dy), "→", font=font_body, fill=(0, 0, 0, 150))
            draw.text((170+dx, y+dy), feat, font=font_body, fill=(0, 0, 0, 150))
        draw.text((130, y), "→", font=font_body, fill=SAND)
        draw.text((170, y), feat, font=font_body, fill=WHITE)
        y += 45
    y += 25
    y = draw_text_left(draw, "Humans outran every animal\non the planet — not by speed,\nbut by endurance.", 100, y, font_body, WHITE)
    y += 20
    draw_text_left(draw, "Running isn't exercise you invented.\nIt's movement you forgot.", 100, y, font_accent, SAND)
    add_watermark(draw)
    add_slide_indicator(draw, 5)
    img.save(OUT / "slide_06_born.png", quality=95)


def slide_7():
    img = load_bg(6)
    draw = ImageDraw.Draw(img)
    font_title = get_font(28, bold=True)
    font_body = get_font(30)
    font_accent = get_font(30, bold=True)
    font_rule = get_font(28, italic=True)
    y = 150
    draw_text_left(draw, "HOW TO START TODAY", 100, y, font_title, SAND)
    y += 80
    weeks = [
        ("Week 1:", "Run 5 min. Walk 1 min. Repeat x3."),
        ("Week 2:", "Run 8 min. Walk 1 min. Repeat x3."),
        ("Week 4:", "Run 15 min straight. Slow."),
        ("Week 8:", "Run 30 min. Conversational pace."),
    ]
    for label, desc in weeks:
        for dx, dy in [(0, 1), (1, 0)]:
            draw.text((100+dx, y+dy), label, font=font_accent, fill=(0, 0, 0, 150))
        draw.text((100, y), label, font=font_accent, fill=SAND)
        bbox = draw.textbbox((0, 0), label, font=font_accent)
        lw = bbox[2] - bbox[0]
        draw.text((100 + lw + 15, y), desc, font=font_body, fill=WHITE)
        y += 55
    y += 30
    draw_text_left(draw, "Rules:", 100, y, font_accent, SAND)
    y += 50
    rules = [
        "If you can't talk, slow down",
        "No pace tracking for the first month",
        "No comparison",
        "It's not about speed. It's about showing up.",
    ]
    for rule in rules:
        draw.text((120, y), "→", font=font_body, fill=SAND)
        draw.text((160, y), rule, font=font_rule, fill=WHITE)
        y += 48
    add_watermark(draw)
    add_slide_indicator(draw, 6)
    img.save(OUT / "slide_07_start.png", quality=95)


def slide_8():
    img = load_bg(7)
    draw = ImageDraw.Draw(img)
    font_big = get_font(56, bold=True)
    font_sub = get_font(34, italic=True)
    y = H // 2 - 100
    y = draw_text_centered(draw, "Lace up.\nGo slow.\nTrust the process.", y, font_big, WHITE)
    y += 50
    draw_text_centered(draw, "Even 5 minutes counts.\nYour body has been waiting.", y, font_sub, SAND)
    font_sm = get_font(22)
    for dx, dy in [(0, 1), (1, 0)]:
        draw.text((W//2 - 60+dx, H - 80+dy), "@oria_naturithm", font=font_sm, fill=(0, 0, 0, 120))
    draw.text((W//2 - 60, H - 80), "@oria_naturithm", font=font_sm, fill=SAND)
    add_watermark(draw)
    add_slide_indicator(draw, 7)
    img.save(OUT / "slide_08_cta.png", quality=95)


if __name__ == "__main__":
    print("  Generating Running Carousel V3 (original text + image backgrounds)...")
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    slide_6()
    slide_7()
    slide_8()
    print(f"  Done! 8 slides in {OUT}/")
