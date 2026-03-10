"""Create Naturithm loop videos V2 — stock video background + text overlays."""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

os.environ.setdefault("IMAGEIO_FFMPEG_EXE", "/opt/homebrew/bin/ffmpeg")

from moviepy import (
    VideoFileClip, VideoClip, ImageClip, AudioFileClip,
    CompositeVideoClip, concatenate_audioclips,
)

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
    return t * t * (3 - 2 * t)


def create_text_frame(texts, alphas, watermark="naturithm", attribution=None):
    """Create a RGBA text overlay frame.

    texts: list of (text, font, color) tuples
    alphas: list of alpha values (0-255) for each text
    """
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Subtle center gradient for text readability
    for y in range(int(H * 0.35), int(H * 0.75)):
        progress = 1 - abs((y - H * 0.55) / (H * 0.2))
        progress = max(0, min(1, progress))
        alpha = int(progress * 120)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Watermark
    wm_font = get_font(22)
    draw.text((30, 40), watermark, font=wm_font, fill=(196, 149, 106, 120))

    # Attribution at bottom
    if attribution:
        attr_font = get_font(22, italic=True)
        bbox = draw.textbbox((0, 0), attribution, font=attr_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H - 80), attribution, font=attr_font, fill=(255, 255, 255, 80))

    # Draw texts centered
    y = H // 2 - 100
    for (text, font, color), alpha in zip(texts, alphas):
        if alpha <= 0:
            # Still advance y position
            lines = text.split('\n')
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                y += (bbox[3] - bbox[1]) + 10
            y += 20
            continue

        lines = text.split('\n')
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (W - tw) // 2

            # Shadow
            for dx, dy in [(0, 2), (2, 0), (0, -1), (-1, 0)]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, min(alpha, 150)))
            draw.text((x, y), line, font=font, fill=(*color[:3], alpha))
            y += th + 10
        y += 20

    return np.array(img)


def make_loop_video(name, bg_path, texts_config, music_file, attribution=None):
    """Create a 6-second loop video with background + animated text."""
    duration = 6.0
    out_path = OUT_BASE / name / f"{name}_v2.mp4"

    print(f"\n  Creating: {name}")

    # Load background video
    if bg_path.exists():
        bg = VideoFileClip(str(bg_path))
        if bg.duration < duration:
            from moviepy import concatenate_videoclips
            loops = int(duration / bg.duration) + 1
            bg = concatenate_videoclips([bg] * loops)
        bg = bg.subclipped(0, duration)
        if bg.size != (W, H):
            bg = bg.resized((W, H))
    else:
        # Gradient fallback
        gradient = np.zeros((H, W, 3), dtype=np.uint8)
        for y in range(H):
            t = y / H
            gradient[y] = [int(52*(1-t)+35*t), int(45*(1-t)+30*t), int(38*(1-t)+25*t)]
        bg = ImageClip(gradient).with_duration(duration).with_fps(FPS)

    # texts_config: list of (text, font, color, fade_start, fade_end)
    def make_overlay(t):
        texts = []
        alphas = []
        for text, font, color, fade_start, fade_end in texts_config:
            if t < fade_start:
                alpha = 0
            elif t < fade_end:
                alpha = int(ease_in_out(min(1.0, (t - fade_start) / (fade_end - fade_start))) * 255)
            else:
                alpha = 255
            texts.append((text, font, color))
            alphas.append(alpha)
        return create_text_frame(texts, alphas, attribution=attribution)

    overlay = VideoClip(make_overlay, duration=duration).with_fps(FPS)
    final = CompositeVideoClip([bg, overlay])

    # Music
    music_path = MUSIC_DIR / music_file
    if music_path.exists():
        music = AudioFileClip(str(music_path))
        if music.duration < duration:
            music = concatenate_audioclips([music] * (int(duration / music.duration) + 1))
        music = music.subclipped(0, duration).with_volume_scaled(0.35)
        final = final.with_audio(music)

    final.write_videofile(
        str(out_path), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4, logger=None,
    )
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ {out_path.name} ({size_mb:.1f}MB)")
    final.close()


# ── Font shortcuts ────────────────────────────────────────────────────
f_main = get_font(46, bold=True)
f_accent = get_font(44, bold=True, italic=True)
f_small = get_font(32)

# ── Loop 1: Wayne Dyer ───────────────────────────────────────────────
LOOP1_TEXTS = [
    ("When you change", f_main, WHITE, 0.3, 1.5),
    ("the way you look\nat things", f_main, WHITE, 1.8, 3.0),
    ("the things you look at\nchange.", f_accent, SAND, 3.5, 5.0),
]

# ── Loop 3: Carl Jung ────────────────────────────────────────────────
LOOP3_TEXTS = [
    ("What you see\nin others", f_main, WHITE, 0.3, 1.5),
    ("lives inside you.", f_accent, SAND, 2.0, 3.2),
    ("It takes one\nto know one.", f_small, WHITE, 4.0, 5.2),
]

# ── Loop 5: Meditation ───────────────────────────────────────────────
LOOP5_TEXTS = [
    ("I am not my thoughts.", f_main, WHITE, 0.3, 1.5),
    ("I am the one\nwatching them.", f_accent, SAND, 2.0, 3.2),
    ("Come back. Again.", f_small, WHITE, 4.0, 5.2),
]


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    loops = {
        "naturithm_loop1": (LOOP1_TEXTS, "deep_meditation_109.mp3", "— Wayne Dyer"),
        "naturithm_loop3": (LOOP3_TEXTS, "serene_view_443.mp3", "— Carl Jung"),
        "naturithm_loop5": (LOOP5_TEXTS, "deep_meditation_109.mp3", None),
    }

    if target == "all":
        for name, (texts, music, attr) in loops.items():
            bg = OUT_BASE / name / "background.mp4"
            make_loop_video(name, bg, texts, music, attr)
    elif target in loops:
        texts, music, attr = loops[target]
        bg = OUT_BASE / target / "background.mp4"
        make_loop_video(target, bg, texts, music, attr)
