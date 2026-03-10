"""Regenerate deodorant apply clip using Veo 3.1 for better body movement accuracy."""

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
    "A stunningly beautiful young woman with radiant olive skin, long flowing dark hair, "
    "full lips, high cheekbones, natural glow, captivating warm brown eyes. "
    "She looks like a Mediterranean goddess. Effortlessly gorgeous, no heavy makeup, "
    "luminous natural beauty. Earth-tone minimal clothing. "
)

PROMPT = (
    ORIA_BEAUTY +
    "She is in a bright clean bathroom with soft morning light from a window. "
    "She raises her LEFT ARM up to expose her underarm/armpit area, "
    "and with her RIGHT HAND she smoothly applies a natural cream deodorant stick "
    "to her left armpit. Simple confident morning routine gesture. "
    "Camera angle is a medium close-up from the front/side showing the application clearly. "
    "Only her own two hands and body visible — no other people. "
    "Warm natural tones, soft focus background, authentic feel. "
    "NOT applying to face or neck — specifically to the armpit/underarm area."
)


def generate_veo31(prompt, output_path, duration=5):
    """Generate video using Veo 3.1 for complex body movements."""
    print(f"  Generating with Veo 3.1: {prompt[:60]}...")

    # Try veo-3.0-generate-preview first, fall back to other model IDs
    models_to_try = [
        "veo-3.0-generate-preview",
        "veo-3.1-generate-preview",
        "veo-2.0-generate-001",
    ]

    for model_id in models_to_try:
        print(f"  Trying model: {model_id}")
        try:
            operation = client.models.generate_videos(
                model=model_id,
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
                print(f"  Done with {model_id}: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
                return True
            print(f"  No video generated with {model_id}")
        except Exception as e:
            print(f"  {model_id} failed: {e}")
            continue

    return False


def crop_720x1280(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", "6", str(output_path)
    ]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


if __name__ == "__main__":
    veo_dir = OUT_BASE / "deodorant_reel" / "video_veo"
    video_dir = OUT_BASE / "deodorant_reel" / "video"
    veo_dir.mkdir(parents=True, exist_ok=True)

    veo_path = veo_dir / "05_apply_v31.mp4"
    final_path = video_dir / "05_apply.mp4"

    if generate_veo31(PROMPT, veo_path):
        crop_720x1280(veo_path, final_path)
        print(f"  Replaced 05_apply.mp4")
        # Reassemble reel
        print("\n  Reassembling deodorant reel...")
        subprocess.run(
            ["python3", "scripts/assemble_reel_v2.py", "deodorant_reel"],
            cwd="/Users/kapi7/Naturithm"
        )
    else:
        print("  Failed to generate clip")
