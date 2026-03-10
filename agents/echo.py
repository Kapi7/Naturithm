"""Cross-promotion between @oria_naturithm and @naturithm7.

When one account posts, the other engages with a like + thoughtful comment.

Usage:
    python3 agents/echo.py              # Run once, check for new posts to echo
    python3 agents/echo.py --loop       # Check every 2 hours
    python3 agents/echo.py --dry-run    # Preview without posting
"""

import requests
import time
import json
import os
import sys
import socket
import argparse
from datetime import datetime

import anthropic
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Config ──────────────────────────────────────────────────────────────

TOKEN = os.getenv("META_ACCESS_TOKEN")
ORIA_IG_ID = os.getenv("ORIA_IG_ID", "17841476177917833")
NATURITHM_IG_ID = os.getenv("NATURITHM_IG_ID", "17841476800394111")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ECHO_LOG = os.path.join(DATA_DIR, "echo_log.json")
ENGAGEMENT_LOG = os.path.join(DATA_DIR, "engagement_log.json")
LOOP_INTERVAL = 7200  # 2 hours

# ── Voice prompts for cross-commenting ───────────────────────────────────

ORIA_ON_NATURITHM_PROMPT = """You are Oria (@oria_naturithm), commenting on a post by @naturithm7 (the Naturithm brand page).
You are the AI persona behind the brand. Your comment should be:
- Personal, warm, genuine — like a creator engaging with their own brand's content
- "I love this perspective..." / "This is exactly what I mean when..." / "This one hits close to home."
- 1-2 sentences max
- No hashtags, no emojis (or max 1 subtle one)
- Sound like you genuinely connect with the content, not like a bot
- Never generic ("great post", "love this") — reference the actual content
"""

NATURITHM_ON_ORIA_PROMPT = """You are @naturithm7 (the Naturithm brand), commenting on a post by @oria_naturithm (Oria, your AI persona).
Your comment should be:
- Philosophical, reflective — the brand voice adding depth
- "This is what wellness looks like when you strip away the noise." / "The body already knows. We just needed someone to remind us."
- 1-2 sentences max
- No hashtags, no emojis (or max 1 subtle one)
- Add a philosophical layer to whatever Oria posted
- Never generic — reference the actual content
"""


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def log_action(action, account, target, details, success=True):
    """Append to central engagement log."""
    _ensure_dirs()
    log = []
    if os.path.exists(ENGAGEMENT_LOG):
        try:
            with open(ENGAGEMENT_LOG) as f:
                log = json.load(f)
        except (json.JSONDecodeError, IOError):
            log = []

    log.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "machine": socket.gethostname(),
        "action": action,
        "account": account,
        "target": target,
        "details": details,
        "success": success,
    })

    with open(ENGAGEMENT_LOG, "w") as f:
        json.dump(log, f, indent=2)


def action_already_done(action, target):
    """Check if this action was already performed on this target."""
    if not os.path.exists(ENGAGEMENT_LOG):
        return False
    try:
        with open(ENGAGEMENT_LOG) as f:
            log = json.load(f)
        return any(e.get("action") == action and e.get("target") == target and e.get("success") for e in log)
    except (json.JSONDecodeError, IOError):
        return False


# ── Echo log ─────────────────────────────────────────────────────────────

def load_echo_log():
    _ensure_dirs()
    if os.path.exists(ECHO_LOG):
        try:
            with open(ECHO_LOG) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"echoed_posts": []}


def save_echo_log(data):
    _ensure_dirs()
    with open(ECHO_LOG, "w") as f:
        json.dump(data, f, indent=2)


def is_echoed(post_id):
    """Check if a post has already been echoed."""
    data = load_echo_log()
    return post_id in data.get("echoed_posts", [])


def mark_echoed(post_id):
    data = load_echo_log()
    data.setdefault("echoed_posts", []).append(post_id)
    save_echo_log(data)


# ── Instagram API ────────────────────────────────────────────────────────

