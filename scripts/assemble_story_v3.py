"""Assemble story time videos V3 — with Oria voice narration + tighter pacing.

Duck story: shortened, better subtitle flow synced to voice.
Fence story: new story replacing thorn, with voice narration.
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
FPS = 24
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
    scale = 1.5
    img = img.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    img_arr = np.array(img)
    ih, iw = img_arr.shape[:2]

    def make_frame(t):
        progress = t / duration if duration > 0 else 0
        zoom = zoom_start + (zoom_end - zoom_start) * progress
        crop_w = int(W / zoom)
        crop_h = int(H / zoom)
        cx = iw // 2 + int(pan_x * iw * progress)
        cy = ih // 2 + int(pan_y * ih * progress)
        x1 = max(0, cx - crop_w // 2)
        y1 = max(0, cy - crop_h // 2)
        x2 = min(iw, x1 + crop_w)
        y2 = min(ih, y1 + crop_h)
        if x2 - x1 < crop_w:
            x1 = max(0, x2 - crop_w)
        if y2 - y1 < crop_h:
            y1 = max(0, y2 - crop_h)
        cropped = img_arr[y1:y2, x1:x2]
        pil_crop = Image.fromarray(cropped).resize((W, H), Image.LANCZOS)
        return np.array(pil_crop)

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


def create_subtitle_overlay(text, size=(W, H), fade_progress=1.0):
    """Create flowing subtitle overlay — appears word by word feel."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Subtle gradient at bottom
    for y in range(int(H * 0.78), H):
        progress = (y - H * 0.78) / (H * 0.22)
        alpha = int(progress * progress * 160)
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    font = get_font(30, italic=True)
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

    # Calculate visible characters based on fade_progress
    total_chars = sum(len(line) for line in lines)
    visible_chars = int(total_chars * min(1.0, fade_progress))

    y = H - 40 - len(lines) * 40
    chars_shown = 0
    for line in lines:
        if chars_shown >= visible_chars:
            break
        # How much of this line to show
        line_visible = min(len(line), visible_chars - chars_shown)
        visible_text = line[:line_visible]
        chars_shown += line_visible

        if not visible_text.strip():
            y += 40
            continue

        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2

        alpha = int(min(255, fade_progress * 300))
        # Shadow
        for dx, dy in [(1, 2), (-1, 0), (0, -1), (2, 1)]:
            draw.text((x+dx, y+dy), visible_text, font=font, fill=(0, 0, 0, min(alpha, 160)))
        draw.text((x, y), visible_text, font=font, fill=(255, 255, 255, alpha))
        y += 40

    return np.array(img)


