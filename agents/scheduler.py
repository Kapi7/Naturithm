"""
Auto-posting scheduler for Naturithm Instagram accounts.

Posts content on schedule to @oria_naturithm and @naturithm7.
Tracks posted status in data/posted.json and logs to data/work_log.json.

Usage:
    python3 agents/scheduler.py                # Check & post today's content
    python3 agents/scheduler.py --dry-run      # Preview without posting
    python3 agents/scheduler.py --status       # Show schedule status
    python3 agents/scheduler.py --force DATE   # Force post for a specific date (YYYY-MM-DD)

NOTE: Instagram API requires publicly accessible URLs for media.
      Video/image files must be served via a public URL (e.g., cloud storage,
      ngrok tunnel, or a public web server) before posting. Set the
      MEDIA_BASE_URL env var to the base URL where output/ files are served.
      Example: MEDIA_BASE_URL=https://your-server.com/naturithm/output
"""

import argparse
import json
import os
import sys
import glob as glob_mod
from datetime import datetime, date

# Ensure project root is on path so we can import sibling modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from agents.instagram import post_reel, post_photo
from agents.sync import git_pull, git_push

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
POSTED_PATH = os.path.join(DATA_DIR, "posted.json")
WORK_LOG_PATH = os.path.join(DATA_DIR, "work_log.json")
CONTENT_DATA_PATH = os.path.join(PROJECT_ROOT, "dashboard", "content_data.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Base URL where output/ files are publicly accessible.
# Must be set for actual posting. Example: https://cdn.example.com/output
MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", "")

# ---------------------------------------------------------------------------
# Content schedule — Day 1 = 2026-03-10
# ---------------------------------------------------------------------------
BATCH_START = date(2026, 3, 10)

# Schedule with staggered evening times (Cyprus time, EET UTC+2)
# Each post gets a unique time between 18:00-23:00 CY
SCHEDULE = [
    # Day 1 — Mar 10 (Mon)
    {"day": 1, "date": "2026-03-10", "time": "18:15", "id": "pancake_reel",
     "type": "reel", "account": "oria", "file": "pancake_reel/pancake_reel_v2.mp4"},
    {"day": 1, "date": "2026-03-10", "time": "21:00", "id": "naturithm_loop1",
     "type": "reel", "account": "naturithm", "file": "naturithm_loop1/naturithm_loop1_v2.mp4"},

    # Day 2 — Mar 11 (Tue)
    {"day": 2, "date": "2026-03-11", "time": "19:30", "id": "garlic_reel",
     "type": "reel", "account": "oria", "file": "garlic_reel/garlic_reel_v2.mp4"},
    {"day": 2, "date": "2026-03-11", "time": "22:00", "id": "naturithm_duck",
     "type": "reel", "account": "naturithm", "file": "naturithm_duck/naturithm_duck_v3.mp4"},

    # Day 3 — Mar 12 (Wed)
    {"day": 3, "date": "2026-03-12", "time": "18:45", "id": "carousel_running",
     "type": "carousel", "account": "oria",
     "slides": [
         "carousel_running/slide_01_hook.png", "carousel_running/slide_02_problem.png",
         "carousel_running/slide_03_science.png", "carousel_running/slide_04_body.png",
         "carousel_running/slide_05_high.png", "carousel_running/slide_06_born.png",
         "carousel_running/slide_07_start.png", "carousel_running/slide_08_cta.png",
     ]},
    {"day": 3, "date": "2026-03-12", "time": "21:30", "id": "naturithm_loop3",
     "type": "reel", "account": "naturithm", "file": "naturithm_loop3/naturithm_loop3_v2.mp4"},

    # Day 4 — Mar 13 (Thu)
    {"day": 4, "date": "2026-03-13", "time": "20:00", "id": "deodorant_reel",
     "type": "reel", "account": "oria", "file": "deodorant_reel/deodorant_reel_v2.mp4"},
    {"day": 4, "date": "2026-03-13", "time": "22:45", "id": "naturithm_fence",
     "type": "reel", "account": "naturithm", "file": "naturithm_fence/naturithm_fence_v3.mp4"},

    # Day 5 — Mar 14 (Fri)
    {"day": 5, "date": "2026-03-14", "time": "19:00", "id": "addiction_reel",
     "type": "reel", "account": "oria", "file": "addiction_reel/addiction_reel_v2.mp4"},
    {"day": 5, "date": "2026-03-14", "time": "21:45", "id": "naturithm_loop5",
     "type": "reel", "account": "naturithm", "file": "naturithm_loop5/naturithm_loop5_v2.mp4"},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path, data):
    ensure_data_dir()
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_posted():
    return load_json(POSTED_PATH, {})


def save_posted(posted):
    save_json(POSTED_PATH, posted)


def log_action(action, details, success=True):
    """Append an entry to data/work_log.json."""
    ensure_data_dir()
    log = load_json(WORK_LOG_PATH, [])
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "success": success,
    }
    log.append(entry)
    save_json(WORK_LOG_PATH, log)
    status = "OK" if success else "FAIL"
    print(f"  [LOG] {status} — {action}: {details}")