def get_recent_media(ig_id):
    r = requests.get(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        params={
            "fields": "id,caption,timestamp,media_type",
            "access_token": TOKEN,
            "limit": 10,
        }
    )
    return r.json().get("data", [])


def like_media(media_id):
    """Like a post (requires Instagram account context — uses comment as engagement)."""
    # Note: The Graph API doesn't support liking via API for IG.
    # We log it but the actual like needs to be done via the account context.
    # For cross-promotion, the comment is the primary engagement.
    pass


def post_comment(media_id, comment_text):
    """Post a comment on a media item."""
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{media_id}/comments",
        params={
            "access_token": TOKEN,
            "message": comment_text,
        }
    )
    return r.json()


# ── Comment generation ───────────────────────────────────────────────────

def generate_echo_comment(post_caption, commenter_account):
    """Generate a cross-promotion comment using Claude."""
    client = anthropic.Anthropic()

    if commenter_account == "oria":
        system = ORIA_ON_NATURITHM_PROMPT
    else:
        system = NATURITHM_ON_ORIA_PROMPT

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        system=system,
        messages=[{
            "role": "user",
            "content": (
                f"Post caption: \"{post_caption[:500]}\"\n\n"
                "Write a thoughtful, genuine comment on this post. "
                "1-2 sentences. Reference the actual content."
            )
        }]
    )
    return response.content[0].text.strip()


# ── Main logic ───────────────────────────────────────────────────────────

def run_once(dry_run=False):
    """Check for new posts on both accounts and cross-engage."""
    echo_pairs = [
        # (source account whose posts we check, commenter account, source IG ID)
        ("naturithm", "oria", NATURITHM_IG_ID),
        ("oria", "naturithm", ORIA_IG_ID),
    ]

    total_echoed = 0

    for source_name, commenter_name, source_ig_id in echo_pairs:
        print(f"\n{'='*50}")
        print(f"  Checking @{source_name}'s posts for @{commenter_name} to echo")
        print(f"{'='*50}")

        posts = get_recent_media(source_ig_id)
        print(f"  Found {len(posts)} recent posts")

        for post in posts:
            post_id = post["id"]
            caption = post.get("caption", "")

            if is_echoed(post_id):
                continue

            # Check if another machine already echoed this
            if action_already_done("echo", post_id):
                mark_echoed(post_id)
                continue

            print(f"\n  Post: \"{caption[:80]}...\"" if len(caption) > 80 else f"\n  Post: \"{caption}\"")

            try:
                comment = generate_echo_comment(caption, commenter_name)
                print(f"  @{commenter_name} comment: \"{comment}\"")

                if not dry_run:
                    result = post_comment(post_id, comment)
                    success = "id" in result
                    if success:
                        print(f"  Posted! ({result['id']})")
                    else:
                        print(f"  Error: {result}")

                    log_action("echo", commenter_name, post_id,
                               f"Echo comment on @{source_name}'s post: {comment[:100]}",
                               success)
                    if success:
                        mark_echoed(post_id)
                        total_echoed += 1
                else:
                    print("  [DRY RUN — not posted]")
                    mark_echoed(post_id)
                    total_echoed += 1

                time.sleep(3)

            except Exception as e:
                print(f"  Error: {e}")
                log_action("echo", commenter_name, post_id, f"Error: {e}", False)

    print(f"\nDone. {total_echoed} posts echoed.")
    return total_echoed


def main():
    parser = argparse.ArgumentParser(description="Cross-promotion between accounts")
    parser.add_argument("--loop", action="store_true", help="Check every 2 hours")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — comments will be generated but NOT posted\n")

    if args.loop:
        print(f"Running in loop mode (every {LOOP_INTERVAL // 3600} hours)\n")
        while True:
            run_once(args.dry_run)
            print(f"\nSleeping {LOOP_INTERVAL // 3600} hours...")
            time.sleep(LOOP_INTERVAL)
    else:
        run_once(args.dry_run)


if __name__ == "__main__":
    main()
