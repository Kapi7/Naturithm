"""Generate 8 carousel slides for the Running post (@oria_naturithm)."""

from PIL import Image, ImageDraw, ImageFont
import textwrap
from pathlib import Path

OUT = Path("/Users/kapi7/Naturithm/output/carousel_running")
W, H = 1080, 1350  # Instagram carousel optimal
SAND = (196, 149, 106)  # #C4956A
WHITE = (255, 255, 255)
DARK = (35, 30, 25)
CREAM = (245, 238, 228)
EARTH_BG = (62, 55, 48)  # Dark earth tone for infographic slides

# Fonts
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
    """Draw text centered, with word wrap."""
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
        draw.text((x, y), line, font=font, fill=fill)
        y += th + 12
    return y


def draw_text_left(draw, text, x, y, font, fill=WHITE, max_width=850):
    """Draw text left-aligned with word wrap."""
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
        draw.text((x, y), line, font=font, fill=fill)
        y += th + 12
    return y


def add_watermark(draw):
    font = get_font(24)
    draw.text((40, 40), "oria", font=font, fill=(*SAND, 180))


def add_slide_indicator(draw, current, total=8):
    """Small dots at bottom showing slide position."""
    dot_y = H - 50
    dot_spacing = 20
    total_w = (total - 1) * dot_spacing
    start_x = (W - total_w) // 2
    for i in range(total):
        x = start_x + i * dot_spacing
        r = 4 if i == current else 3
        color = WHITE if i == current else (255, 255, 255, 80)
        draw.ellipse([x-r, dot_y-r, x+r, dot_y+r], fill=color)


