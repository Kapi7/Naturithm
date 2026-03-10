"""Generate illustrated frames for the Dog & Fence story (replaces thorn story).

Story: A dog behind a fence, approaches it, accepts the pain, gets through to freedom.
Uses Imagen 3.0 watercolor illustrations.
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

FENCE_FRAMES = [
    ("01_fence",
     "A gentle dog sitting behind a wooden fence, looking through the gaps "
     "at a vast beautiful open field with wildflowers and golden sunshine beyond. "
     "The dog looks longing but afraid. Warm watercolor illustration, empathetic mood."),

    ("02_approach",
     "A dog carefully walking toward a wooden fence, hesitant, ears back, "
     "one paw reaching forward. The fence glows slightly with a warm red tint "
     "suggesting pain or fear. Beautiful field visible beyond. Watercolor illustration."),

    ("03_retreat",
     "A dog retreating from a fence, curled up in a small corner of a yard, "
     "while the vast beautiful field stretches beyond the fence. The dog looks small "
     "and protected but trapped. Watercolor illustration showing contrast of safety vs freedom."),

    ("04_decide",
     "A dog standing tall, facing the fence with determination in its eyes. "
     "Morning light breaking through the fence slats. The dog looks brave, "
     "ready to face the challenge. Warm golden watercolor illustration of courage."),

    ("05_through",
     "A dog pushing through a gap in a wooden fence, squeezing through with effort, "
     "a wince of pain but light flooding in from the other side. "
     "Half in shadow, half in warm golden light. Watercolor illustration of breakthrough."),

    ("06_free",
     "A joyful dog running freely through a vast open field of wildflowers, "
     "sun shining, tail wagging, pure joy and freedom. The broken fence small "
     "in the background. Beautiful watercolor illustration of liberation and joy."),
]


def generate_image(prompt, output_path):
    """Generate an illustration with Imagen."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        print(f"    Already exists: {output_path.name}")
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
            output_path.write_bytes(response.generated_images[0].image.image_bytes)
            print(f"    Done: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
            return True
        else:
            print(f"    No image generated")
            return False
    except Exception as e:
        print(f"    Error: {e}")
        return False


if __name__ == "__main__":
    out_dir = OUT_BASE / "naturithm_fence" / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  Generating: Dog & Fence Story Frames")
    print(f"{'='*50}")

    for frame_name, prompt in FENCE_FRAMES:
        out_path = out_dir / f"{frame_name}.png"
        print(f"\n  [{frame_name}]")
        success = generate_image(prompt, out_path)
        if not success:
            print("    Waiting 60s for rate limit...")
            time.sleep(60)
            generate_image(prompt, out_path)
        time.sleep(15)

    print("\n  Done!")
