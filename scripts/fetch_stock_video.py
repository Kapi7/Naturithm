"""Fetch stock video clips from Pexels for all Oria reels."""

import requests
import os
from pathlib import Path

# Pexels API - free, no key needed for basic searches
# Using direct download from Pexels video search
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}

BASE = "https://api.pexels.com/videos/search"


def search_pexels(query, per_page=5, orientation="portrait"):
    """Search Pexels for videos."""
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": orientation,
        "size": "medium",
    }
    resp = requests.get(BASE, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"  Pexels API error {resp.status_code}: {resp.text[:200]}")
        return []
    data = resp.json()
    return data.get("videos", [])


def download_video(url, path):
    """Download video file."""
    path = Path(path)
    if path.exists():
        print(f"  ✓ {path.name} (exists)")
        return True
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {path.name} ({size_mb:.1f}MB)")
        return True
    print(f"  ✗ Failed to download {path.name}")
    return False


def get_best_file(video, max_height=1280):
    """Get the best video file URL (portrait, closest to 720x1280)."""
    files = video.get("video_files", [])
    # Prefer HD portrait
    best = None
    for f in files:
        h = f.get("height", 0)
        w = f.get("width", 0)
        if h >= 720 and (best is None or abs(h - max_height) < abs(best.get("height", 0) - max_height)):
            best = f
    if best:
        return best["link"]
    # Fallback to first available
    return files[0]["link"] if files else None


# ── Stock video needs per reel ────────────────────────────────────────

PANCAKE_CLIPS = [
    ("01_hook", "child eating pancake morning kitchen"),
    ("02_eggs", "cracking eggs into bowl close up cooking"),
    ("03_mix", "mixing batter bowl banana almond flour"),
    ("04_cook", "pancake cooking on pan flipping"),
    ("05_plate", "stack golden pancakes plate berries breakfast"),
    ("06_close", "parent child breakfast table morning light"),
]

GARLIC_CLIPS = [
    ("01_hook", "garlic bulb breaking apart wooden cutting board"),
    ("02_crush", "crushing garlic cloves knife cooking"),
    ("03_jar", "honey pouring into glass jar close up"),
    ("04_flip", "glass jar honey bubbles close up"),
    ("05_spoon", "honey spoon golden close up"),
    ("06_close", "natural ingredients herbs wooden surface golden hour"),
]

DEODORANT_CLIPS = [
    ("01_hook", "reading product label ingredients close up"),
    ("02_melt", "melting beeswax coconut oil double boiler"),
    ("03_mix", "mixing natural ingredients powder essential oil"),
    ("04_pour", "pouring liquid into small jar container"),
    ("05_apply", "morning routine skincare natural"),
    ("06_close", "natural ingredients laid out wooden surface"),
]

ADDICTION_CLIPS = [
    ("01_hook", "person sitting alone looking out window rain"),
    ("02_thing", "person scrolling phone in dark"),
    ("03_pain", "person walking alone crowd city"),
    ("04_feel", "sunrise nature person walking outdoors"),
    ("05_connect", "friends walking together nature connection"),
    ("06_close", "person sitting stillness nature peaceful"),
]

ALL_REELS = {
    "pancake_reel": PANCAKE_CLIPS,
    "garlic_reel": GARLIC_CLIPS,
    "deodorant_reel": DEODORANT_CLIPS,
    "addiction_reel": ADDICTION_CLIPS,
}


def fetch_all():
    for reel_name, clips in ALL_REELS.items():
        out_dir = Path(f"/Users/kapi7/Naturithm/output/{reel_name}/video")
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n{'='*50}")
        print(f"  {reel_name}")
        print(f"{'='*50}")

        for filename, query in clips:
            out_path = out_dir / f"{filename}.mp4"
            if out_path.exists():
                print(f"  ✓ {filename}.mp4 (exists)")
                continue

            print(f"  Searching: {query}")
            videos = search_pexels(query)
            if not videos:
                print(f"  ✗ No results for: {query}")
                continue

            url = get_best_file(videos[0])
            if url:
                download_video(url, out_path)
            else:
                print(f"  ✗ No suitable file for: {query}")


if __name__ == "__main__":
    if not PEXELS_API_KEY:
        print("Note: No PEXELS_API_KEY set. Will try without auth (rate limited).")
        print("Set PEXELS_API_KEY in .env for better results.\n")
    fetch_all()
