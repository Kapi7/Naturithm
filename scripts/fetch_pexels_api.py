"""Fetch stock videos from Pexels API for all reels."""

import requests
import subprocess
from pathlib import Path
import sys
import time

API_KEY = "JxGx5g6vMaqBxMpyrfqtYxIvGnMmsUiRYDdDs7JAtD5uDwRvFiOXOb8h"
HEADERS = {"Authorization": API_KEY}
BASE = "https://api.pexels.com/videos/search"
OUT_BASE = Path("/Users/kapi7/Naturithm/output")


def search_videos(query, orientation="portrait", per_page=3):
    """Search Pexels API for videos."""
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation,
    }
    resp = requests.get(BASE, headers=HEADERS, params=params)
    if resp.status_code == 200:
        return resp.json().get("videos", [])
    print(f"  API error {resp.status_code}: {resp.text[:200]}")
    return []


def get_best_file(video, prefer_vertical=True):
    """Get best video file URL, preferring HD vertical."""
    files = video.get("video_files", [])
    # Sort by quality: prefer 720-1080 height for vertical, or 720-1080 width
    best = None
    best_score = -1

    for f in files:
        h = f.get("height", 0)
        w = f.get("width", 0)
        quality = f.get("quality", "")

        # For vertical: prefer files where h > w (already vertical)
        # For horizontal: we'll crop, prefer 1080p
        if prefer_vertical and h > w:
            score = 1000  # Bonus for already vertical
        else:
            score = 0

        # Prefer HD
        if quality == "hd":
            score += 500
        elif quality == "sd":
            score += 100

        # Prefer close to 1080 height
        score += max(0, 500 - abs(h - 1080))

        if score > best_score:
            best_score = score
            best = f

    return best["link"] if best else (files[0]["link"] if files else None)


