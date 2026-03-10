"""Create Naturithm loop videos (6s seamless text animations).

These are text-driven philosophical reels for @naturithm7.
Visual: earth-tone gradient with animated text overlays.
The text fades in/out in sequence, creating a hypnotic loop.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

os.environ.setdefault("IMAGEIO_FFMPEG_EXE", "/opt/homebrew/bin/ffmpeg")

from moviepy import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips

W, H = 720, 1280
FPS = 30
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
MUSIC_DIR = Path("/Users/kapi7/Naturithm/output/music_library")
OUT_BASE = Path("/Users/kapi7/Naturithm/output")


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


def ease_in_out(t):
    """Smooth ease in/out curve."""
    return t * t * (3 - 2 * t)


def make_gradient():
    """Create earth-tone gradient background as numpy array."""
    top = np.array([52, 45, 38])
    bot = np.array([35, 30, 25])
    gradient = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / H
        gradient[y] = (top * (1 - t) + bot * t).astype(np.uint8)
    return gradient


def draw_centered_text(draw, text, y, font, fill, alpha=255, max_width=620):
    """Draw centered multi-line text with alpha."""
    color = (*fill[:3], alpha) if len(fill) == 3 else fill
    lines = []
    for para in text.split('\n'):
        if not para.strip():
            lines.append('')
            continue
        words = para.split()
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
            y += 15
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (W - tw) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += th + 10
    return y


BG_CACHE = None

def get_bg():
    global BG_CACHE
    if BG_CACHE is None:
        BG_CACHE = make_gradient()
    return BG_CACHE.copy()


# ── LOOP VIDEO 1: "Change the way you look at things" ────────────────

def loop1_frame(t):
    """
    0-2s: "When you change" fades in (white)
    2-4s: "the way you look at things" fades in (white)
    4-6s: "the things you look at change." fades in (sand italic)
    Each text stays visible after appearing. At 6s loops back to 0.
    """
    img = Image.fromarray(get_bg())
    draw = ImageDraw.Draw(img, 'RGBA')

    font_main = get_font(44, bold=True)
    font_accent = get_font(42, bold=True, italic=True)
    font_wm = get_font(20)
    font_attr = get_font(22, italic=True)

    # Watermark
    draw.text((30, 30), "naturithm", font=font_wm, fill=(*SAND, 120))

    y_start = H // 2 - 120

    # Text 1: "When you change" (0-2s fade in, stays)
    if t < 0.5:
        alpha1 = 0
    elif t < 2.0:
        alpha1 = int(ease_in_out(min(1.0, (t - 0.5) / 1.0)) * 255)
    else:
        alpha1 = 255

    if alpha1 > 0:
        y = draw_centered_text(draw, "When you change", y_start, font_main, WHITE, alpha1)
    else:
        y = y_start + 55

    # Text 2: "the way you look at things" (2-4s fade in, stays)
    if t < 2.0:
        alpha2 = 0
    elif t < 3.5:
        alpha2 = int(ease_in_out(min(1.0, (t - 2.0) / 1.0)) * 255)
    else:
        alpha2 = 255

    y += 15
    if alpha2 > 0:
        y = draw_centered_text(draw, "the way you look\nat things", y, font_main, WHITE, alpha2)
    else:
        y += 70

    # Text 3: "the things you look at change." (4-6s fade in)
    if t < 4.0:
        alpha3 = 0
    elif t < 5.5:
        alpha3 = int(ease_in_out(min(1.0, (t - 4.0) / 1.0)) * 255)
    else:
        alpha3 = 255

    y += 25
    if alpha3 > 0:
        draw_centered_text(draw, "the things you look at\nchange.", y, font_accent, SAND, alpha3)

    # Attribution (subtle, always visible)
    draw.text((W // 2 - 60, H - 80), "— Wayne Dyer", font=font_attr, fill=(*WHITE, 80))

    return np.array(img)


# ── LOOP VIDEO 3: "We only see in people what lives inside us" ────────

def loop3_frame(t):
    """
    0-2s: "What you see in others" (white)
    2-4s: "lives inside you." (sand)
    4-6s: "It takes one to know one." (white, smaller)
    """
    img = Image.fromarray(get_bg())
    draw = ImageDraw.Draw(img, 'RGBA')

    font_main = get_font(44, bold=True)
    font_accent = get_font(46, bold=True, italic=True)
    font_small = get_font(32)
    font_wm = get_font(20)
    font_attr = get_font(22, italic=True)

    draw.text((30, 30), "naturithm", font=font_wm, fill=(*SAND, 120))

    y_start = H // 2 - 120

    # Text 1
    if t < 0.5:
        a1 = 0
    elif t < 2.0:
        a1 = int(ease_in_out(min(1.0, (t - 0.5) / 1.0)) * 255)
    else:
        a1 = 255

    if a1 > 0:
        y = draw_centered_text(draw, "What you see\nin others", y_start, font_main, WHITE, a1)
    else:
        y = y_start + 100

    # Text 2
    if t < 2.0:
        a2 = 0
    elif t < 3.5:
        a2 = int(ease_in_out(min(1.0, (t - 2.0) / 1.0)) * 255)
    else:
        a2 = 255

    y += 25
    if a2 > 0:
        y = draw_centered_text(draw, "lives inside you.", y, font_accent, SAND, a2)
    else:
        y += 55

    # Text 3
    if t < 4.0:
        a3 = 0
    elif t < 5.5:
        a3 = int(ease_in_out(min(1.0, (t - 4.0) / 1.0)) * 255)
    else:
        a3 = 255

    y += 35
    if a3 > 0:
        draw_centered_text(draw, "It takes one\nto know one.", y, font_small, WHITE, a3)

    draw.text((W // 2 - 60, H - 80), "— Carl Jung", font=font_attr, fill=(*WHITE, 80))

    return np.array(img)


# ── LOOP VIDEO 5: Meditation Mantra ──────────────────────────────────

def loop5_frame(t):
    """
    0-2s: "I am not my thoughts." (white)
    2-4s: "I am the one watching them." (sand)
    4-6s: "Come back. Again." (white, smaller)
    """
    img = Image.fromarray(get_bg())
    draw = ImageDraw.Draw(img, 'RGBA')

    font_main = get_font(42, bold=True)
    font_accent = get_font(40, bold=True, italic=True)
    font_small = get_font(30)
    font_wm = get_font(20)

    draw.text((30, 30), "naturithm", font=font_wm, fill=(*SAND, 120))

    y_start = H // 2 - 80

    # Text 1
    if t < 0.3:
        a1 = 0
    elif t < 1.8:
        a1 = int(ease_in_out(min(1.0, (t - 0.3) / 1.0)) * 255)
    else:
        a1 = 255

    if a1 > 0:
        y = draw_centered_text(draw, "I am not my thoughts.", y_start, font_main, WHITE, a1)
    else:
        y = y_start + 50

    # Text 2
    if t < 2.0:
        a2 = 0
    elif t < 3.5:
        a2 = int(ease_in_out(min(1.0, (t - 2.0) / 1.0)) * 255)
    else:
        a2 = 255

    y += 30
    if a2 > 0:
        y = draw_centered_text(draw, "I am the one\nwatching them.", y, font_accent, SAND, a2)
    else:
        y += 70

    # Text 3
    if t < 4.0:
        a3 = 0
    elif t < 5.5:
        a3 = int(ease_in_out(min(1.0, (t - 4.0) / 1.0)) * 255)
    else:
        a3 = 255

    y += 40
    if a3 > 0:
        draw_centered_text(draw, "Come back. Again.", y, font_small, WHITE, a3)

    return np.array(img)


LOOPS = {
    "naturithm_loop1": (loop1_frame, "deep_meditation_109.mp3"),
    "naturithm_loop3": (loop3_frame, "serene_view_443.mp3"),
    "naturithm_loop5": (loop5_frame, "deep_meditation_109.mp3"),
}


def create_loop(name, frame_fn, music_file):
    """Create a 6-second loop video."""
    duration = 6.0
    out_dir = OUT_BASE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}_final.mp4"

    print(f"\n  Creating: {name} ({duration}s loop)")

    video = VideoClip(frame_fn, duration=duration).with_fps(FPS)

    # Add music
    music_path = MUSIC_DIR / music_file
    if music_path.exists():
        music = AudioFileClip(str(music_path))
        if music.duration < duration:
            loops = int(duration / music.duration) + 1
            music = concatenate_audioclips([music] * loops)
        music = music.subclipped(0, duration).with_volume_scaled(0.4)
        video = video.with_audio(music)

    video.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ {out_path.name} ({size_mb:.1f}MB)")
    video.close()


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target == "all":
        for name, (fn, music) in LOOPS.items():
            create_loop(name, fn, music)
    elif target in LOOPS:
        fn, music = LOOPS[target]
        create_loop(target, fn, music)
    else:
        print(f"Unknown loop: {target}")
        print(f"Options: {', '.join(LOOPS.keys())} or 'all'")
