"""Generate Oria character image + Veo video clips for reels.

Creates a consistent Oria character and generates video clips of her
for use as hooks in pancake, garlic, and deodorant reels.
"""

import os
import time
import subprocess
from pathlib import Path
from google import genai
from google.genai import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/kapi7/Naturithm/credentials.json'

client = genai.Client(
    vertexai=True,
    project='naturitm',
    location='us-central1',
)

OUT_BASE = Path("/Users/kapi7/Naturithm/output")
ORIA_DIR = OUT_BASE / "oria_character"
ORIA_DIR.mkdir(parents=True, exist_ok=True)

# Oria character description (consistent across all prompts)
ORIA_DESC = (
    "A beautiful woman in her late 20s with warm olive skin, long dark wavy hair, "
    "natural minimal makeup, soft brown eyes, gentle confident smile. "
    "She wears earth-tone linen clothing. Mediterranean beauty. "
)


def generate_oria_portrait():
    """Generate Oria reference portrait with Imagen."""
    out_path = ORIA_DIR / "oria_portrait.png"
    if out_path.exists() and out_path.stat().st_size > 5000:
        print(f"  Already exists: {out_path.name}")
        return out_path

    prompt = (
        ORIA_DESC +
        "Close-up portrait in warm golden morning kitchen light, "
        "soft bokeh background, cinematic photography, warm earth tones, "
        "natural and authentic, 9:16 vertical portrait"
    )

    print("  Generating Oria portrait...")
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="9:16",
            safety_filter_level="BLOCK_ONLY_HIGH",
            person_generation="ALLOW_ADULT",
        ),
    )

    if response.generated_images:
        out_path.write_bytes(response.generated_images[0].image.image_bytes)
        print(f"  Oria portrait: {out_path.stat().st_size // 1024}KB")
        return out_path
    else:
        print("  Failed to generate portrait")
        return None


def generate_veo_clip(prompt, output_path, duration=5):
    """Generate a Veo clip."""
    if output_path.exists() and output_path.stat().st_size > 10000:
        print(f"  Already exists: {output_path.name}")
        return True

    print(f"  Generating: {prompt[:60]}...")
    try:
        operation = client.models.generate_videos(
            model="veo-2.0-generate-001",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                number_of_videos=1,
                duration_seconds=duration,
                person_generation="allow_adult",
            ),
        )

        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("    ... generating")

        if operation.result and operation.result.generated_videos:
            video = operation.result.generated_videos[0]
            output_path.write_bytes(video.video.video_bytes)
            print(f"  Done: {output_path.stat().st_size // 1024}KB")
            return True
        else:
            print(f"  No video generated")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def crop_720x1280(input_path, output_path):
    """Crop to exact 720x1280."""
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", "6", str(output_path)
    ]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


# Oria clips needed
ORIA_CLIPS = {
    "pancake_reel": [
        ("01_hook",
         ORIA_DESC +
         "Standing in a warm sunlit kitchen, picking up a golden pancake from a plate with a gentle smile. "
         "Morning light streaming through window. Cinematic food photography. Cozy authentic atmosphere. "
         "No children in frame. Just the woman alone."),
        ("06_close",
         ORIA_DESC +
         "Placing a beautiful plate of golden pancakes with fresh berries on a wooden breakfast table. "
         "Warm morning kitchen light. She looks content and natural. "
         "Cinematic warm tones. No children visible."),
    ],
    "garlic_reel": [
        ("01_hook",
         ORIA_DESC +
         "Close-up holding fresh garlic cloves and a jar of golden honey, looking into camera with a knowing smile. "
         "Warm natural kitchen light, wooden countertop. Cinematic close-up portrait. "
         "Earth tones, authentic, warm."),
    ],
    "deodorant_reel": [
        ("01_hook",
         ORIA_DESC +
         "Close-up applying something to her underarm, then looking at camera with a confident expression. "
         "Clean bathroom, natural morning light. Authentic natural beauty. No commercial products visible."),
        ("02_melt",
         "Close-up overhead shot of beeswax and coconut oil melting together in a small pot on a stove. "
         "Golden liquid forming. Warm kitchen light. Clean minimalist surface. Cinematic food photography."),
        ("03_mix",
         "Hands adding white arrowroot powder to a small bowl of melted oils, stirring gently. "
         "Then adding drops from a small essential oil bottle. "
         "Close-up overhead angle. Clean wooden surface. Warm natural light."),
        ("04_pour",
         "Pouring a smooth creamy mixture into a small glass jar or deodorant tube container. "
         "Clean hands, careful pour. Close-up. Clean surface, warm tones. "
         "Natural homemade beauty product."),
        ("05_apply",
         ORIA_DESC +
         "Morning routine, applying natural deodorant stick and smiling confidently. "
         "Soft bathroom light, clean simple background. Natural beauty, earth tones."),
        ("06_close",
         ORIA_DESC +
         "Holding up the finished homemade deodorant jar with natural ingredients (lavender, coconut) "
         "arranged around it on a wooden surface. Proud, warm smile. Golden hour light."),
    ],
}


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    print(f"\n{'='*50}")
    print(f"  Generating Oria Character & Clips")
    print(f"{'='*50}\n")

    # Step 1: Generate Oria portrait
    portrait = generate_oria_portrait()
    time.sleep(15)

    # Step 2: Generate Veo clips
    reels_to_generate = ORIA_CLIPS.keys() if target == "all" else [target]

    for reel_name in reels_to_generate:
        if reel_name not in ORIA_CLIPS:
            continue

        veo_dir = OUT_BASE / reel_name / "video_veo"
        video_dir = OUT_BASE / reel_name / "video"
        veo_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n  --- {reel_name} ---")
        for clip_name, prompt in ORIA_CLIPS[reel_name]:
            veo_path = veo_dir / f"{clip_name}_veo.mp4"
            final_path = video_dir / f"{clip_name}.mp4"

            if generate_veo_clip(prompt, veo_path):
                if crop_720x1280(veo_path, final_path):
                    print(f"  Replaced {clip_name}.mp4")
            time.sleep(5)

    print("\n  Done!")
