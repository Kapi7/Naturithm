"""Auto-reply to Instagram comments for both @oria_naturithm and @naturithm7.

Usage:
    python3 agents/auto_reply.py                          # Reply on both accounts
    python3 agents/auto_reply.py --account oria            # Only @oria_naturithm
    python3 agents/auto_reply.py --account naturithm       # Only @naturithm7
    python3 agents/auto_reply.py --account all             # Both (default)
    python3 agents/auto_reply.py --loop                    # Run continuously (every 30 min)
    python3 agents/auto_reply.py --dry-run                 # Preview replies without posting
"""

import requests
import time
import json
import os
import sys
import socket
import argparse
from datetime import datetime, date

from google import genai
from dotenv import load_dotenv

# Ensure imports work from project root or agents dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oria_voice import ORIA_REPLY_SYSTEM_PROMPT
from sync import git_pull, git_push

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Config ──────────────────────────────────────────────────────────────

TOKEN = os.getenv("META_ACCESS_TOKEN")
ORIA_IG_ID = os.getenv("ORIA_IG_ID", "17841476177917833")
NATURITHM_IG_ID = os.getenv("NATURITHM_IG_ID", "17841476800394111")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPLIED_FILE = os.path.join(DATA_DIR, "replied_comments.json")
ENGAGEMENT_LOG = os.path.join(DATA_DIR, "engagement_log.json")
CHECK_INTERVAL = 1800  # 30 minutes
MAX_FOLLOWS_PER_DAY = 2

# Question detection
QUESTION_WORDS = {"how", "what", "why", "when", "where", "can", "does", "is", "should",
                  "do", "will", "would", "could", "are", "has", "have", "which", "who"}

# Naturithm7 voice — more philosophical, less personal
NATURITHM_REPLY_SYSTEM_PROMPT = """You are the voice behind @naturithm7 on Instagram — a wellness brand rooted in nature's intelligence.

WHO YOU ARE:
- The brand voice of Naturithm — you speak for the philosophy, not as a person
- You believe the body already knows what it needs; modern life just adds noise
- You're thoughtful, philosophical, slightly poetic — never preachy
- You reference evolution, nature's design, the body's intelligence

YOUR VOICE:
- Short, reflective sentences. Think nature documentary narrator meets zen teacher.
- More philosophical than personal — use "the body" or "nature" more than "I"
- Occasionally profound, never pretentious
- No emojis unless absolutely natural — max one per reply
- Never say "amazing", "incredible", "journey", "game-changer"
- Reference millions of years of evolution, natural design, simplicity

REPLY RULES:
- Keep replies 1-3 sentences MAX
- Add insight — a perspective shift, a deeper truth, a gentle reframe
- If someone asks a question, answer with wisdom and clarity
- If someone shares their experience, honor it with a philosophical reflection
- If someone is skeptical, meet them with curiosity, not defense
- Never hard-sell or push products

EXAMPLES:

Comment: "This changed how I eat!"
Reply: "That's the thing about real food — once you taste the difference, there's no going back. The body remembers."

Comment: "Is cold water really better than warm?"
Reply: "Your ancestors didn't have temperature settings. The body adapts to what nature provides — that adaptation is where the strength lives."

Comment: "Love this!"
Reply: "Glad it resonated."
"""


def _ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)


def log_action(action, account, target, details, success=True):
    """Append an entry to the central engagement log."""
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
    """Check if another machine already performed this action on this target."""
    if not os.path.exists(ENGAGEMENT_LOG):
        return False
    try:
        with open(ENGAGEMENT_LOG) as f:
            log = json.load(f)
        return any(e.get("action") == action and e.get("target") == target and e.get("success") for e in log)
    except (json.JSONDecodeError, IOError):
        return False


def follows_today(account):
    """Count how many follows were done today for a given account."""
    if not os.path.exists(ENGAGEMENT_LOG):
        return 0
    try:
        with open(ENGAGEMENT_LOG) as f:
            log = json.load(f)
        today = date.today().isoformat()
        return sum(1 for e in log
                   if e.get("action") == "follow"
                   and e.get("account") == account
                   and e.get("success")
                   and e.get("timestamp", "").startswith(today))
    except (json.JSONDecodeError, IOError):
        return 0


# ── Replied comments tracking (per account) ─────────────────────────────

def load_replied():
    """Load replied comment IDs, keyed by account."""
    _ensure_dirs()
    if os.path.exists(REPLIED_FILE):
        try:
            with open(REPLIED_FILE) as f:
                data = json.load(f)
            # Migrate old flat-list format
            if isinstance(data, list):
                return {"oria_replied": data, "naturithm_replied": []}
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return {"oria_replied": [], "naturithm_replied": []}


def save_replied(replied: dict):
    _ensure_dirs()
    with open(REPLIED_FILE, "w") as f:
        json.dump(replied, f, indent=2)


def _replied_key(account):
    return f"{account}_replied"


# ── Instagram API helpers ────────────────────────────────────────────────

def get_recent_media(ig_id):
    """Get recent Instagram posts for an account."""
    r = requests.get(
        f"https://graph.facebook.com/v21.0/{ig_id}/media",
        params={
            "fields": "id,caption,timestamp,media_type",
            "access_token": TOKEN,
            "limit": 25,
        }
    )
    return r.json().get("data", [])


