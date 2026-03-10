"""Assemble Naturithm story time videos from illustrated frames + narration + music.

Uses Ken Burns effect (slow zoom/pan) on each frame to create movement.
Adds text narration overlays + background music.
"""

import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("IMAGEIO_FFMPEG_EXE", "/opt/homebrew/bin/ffmpeg")

from moviepy import (
    VideoClip, ImageClip, AudioFileClip, CompositeVideoClip,
    CompositeAudioClip, concatenate_videoclips, concatenate_audioclips,
)

W, H = 720, 1280
FPS = 24  # Slightly lower for storybook feel
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
OUT_BASE = Path("/Users/kapi7/Naturithm/output")
MUSIC_DIR = OUT_BASE / "music_library"


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


def ken_burns_clip(image_path, duration, zoom_start=1.0, zoom_end=1.15, pan_x=0, pan_y=-0.02):
    """Create a Ken Burns (slow zoom + pan) clip from a still image."""
    img = Image.open(image_path).convert('RGB')
    # Scale image larger so we have room to zoom/pan
    scale = 1.5
    img = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    img_arr = np.array(img)
    ih, iw = img_arr.shape[:2]

    def make_frame(t):
        progress = t / duration
        # Interpolate zoom
        zoom = zoom_start + (zoom_end - zoom_start) * progress
        # Calculate crop size
        crop_w = int(W / zoom)
        crop_h = int(H / zoom)
        # Center with pan offset
        cx = iw // 2 + int(pan_x * iw * progress)
        cy = ih // 2 + int(pan_y * ih * progress)
        # Crop bounds
        x1 = max(0, cx - crop_w // 2)
        y1 = max(0, cy - crop_h // 2)
        x2 = min(iw, x1 + crop_w)
        y2 = min(ih, y1 + crop_h)
        # Adjust if out of bounds
        if x2 - x1 < crop_w:
            x1 = max(0, x2 - crop_w)
        if y2 - y1 < crop_h:
            y1 = max(0, y2 - crop_h)

        cropped = img_arr[y1:y2, x1:x2]
        # Resize to output dimensions
        pil_crop = Image.fromarray(cropped).resize((W, H), Image.LANCZOS)
        return np.array(pil_crop)

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


def create_narration_overlay(text, size=(W, H)):
    """Create text overlay for narration."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Subtle gradient at bottom for text
    for y in range(int(H * 0.75), H):
        progress = (y - H * 0.75) / (H * 0.25)
        alpha = int(progress * progress * 180)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Narration text
    font = get_font(28, italic=True)
    lines = []
    words = text.split()
    current = ''
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > W - 80 and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    y = H - 40 - len(lines) * 38
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        # Shadow
        for dx, dy in [(1, 2), (-1, 0), (0, -1), (2, 1)]:
            draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, 160))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 240))
        y += 38

    return np.array(img)


def assemble_story(name, scenes, music_file, final_text=None, credit=None):
    """Assemble a story time video from illustrated frames."""
    frames_dir = OUT_BASE / name / "frames"
    out_path = OUT_BASE / name / f"{name}_v2.mp4"

    print(f"\n{'='*50}")
    print(f"  Assembling: {name}")
    print(f"{'='*50}")

    segments = []
    total_duration = 0

    for i, (frame_file, narration, duration, zoom_dir) in enumerate(scenes):
        frame_path = frames_dir / frame_file
        if not frame_path.exists():
            print(f"  ✗ Missing: {frame_file}")
            continue

        # Ken Burns zoom directions
        zoom_params = {
            "in": (1.0, 1.12, 0, -0.01),
            "out": (1.12, 1.0, 0, 0.01),
            "left": (1.05, 1.1, -0.03, 0),
            "right": (1.05, 1.1, 0.03, 0),
        }
        zs, ze, px, py = zoom_params.get(zoom_dir, (1.0, 1.1, 0, 0))

        # Create Ken Burns video from still
        bg = ken_burns_clip(frame_path, duration, zs, ze, px, py)

        # Add narration text overlay
        overlay_arr = create_narration_overlay(narration)
        overlay = ImageClip(overlay_arr).with_duration(duration).with_fps(FPS)

        composite = CompositeVideoClip([bg, overlay])
        segments.append(composite)
        total_duration += duration
        print(f"  Scene {i+1}: {duration}s — \"{narration[:45]}...\"")

    # Add final text card if provided
    if final_text:
        final_img = Image.new('RGB', (W, H), (35, 30, 25))
        draw = ImageDraw.Draw(final_img)

        font_big = get_font(40, bold=True, italic=True)
        font_credit = get_font(22, italic=True)
        font_wm = get_font(20)

        # Main text
        lines = final_text.split('\n')
        y = H // 2 - 50
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_big)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, y), line, font=font_big, fill=SAND)
            y += (bbox[3] - bbox[1]) + 12

        # Credit
        if credit:
            y += 30
            bbox = draw.textbbox((0, 0), credit, font=font_credit)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, y), credit, font=font_credit, fill=WHITE)

        # Watermark
        draw.text((W // 2 - 45, H - 60), "@naturithm7", font=font_wm, fill=SAND)

        final_card = ImageClip(np.array(final_img)).with_duration(4).with_fps(FPS)
        segments.append(final_card)
        total_duration += 4

    if not segments:
        print("  ✗ No segments!")
        return

    final = concatenate_videoclips(segments, method="compose")

    # Add music
    music_path = MUSIC_DIR / music_file
    if music_path.exists():
        music = AudioFileClip(str(music_path))
        if music.duration < total_duration:
            music = concatenate_audioclips([music] * (int(total_duration / music.duration) + 1))
        music = music.subclipped(0, final.duration).with_volume_scaled(0.30)
        final = final.with_audio(music)

    print(f"\n  Rendering {out_path.name} ({total_duration:.0f}s)...")
    final.write_videofile(
        str(out_path), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4, logger=None,
    )
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ {out_path.name} ({size_mb:.1f}MB)")
    final.close()


# ── DUCK STORY scenes ─────────────────────────────────────────────────
# (frame_file, narration_text, duration_seconds, zoom_direction)

DUCK_SCENES = [
    ("01_pond.png",
     "Two ducks are floating peacefully on a pond.",
     7, "in"),

    ("02_fight.png",
     "Suddenly, they clash. A fight breaks out. Feathers fly. Water splashes.",
     7, "right"),

    ("03_shake.png",
     "Then it's over. They separate. Each duck flaps its wings — hard. Releasing the energy. Shaking it off.",
     8, "out"),

    ("04_peace.png",
     "And then… peace. As if nothing happened. The fight is forgotten.",
     7, "in"),

    ("05_human.png",
     "Now imagine the duck had a human mind. It would replay the fight for days. 'I can't believe he did that. He thinks he owns this pond.' The fight would never end.",
     12, "left"),

    ("06_message.png",
     "The duck knew something we forgot. The fight is over. Flap your wings. Let it go.",
     9, "in"),
]


# ── THORN STORY scenes ────────────────────────────────────────────────

THORN_SCENES = [
    ("01_thorn.png",
     "Imagine a dog with a thorn in its paw. Deep. Pressing against a nerve.",
     7, "in"),

    ("02_snap.png",
     "Now everything that touches it — even gently — brings pain. The dog doesn't see a friendly hand. It only feels the thorn.",
     8, "right"),

    ("03_push.png",
     "People come and go. Some with good intentions. The dog pushes them all away. Not because of them — because of the thorn.",
     8, "left"),

    ("04_shrink.png",
     "Over time, the dog builds its entire life around protecting the thorn. It stops running. Stops playing. The whole world shrinks to the size of its pain.",
     10, "out"),

    ("05_remove.png",
     "Or… it could just remove the thorn. Yes, it hurts for a moment. But then—",
     7, "in"),

    ("06_free.png",
     "Freedom. The field is open. The dog was never broken — it was just in pain.",
     8, "right"),
]


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "duck"

    if target == "duck":
        assemble_story(
            "naturithm_duck", DUCK_SCENES,
            "hope_and_kindness_534.mp3",
            final_text="Flap your wings.",
            credit="Based on Eckhart Tolle — A New Earth"
        )
    elif target == "thorn":
        assemble_story(
            "naturithm_thorn", THORN_SCENES,
            "deep_meditation_109.mp3",
            final_text="What thorn are you\nstill protecting?",
            credit="Inspired by Michael Singer — The Untethered Soul"
        )
    elif target == "all":
        assemble_story(
            "naturithm_duck", DUCK_SCENES,
            "hope_and_kindness_534.mp3",
            final_text="Flap your wings.",
            credit="Based on Eckhart Tolle — A New Earth"
        )
        assemble_story(
            "naturithm_thorn", THORN_SCENES,
            "deep_meditation_109.mp3",
            final_text="What thorn are you\nstill protecting?",
            credit="Inspired by Michael Singer — The Untethered Soul"
        )
