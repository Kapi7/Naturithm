"""Git sync for multi-machine operation.

Pull before reading state, push after writing state.
Prevents double-posting, double-replying across machines.
"""

import subprocess
import socket
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git_pull():
    """Pull latest state from GitHub."""
    try:
        r = subprocess.run(
            ["git", "pull", "--rebase", "--autostash"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            print("  [SYNC] pull OK")
        else:
            print(f"  [SYNC] pull warning: {r.stderr.strip()}")
        return r.returncode == 0
    except Exception as e:
        print(f"  [SYNC] pull failed: {e}")
        return False


def git_push(message="auto: sync state"):
    """Commit and push data files."""
    hostname = socket.gethostname()
    try:
        subprocess.run(
            ["git", "add", "data/"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", f"{message} [{hostname}]"],
            cwd=PROJECT_ROOT, capture_output=True, timeout=10,
        )
        r = subprocess.run(
            ["git", "push"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            print("  [SYNC] push OK")
        else:
            print(f"  [SYNC] push warning: {r.stderr.strip()}")
        return r.returncode == 0
    except Exception as e:
        print(f"  [SYNC] push failed: {e}")
        return False