def download(url, path):
    """Download file."""
    if path.exists() and path.stat().st_size > 10000:
        print(f"    ✓ exists ({path.stat().st_size // 1024}KB)")
        return True
    resp = requests.get(url, stream=True, timeout=60)
    if resp.status_code == 200:
        with open(path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        print(f"    ✓ downloaded ({path.stat().st_size // 1024}KB)")
        return True
    print(f"    ✗ HTTP {resp.status_code}")
    return False


def crop_vertical(input_path, output_path, max_duration=6):
    """Crop to 720x1280 vertical."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        return True

    # Get dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(input_path)],
        capture_output=True, text=True
    )
    if probe.returncode != 0:
        return False

    w, h = map(int, probe.stdout.strip().split(","))

    # Build filter chain
    if w > h:
        # Horizontal → crop center to vertical
        vf = f"scale=-2:1280,crop=720:1280"
    elif w == h:
        # Square → scale and pad
        vf = f"scale=720:-2,crop=720:1280"
    else:
        # Already vertical → scale to fit
        vf = f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280"

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an", "-t", str(max_duration),
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# ── Clip definitions per reel ─────────────────────────────────────────
# (clip_name, search_query, preferred_orientation)

PANCAKE_CLIPS = [
    ("01_hook", "child reaching pancake breakfast", "portrait"),
    ("02_eggs", "cracking eggs bowl cooking", "portrait"),
    ("03_mix", "mixing batter bowl cooking", "portrait"),
    ("04_cook", "pancake cooking pan flipping", "portrait"),
    ("05_plate", "stack pancakes plate berries breakfast", "portrait"),
    ("06_close", "family breakfast table morning", "portrait"),
]

GARLIC_CLIPS = [
    ("01_hook", "garlic cloves cutting board", "portrait"),
    ("02_crush", "crushing garlic knife", "portrait"),
    ("03_jar", "honey pouring jar", "portrait"),
    ("04_flip", "honey jar golden", "portrait"),
    ("05_spoon", "honey spoon close up", "portrait"),
    ("06_close", "herbs wooden surface golden hour nature", "portrait"),
]

DEODORANT_CLIPS = [
    ("01_hook", "skincare product label ingredients", "portrait"),
    ("02_melt", "melting coconut oil double boiler", "portrait"),
    ("03_mix", "mixing powder essential oil natural", "portrait"),
    ("04_pour", "pouring liquid small jar container", "portrait"),
    ("05_apply", "morning routine natural beauty", "portrait"),
    ("06_close", "natural ingredients wooden surface lavender", "portrait"),
]

ADDICTION_CLIPS = [
    ("01_hook", "person sitting alone window rain contemplative", "portrait"),
    ("02_thing", "scrolling phone dark night", "portrait"),
    ("03_pain", "person walking alone empty street", "portrait"),
    ("04_feel", "sunrise person walking nature", "portrait"),
    ("05_connect", "friends walking together laughing", "portrait"),
    ("06_close", "person meditating outdoors peaceful", "portrait"),
]

# Loop videos for naturithm
LOOP_CLIPS = [
    ("naturithm_loop1", "mountain landscape sunrise cinematic", "portrait"),
    ("naturithm_loop3", "mirror reflection water person", "portrait"),
    ("naturithm_loop5", "person meditating nature morning", "portrait"),
]

ALL = {
    "pancake_reel": PANCAKE_CLIPS,
    "garlic_reel": GARLIC_CLIPS,
    "deodorant_reel": DEODORANT_CLIPS,
    "addiction_reel": ADDICTION_CLIPS,
}


def fetch_reel_clips(reel_name, clips):
    """Fetch all clips for a reel."""
    video_dir = OUT_BASE / reel_name / "video"
    raw_dir = OUT_BASE / reel_name / "video_raw"
    video_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  {reel_name}")
    print(f"{'='*50}")

    for clip_name, query, orientation in clips:
        crop_path = video_dir / f"{clip_name}.mp4"
        if crop_path.exists() and crop_path.stat().st_size > 5000:
            print(f"\n  [{clip_name}] ✓ already done")
            continue

        raw_path = raw_dir / f"{clip_name}_raw.mp4"

        print(f"\n  [{clip_name}] Searching: {query}")

        # Search with preferred orientation, fallback to any
        videos = search_videos(query, orientation=orientation)
        if not videos:
            videos = search_videos(query, orientation="landscape")
        if not videos:
            print(f"    ✗ No results")
            continue

        # Try first result
        url = get_best_file(videos[0])
        if not url:
            print(f"    ✗ No download URL")
            continue

        print(f"    URL: {url[:80]}...")
        if download(url, raw_path):
            if crop_vertical(raw_path, crop_path):
                print(f"    ✓ Cropped to 720x1280")
            else:
                print(f"    ✗ Crop failed")

        time.sleep(0.5)  # Rate limit


def fetch_loop_backgrounds():
    """Fetch background clips for loop videos."""
    print(f"\n{'='*50}")
    print(f"  Loop Video Backgrounds")
    print(f"{'='*50}")

    for name, query, orientation in LOOP_CLIPS:
        video_dir = OUT_BASE / name
        video_dir.mkdir(parents=True, exist_ok=True)
        bg_path = video_dir / "background.mp4"

        if bg_path.exists() and bg_path.stat().st_size > 5000:
            print(f"\n  [{name}] ✓ already done")
            continue

        raw_path = video_dir / "bg_raw.mp4"
        print(f"\n  [{name}] Searching: {query}")

        videos = search_videos(query, orientation=orientation, per_page=5)
        if not videos:
            videos = search_videos(query, orientation="landscape", per_page=5)
        if not videos:
            continue

        url = get_best_file(videos[0])
        if url and download(url, raw_path):
            crop_vertical(raw_path, bg_path, max_duration=6)

        time.sleep(0.5)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "pancake_reel"

    if target == "all":
        for name, clips in ALL.items():
            fetch_reel_clips(name, clips)
        fetch_loop_backgrounds()
    elif target == "loops":
        fetch_loop_backgrounds()
    elif target in ALL:
        fetch_reel_clips(target, ALL[target])
    else:
        print(f"Options: {', '.join(ALL.keys())}, loops, or all")
