"""Fetch better stock video from Pexels for reworked reels.

Replaces generic footage with more specific, emotional, hooking clips.
"""

import os
import subprocess
import requests
from pathlib import Path

API_KEY = "JxGx5g6vMaqBxMpyrfqtYxIvGnMmsUiRYDdDs7JAtD5uDwRvFiOXOb8h"
OUT_BASE = Path("/Users/kapi7/Naturithm/output")


def search_and_download(query, output_path, orientation="portrait", max_duration=8):
    """Search Pexels and download best matching video."""
    if output_path.exists() and output_path.stat().st_size > 50000:
        print(f"    Already exists: {output_path.name}")
        return True

    headers = {"Authorization": API_KEY}
    params = {"query": query, "orientation": orientation, "per_page": 5, "size": "medium"}
    resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)

    if resp.status_code != 200:
        print(f"    API error: {resp.status_code}")
        return False

    videos = resp.json().get("videos", [])
    if not videos:
        # Fallback without orientation
        params.pop("orientation")
        resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        videos = resp.json().get("videos", [])

    if not videos:
        print(f"    No videos found for: {query}")
        return False

    # Get best quality HD file
    video = videos[0]
    video_files = sorted(video.get("video_files", []),
                         key=lambda f: f.get("height", 0), reverse=True)

    # Prefer HD portrait
    for vf in video_files:
        if vf.get("height", 0) >= 720:
            url = vf["link"]
            break
    else:
        url = video_files[0]["link"] if video_files else None

    if not url:
        return False

    # Download
    raw_path = output_path.with_suffix(".raw.mp4")
    print(f"    Downloading: {query[:40]}...")
    r = requests.get(url, stream=True)
    with open(raw_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    # Crop to 720x1280
    cmd = [
        "ffmpeg", "-y", "-i", str(raw_path),
        "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", str(max_duration),
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    raw_path.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"    Done: {output_path.name} ({output_path.stat().st_size // 1024}KB)")
        return True
    else:
        print(f"    FFmpeg error: {result.stderr[:100]}")
        return False


# Better footage for addiction reel — more personal, emotional
ADDICTION_FOOTAGE = [
    ("01_hook", "person staring out window rain alone contemplative close up"),
    ("02_thing", "person holding phone in dark room late night scrolling lonely"),
    ("03_pain", "person sitting alone park bench emotional thinking sunset"),
    ("04_feel", "tears close up face emotional crying vulnerable"),
    ("05_connect", "two people hugging warmly emotional reunion"),
    ("06_close", "person walking alone sunrise hope new beginning"),
]

# Better footage for loops 3 & 5 — more hooking/cinematic
LOOP_FOOTAGE = {
    "naturithm_loop3": "eye close up macro dramatic reflection deep",
    "naturithm_loop5": "storm clouds time lapse dramatic transforming to calm",
}

# Running carousel needs stock photos (not video)
# Will handle separately with Imagen


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    if target in ("all", "addiction"):
        print(f"\n{'='*50}")
        print(f"  Fetching: Addiction Reel (emotional footage)")
        print(f"{'='*50}\n")
        video_dir = OUT_BASE / "addiction_reel" / "video"
        video_dir.mkdir(parents=True, exist_ok=True)
        for clip_name, query in ADDICTION_FOOTAGE:
            path = video_dir / f"{clip_name}.mp4"
            # Delete old generic footage
            if path.exists():
                path.unlink()
            search_and_download(query, path)

    if target in ("all", "loops"):
        print(f"\n{'='*50}")
        print(f"  Fetching: Loop Backgrounds (more hooking)")
        print(f"{'='*50}\n")
        for loop_name, query in LOOP_FOOTAGE.items():
            bg_dir = OUT_BASE / loop_name
            bg_dir.mkdir(parents=True, exist_ok=True)
            path = bg_dir / "background.mp4"
            if path.exists():
                path.unlink()
            search_and_download(query, path, max_duration=7)

    print("\n  Done!")