def assemble_story_v3(name, scenes, music_file, final_text=None, credit=None):
    """Assemble story with voice narration + flowing subtitles."""
    frames_dir = OUT_BASE / name / "frames"
    audio_dir = OUT_BASE / name / "audio"
    out_path = OUT_BASE / name / f"{name}_v3.mp4"

    print(f"\n{'='*50}")
    print(f"  Assembling: {name} (V3 — with voice)")
    print(f"{'='*50}")

    segments = []
    total_duration = 0

    for i, (frame_file, narration, min_duration, zoom_dir) in enumerate(scenes):
        frame_path = frames_dir / frame_file
        if not frame_path.exists():
            print(f"  Missing: {frame_file}")
            continue

        # Check for voice audio
        audio_name = frame_file.replace('.png', '.wav')
        audio_path = audio_dir / audio_name
        has_voice = audio_path.exists()

        if has_voice:
            voice = AudioFileClip(str(audio_path))
            duration = max(min_duration, voice.duration + 0.5)
        else:
            duration = min_duration
            voice = None

        # Ken Burns zoom
        zoom_params = {
            "in": (1.0, 1.12, 0, -0.01),
            "out": (1.12, 1.0, 0, 0.01),
            "left": (1.05, 1.1, -0.03, 0),
            "right": (1.05, 1.1, 0.03, 0),
        }
        zs, ze, px, py = zoom_params.get(zoom_dir, (1.0, 1.1, 0, 0))
        bg = ken_burns_clip(frame_path, duration, zs, ze, px, py)

        # Flowing subtitle overlay — text appears progressively
        text = narration
        def make_subtitle(t, text=text, duration=duration):
            # Text starts appearing at 0.3s, fully visible by 70% of duration
            if t < 0.3:
                progress = 0
            else:
                progress = min(1.0, (t - 0.3) / (duration * 0.65))
            return create_subtitle_overlay(text, fade_progress=progress)

        overlay = VideoClip(make_subtitle, duration=duration).with_fps(FPS)
        composite = CompositeVideoClip([bg, overlay])

        # Add voice audio
        if voice:
            composite = composite.with_audio(voice)

        segments.append(composite)
        total_duration += duration
        print(f"  Scene {i+1}: {duration:.1f}s {'(voice)' if has_voice else '(text only)'} — \"{narration[:40]}...\"")

    # Final text card
    if final_text:
        final_img = Image.new('RGB', (W, H), (35, 30, 25))
        draw = ImageDraw.Draw(final_img)

        font_big = get_font(40, bold=True, italic=True)
        font_credit = get_font(22, italic=True)
        font_wm = get_font(20)

        lines = final_text.split('\n')
        y = H // 2 - 50
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_big)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, y), line, font=font_big, fill=SAND)
            y += (bbox[3] - bbox[1]) + 12

        if credit:
            y += 30
            bbox = draw.textbbox((0, 0), credit, font=font_credit)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, y), credit, font=font_credit, fill=WHITE)

        draw.text((W // 2 - 45, H - 60), "@naturithm7", font=font_wm, fill=SAND)

        final_card = ImageClip(np.array(final_img)).with_duration(3.5).with_fps(FPS)
        segments.append(final_card)
        total_duration += 3.5

    if not segments:
        print("  No segments!")
        return

    final = concatenate_videoclips(segments, method="compose")

    # Mix voice + background music
    music_path = MUSIC_DIR / music_file
    if music_path.exists():
        music = AudioFileClip(str(music_path))
        if music.duration < total_duration:
            music = concatenate_audioclips([music] * (int(total_duration / music.duration) + 1))
        music = music.subclipped(0, final.duration).with_volume_scaled(0.18)

        if final.audio:
            final = final.with_audio(CompositeAudioClip([final.audio, music]))
        else:
            final = final.with_audio(music)

    print(f"\n  Rendering {out_path.name} ({total_duration:.0f}s)...")
    final.write_videofile(
        str(out_path), fps=FPS, codec="libx264", audio_codec="aac",
        preset="medium", threads=4, logger=None,
    )
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  Done: {out_path.name} ({size_mb:.1f}MB)")
    final.close()


# ── DUCK STORY (shortened, punchier) ────────────────────────────────
DUCK_SCENES = [
    ("01_pond.png",
     "Two ducks. Floating on a pond. Quiet. Still.",
     5, "in"),
    ("02_fight.png",
     "Then — chaos. They clash. Feathers fly. Water splashes everywhere.",
     5, "right"),
    ("03_shake.png",
     "And then it's over. Each duck flaps its wings hard. Shaking off the energy. Letting it go.",
     6, "out"),
    ("04_peace.png",
     "Peace. Like nothing happened.",
     4, "in"),
    ("05_human.png",
     "Now imagine that duck had a human mind. It would replay that fight for days. I can't believe he did that. He thinks he owns this pond.",
     8, "left"),
    ("06_message.png",
     "The duck knew something we forgot. The fight is over. Flap your wings. Let it go.",
     7, "in"),
]

# ── FENCE/COLLAR STORY (invisible fence with shock collar) ──────────
FENCE_SCENES = [
    ("01_fence.png",
     "There's a dog. Wearing a collar. Around the yard, an invisible fence. Every time it gets close — the collar buzzes.",
     7, "in"),
    ("02_approach.png",
     "So the dog learns. Don't go near the edge. Stay in the middle. Stay safe.",
     5, "right"),
    ("03_retreat.png",
     "Over time, the dog forgets there's even a world beyond the yard. Its whole life shrinks to the size of what doesn't hurt.",
     7, "left"),
    ("04_decide.png",
     "One day, the dog sees something on the other side. And something shifts. It walks toward the edge. The collar buzzes. It keeps walking.",
     7, "in"),
    ("05_through.png",
     "The buzz gets louder. The pain gets sharper. Every part of the dog says stop. But it takes one more step. And then — silence.",
     7, "right"),
    ("06_free.png",
     "The field was always there. The collar couldn't stop it. Only the dog's belief in the collar could. What invisible fence are you still obeying?",
     8, "in"),
]


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ("duck", "all"):
        assemble_story_v3(
            "naturithm_duck", DUCK_SCENES,
            "story_discover_587.mp3",
            final_text="Flap your wings.",
            credit="Based on Eckhart Tolle — A New Earth"
        )

    if target in ("fence", "all"):
        assemble_story_v3(
            "naturithm_fence", FENCE_SCENES,
            "story_miss_you_592.mp3",
            final_text="What invisible fence\nare you still obeying?",
            credit="Inspired by Michael Singer — The Untethered Soul"
        )
