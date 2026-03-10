"""Generate illustrated story frames using Gemini Imagen for Naturithm story time videos.

Creates 6 illustrated frames per story, then assembles them with Ken Burns
effect (zoom/pan) + narration TTS + music into a 45-60s animated reel.

Using Imagen 3 for cost efficiency (~$0.03 per image vs $0.50+ for video gen).
"""

import os
import time
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
MODEL = "imagen-3.0-generate-002"

STYLE_PREFIX = (
    "Warm watercolor illustration style, soft hand-drawn feel, "
    "gentle storybook quality, earth tones and muted pastels, "
    "vertical 9:16 aspect ratio, no text on image, "
)


def generate_image(prompt, output_path):
    """Generate an illustration with Imagen."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        print(f"    ✓ {output_path.name} (exists)")
        return True

    full_prompt = STYLE_PREFIX + prompt

    try:
        response = client.models.generate_images(
            model=MODEL,
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16",
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation="ALLOW_ADULT",
            ),
        )

        if response.generated_images:
            img_bytes = response.generated_images[0].image.image_bytes
            output_path.write_bytes(img_bytes)
            size_kb = output_path.stat().st_size // 1024
            print(f"    ✓ {output_path.name} ({size_kb}KB)")
            return True
        else:
            print(f"    ✗ No image generated")
            return False

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False


# ── DUCK STORY (Eckhart Tolle) — 6 frames ────────────────────────────

DUCK_FRAMES = [
    ("01_pond",
     "Two ducks floating peacefully on a serene pond, lily pads, gentle ripples, "
     "morning light, calm and beautiful watercolor illustration"),

    ("02_fight",
     "Two ducks fighting on a pond, splashing water, flapping wings, feathers flying, "
     "chaotic energy, watercolor illustration with dynamic movement"),

    ("03_shake",
     "Two ducks separated after a fight, each duck flapping its wings vigorously, "
     "visible energy releasing from their bodies, water splashing, watercolor illustration"),

    ("04_peace",
     "Two ducks floating peacefully again on calm pond, serene, as if nothing happened, "
     "beautiful golden light on water, watercolor illustration"),

    ("05_human",
     "Split scene: on left, a duck floating peacefully on water. On right, a person "
     "sitting at a desk with worried thought bubbles above their head, replaying conversations, "
     "dark clouds of overthinking, watercolor illustration"),

    ("06_message",
     "A single duck floating on a beautiful peaceful pond at golden hour, "
     "everything calm and simple, wide open space, freedom, "
     "warm watercolor illustration, storybook ending"),
]

# ── THORN STORY (Michael Singer) — 6 frames ──────────────────────────

THORN_FRAMES = [
    ("01_thorn",
     "A gentle dog sitting in a beautiful field, looking at a thorn stuck in its paw, "
     "visible pain expression, red glow around the thorn, "
     "warm watercolor illustration, empathetic"),

    ("02_snap",
     "A hurt dog by a fence, growling at a child who is reaching out to pet it, "
     "the child looks scared and confused, the dog is protecting its paw, "
     "watercolor illustration showing both pain and innocence"),

    ("03_push",
     "Montage of different people approaching a fence where a hurt dog lies, "
     "a woman with food, a man with a ball, the dog barks at all of them, "
     "watercolor illustration showing isolation"),

    ("04_shrink",
     "A dog in a tiny corner of a vast beautiful open field, surrounded by padding "
     "and walls it built, the enormous beautiful field stretches behind it unused, "
     "watercolor illustration contrasting smallness and vastness"),

    ("05_remove",
     "A gentle dog carefully pulling a thorn from its paw with its teeth, "
     "a brief wince of pain but then visible relief on its face, "
     "warm light starting to glow, watercolor illustration of courage"),

    ("06_free",
     "A joyful dog running freely through a vast open field, playing, the sun shining, "
     "people approaching and the dog greeting them warmly, "
     "beautiful watercolor illustration of freedom and joy"),
]


def generate_story(name, frames):
    """Generate all frames for a story."""
    out_dir = OUT_BASE / name / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  Generating: {name}")
    print(f"{'='*50}")

    for frame_name, prompt in frames:
        out_path = out_dir / f"{frame_name}.png"
        print(f"\n  [{frame_name}]")
        success = generate_image(prompt, out_path)
        if not success:
            print("    Waiting 60s for rate limit...")
            time.sleep(60)
            generate_image(prompt, out_path)
        time.sleep(15)  # Rate limit spacing


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    stories = {
        "naturithm_duck": DUCK_FRAMES,
        "naturithm_thorn": THORN_FRAMES,
    }

    if target == "all":
        for name, frames in stories.items():
            generate_story(name, frames)
    elif target in stories:
        generate_story(target, stories[target])
    else:
        print(f"Options: {', '.join(stories.keys())} or 'all'")
