"""Generate TTS voice-overs for all 4 Oria reels using Google Cloud TTS."""

from google.cloud import texttospeech
from pathlib import Path
import os

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS",
    str(Path(__file__).parent.parent / "credentials.json"))

client = texttospeech.TextToSpeechClient()

# Use Studio-O voice (warm, feminine, natural)
VOICE = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O",
)
AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=0.92,  # Slightly slower for gravitas
    pitch=-1.0,  # Slightly lower for warmth
)

# ── All voice-over clips ──────────────────────────────────────────────

REELS = {
    "pancake_reel": [
        ("01_hook", "Your kid doesn't know this is healthy. And that's the point."),
        ("02_eggs", "Three eggs. That's your protein. That's your foundation. Not flour — eggs."),
        ("03_mix", "Almond flour. Half a crushed banana for natural sweetness. A pinch of baking soda. That's it."),
        ("04_cook", "It will break easier than regular pancakes. Good. That means there's no gluten holding it together with inflammation."),
        ("05_plate", "Your gut processes this in hours, not days. No bloat. No crash. Just clean fuel for a small body that's still building itself."),
        ("06_close", "Feed them what their body recognizes. Not what a factory designed."),
    ],
    "garlic_reel": [
        ("01_hook", "Two ingredients. No lab. No patent. Just ancient medicine."),
        ("02_crush", "Crush fresh garlic. Not chop. Crushing unlocks allicin — nature's antibiotic."),
        ("03_jar", "Fill a jar halfway with cloves. Pour raw honey until they disappear. Raw — not pasteurized. The wild yeast in raw honey is what makes this alive."),
        ("04_flip", "Flip it once a day. In one month, the honey thins, darkens, and becomes something no pharmacy can sell you."),
        ("05_spoon", "Allicin meets raw enzymes. Antimicrobial. Immune-boosting. Bioavailable. One spoonful a day."),
        ("06_close", "Nature already made the medicine. You just have to be patient enough to let it work."),
    ],
    "deodorant_reel": [
        ("01_hook", "Aluminum. Parabens. Phthalates. Synthetic fragrance. You put this on your skin every single day."),
        ("02_melt", "Or you could make your own. Beeswax. Coconut oil. Shea butter. Melt them together."),
        ("03_mix", "Add arrowroot powder to absorb moisture. A pinch of baking soda. A few drops of tea tree and lavender oil — nature's antibacterials."),
        ("04_pour", "Pour it. Let it set. Two hours. Done. Six months of deodorant for less than one stick costs."),
        ("05_apply", "It won't stop you from sweating. Good. Your body sweats to cool itself and flush toxins. Aluminum stops that. This doesn't."),
        ("06_close", "Your skin absorbs what you put on it. Choose what nature made, not what a factory engineered."),
    ],
    "addiction_reel": [
        ("01_hook", "Nobody wakes up and chooses addiction. They choose relief. And the addiction is what relief looked like at the time."),
        ("02_thing", "The phone. The sugar. The bottle. The shopping cart. The scroll at 2 AM. It was never about the thing. It was about the feeling underneath it."),
        ("03_pain", "The question isn't 'why the addiction.' The question is 'why the pain.'"),
        ("04_feel", "Willpower doesn't fix a wound. You can't think your way out of something you never let yourself feel."),
        ("05_connect", "The opposite of addiction isn't sobriety. It's connection. To yourself. To someone. To something real."),
        ("06_close", "You are not your coping mechanism. You are the person underneath it. And that person deserves gentleness."),
    ],
}

def generate():
    for reel_name, clips in REELS.items():
        out_dir = Path(f"/Users/kapi7/Naturithm/output/{reel_name}/audio")
        out_dir.mkdir(parents=True, exist_ok=True)

        for filename, text in clips:
            out_path = out_dir / f"{filename}.wav"
            if out_path.exists():
                print(f"  ✓ {out_path.name} (exists)")
                continue

            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = client.synthesize_speech(
                input=synthesis_input, voice=VOICE, audio_config=AUDIO_CONFIG
            )

            with open(out_path, "wb") as f:
                f.write(response.audio_content)
            print(f"  ✓ {out_path.name}")

        print(f"✓ {reel_name}: {len(clips)} clips generated\n")


if __name__ == "__main__":
    generate()