def load_captions():
    """Load captions from content_data.json, keyed by content id."""
    data = load_json(CONTENT_DATA_PATH, {})
    captions = {}
    for account_key, items in data.items():
        for item in items:
            captions[item["id"]] = item.get("caption", "")
    return captions


def media_url(relative_path):
    """Build a public URL for a file in output/."""
    if not MEDIA_BASE_URL:
        # Return local file path with a warning
        local = os.path.join(OUTPUT_DIR, relative_path)
        return local
    return f"{MEDIA_BASE_URL}/{relative_path}"


def get_items_for_date(target_date):
    """Return all schedule items whose date matches target_date, sorted by time."""
    target_str = target_date.strftime("%Y-%m-%d") if isinstance(target_date, date) else target_date
    items = [item for item in SCHEDULE if item["date"] == target_str]
    items.sort(key=lambda x: x.get("time", "00:00"))
    return items


def get_due_items():
    """Return items that are due NOW (date matches today, time has passed)."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    items = [
        item for item in SCHEDULE
        if item["date"] == today_str and item.get("time", "00:00") <= current_time
    ]
    items.sort(key=lambda x: x.get("time", "00:00"))
    return items


# ---------------------------------------------------------------------------
# Posting functions
# ---------------------------------------------------------------------------

def post_carousel(account, image_urls, caption):
    """Post a carousel (multi-image) to Instagram using the container API.

    Instagram carousel flow:
      1. Create child containers for each image
      2. Create a carousel container referencing the children
      3. Publish the carousel container
    Also posts images to Facebook as a multi-photo post.
    """
    import requests
    import time

    TOKEN = os.getenv("META_ACCESS_TOKEN")

    if account == "naturithm":
        ig_id = os.getenv("NATURITHM_IG_ID", "17841476800394111")
        page_id = os.getenv("NATURITHM_PAGE_ID", "1004541299415112")
    else:
        ig_id = os.getenv("ORIA_IG_ID", "17841476177917833")
        page_id = os.getenv("ORIA_PAGE_ID", "1068966376289042")

    results = {"ig": None, "fb": None}

    # --- Instagram Carousel ---
    child_ids = []
    for i, url in enumerate(image_urls):
        print(f"  [IG] Creating child container {i+1}/{len(image_urls)}...")
        r = requests.post(
            f"https://graph.facebook.com/v21.0/{ig_id}/media",
            params={
                "access_token": TOKEN,
                "image_url": url,
                "is_carousel_item": "true",
            }
        )
        data = r.json()
        if "id" in data:
            child_ids.append(data["id"])
            print(f"  [IG] Child container {i+1}: {data['id']}")
        else:
            print(f"  [IG] ERROR creating child {i+1}: {data}")
            log_action("carousel_child_error", f"slide {i+1}: {data}", success=False)
            return results

    if len(child_ids) != len(image_urls):
        print(f"  [IG] ERROR: only {len(child_ids)}/{len(image_urls)} children created")
        return results

    # Create carousel container
    print(f"  [IG] Creating carousel container with {len(child_ids)} children...")
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        params={
            "access_token": TOKEN,
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(child_ids),
        }
    )
    data = r.json()

    if "id" in data:
        container_id = data["id"]
        print(f"  [IG] Carousel container: {container_id}, waiting...")
        time.sleep(15)

        r2 = requests.post(
            f"https://graph.facebook.com/v21.0/{ig_id}/media_publish",
            params={"access_token": TOKEN, "creation_id": container_id}
        )
        pub = r2.json()
        if "id" in pub:
            print(f"  [IG] CAROUSEL PUBLISHED: {pub['id']}")
            results["ig"] = pub["id"]
        else:
            print(f"  [IG] PUBLISH ERROR: {pub}")
    else:
        print(f"  [IG] CAROUSEL ERROR: {data}")

    # --- Facebook multi-photo ---
    from agents.instagram import get_page_tokens
    page_tokens = get_page_tokens()
    page_token = page_tokens.get(page_id, TOKEN)

    print(f"  [FB] Posting carousel as album...")
    for i, url in enumerate(image_urls):
        r_fb = requests.post(
            f"https://graph.facebook.com/v21.0/{page_id}/photos",
            params={
                "access_token": page_token,
                "url": url,
                "message": caption if i == 0 else "",
                "published": "false" if i < len(image_urls) - 1 else "true",
            }
        )
        fb_data = r_fb.json()
        if "id" in fb_data:
            print(f"  [FB] Photo {i+1}: {fb_data['id']}")
            if i == len(image_urls) - 1:
                results["fb"] = fb_data["id"]
        else:
            print(f"  [FB] ERROR photo {i+1}: {fb_data}")

    return results


def do_post(item, caption, dry_run=False):
    """Execute a single post. Returns True on success."""
    content_id = item["id"]
    account = item["account"]
    content_type = item["type"]

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Posting: {content_id} -> @{'oria_naturithm' if account == 'oria' else 'naturithm7'}")
    print(f"  Type: {content_type}")

    if content_type == "reel":
        file_path = item["file"]
        url = media_url(file_path)
        local_path = os.path.join(OUTPUT_DIR, file_path)

        if not os.path.exists(local_path):
            msg = f"Video file not found: {local_path}"
            print(f"  ERROR: {msg}")
            log_action("post_error", msg, success=False)
            return False

        if not MEDIA_BASE_URL:
            print(f"  WARNING: MEDIA_BASE_URL not set. File path: {local_path}")
            print(f"  Set MEDIA_BASE_URL to a public URL serving the output/ directory.")
            if not dry_run:
                log_action("post_skipped", f"{content_id}: MEDIA_BASE_URL not set", success=False)
                return False

        print(f"  Video URL: {url}")
        print(f"  Caption: {caption[:80]}...")

        if dry_run:
            log_action("dry_run", f"Would post reel {content_id} to {account}")
            return True

        results = post_reel(account=account, video_url=url, caption=caption)
        success = results.get("ig") is not None
        log_action(
            "post_reel",
            f"{content_id} -> {account} | IG={results.get('ig')} FB={results.get('fb')}",
            success=success,
        )
        return success

    elif content_type == "carousel":
        slides = item.get("slides", [])
        if not slides:
            print(f"  ERROR: No slides defined for carousel {content_id}")
            return False

        slide_urls = []
        for slide in slides:
            local_path = os.path.join(OUTPUT_DIR, slide)
            if not os.path.exists(local_path):
                print(f"  ERROR: Slide not found: {local_path}")
                log_action("post_error", f"Slide missing: {local_path}", success=False)
                return False
            slide_urls.append(media_url(slide))

        if not MEDIA_BASE_URL:
            print(f"  WARNING: MEDIA_BASE_URL not set. Slides at: {OUTPUT_DIR}")
            print(f"  Set MEDIA_BASE_URL to a public URL serving the output/ directory.")
            if not dry_run:
                log_action("post_skipped", f"{content_id}: MEDIA_BASE_URL not set", success=False)
                return False

        print(f"  Slides: {len(slide_urls)} images")
        print(f"  Caption: {caption[:80]}...")

        if dry_run:
            log_action("dry_run", f"Would post carousel {content_id} ({len(slides)} slides) to {account}")
            return True

        results = post_carousel(account=account, image_urls=slide_urls, caption=caption)
        success = results.get("ig") is not None
        log_action(
            "post_carousel",
            f"{content_id} -> {account} | IG={results.get('ig')} FB={results.get('fb')}",
            success=success,
        )
        return success

    else:
        print(f"  ERROR: Unknown content type: {content_type}")
        return False


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_post(target_date, dry_run=False):
    """Check and post content for the given date."""
    # Sync from GitHub first — get latest posted.json from other machine
    if not dry_run:
        git_pull()

    items = get_items_for_date(target_date)
    if not items:
        print(f"No content scheduled for {target_date}.")
        log_action("check", f"No content for {target_date}")
        return

    posted = load_posted()
    captions = load_captions()

    posted_count = 0
    skipped_count = 0

    for item in items:
        content_id = item["id"]

        if content_id in posted:
            ts = posted[content_id].get("timestamp", "unknown")
            print(f"\nSkipping {content_id} — already posted at {ts}")
            skipped_count += 1
            continue

        caption = captions.get(content_id, "")
        if not caption:
            print(f"\nWARNING: No caption found for {content_id} in content_data.json")

        success = do_post(item, caption, dry_run=dry_run)

        if success and not dry_run:
            posted[content_id] = {
                "timestamp": datetime.now().isoformat(),
                "date": item["date"],
                "account": item["account"],
                "type": item["type"],
            }
            save_posted(posted)
            # Push immediately so the other machine sees it
            git_push(f"auto: posted {content_id}")
            posted_count += 1
        elif success and dry_run:
            posted_count += 1

    print(f"\n--- Summary ---")
    print(f"Date: {target_date}")
    print(f"Posted: {posted_count} | Skipped (already posted): {skipped_count}")
    if dry_run:
        print("(dry run — nothing was actually posted)")


def cmd_status():
    """Show the full schedule status."""
    posted = load_posted()

    print("=" * 75)
    print("NATURITHM CONTENT SCHEDULE — Batch starting 2026-03-10 (times in CY/EET)")
    print("=" * 75)

    for item in SCHEDULE:
        content_id = item["id"]
        status_info = posted.get(content_id)
        day = item["day"]
        sched_date = item["date"]
        sched_time = item.get("time", "?")
        content_type = item["type"]
        account = "@oria" if item["account"] == "oria" else "@nat7"

        if status_info:
            ts = status_info.get("timestamp", "")[:16]
            status = f"POSTED ({ts})"
        else:
            today = date.today()
            item_date = date.fromisoformat(sched_date)
            if item_date < today:
                status = "MISSED"
            elif item_date == today:
                status = "DUE TODAY"
            else:
                status = "upcoming"

        print(f"  Day {day} {sched_date} {sched_time} | {account:<6} | {content_id:<22} | {content_type:<10} | {status}")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Naturithm auto-posting scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--status", action="store_true", help="Show schedule status")
    parser.add_argument("--run-due", action="store_true", help="Post only items whose time has passed (for cron)")
    parser.add_argument("--force", metavar="DATE", help="Force post for a specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.status:
        cmd_status()
        return

    if args.force:
        try:
            target = date.fromisoformat(args.force)
        except ValueError:
            print(f"Invalid date format: {args.force}. Use YYYY-MM-DD.")
            sys.exit(1)
        cmd_post(target, dry_run=args.dry_run)
        return

    if args.run_due:
        # Cron mode: only post items whose scheduled time has passed
        now = datetime.now()
        print(f"Naturithm Scheduler — {now.strftime('%Y-%m-%d %H:%M')} (cron check)")
        if not args.dry_run:
            git_pull()
        items = get_due_items()
        if not items:
            print("  Nothing due right now.")
            return
        posted = load_posted()
        captions = load_captions()
        for item in items:
            cid = item["id"]
            if cid in posted:
                continue
            caption = captions.get(cid, "")
            success = do_post(item, caption, dry_run=args.dry_run)
            if success and not args.dry_run:
                posted[cid] = {
                    "timestamp": now.isoformat(),
                    "date": item["date"],
                    "account": item["account"],
                    "type": item["type"],
                }
                save_posted(posted)
                git_push(f"auto: posted {cid}")
        return

    # Default: post all of today's content
    today = date.today()
    print(f"Naturithm Scheduler — {today.isoformat()}")
    print()
    cmd_post(today, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
