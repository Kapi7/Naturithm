"""Assemble Oria reels from TTS audio + text overlays + background music.

Creates complete reels using:
- TTS voice-over clips (already generated)
- Animated text overlays (Palatino, white + sand)
- Background music from music_library
- Branded earth-tone gradient background

Output: 720x1280 vertical reels ready for Instagram.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Ensure moviepy can find ffmpeg
os.environ.setdefault("IMAGEIO_FFMPEG_EXE", "/opt/homebrew/bin/ffmpeg")

from moviepy import (
    VideoClip,
    AudioFileClip,
    CompositeAudioClip,
    concatenate_videoclips,
    concatenate_audioclips,
)

W, H = 720, 1280
FPS = 30
SAND = (196, 149, 106)
WHITE = (255, 255, 255)
EARTH_BG_TOP = (52, 45, 38)
EARTH_BG_BOT = (35, 30, 25)
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


def make_gradient_frame():
    """Create earth-tone gradient background."""
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(EARTH_BG_TOP[0] * (1 - t) + EARTH_BG_BOT[0] * t)
        g = int(EARTH_BG_TOP[1] * (1 - t) + EARTH_BG_BOT[1] * t)
        b = int(EARTH_BG_TOP[2] * (1 - t) + EARTH_BG_BOT[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def draw_centered_text(draw, text, y, font, fill=WHITE, max_width=620):
    """Draw centered text with word wrap, return bottom y."""
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
        draw.text((x, y), line, font=font, fill=fill)
        y += th + 8
    return y


def make_clip_frame(text_white, text_sand, watermark="oria"):
    """Create a single frame with two-tone text overlay."""
    bg = make_gradient_frame()
    draw = ImageDraw.Draw(bg)

    # Watermark
    wm_font = get_font(22)
    draw.text((30, 30), watermark, font=wm_font, fill=(*SAND, 180))

    # Main text
    font_white = get_font(38, bold=True)
    font_sand = get_font(36, bold=True, italic=True)

    y = H // 2 - 100
    if text_white:
        y = draw_centered_text(draw, text_white, y, font_white, WHITE)
    y += 25
    if text_sand:
        draw_centered_text(draw, text_sand, y, font_sand, SAND)

    return np.array(bg)


def create_text_clip(text_white, text_sand, duration, watermark="oria"):
    """Create a video clip with static text overlay on gradient."""
    frame = make_clip_frame(text_white, text_sand, watermark)

    def make_frame(t):
        return frame

    return VideoClip(make_frame, duration=duration).with_fps(FPS)


def assemble_reel(reel_name, clips_data, music_file=None):
    """
    Assemble a complete reel.

    clips_data: list of dicts with keys:
        - audio: path to TTS wav file
        - text_white: white text overlay
        - text_sand: sand italic text overlay
    """
    audio_dir = OUT_BASE / reel_name / "audio"
    out_path = OUT_BASE / reel_name / f"{reel_name}_final.mp4"

    print(f"\n{'='*50}")
    print(f"  Assembling: {reel_name}")
    print(f"{'='*50}")

    video_clips = []
    audio_clips = []
    total_duration = 0

    for i, clip_data in enumerate(clips_data):
        # Load TTS audio
        audio_path = audio_dir / clip_data["audio"]
        if not audio_path.exists():
            print(f"  ✗ Missing audio: {audio_path}")
            continue

        audio = AudioFileClip(str(audio_path))
        duration = audio.duration + 0.5  # Add 0.5s padding after each clip

        # Create text video clip
        video = create_text_clip(
            clip_data["text_white"],
            clip_data["text_sand"],
            duration,
        )

        video_clips.append(video)
        audio_clips.append(audio)
        total_duration += duration
        print(f"  Clip {i+1}: {duration:.1f}s — \"{clip_data['text_white'][:40]}...\"")

    if not video_clips:
        print("  ✗ No clips to assemble!")
        return

    # Concatenate video
    final_video = concatenate_videoclips(video_clips, method="compose")

    # Concatenate audio with gaps
    padded_audio = []
    for ac in audio_clips:
        padded_audio.append(ac)

    final_audio = concatenate_audioclips(padded_audio)

    # Add background music if available
    if music_file and Path(music_file).exists():
        music = AudioFileClip(str(music_file))
        # Loop music if shorter than video, trim if longer
        if music.duration < total_duration:
            loops_needed = int(total_duration / music.duration) + 1
            music = concatenate_audioclips([music] * loops_needed)
        music = music.subclipped(0, min(total_duration, final_audio.duration))
        music = music.with_volume_scaled(0.15)

        # Mix voice + music
        combined_audio = CompositeAudioClip([final_audio, music])
        final_video = final_video.with_audio(combined_audio)
    else:
        final_video = final_video.with_audio(final_audio)

    # Write
    print(f"\n  Rendering {out_path.name}...")
    final_video.write_videofile(
        str(out_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ {out_path.name} ({size_mb:.1f}MB, {total_duration:.1f}s)")

    # Cleanup
    for clip in video_clips:
        clip.close()
    for clip in audio_clips:
        clip.close()
    final_video.close()


# ── Reel definitions ──────────────────────────────────────────────────

PANCAKE = [
    {"audio": "01_hook.wav", "text_white": "Your kid doesn't know", "text_sand": "And that's the point"},
    {"audio": "02_eggs.wav", "text_white": "3 eggs = your foundation", "text_sand": "Not flour — eggs"},
    {"audio": "03_mix.wav", "text_white": "Almond flour • banana\n• baking soda", "text_sand": "That's it"},
    {"audio": "04_cook.wav", "text_white": "It might break", "text_sand": "That means no gluten,\nno inflammation"},
    {"audio": "05_plate.wav", "text_white": "No bloat. No crash.", "text_sand": "Clean fuel for\na growing body"},
    {"audio": "06_close.wav", "text_white": "Feed them what their\nbody recognizes", "text_sand": "Not what a factory designed"},
]

GARLIC = [
    {"audio": "01_hook.wav", "text_white": "Two ingredients", "text_sand": "Ancient medicine"},
    {"audio": "02_crush.wav", "text_white": "Crush, don't chop", "text_sand": "Nature's antibiotic"},
    {"audio": "03_jar.wav", "text_white": "Raw honey only", "text_sand": "The wild yeast\nmakes it alive"},
    {"audio": "04_flip.wav", "text_white": "Flip daily.\nWait one month.", "text_sand": "No pharmacy can\nsell you this"},
    {"audio": "05_spoon.wav", "text_white": "Antimicrobial •\nImmune-boosting", "text_sand": "One spoonful a day"},
    {"audio": "06_close.wav", "text_white": "Nature already made\nthe medicine", "text_sand": "Be patient enough\nto let it work"},
]

DEODORANT = [
    {"audio": "01_hook.wav", "text_white": "Aluminum • Parabens\n• Phthalates", "text_sand": "Every. Single. Day."},
    {"audio": "02_melt.wav", "text_white": "Beeswax • coconut oil\n• shea butter", "text_sand": "Melt together"},
    {"audio": "03_mix.wav", "text_white": "Arrowroot + baking soda", "text_sand": "Tea tree + lavender"},
    {"audio": "04_pour.wav", "text_white": "2 hours to set", "text_sand": "6 months of deodorant"},
    {"audio": "05_apply.wav", "text_white": "Sweating is not the enemy", "text_sand": "Blocking it is"},
    {"audio": "06_close.wav", "text_white": "Your skin absorbs\neverything", "text_sand": "Choose wisely"},
]

ADDICTION = [
    {"audio": "01_hook.wav", "text_white": "Nobody chooses addiction", "text_sand": "They choose relief"},
    {"audio": "02_thing.wav", "text_white": "It was never\nabout the thing", "text_sand": "It was about the feeling\nunderneath"},
    {"audio": "03_pain.wav", "text_white": "Not why the addiction", "text_sand": "Why the pain"},
    {"audio": "04_feel.wav", "text_white": "Willpower doesn't\nfix a wound", "text_sand": "Feel what you've been\nrunning from"},
    {"audio": "05_connect.wav", "text_white": "The opposite of addiction", "text_sand": "Is connection"},
    {"audio": "06_close.wav", "text_white": "You are not your\ncoping mechanism", "text_sand": "You deserve gentleness"},
]

MUSIC_MAP = {
    "pancake_reel": MUSIC_DIR / "hope_and_kindness_534.mp3",
    "garlic_reel": MUSIC_DIR / "hope_and_kindness_534.mp3",
    "deodorant_reel": MUSIC_DIR / "serene_view_443.mp3",
    "addiction_reel": MUSIC_DIR / "deep_meditation_109.mp3",
}


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    reels = {
        "pancake_reel": PANCAKE,
        "garlic_reel": GARLIC,
        "deodorant_reel": DEODORANT,
        "addiction_reel": ADDICTION,
    }

    if target == "all":
        for name, data in reels.items():
            assemble_reel(name, data, MUSIC_MAP.get(name))
    elif target in reels:
        assemble_reel(target, reels[target], MUSIC_MAP.get(target))
    else:
        print(f"Unknown reel: {target}")
        print(f"Options: {', '.join(reels.keys())} or 'all'")
