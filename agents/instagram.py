"""Instagram & Facebook posting utilities for Naturithm."""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("META_ACCESS_TOKEN")
NATURITHM_IG_ID = os.getenv("NATURITHM_IG_ID", "17841476800394111")
NATURITHM_PAGE_ID = os.getenv("NATURITHM_PAGE_ID", "1004541299415112")
ORIA_IG_ID = os.getenv("ORIA_IG_ID", "17841476177917833")
ORIA_PAGE_ID = os.getenv("ORIA_PAGE_ID", "1068966376289042")

# Page tokens (retrieved from system user token)
def get_page_tokens():
    r = requests.get(
        f"https://graph.facebook.com/v21.0/me/accounts",
        params={"fields": "id,name,access_token", "access_token": TOKEN}
    )
    tokens = {}
    for page in r.json().get("data", []):
        tokens[page["id"]] = page["access_token"]
    return tokens


def post_photo(account="naturithm", image_url="", caption=""):
    """Post a square photo to Instagram + Facebook.

    account: "naturithm" or "oria"
    image_url: publicly accessible URL (e.g. raw GitHub)
    caption: full caption with hashtags inline
    """
    page_tokens = get_page_tokens()

    if account == "naturithm":
        ig_id = NATURITHM_IG_ID
        page_id = NATURITHM_PAGE_ID
    else:
        ig_id = ORIA_IG_ID
        page_id = ORIA_PAGE_ID

    page_token = page_tokens.get(page_id, TOKEN)
    results = {"ig": None, "fb": None}

    # Instagram
    print(f"  [IG] Creating container...")
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        params={
            "access_token": TOKEN,
            "image_url": image_url,
            "caption": caption,
        }
    )
    data = r.json()

    if "id" in data:
        container_id = data["id"]
        print(f"  [IG] Container: {container_id}, waiting...")
        time.sleep(12)

        r2 = requests.post(
            f"https://graph.facebook.com/v21.0/{ig_id}/media_publish",
            params={"access_token": TOKEN, "creation_id": container_id}
        )
        pub = r2.json()
        if "id" in pub:
            print(f"  [IG] PUBLISHED: {pub['id']}")
            results["ig"] = pub["id"]
        else:
            print(f"  [IG] ERROR: {pub}")
    else:
        print(f"  [IG] ERROR: {data}")

    # Facebook
    print(f"  [FB] Posting...")
    r_fb = requests.post(
        f"https://graph.facebook.com/v21.0/{page_id}/photos",
        params={
            "access_token": page_token,
            "url": image_url,
            "message": caption,
        }
    )
    fb_data = r_fb.json()
    if "id" in fb_data:
        print(f"  [FB] PUBLISHED: {fb_data['id']}")
        results["fb"] = fb_data["id"]
    else:
        print(f"  [FB] ERROR: {fb_data}")

    return results


def post_reel(account="oria", video_url="", caption="", cover_url=None):
    """Post a Reel to Instagram + Facebook.

    account: "naturithm" or "oria"
    video_url: publicly accessible video URL
    caption: full caption with hashtags inline
    cover_url: optional cover image URL
    """
    page_tokens = get_page_tokens()

    if account == "naturithm":
        ig_id = NATURITHM_IG_ID
        page_id = NATURITHM_PAGE_ID
    else:
        ig_id = ORIA_IG_ID
        page_id = ORIA_PAGE_ID

    page_token = page_tokens.get(page_id, TOKEN)
    results = {"ig": None, "fb": None}

    # Instagram Reel
    print(f"  [IG] Creating Reel container...")
    params = {
        "access_token": TOKEN,
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": "true",
    }
    if cover_url:
        params["cover_url"] = cover_url

    r = requests.post(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        params=params
    )
    data = r.json()

    if "id" in data:
        container_id = data["id"]
        print(f"  [IG] Container: {container_id}, waiting for processing...")

        # Poll for status (video takes longer)
        for attempt in range(30):
            time.sleep(10)
            status_r = requests.get(
                f"https://graph.facebook.com/v21.0/{container_id}",
                params={"fields": "status_code", "access_token": TOKEN}
            )
            status = status_r.json().get("status_code")
            print(f"  [IG] Status: {status} (attempt {attempt+1})")
            if status == "FINISHED":
                break
            elif status == "ERROR":
                print(f"  [IG] Processing failed!")
                return results

        r2 = requests.post(
            f"https://graph.facebook.com/v21.0/{ig_id}/media_publish",
            params={"access_token": TOKEN, "creation_id": container_id}
        )
        pub = r2.json()
        if "id" in pub:
            print(f"  [IG] REEL PUBLISHED: {pub['id']}")
            results["ig"] = pub["id"]
        else:
            print(f"  [IG] ERROR: {pub}")
    else:
        print(f"  [IG] ERROR: {data}")

    # Facebook Video
    print(f"  [FB] Posting video...")
    r_fb = requests.post(
        f"https://graph.facebook.com/v21.0/{page_id}/videos",
        params={
            "access_token": page_token,
            "file_url": video_url,
            "description": caption,
        }
    )
    fb_data = r_fb.json()
    if "id" in fb_data:
        print(f"  [FB] PUBLISHED: {fb_data['id']}")
        results["fb"] = fb_data["id"]
    else:
        print(f"  [FB] ERROR: {fb_data}")

    return results
