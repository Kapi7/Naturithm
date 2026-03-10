"""On-demand focused engagement session for Naturithm accounts.

Runs a timed engagement session that:
1. Checks comments on all posts and replies to unanswered ones
2. Echoes between accounts (cross-promotion)
3. Logs all actions with timestamps

Usage:
    python3 agents/engagement_session.py                    # 15-minute session (both accounts)
    python3 agents/engagement_session.py --duration 30      # 30-minute session
    python3 agents/engagement_session.py --account oria     # Only @oria_naturithm
    python3 agents/engagement_session.py --dry-run          # Preview without posting
"""

import time
import sys
import os
import socket
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from auto_reply import run_once as reply_run_once, log_action
from echo import run_once as echo_run_once

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ENGAGEMENT_LOG = os.path.join(DATA_DIR, "engagement_log.json")


def run_session(duration_minutes=15, accounts=None, dry_run=False):
    """Run a focused engagement session for the given duration."""
    if accounts is None:
        accounts = ["oria", "naturithm"]

    start = time.time()
    end_time = start + (duration_minutes * 60)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n{'='*60}")
    print(f"  ENGAGEMENT SESSION — {session_id}")
    print(f"  Duration: {duration_minutes} min | Accounts: {', '.join(accounts)}")
    print(f"  Machine: {socket.gethostname()}")
    if dry_run:
        print("  MODE: DRY RUN")
    print(f"{'='*60}")

    log_action("session_start", "all", session_id,
               f"Session started: {duration_minutes}min, accounts={accounts}", True)

    stats = {"replies": 0, "echoes": 0, "phases_completed": []}

    # ── Phase 1: Reply to unanswered comments ────────────────────────────
    if time.time() < end_time:
        print(f"\n{'─'*40}")
        print("  Phase 1: Replying to unanswered comments")
        print(f"{'─'*40}")
        try:
            new_replies = reply_run_once(accounts, dry_run)
            stats["replies"] = new_replies
            stats["phases_completed"].append("replies")
        except Exception as e:
            print(f"  Error in reply phase: {e}")
            log_action("session_error", "all", session_id, f"Reply phase error: {e}", False)

    # Brief pause between phases
    if time.time() < end_time:
        pause = min(10, max(0, end_time - time.time()))
        if pause > 0:
            print(f"\n  Pausing {int(pause)}s between phases...")
            time.sleep(pause)

    # ── Phase 2: Cross-promotion echo ────────────────────────────────────
    if time.time() < end_time and len(accounts) > 1:
        print(f"\n{'─'*40}")
        print("  Phase 2: Cross-promotion (echo)")
        print(f"{'─'*40}")
        try:
            new_echoes = echo_run_once(dry_run)
            stats["echoes"] = new_echoes
            stats["phases_completed"].append("echo")
        except Exception as e:
            print(f"  Error in echo phase: {e}")
            log_action("session_error", "all", session_id, f"Echo phase error: {e}", False)

    # ── Phase 3: If time remains, do a second pass on replies ────────────
    if time.time() < end_time:
        remaining = int((end_time - time.time()) / 60)
        if remaining > 2:
            pause = min(30, max(0, end_time - time.time() - 120))
            if pause > 0:
                print(f"\n  Waiting {int(pause)}s before second reply pass...")
                time.sleep(pause)

            if time.time() < end_time:
                print(f"\n{'─'*40}")
                print("  Phase 3: Second reply pass")
                print(f"{'─'*40}")
                try:
                    extra = reply_run_once(accounts, dry_run)
                    stats["replies"] += extra
                    stats["phases_completed"].append("replies_2nd")
                except Exception as e:
                    print(f"  Error in second pass: {e}")

    # ── Session summary ──────────────────────────────────────────────────
    elapsed = int(time.time() - start)
    elapsed_min = elapsed // 60
    elapsed_sec = elapsed % 60

    print(f"\n{'='*60}")
    print(f"  SESSION COMPLETE — {elapsed_min}m {elapsed_sec}s")
    print(f"  Replies: {stats['replies']} | Echoes: {stats['echoes']}")
    print(f"  Phases: {', '.join(stats['phases_completed'])}")
    print(f"{'='*60}\n")

    log_action("session_end", "all", session_id,
               f"Session complete: {elapsed_min}m {elapsed_sec}s, "
               f"replies={stats['replies']}, echoes={stats['echoes']}", True)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Run a focused engagement session")
    parser.add_argument("--duration", type=int, default=15,
                        help="Session duration in minutes (default: 15)")
    parser.add_argument("--account", choices=["oria", "naturithm", "all"], default="all",
                        help="Which account to engage with")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without posting")
    args = parser.parse_args()

    accounts = ["oria", "naturithm"] if args.account == "all" else [args.account]
    run_session(args.duration, accounts, args.dry_run)


if __name__ == "__main__":
    main()