def get_comments(media_id):
    """Get comments on a specific post."""
    r = requests.get(
        f"https://graph.facebook.com/v21.0/{media_id}/comments",
        params={
            "fields": "id,text,username,timestamp",
            "access_token": TOKEN,
            "limit": 50,
        }
    )
    return r.json().get("data", [])


def post_reply(comment_id, reply_text):
    """Post a reply to a comment."""
    r = requests.post(
        f"https://graph.facebook.com/v21.0/{comment_id}/replies",
        params={
            "access_token": TOKEN,
            "message": reply_text,
        }
    )
    return r.json()


# ── Question detection ───────────────────────────────────────────────────

def is_question(text):
    """Detect if a comment contains a question."""
    if "?" in text:
        return True
    words = set(text.lower().split())
    return bool(words & QUESTION_WORDS)


# ── Reply generation ─────────────────────────────────────────────────────

_genai_client = None

def _get_genai():
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(vertexai=True, project="naturitm", location="us-central1")
    return _genai_client


def generate_reply(comment_text, post_caption, account="oria"):
    """Generate a reply using Gemini in the appropriate voice."""
    client = _get_genai()

    if account == "oria":
        system = ORIA_REPLY_SYSTEM_PROMPT
    else:
        system = NATURITHM_REPLY_SYSTEM_PROMPT

    question_detected = is_question(comment_text)
    instruction = (
        f"Post caption (for context): {post_caption[:300]}\n\n"
        f"Comment to reply to: \"{comment_text}\"\n\n"
    )
    if question_detected:
        instruction += (
            "This comment contains a QUESTION. Answer it directly and helpfully, "
            "then add a small insight or encouragement. Be accurate — if you're unsure, say so.\n\n"
        )
    instruction += "Write a reply. 1-3 sentences max. No hashtags. No emojis unless absolutely natural."

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=instruction,
        config={"system_instruction": system, "max_output_tokens": 200},
    )
    return response.text.strip()


# ── Main logic ───────────────────────────────────────────────────────────

def run_once(accounts=None, dry_run=False):
    """Check posts for unreplied comments and reply."""
    git_pull()

    if accounts is None:
        accounts = ["oria", "naturithm"]

    replied_data = load_replied()
    total_new = 0

    account_config = {
        "oria": {"ig_id": ORIA_IG_ID, "name": "@oria_naturithm"},
        "naturithm": {"ig_id": NATURITHM_IG_ID, "name": "@naturithm7"},
    }

    for account in accounts:
        cfg = account_config[account]
        key = _replied_key(account)
        replied_set = set(replied_data.get(key, []))

        print(f"\n{'='*50}")
        print(f"  {cfg['name']} — checking comments")
        print(f"{'='*50}")

        media = get_recent_media(cfg["ig_id"])
        print(f"  Found {len(media)} posts")

        for post in media:
            comments = get_comments(post["id"])
            caption = post.get("caption", "")

            for comment in comments:
                cid = comment["id"]
                if cid in replied_set:
                    continue

                # Check if another machine already handled this
                if action_already_done("reply", cid):
                    replied_set.add(cid)
                    continue

                text = comment.get("text", "")
                user = comment.get("username", "unknown")

                # Skip very short comments (just emojis) or own accounts
                if len(text.strip()) < 3:
                    replied_set.add(cid)
                    continue
                if user in ("oria_naturithm", "naturithm7"):
                    replied_set.add(cid)
                    continue

                q_flag = " [Q]" if is_question(text) else ""
                print(f"\n  @{user}: \"{text}\"{q_flag}")

                try:
                    reply = generate_reply(text, caption, account)
                    print(f"  {cfg['name']}: \"{reply}\"")

                    if not dry_run:
                        result = post_reply(cid, reply)
                        success = "id" in result
                        if success:
                            print(f"  Posted! ({result['id']})")
                        else:
                            print(f"  Error: {result}")
                        log_action("reply", account, cid,
                                   f"Replied to @{user}: {reply[:100]}", success)
                    else:
                        print("  [DRY RUN — not posted]")

                    replied_set.add(cid)
                    total_new += 1
                    time.sleep(2)

                except Exception as e:
                    print(f"  Error generating reply: {e}")
                    log_action("reply", account, cid, f"Error: {e}", False)

        replied_data[key] = list(replied_set)

    save_replied(replied_data)
    if total_new > 0:
        git_push(f"auto: {total_new} replies")
    print(f"\nDone. {total_new} new replies across all accounts.")
    return total_new


def main():
    parser = argparse.ArgumentParser(description="Auto-reply to Instagram comments")
    parser.add_argument("--account", choices=["oria", "naturithm", "all"], default="all",
                        help="Which account to process")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    args = parser.parse_args()

    accounts = ["oria", "naturithm"] if args.account == "all" else [args.account]

    if args.dry_run:
        print("DRY RUN — replies will be generated but NOT posted\n")

    if args.loop:
        print(f"Running in loop mode (every {CHECK_INTERVAL // 60} min)\n")
        while True:
            run_once(accounts, args.dry_run)
            print(f"\nSleeping {CHECK_INTERVAL // 60} min...")
            time.sleep(CHECK_INTERVAL)
    else:
        run_once(accounts, args.dry_run)


if __name__ == "__main__":
    main()
