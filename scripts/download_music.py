"""Download varied royalty-free music from Pixabay for different video types."""

import requests
import re
from pathlib import Path

MUSIC_DIR = Path("/Users/kapi7/Naturithm/output/music_library")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# Pixabay music download URLs (direct CDN links from the pages)
TRACKS = {
    # Story time (duck + dog)
    "story_hopeful_nostalgic.mp3": "https://pixabay.com/music/acoustic-group-hopeful-nostalgic-acoustic-folk-version-448769/",
    "story_hopeful_heart.mp3": "https://pixabay.com/music/acoustic-group-sentimental-acoustic-cinematic-ballad-hopeful-heart-283993/",

    # How-to reels (pancake, garlic, deodorant)
    "howto_warm_lounge.mp3": "https://pixabay.com/music/upbeat-warm-lounge-night-breeze-341691/",
    "howto_chill_vlog.mp3": "https://pixabay.com/music/rnb-chill-vlog-summer-beat-no-vocals-391930/",

    # Deep/personal (addiction)
    "deep_sad_piano.mp3": "https://pixabay.com/music/small-emotions-sad-minimal-piano-163678/",
    "deep_mirrors_piano.mp3": "https://pixabay.com/music/solo-piano-mirrors-piano-music-491139/",

    # Loops (cinematic)
    "loop_cinematic_strings.mp3": "https://pixabay.com/music/main-title-cinematic-strings-1-156493/",
    "loop_atmospheric_piano.mp3": "https://pixabay.com/music/modern-classical-enchanted-explorations-documentary-atmospheric-piano-201653/",
}


def get_pixabay_download_url(page_url):
    """Try to extract the actual download URL from the Pixabay page."""
    # Pixabay uses CDN URLs like https://cdn.pixabay.com/download/audio/...
    # We need to extract the track ID from the page URL
    match = re.search(r'-(\d+)/$', page_url)
    if not match:
        return None
    track_id = match.group(1)

    # Try the direct download API endpoint
    # Pixabay uses: https://pixabay.com/music/download/{slug}-{id}.mp3
    slug = page_url.rstrip('/').split('/')[-1]
    return f"https://cdn.pixabay.com/download/audio/2024/01/01/audio_{track_id}.mp3"


def download_from_pixabay_api(query, output_path):
    """Use Pixabay API to search and download music."""
    # Pixabay has a free API for music too
    api_key = "47628144-f31cf9b36e3b15c3d0d89a5c5"  # Free API key from pixabay
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={query}"  # Note: music API is different

    # Actually, Pixabay music API isn't publicly documented the same way
    # Let's try direct download approach
    pass


if __name__ == "__main__":
    print("Music tracks to download from Pixabay:")
    print("(Pixabay requires browser download - printing URLs)")
    print()
    for name, url in TRACKS.items():
        path = MUSIC_DIR / name
        if path.exists() and path.stat().st_size > 10000:
            print(f"  Already: {name}")
            continue
        print(f"  {name}")
        print(f"    → {url}")
    print()
    print("Note: Pixabay requires login for downloads. Use browser or Playwright.")
