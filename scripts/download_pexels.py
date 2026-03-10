"""Download stock videos from Pexels by ID and prepare for reel assembly.

Uses Pexels download endpoint which redirects to the actual video file.
Downloads HD quality, then crops to vertical 720x1280 for Instagram reels.
"""

import requests
import subprocess
from pathlib import Path
import sys

OUT_BASE = Path("/Users/kapi7/Naturithm/output")

# Video IDs from Pexels search results, mapped to reel clips
# Format: (pexels_id, description)
PANCAKE_VIDEOS = {
    "01_hook": (7677142, "child cooking"),      # a-child-cooking
    "02_eggs": (855849, "cooking pancakes breakfast"),  # cooking-pancakes-for-breakfast
    "03_mix": (7015389, "mixing pancake batter"),  # mixing-pancake-batter
    "04_cook": (2959327, "flipping pancake"),    # flipping-a-pancake
    "05_plate": (7010649, "stacking pancakes"),  # stacking-pancakes
    "06_close": (7677413, "mother child cooking"),  # mother-cooking-with-child
}

GARLIC_VIDEOS = {
    "01_hook": (5677375, "garlic on cutting board"),
    "02_crush": (5677375, "garlic prep"),  # same video, diff timestamp
    "03_jar": (6209572, "honey pouring"),
    "04_flip": (6209572, "honey jar"),
    "05_spoon": (5945631, "honey spoon"),
    "06_close": (6774137, "herbs wooden surface"),
}

DEODORANT_VIDEOS = {
    "01_hook": (5765024, "reading label"),
    "02_melt": (4868348, "melting ingredients"),
    "03_mix": (4868348, "mixing natural"),
    "04_pour": (4868348, "pouring mixture"),
    "05_apply": (3997023, "morning routine"),
    "06_close": (4046637, "natural ingredients"),
}

ADDICTION_VIDEOS = {
    "01_hook": (3699975, "person window rain"),
    "02_thing": (5537791, "scrolling phone dark"),
    "03_pain": (3694881, "person walking alone"),
    "04_feel": (1409899, "sunrise nature walking"),
    "05_connect": (5186918, "friends walking nature"),
    "06_close": (4203246, "meditation outdoors"),
}

ALL_REELS = {
    "pancake_reel": PANCAKE_VIDEOS,
    "garlic_reel": GARLIC_VIDEOS,
    "deodorant_reel": DEODORANT_VIDEOS,
    "addiction_reel": ADDICTION_VIDEOS,
}


def download_pexels_video(video_id, out_path):
    """Download a video from Pexels using the download endpoint."""
    if out_path.exists() and out_path.stat().st_size > 10000:
        print(f"  ✓ {out_path.name} (exists)")
        return True

    url = f"https://www.pexels.com/download/video/{video_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": f"https://www.pexels.com/video/{video_id}/",
    }

    try:
        resp = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=30)
        if resp.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_mb = out_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {out_path.name} ({size_mb:.1f}MB)")
            return True
        else:
            print(f"  ✗ {out_path.name}: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ {out_path.name}: {e}")
        return False


def crop_to_vertical(input_path, output_path, target_w=720, target_h=1280):
    """Crop horizontal video to vertical center-crop."""
    if output_path.exists() and output_path.stat().st_size > 5000:
        print(f"  ✓ {output_path.name} (exists)")
        return True

    # Get input dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0",
         str(input_path)],
        capture_output=True, text=True
    )
    if probe.returncode != 0:
        print(f"  ✗ Can't probe {input_path.name}")
        return False

    w, h = map(int, probe.stdout.strip().split(","))

    # Calculate crop: scale so height matches, then center-crop width
    # For vertical output from horizontal input:
    # Scale height to 1280, then crop width to 720
    scale_factor = target_h / h
    scaled_w = int(w * scale_factor)

    if scaled_w < target_w:
        # Video is already taller than wide, scale by width
        scale_filter = f"scale={target_w}:-2"
        crop_filter = f"crop={target_w}:{target_h}"
    else:
        scale_filter = f"scale=-2:{target_h}"
        crop_filter = f"crop={target_w}:{target_h}"

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", f"{scale_filter},{crop_filter}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-an",  # No audio (we'll add TTS)
        "-t", "6",  # Max 6 seconds per clip
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✓ {output_path.name} (cropped, {size_mb:.1f}MB)")
        return True
    else:
        print(f"  ✗ Crop failed: {result.stderr[-200:]}")
        return False


def process_reel(reel_name, videos):
    """Download and crop all videos for a reel."""
    raw_dir = OUT_BASE / reel_name / "video_raw"
    crop_dir = OUT_BASE / reel_name / "video"
    raw_dir.mkdir(parents=True, exist_ok=True)
    crop_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"  {reel_name}")
    print(f"{'='*50}")

    for clip_name, (video_id, desc) in videos.items():
        raw_path = raw_dir / f"{clip_name}_raw.mp4"
        crop_path = crop_dir / f"{clip_name}.mp4"

        print(f"\n  [{clip_name}] ID:{video_id} — {desc}")

        # Download
        if download_pexels_video(video_id, raw_path):
            # Crop to vertical
            crop_to_vertical(raw_path, crop_path)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "pancake_reel"

    if target == "all":
        for name, videos in ALL_REELS.items():
            process_reel(name, videos)
    elif target in ALL_REELS:
        process_reel(target, ALL_REELS[target])
    else:
        print(f"Unknown reel: {target}")
