"""Generate video clips using Veo via Vertex AI for scenes that need custom footage."""

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

# Use veo-2.0 (cheapest) for stock-like clips
MODEL = "veo-2.0-generate-001"


def generate_clip(prompt, output_path, aspect_ratio="9:16", duration_seconds=5):
    """Generate a video clip with Veo."""
    if output_path.exists() and output_path.stat().st_size > 10000:
        print(f"  ✓ {output_path.name} (exists)")
        return True

    print(f"  Generating: {prompt[:60]}...")

    try:
        operation = client.models.generate_videos(
            model=MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=duration_seconds,
                person_generation="allow_adult",
            ),
        )

        # Poll for completion
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("    ... generating")

        if operation.result and operation.result.generated_videos:
            video = operation.result.generated_videos[0]
            # Save video bytes directly
            output_path.write_bytes(video.video.video_bytes)
            size_kb = output_path.stat().st_size // 1024
            print(f"  ✓ {output_path.name} ({size_kb}KB)")
            return True
        else:
            print(f"  ✗ No video generated")
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def crop_to_720x1280(input_path, output_path):
    """Ensure exact 720x1280 dimensions."""
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", "6",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# ── Pancake reel clips to regenerate ──────────────────────────────────

PANCAKE_VEO = [
    ("01_hook",
     "Close-up of a child's small hand reaching for a golden pancake on a white plate. "
     "Warm morning kitchen light, soft bokeh background. Cozy, intimate, natural. "
     "Shot on a macro lens. No bacon, healthy wholesome breakfast setting."),

    ("02_eggs",
     "Close-up overhead shot of three eggs being cracked into a glass mixing bowl, "
     "one at a time. Yolks dropping into the bowl. Clean wooden countertop. "
     "Warm natural kitchen light. Cinematic food photography style."),

    ("03_mix",
     "Hands adding almond flour to a glass bowl, then mashing half a banana into the batter. "
     "Close-up overhead angle. A pinch of baking soda being added. "
     "Clean minimalist kitchen. Warm morning light. Natural cooking."),

    ("04_cook",
     "Close-up of golden pancake batter being poured onto a non-stick pan, "
     "then the pancake cooking with small bubbles forming. Someone flipping it with a spatula. "
     "The pancake cracks slightly — a natural healthy look. Kitchen morning light."),
]

# Add family scene - clip 6
PANCAKE_VEO.append(
    ("06_close",
     "A parent and young child sitting at a breakfast table, sharing a warm morning meal. "
     "Golden morning light through a window. Plates with healthy pancakes and fresh berries. "
     "Genuine warmth, candid moment. Shot at eye level, soft focus background.")
)


if __name__ == "__main__":
    import sys
    reel = sys.argv[1] if len(sys.argv) > 1 else "pancake"

    if reel == "pancake":
        video_dir = OUT_BASE / "pancake_reel" / "video"
        veo_dir = OUT_BASE / "pancake_reel" / "video_veo"
        veo_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*50}")
        print(f"  Generating Veo clips for pancake_reel")
        print(f"{'='*50}\n")

        for clip_name, prompt in PANCAKE_VEO:
            veo_path = veo_dir / f"{clip_name}_veo.mp4"
            final_path = video_dir / f"{clip_name}.mp4"

            if generate_clip(prompt, veo_path):
                # Crop to exact dimensions and replace stock clip
                if crop_to_720x1280(veo_path, final_path):
                    print(f"  ✓ Replaced {clip_name}.mp4 with Veo version")
