"""Fix deodorant Oria clips (more beautiful, correct application) + addiction footage."""

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


def generate_veo(prompt, output_path, duration=5):
    if output_path.exists() and output_path.stat().st_size > 10000:
        print(f"  Exists: {output_path.name}")
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


# Deodorant clips that need fixing
DEODORANT_FIXES = [
    ("01_hook",
     ORIA_BEAUTY +
     "Close-up portrait in a clean minimalist bathroom, soft natural morning light. "
     "She looks into camera knowingly, then glances down at a commercial deodorant spray. "
     "Slightly concerned expression. Cinematic close-up, shallow depth of field."),

    ("05_apply",
     ORIA_BEAUTY +
     "Morning routine in a clean bathroom. She lifts her arm slightly and applies "
     "a natural stick deodorant to her UNDERARM (armpit area). Confident natural gesture. "
     "Soft morning light. NOT on face. Deodorant goes under the arm. "
     "Natural beauty, authentic, warm tones."),

    ("06_close",
     ORIA_BEAUTY +
     "Standing in a bright kitchen or bathroom, holding up a small glass jar of homemade "
     "natural deodorant. Fresh lavender sprigs and coconut on the counter. "
     "Warm proud smile, golden hour light through window. "
     "She looks radiant and confident. Cinematic warm tones."),
]

# Addiction clips - more cinematic, emotional
ADDICTION_FIXES = [
    ("01_hook",
     "Extreme close-up of a person's eyes in dim light, reflecting a phone screen glow. "
     "The eyes look exhausted, haunted, searching. Cinematic, raw, intimate. "
     "Shallow depth of field, muted colors, grain texture."),

    ("02_thing",
     "A person's hand reaching for their phone on a nightstand in the dark, "
     "then pulling back. The hand trembles slightly. Close-up. "
     "Blue phone light on skin. Raw, intimate, cinematic."),

    ("03_pain",
     "A person sitting on the floor against a wall, knees pulled up, head down. "
     "Single window light casting long shadows. Vulnerable, isolated. "
     "Wide shot gradually pushing in. Cinematic, emotional, muted tones."),

    ("04_feel",
     "Close-up of tears forming in someone's eyes, then one tear falling. "
     "Beautiful in its rawness. Soft natural light on face. "
     "Intimate, cinematic, no shame — just feeling. Warm skin tones."),

    ("05_connect",
     "Two hands reaching toward each other and clasping together tightly. "
     "Warm golden light. Close-up of the hands, genuine grip. "
     "Then pulling back to show two people sitting together in nature. "
     "Hope, warmth, connection. Cinematic."),

    ("06_close",
     "A person walking alone on an empty road at golden hour sunrise. "
     "Shot from behind. Warm light streaming forward, long shadow. "
     "The person walks with quiet determination. Beautiful, hopeful. "
     "Cinematic wide shot, warm earth tones."),
]


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ("all", "deodorant"):
        print(f"\n{'='*50}")
        print(f"  Fixing Deodorant Oria Clips")
        print(f"{'='*50}\n")
        veo_dir = OUT_BASE / "deodorant_reel" / "video_veo"
        video_dir = OUT_BASE / "deodorant_reel" / "video"

        for clip_name, prompt in DEODORANT_FIXES:
            veo_path = veo_dir / f"{clip_name}_fix.mp4"
            final_path = video_dir / f"{clip_name}.mp4"
            if generate_veo(prompt, veo_path):
                crop_720x1280(veo_path, final_path)
                print(f"  Replaced {clip_name}.mp4")
            time.sleep(5)

    if target in ("all", "addiction"):
        print(f"\n{'='*50}")
        print(f"  Fixing Addiction Reel Footage")
        print(f"{'='*50}\n")
        veo_dir = OUT_BASE / "addiction_reel" / "video_veo"
        video_dir = OUT_BASE / "addiction_reel" / "video"
        veo_dir.mkdir(parents=True, exist_ok=True)

        for clip_name, prompt in ADDICTION_FIXES:
            veo_path = veo_dir / f"{clip_name}_veo.mp4"
            final_path = video_dir / f"{clip_name}.mp4"
            if generate_veo(prompt, veo_path):
                crop_720x1280(veo_path, final_path)
                print(f"  Replaced {clip_name}.mp4")
            time.sleep(5)

    print("\n  Done!")