# ─── SLIDE 1: HOOK ───────────────────────────────────────────────────
def slide_1():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    # Gradient overlay effect
    for y_pos in range(H):
        alpha = int(30 + (y_pos / H) * 40)
        draw.line([(0, y_pos), (W, y_pos)], fill=(45, 40, 35))

    draw = ImageDraw.Draw(img)

    # Main text
    font_big = get_font(72, bold=True)
    font_sub = get_font(36, italic=True)

    y = draw_text_centered(draw, "You're running\ntoo fast.", H//2 - 120, font_big, WHITE)
    y += 40
    draw_text_centered(draw, "Or not running at all.\nBoth are the same mistake.", y, font_sub, SAND)

    add_watermark(draw)
    add_slide_indicator(draw, 0)

    # Swipe hint
    font_sm = get_font(20)
    draw.text((W - 160, H - 50), "swipe →", font=font_sm, fill=(*SAND, 150))

    img.save(OUT / "slide_01_hook.png", quality=95)


# ─── SLIDE 2: THE PROBLEM ────────────────────────────────────────────
def slide_2():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_title = get_font(28, bold=True)
    font_body = get_font(34)
    font_accent = get_font(34, italic=True)

    y = 180
    draw.text((100, y), "THE PROBLEM", font=font_title, fill=SAND)
    y += 80

    y = draw_text_left(draw, "80% of beginner runners quit\nbecause they start too fast.", 100, y, font_body, WHITE, max_width=850)
    y += 40
    y = draw_text_left(draw, "Your ego says: run until it hurts.", 100, y, font_body, WHITE)
    y += 10
    y = draw_text_left(draw, "Your body says: please stop.", 100, y, font_accent, SAND)
    y += 40
    y = draw_text_left(draw, "So you stop.\nAnd you never come back.", 100, y, font_body, WHITE)

    add_watermark(draw)
    add_slide_indicator(draw, 1)
    img.save(OUT / "slide_02_problem.png", quality=95)


# ─── SLIDE 3: THE SCIENCE (Zone 2) ──────────────────────────────────
def slide_3():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_title = get_font(28, bold=True)
    font_body = get_font(32)
    font_accent = get_font(34, bold=True)
    font_small = get_font(26)

    y = 150
    draw.text((100, y), "THE SCIENCE", font=font_title, fill=SAND)
    y += 70

    draw_text_left(draw, "Zone 2: 60-70% of max heart rate", 100, y, font_accent, WHITE)
    y += 60

    # Heart rate zone bar
    zone_colors = [(80, 180, 80), (120, 200, 80), (200, 200, 60), (220, 140, 50), (200, 60, 60)]
    zone_labels = ["Z1", "Z2", "Z3", "Z4", "Z5"]
    bar_x, bar_w = 100, 850
    bar_h = 50
    zone_w = bar_w // 5

    for i, (color, label) in enumerate(zip(zone_colors, zone_labels)):
        x = bar_x + i * zone_w
        draw.rectangle([x, y, x + zone_w, y + bar_h], fill=color)
        bbox = draw.textbbox((0, 0), label, font=font_small)
        lw = bbox[2] - bbox[0]
        draw.text((x + (zone_w - lw) // 2, y + 10), label, font=font_small, fill=DARK)

    # Highlight Zone 2
    z2_x = bar_x + zone_w
    draw.rectangle([z2_x - 3, y - 3, z2_x + zone_w + 3, y + bar_h + 3], outline=WHITE, width=3)

    y += bar_h + 50

    y = draw_text_left(draw, "The test is simple:", 100, y, font_body, WHITE)
    y += 20
    y = draw_text_left(draw, "Can you hold a conversation\nwhile running?", 100, y, font_body, WHITE)
    y += 30
    y = draw_text_left(draw, "Yes → you're in the zone.", 100, y, font_accent, (120, 200, 80))
    y += 10
    y = draw_text_left(draw, "No → slow down.", 100, y, font_accent, (220, 140, 50))
    y += 40
    y = draw_text_left(draw, "Elite marathon runners train here\n80% of the time. You should too.", 100, y, font_body, SAND)

    add_watermark(draw)
    add_slide_indicator(draw, 2)
    img.save(OUT / "slide_03_science.png", quality=95)


# ─── SLIDE 4: WHAT HAPPENS IN YOUR BODY ─────────────────────────────
def slide_4():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_title = get_font(28, bold=True)
    font_body = get_font(32)
    font_accent = get_font(30, italic=True)
    font_label = get_font(28)

    y = 150
    draw.text((100, y), "WHAT SLOW RUNNING BUILDS", font=font_title, fill=SAND)
    y += 90

    benefits = [
        ("♥", "Stronger heart", "pumps more blood per beat"),
        ("⚡", "More mitochondria", "your cells' energy factories"),
        ("🔥", "Better fat burning", "metabolic flexibility"),
        ("🧠", "Sharper focus", "prefrontal cortex activation"),
        ("🦴", "Stronger bones", "tendons & ligaments too"),
    ]

    for icon, title, desc in benefits:
        # Icon circle
        draw.ellipse([100, y, 150, y+50], fill=SAND)

        draw.text((175, y), title, font=font_body, fill=WHITE)
        draw.text((175, y + 42), desc, font=font_accent, fill=(180, 170, 155))
        y += 100

    y += 30
    y = draw_text_left(draw, "All of this happens at EASY pace.", 100, y, get_font(34, bold=True), WHITE)
    y += 15
    draw_text_left(draw, "None of it requires suffering.", 100, y, get_font(34, italic=True), SAND)

    add_watermark(draw)
    add_slide_indicator(draw, 3)
    img.save(OUT / "slide_04_body.png", quality=95)


# ─── SLIDE 5: THE RUNNER'S HIGH ──────────────────────────────────────
def slide_5():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_big = get_font(52, bold=True)
    font_body = get_font(32)
    font_accent = get_font(34, italic=True)
    font_title = get_font(28, bold=True)

    y = 180
    draw.text((100, y), "THE RUNNER'S HIGH", font=font_title, fill=SAND)
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


# ─── SLIDE 6: BORN TO RUN ────────────────────────────────────────────
def slide_6():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_big = get_font(48, bold=True)
    font_body = get_font(32)
    font_accent = get_font(34, italic=True)
    font_title = get_font(28, bold=True)

    y = 180
    draw.text((100, y), "BORN TO RUN", font=font_title, fill=SAND)
    y += 80

    y = draw_text_centered(draw, "2 million years of\nevolution designed\nyou for this.", y, font_big, WHITE)
    y += 50

    features = [
        "Your Achilles tendon.",
        "Your arched foot.",
        "Your ability to sweat instead of pant.",
    ]

    for feat in features:
        draw.text((130, y), "→", font=font_body, fill=SAND)
        draw.text((170, y), feat, font=font_body, fill=WHITE)
        y += 50

    y += 30
    y = draw_text_left(draw, "Humans outran every animal\non the planet — not by speed,\nbut by endurance.", 100, y, font_body, WHITE)
    y += 30
    draw_text_left(draw, "Running isn't exercise you invented.\nIt's movement you forgot.", 100, y, font_accent, SAND)

    add_watermark(draw)
    add_slide_indicator(draw, 5)
    img.save(OUT / "slide_06_born.png", quality=95)


# ─── SLIDE 7: HOW TO START ───────────────────────────────────────────
def slide_7():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_title = get_font(28, bold=True)
    font_body = get_font(30)
    font_accent = get_font(30, bold=True)
    font_rule = get_font(28, italic=True)

    y = 150
    draw.text((100, y), "HOW TO START TODAY", font=font_title, fill=SAND)
    y += 80

    weeks = [
        ("Week 1:", "Run 5 min. Walk 1 min. Repeat x3."),
        ("Week 2:", "Run 8 min. Walk 1 min. Repeat x3."),
        ("Week 4:", "Run 15 min straight. Slow."),
        ("Week 8:", "Run 30 min. Conversational pace."),
    ]

    for label, desc in weeks:
        draw.text((100, y), label, font=font_accent, fill=SAND)
        bbox = draw.textbbox((0, 0), label, font=font_accent)
        lw = bbox[2] - bbox[0]
        draw.text((100 + lw + 15, y), desc, font=font_body, fill=WHITE)
        y += 55

    y += 30

    # Rules
    draw.text((100, y), "Rules:", font=font_accent, fill=SAND)
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


# ─── SLIDE 8: CTA ────────────────────────────────────────────────────
def slide_8():
    img = Image.new('RGB', (W, H), EARTH_BG)
    draw = ImageDraw.Draw(img)

    font_big = get_font(56, bold=True)
    font_sub = get_font(34, italic=True)

    y = H // 2 - 100
    y = draw_text_centered(draw, "Lace up.\nGo slow.\nTrust the process.", y, font_big, WHITE)
    y += 50
    draw_text_centered(draw, "Even 5 minutes counts.\nYour body has been waiting.", y, font_sub, SAND)

    # Bottom branding
    font_sm = get_font(22)
    draw.text((W//2 - 60, H - 80), "@oria_naturithm", font=font_sm, fill=SAND)

    add_watermark(draw)
    add_slide_indicator(draw, 7)
    img.save(OUT / "slide_08_cta.png", quality=95)


if __name__ == "__main__":
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    slide_6()
    slide_7()
    slide_8()
    print(f"✓ 8 carousel slides saved to {OUT}/")
