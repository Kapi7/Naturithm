"""Analytics tracker for @oria_naturithm — pulls and logs Instagram performance data.

Usage:
    python agents/analytics.py              # Pull and display current stats
    python agents/analytics.py --save       # Pull, display, and save to data/analytics/
    python agents/analytics.py --report     # Generate weekly summary report
"""

import requests
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Config
TOKEN = os.getenv("META_ACCESS_TOKEN", "EAHlwoIITZCZC8BQ4Hv7iUfaGvC3XBfZCZA7fXPZBdYknDKeZA4D09tsFcUCWsdyOs2VPI7ybL2NvjYJkCWBwAl16iP6rgyStL3fKNRCP5LiEDqsHeDIhIRaLg0vSzzAvFFMVjBNtzFcoSouj5ZAo796Hue63xhZBW44bQ0cVHTDT35RfQbgxq7MtofHiGXIdpCEuxwZDZD")
ORIA_IG_ID = os.getenv("ORIA_IG_ID", "17841476177917833")
DATA_DIR = Path("data/analytics")
API_BASE = "https://graph.facebook.com/v21.0"


def get_media_list():
    """Get all media from @oria_naturithm."""
    r = requests.get(
        f"{API_BASE}/{ORIA_IG_ID}/media",
        params={
            "fields": "id,caption,timestamp,media_type,like_count,comments_count,permalink",
            "access_token": TOKEN,
            "limit": 50,
        }
    )
    return r.json().get("data", [])


def get_media_insights(media_id):
    """Get insights for a specific media (works for Reels)."""
    r = requests.get(
        f"{API_BASE}/{media_id}/insights",
        params={
            "metric": "plays,reach,saved,shares,comments,likes,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time",
            "access_token": TOKEN,
        }
    )
    data = r.json().get("data", [])
    return {item["name"]: item["values"][0]["value"] for item in data}


def get_account_insights(since_date=None, until_date=None):
    """Get account-level insights."""
    if not since_date:
        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not until_date:
        until_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    r = requests.get(
        f"{API_BASE}/{ORIA_IG_ID}/insights",
        params={
            "metric": "reach,impressions,accounts_engaged,profile_views",
            "period": "day",
            "since": since_date,
            "until": until_date,
            "access_token": TOKEN,
        }
    )
    return r.json().get("data", [])


def pull_all_stats():
    """Pull complete analytics snapshot."""
    print("Pulling media list...")
    media = get_media_list()
    print(f"Found {len(media)} posts.\n")

    results = []
    for post in media:
        media_id = post["id"]
        media_type = post.get("media_type", "UNKNOWN")
        caption_preview = (post.get("caption", "") or "")[:80]
        permalink = post.get("permalink", "")

        print(f"  Pulling insights for {media_id} ({media_type})...")
        insights = get_media_insights(media_id)

        entry = {
            "id": media_id,
            "type": media_type,
            "caption_preview": caption_preview,
            "permalink": permalink,
            "timestamp": post.get("timestamp", ""),
            "like_count": post.get("like_count", 0),
            "comments_count": post.get("comments_count", 0),
            "insights": insights,
        }
        results.append(entry)

    # Account-level
    print("\n  Pulling account insights...")
    account = get_account_insights()

    return {"posts": results, "account": account, "pulled_at": datetime.now().isoformat()}


def display_stats(stats):
    """Print a formatted analytics report."""
    print(f"\n{'='*70}")
    print(f"  @oria_naturithm — Analytics Report")
    print(f"  Pulled: {stats['pulled_at'][:19]}")
    print(f"{'='*70}\n")

    # Post-level table
    print(f"{'Post':<12} {'Views':>8} {'Reach':>8} {'AvgWatch':>9} {'Likes':>6} {'Saves':>6} {'Shares':>7} {'Eng%':>6}")
    print(f"{'-'*12} {'-'*8} {'-'*8} {'-'*9} {'-'*6} {'-'*6} {'-'*7} {'-'*6}")

    for post in stats["posts"]:
        ins = post["insights"]
        views = ins.get("plays", 0)
        reach = ins.get("reach", 0)
        avg_watch = ins.get("ig_reels_avg_watch_time", 0)
        likes = ins.get("likes", 0)
        saves = ins.get("saved", 0)
        shares = ins.get("shares", 0)
        total_int = ins.get("total_interactions", 0)
        eng_rate = (total_int / reach * 100) if reach > 0 else 0

        # Extract short label from caption
        caption = post["caption_preview"]
        label = caption[:10] + ".." if len(caption) > 10 else caption

        avg_watch_str = f"{avg_watch / 1000:.1f}s" if avg_watch > 100 else f"{avg_watch:.1f}s"

        print(f"{label:<12} {views:>8} {reach:>8} {avg_watch_str:>9} {likes:>6} {saves:>6} {shares:>7} {eng_rate:>5.1f}%")

    # Account summary
    print(f"\n{'='*70}")
    print("  Account-Level Insights (last 7 days)")
    print(f"{'='*70}")
    for metric in stats.get("account", []):
        name = metric.get("name", "")
        values = metric.get("values", [])
        total = sum(v.get("value", 0) for v in values)
        print(f"  {name}: {total}")

    print()


def save_stats(stats):
    """Save analytics snapshot to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filepath = DATA_DIR / f"snapshot_{date_str}.json"

    with open(filepath, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Saved to: {filepath}")
    return filepath


def generate_report():
    """Generate a comparison report from saved snapshots."""
    if not DATA_DIR.exists():
        print("No analytics data found. Run with --save first.")
        return

    snapshots = sorted(DATA_DIR.glob("snapshot_*.json"))
    if not snapshots:
        print("No snapshots found.")
        return

    print(f"\nFound {len(snapshots)} snapshot(s).\n")

    # Load latest
    with open(snapshots[-1]) as f:
        latest = json.load(f)

    display_stats(latest)

    # If we have 2+, show growth
    if len(snapshots) >= 2:
        with open(snapshots[-2]) as f:
            previous = json.load(f)

        print("Growth since last snapshot:")
        print("-" * 40)

        prev_posts = {p["id"]: p for p in previous["posts"]}
        for post in latest["posts"]:
            pid = post["id"]
            if pid in prev_posts:
                prev_views = prev_posts[pid]["insights"].get("plays", 0)
                curr_views = post["insights"].get("plays", 0)
                growth = curr_views - prev_views
                if growth > 0:
                    label = post["caption_preview"][:20]
                    print(f"  {label}..  +{growth} views")

    print()


def main():
    save = "--save" in sys.argv
    report = "--report" in sys.argv

    if report:
        generate_report()
        return

    stats = pull_all_stats()
    display_stats(stats)

    if save:
        save_stats(stats)


if __name__ == "__main__":
    main()
