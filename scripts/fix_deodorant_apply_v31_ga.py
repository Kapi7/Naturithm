"""Regenerate deodorant apply clip using Veo 3.1 GA for accurate body movement."""

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

ORIA = (
    "A stunningly beautiful young woman with radiant olive skin, long flowing dark hair, "
    "full lips, high cheekbones, natural glow, captivating warm brown eyes. "
    "Mediterranean goddess beauty. No heavy makeup, luminous natural skin. "
    "Wearing a simple earth-tone tank top. "
)

PROMPT = (
    ORIA +
    "Morning bathroom routine scene. Bright clean bathroom, soft golden morning light from window. "
    "She raises her LEFT ARM above her head to expose her armpit, "
    "and uses her RIGHT HAND to glide a natural cream deodorant stick under her raised arm. "
    "The deodorant goes on the ARMPIT area — clearly visible underarm application. "
    "Confident, casual morning gesture. Medium shot from front-side angle. "
    "Warm cinematic tones, shallow depth of field on background. "
    "Only one person in frame. Natural, authentic, beautiful."
)


def generate_veo31(prompt, output_path, duration=5):
    print(f"  Generating with veo-3.1-generate-001...")
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-001",
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
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


if __name__ == "__main__":
    veo_dir = OUT_BASE / "deodorant_reel" / "video_veo"
    video_dir = OUT_BASE / "deodorant_reel" / "video"
    veo_dir.mkdir(parents=True, exist_ok=True)

    veo_path = veo_dir / "05_apply_v31_ga.mp4"
    final_path = video_dir / "05_apply.mp4"

    if generate_veo31(PROMPT, veo_path):
        crop_720x1280(veo_path, final_path)
        print(f"  Replaced 05_apply.mp4")
        print("\n  Reassembling deodorant reel...")
        subprocess.run(
            ["python3", "scripts/assemble_reel_v2.py", "deodorant_reel"],
            cwd="/Users/kapi7/Naturithm"
        )
    else:
        print("  Failed — try checking Veo 3.1 quota/access")
