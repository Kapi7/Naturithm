"""Regenerate garlic crushing clip — crush, don't chop."""

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

ORIA_BEAUTY = (
    "A stunningly beautiful Mediterranean woman in her late 20s with radiant olive skin, "
    "long flowing dark hair, warm brown eyes. She has a luminous natural beauty — "
    "full lips, defined cheekbones, a serene expression."
)

CRUSH_PROMPT = (
    ORIA_BEAUTY + " "
    "In a warm rustic kitchen with natural light, she places a garlic clove on a wooden "
    "cutting board and CRUSHES it firmly with the flat side of a large chef's knife, "
    "pressing down with the heel of her palm. The garlic splits and flattens under the blade. "
    "Close-up showing the crushing technique clearly — NOT chopping, NOT slicing. "
    "She uses a single decisive press to smash the clove flat. "
    "Warm golden tones, cinematic shallow depth of field, soft natural lighting."
)


def generate_veo(prompt, output_path, duration=5):
    if output_path.exists() and output_path.stat().st_size > 10000:
        print(f"  Exists: {output_path.name}")
        return True
    print(f"  Generating: {prompt[:80]}...")
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
            print(f"  Done: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
            return True
        print("  No video generated")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def crop_720x1280(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", "6", str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Cropped to 720x1280: {output_path.name}")
    else:
        print(f"  Crop error: {result.stderr[-200:]}")
    return result.returncode == 0


if __name__ == "__main__":
    veo_dir = OUT_BASE / "garlic_reel" / "video_veo"
    video_dir = OUT_BASE / "garlic_reel" / "video"
    veo_dir.mkdir(parents=True, exist_ok=True)

    veo_path = veo_dir / "02_crush_fix.mp4"
    final_path = video_dir / "02_crush.mp4"

    # Remove existing veo file to force regeneration
    if veo_path.exists():
        veo_path.unlink()
        print("  Removed old veo file to force regeneration")

    print(f"\n{'='*50}")
    print(f"  Regenerating Garlic Crush Clip")
    print(f"{'='*50}\n")
    print(f"  Prompt: {CRUSH_PROMPT[:100]}...\n")

    if generate_veo(CRUSH_PROMPT, veo_path):
        crop_720x1280(veo_path, final_path)
        print(f"\n  SUCCESS: {final_path}")
    else:
        print("\n  FAILED to generate clip")

    print("\n  Done!")
