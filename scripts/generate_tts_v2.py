"""Generate TTS voice-overs V2 — Oria's voice (female) for story narration.

Uses Google Cloud TTS Studio-Q (warm female voice) for duck + fence stories.
"""

import os
from pathlib import Path
from google.cloud import texttospeech

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/kapi7/Naturithm/credentials.json'

tts_client = texttospeech.TextToSpeechClient()
OUT_BASE = Path("/Users/kapi7/Naturithm/output")

# Oria's voice — warm, intimate female narrator
VOICE_ORIA = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-Q",
)

AUDIO_CONFIG = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=0.88,  # Slightly slower for storytelling
    pitch=-0.5,
)


def generate_tts(text, output_path, voice=None):
    """Generate TTS audio clip."""
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"    Already exists: {output_path.name}")
        return True

    try:
        response = tts_client.synthesize_speech(
            input=texttospeech.SynthesisInput(text=text),
            voice=voice or VOICE_ORIA,
            audio_config=AUDIO_CONFIG,
        )
        output_path.write_bytes(response.audio_content)
        print(f"    Done: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


# Duck story narration (shorter, punchier — flows with subtitle timing)
DUCK_NARRATION = [
    ("01_pond", "Two ducks. Floating on a pond. Quiet. Still."),
    ("02_fight", "Then — chaos. They clash. Feathers fly. Water splashes everywhere."),
    ("03_shake", "And then... it's over. Each duck flaps its wings hard. Shaking off the energy. Letting it go."),
    ("04_peace", "Peace. Like nothing happened. The fight is forgotten."),
    ("05_human", "Now imagine that duck had a human mind. It would replay that fight for days. I can't believe he did that. He thinks he owns this pond."),
    ("06_message", "The duck knew something we forgot. The fight is over. Flap your wings. Let it go."),
]

# Fence/Collar story narration (invisible fence with shock collar)
FENCE_NARRATION = [
    ("01_fence", "There's a dog. Wearing a collar. Around the yard, an invisible fence. Every time it gets close — the collar buzzes."),
    ("02_approach", "So the dog learns. Don't go near the edge. Stay in the middle. Stay safe."),
    ("03_retreat", "Over time, the dog forgets there's even a world beyond the yard. Its whole life shrinks to the size of what doesn't hurt."),
    ("04_decide", "One day, the dog sees something on the other side. And something shifts. It walks toward the edge. The collar buzzes. It keeps walking."),
    ("05_through", "The buzz gets louder. The pain gets sharper. Every part of the dog says stop. But it takes one more step. And then — silence."),
    ("06_free", "The field was always there. The collar couldn't stop it. Only the dog's belief in the collar could. What invisible fence are you still obeying?"),
]


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    stories = {
        "duck": ("naturithm_duck", DUCK_NARRATION),
        "fence": ("naturithm_fence", FENCE_NARRATION),
    }

    to_generate = stories.keys() if target == "all" else [target]

    for story_key in to_generate:
        if story_key not in stories:
            continue
        name, narration = stories[story_key]
        audio_dir = OUT_BASE / name / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*50}")
        print(f"  Generating Oria narration: {name}")
        print(f"{'='*50}")

        for clip_name, text in narration:
            out_path = audio_dir / f"{clip_name}.wav"
            print(f"\n  [{clip_name}]")
            generate_tts(text, out_path)

    print("\n  Done!")
