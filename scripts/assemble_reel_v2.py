"""Assemble Oria reels V2 — stock video + TTS audio + text overlays + music.

Uses actual stock video clips as background with text overlays.
"""

import os
import sys
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault("IMAGEIO_FFMPEG_EXE", "/opt/homebrew/bin/ffmpeg")

from moviepy import (
    VideoFileClip,
    VideoClip,
    AudioFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
    concatenate_audioclips,
    ImageClip,
)

W, H = 720, 1280
FPS = 30
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


def create_text_overlay(text_white, text_sand, size=(W, H)):
    """Create a transparent PNG text overlay."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Subtle gradient only at bottom 30% — let the video breathe
    for y in range(int(H * 0.65), H):
        progress = (y - H * 0.65) / (H * 0.35)
        alpha = int(min(200, progress * progress * 230))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        draw.line([(0, y), (W, y)], fill=(20, 18, 15, alpha))

    # Watermark
    wm_font = get_font(24)
    draw.text((30, 40), "oria", font=wm_font, fill=(196, 149, 106, 200))

    font_white = get_font(42, bold=True)
    font_sand = get_font(38, bold=True, italic=True)

    # Draw text at very bottom (where gradient is darkest)
    y_base = H - 240

    # White text
    if text_white:
        lines = text_white.split('\n')
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_white)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (W - tw) // 2
            # Text shadow for readability (stronger)
            for dx, dy in [(0,3),(3,0),(0,-1),(-1,0),(2,2),(-2,2)]:
                draw.text((x+dx, y_base+dy), line, font=font_white, fill=(0, 0, 0, 180))
            draw.text((x, y_base), line, font=font_white, fill=(255, 255, 255, 255))
            y_base += th + 10

    y_base += 15

    # Sand text
    if text_sand:
        lines = text_sand.split('\n')
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_sand)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = (W - tw) // 2
            for dx, dy in [(0,3),(3,0),(0,-1),(-1,0),(2,2),(-2,2)]:
                draw.text((x+dx, y_base+dy), line, font=font_sand, fill=(0, 0, 0, 180))
            draw.text((x, y_base), line, font=font_sand, fill=(*SAND, 255))
            y_base += th + 10

    return np.array(img)


def assemble_reel(reel_name, clips_data, music_file=None):
    """Assemble reel with video backgrounds + text overlays + TTS audio."""
    audio_dir = OUT_BASE / reel_name / "audio"
    video_dir = OUT_BASE / reel_name / "video"
    out_path = OUT_BASE / reel_name / f"{reel_name}_v2.mp4"

    print(f"\n{'='*50}")
    print(f"  Assembling: {reel_name} (V2 — with stock video)")
    print(f"{'='*50}")

    segments = []
    total_duration = 0

    for i, clip_data in enumerate(clips_data):
        audio_path = audio_dir / clip_data["audio"]
        video_path = video_dir / clip_data["video"]

        if not audio_path.exists():
            print(f"  ✗ Missing audio: {audio_path.name}")
            continue

        # Load TTS audio to get duration
        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 0.3  # Slight padding

        # Load video clip (or create gradient fallback)
        if video_path.exists():
            bg_clip = VideoFileClip(str(video_path))
            # Loop or trim to match audio duration
            if bg_clip.duration < duration:
                # Loop the video
                loops_needed = int(duration / bg_clip.duration) + 1
                bg_clip = concatenate_videoclips([bg_clip] * loops_needed)
            bg_clip = bg_clip.subclipped(0, duration)
            # Resize to exact dimensions if needed
            if bg_clip.size != (W, H):
                bg_clip = bg_clip.resized((W, H))
        else:
            print(f"  ⚠ No video for {clip_data['video']}, using gradient")
            # Gradient fallback
            gradient = np.zeros((H, W, 3), dtype=np.uint8)
            for y in range(H):
                t = y / H
                gradient[y] = [int(52*(1-t)+35*t), int(45*(1-t)+30*t), int(38*(1-t)+25*t)]
            bg_clip = ImageClip(gradient).with_duration(duration).with_fps(FPS)

        # Create text overlay as image clip
        overlay_arr = create_text_overlay(clip_data["text_white"], clip_data["text_sand"])
        overlay_clip = ImageClip(overlay_arr).with_duration(duration).with_fps(FPS)

        # Composite: video + text overlay
        composite = CompositeVideoClip([bg_clip, overlay_clip])
        composite = composite.with_audio(audio)

        segments.append(composite)
        total_duration += duration
        print(f"  Clip {i+1}: {duration:.1f}s — \"{clip_data['text_white'][:35]}...\"")

    if not segments:
        print("  ✗ No segments!")
        return

    # Concatenate all segments
    final = concatenate_videoclips(segments, method="compose")

    # Add background music
    if music_file and Path(music_file).exists():
        music = AudioFileClip(str(music_file))
        if music.duration < total_duration:
            loops = int(total_duration / music.duration) + 1
            music = concatenate_audioclips([music] * loops)
        music = music.subclipped(0, final.duration).with_volume_scaled(0.12)

        final = final.with_audio(
            CompositeAudioClip([final.audio, music])
        )

    print(f"\n  Rendering {out_path.name} ({total_duration:.0f}s)...")
    final.write_videofile(
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

    # Cleanup
    final.close()
    for seg in segments:
        seg.close()


# ── Clip data ─────────────────────────────────────────────────────────

PANCAKE = [
    {"audio": "01_hook.wav", "video": "01_hook.mp4",
     "text_white": "Your kid doesn't know", "text_sand": "And that's the point"},
    {"audio": "02_eggs.wav", "video": "02_eggs.mp4",
     "text_white": "3 eggs = your foundation", "text_sand": "Not flour — eggs"},
    {"audio": "03_mix.wav", "video": "03_mix.mp4",
     "text_white": "Almond flour • banana\n• baking soda", "text_sand": "That's it"},
    {"audio": "04_cook.wav", "video": "04_cook.mp4",
     "text_white": "It breaks easier — good.", "text_sand": "No gluten holding it together"},
    {"audio": "05_plate.wav", "video": "05_plate.mp4",
     "text_white": "No bloat. No crash.", "text_sand": "Clean fuel for a growing body"},
    {"audio": "06_close.wav", "video": "06_close.mp4",
     "text_white": "Feed them what their\nbody recognizes", "text_sand": "Not what a factory designed"},
]

GARLIC = [
    {"audio": "01_hook.wav", "video": "01_hook.mp4",
     "text_white": "Two ingredients", "text_sand": "Ancient medicine"},
    {"audio": "02_crush.wav", "video": "02_crush.mp4",
     "text_white": "Crush, don't chop", "text_sand": "Nature's antibiotic"},
    {"audio": "03_jar.wav", "video": "03_jar.mp4",
     "text_white": "Raw honey only", "text_sand": "The wild yeast makes it alive"},
    {"audio": "04_flip.wav", "video": "04_flip.mp4",
     "text_white": "Flip daily. Wait one month.", "text_sand": "No pharmacy can sell you this"},
    {"audio": "05_spoon.wav", "video": "05_spoon.mp4",
     "text_white": "Antimicrobial •\nImmune-boosting", "text_sand": "One spoonful a day"},
    {"audio": "06_close.wav", "video": "06_close.mp4",
     "text_white": "Nature already made\nthe medicine", "text_sand": "Be patient enough to let it work"},
]

DEODORANT = [
    {"audio": "01_hook.wav", "video": "01_hook.mp4",
     "text_white": "Aluminum • Parabens\n• Phthalates", "text_sand": "Every. Single. Day."},
    {"audio": "02_melt.wav", "video": "02_melt.mp4",
     "text_white": "Beeswax • coconut oil\n• shea butter", "text_sand": "Melt together"},
    {"audio": "03_mix.wav", "video": "03_mix.mp4",
     "text_white": "Arrowroot + baking soda", "text_sand": "Tea tree + lavender"},
    {"audio": "04_pour.wav", "video": "04_pour.mp4",
     "text_white": "2 hours to set", "text_sand": "6 months of deodorant"},
    {"audio": "05_apply.wav", "video": "05_apply.mp4",
     "text_white": "Sweating is not the enemy", "text_sand": "Blocking it is"},
    {"audio": "06_close.wav", "video": "06_close.mp4",
     "text_white": "Your skin absorbs\neverything", "text_sand": "Choose wisely"},
]

ADDICTION = [
    {"audio": "01_hook.wav", "video": "01_hook.mp4",
     "text_white": "Nobody chooses addiction", "text_sand": "They choose relief"},
    {"audio": "02_thing.wav", "video": "02_thing.mp4",
     "text_white": "It was never\nabout the thing", "text_sand": "It was about the feeling\nunderneath"},
    {"audio": "03_pain.wav", "video": "03_pain.mp4",
     "text_white": "Not why the addiction", "text_sand": "Why the pain"},
    {"audio": "04_feel.wav", "video": "04_feel.mp4",
     "text_white": "Willpower doesn't\nfix a wound", "text_sand": "Feel what you've been\nrunning from"},
    {"audio": "05_connect.wav", "video": "05_connect.mp4",
     "text_white": "The opposite of addiction", "text_sand": "Is connection"},
    {"audio": "06_close.wav", "video": "06_close.mp4",
     "text_white": "You are not your\ncoping mechanism", "text_sand": "You deserve gentleness"},
]

MUSIC_MAP = {
    "pancake_reel": MUSIC_DIR / "howto_dreaming_big_31.mp3",
    "garlic_reel": MUSIC_DIR / "howto_driving_32.mp3",
    "deodorant_reel": MUSIC_DIR / "howto_dreaming_big_31.mp3",
    "addiction_reel": MUSIC_DIR / "deep_silent_descent_614.mp3",
}

REELS = {
    "pancake_reel": PANCAKE,
    "garlic_reel": GARLIC,
    "deodorant_reel": DEODORANT,
    "addiction_reel": ADDICTION,
}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "pancake_reel"

    if target == "all":
        for name, data in REELS.items():
            assemble_reel(name, data, MUSIC_MAP.get(name))
    elif target in REELS:
        assemble_reel(target, REELS[target], MUSIC_MAP.get(target))
    else:
        print(f"Options: {', '.join(REELS.keys())} or 'all'")
