"""Instagram Engagement Automation via Playwright MCP.

Automates daily engagement routine on Instagram:
- Searches target hashtags
- Likes posts
- Follows relevant accounts
- Leaves genuine comments in Oria's voice

RISK WARNING: This uses browser automation which violates Instagram's ToS.
Uses human-like delays and conservative limits to minimize detection risk.
Use at your own discretion.

Usage (via Claude Code with Playwright MCP):
    This script is designed to be run through Claude Code's Playwright MCP tools.
    It provides the engagement plan and comment templates.
    The actual browser automation is orchestrated by Claude Code.

Manual usage:
    python agents/engage.py --plan     # Show today's engagement plan
    python agents/engage.py --comments # Generate fresh comments for today
"""

import random
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Try to import anthropic for comment generation
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ── Config ──────────────────────────────────────────────────────────────

# Target hashtags — rotate daily across ALL 5 pillars
# Each group picks one hashtag per pillar so every session covers the full brand
HASHTAG_GROUPS = [
    # Group A — Nourishment + Movement + Stillness
    ["fermentation", "fermentedfoods", "guthealth"],
    # Group B — Movement + Presence + Trust
    ["naturalmovement", "mindfulrunning", "barefoot"],
    # Group C — Stillness + Nourishment + Presence
    ["meditation", "breathwork", "mindfulness"],
    # Group D — Nourishment broad + Natural living
    ["realfood", "wholefood", "cleaneating"],
    # Group E — Wellness + Holistic + Natural
    ["holistichealth", "naturalhealth", "cleanliving"],
    # Group F — Movement + Body intelligence
    ["functionalfitness", "zone2training", "slowrunning"],
    # Group G — Presence + Digital wellness + Trust
    ["digitaldetox", "presentmoment", "selfawareness"],
    # Group H — Fermentation deep + Gut
    ["lactofermentation", "probiotics", "healthygut"],
    # Group I — Nature + Grounding + Earthing
    ["earthing", "grounding", "backtonature"],
    # Group J — AI + Wellness tech + Unique angle
    ["wellnesstech", "aicreator", "consciousai"],
]

# Engagement limits per session (conservative to avoid detection)
LIMITS = {
    "likes": 20,
    "follows": 10,
    "comments": 5,
    "delay_min_sec": 15,   # Minimum delay between actions
    "delay_max_sec": 45,   # Maximum delay between actions
    "scroll_pause_min": 3,  # Min pause while scrolling
    "scroll_pause_max": 8,  # Max pause while scrolling
    "session_duration_min": 12,  # Min session in minutes
    "session_duration_max": 18,  # Max session in minutes
}

# Comment templates — genuine, varied, in Oria's spirit (but not AS Oria)
# Organized by pillar so the right comments match the right content
COMMENT_TEMPLATES = {
    "nourishment": [
        "This is exactly what more people need to see.",
        "The simplicity of this is what makes it powerful.",
        "Saving this. Real food knowledge is underrated.",
        "Your gut knows the difference even when your taste buds don't.",
        "More of this, less processed everything.",
        "Nature figured this out millions of years ago. We just keep forgetting.",
        "The science behind fermentation is so much deeper than people realize.",
        "Two ingredients and patience. That's real medicine.",
        "Real food doesn't need a label. It just needs time.",
        "Your microbiome would thank you for this if it could talk.",
    ],
    "movement": [
        "This is the kind of movement that actually sticks.",
        "Slow and consistent beats fast and burned out. Every time.",
        "The body was designed for this. We just forgot.",
        "No ego, just movement. That's the whole point.",
        "More people need to hear that slower is actually better.",
        "2 million years of evolution agrees with this.",
        "The best workout is the one you'll actually do tomorrow too.",
        "Running slow changed everything for me. This is spot on.",
        "Movement should feel like freedom, not punishment.",
        "Your body already knows how to do this. Just let it.",
    ],
    "stillness": [
        "Needed this reminder today.",
        "The hardest part isn't the practice. It's sitting still long enough to start.",
        "Stillness isn't doing nothing. It's doing the most important thing.",
        "Five minutes of this changes the entire day. Not exaggerating.",
        "The noise is always there. The quiet has to be chosen.",
        "Breath is the one thing you can always come back to.",
        "This is the kind of content that actually changes habits.",
        "Most people skip the pause. That's where everything lives.",
        "Simple. Effective. How wellness should be.",
        "The mind needs this as much as the body needs movement.",
    ],
    "presence": [
        "We scroll to escape. Then wonder why we feel empty.",
        "Presence isn't a skill. It's what's left when you stop distracting yourself.",
        "Bookmarking this for later — which is ironic, I know.",
        "Real talk — this is underrated.",
        "The attention you give something is the most valuable thing you own.",
        "Less screen, more sky. Simple math.",
        "This deserves more attention. Pun intended.",
        "Being here is the whole practice. Everything else follows.",
        "One thing at a time. That's the revolution.",
        "Your nervous system needed to hear this.",
    ],
    "trust": [
        "The body already knows what to do. We just need to stop getting in the way.",
        "Self-trust is the foundation everything else is built on.",
        "You already know the answer. You just haven't been quiet enough to hear it.",
        "Intuition isn't woo. It's pattern recognition your conscious mind missed.",
        "This is the kind of honesty that builds real community.",
        "No guru needed. Just you, paying attention.",
        "Trust the process. But also — trust yourself to know when the process is wrong.",
        "The body sends signals constantly. Most people just stopped listening.",
        "This hit different. Saving it.",
        "Connection starts with being honest about where you are.",
    ],
}

# Flat list for backward compatibility
COMMENT_TEMPLATES_FLAT = [c for comments in COMMENT_TEMPLATES.values() for c in comments]

# Map hashtag groups to their primary pillar (for comment selection)
GROUP_PILLAR = {
    0: "nourishment",   # A — fermentation
    1: "movement",      # B — natural movement
    2: "stillness",     # C — meditation
    3: "nourishment",   # D — real food
    4: "trust",         # E — holistic
    5: "movement",      # F — functional fitness
    6: "presence",      # G — digital detox
    7: "nourishment",   # H — fermentation deep
    8: "presence",      # I — nature/grounding
    9: "trust",         # J — AI/wellness tech
}

DATA_DIR = Path("data/engagement")
LOG_FILE = DATA_DIR / "engagement_log.json"


def get_todays_hashtags():
    """Get today's hashtag group (rotates daily)."""
    day_of_year = datetime.now().timetuple().tm_yday
    group_idx = day_of_year % len(HASHTAG_GROUPS)
    return HASHTAG_GROUPS[group_idx]


def get_random_delay():
    """Get a human-like random delay in seconds."""
    return random.uniform(LIMITS["delay_min_sec"], LIMITS["delay_max_sec"])


def get_random_comments(n=5, pillar=None):
    """Get n random comment templates, optionally filtered by pillar."""
    if pillar and pillar in COMMENT_TEMPLATES:
        pool = COMMENT_TEMPLATES[pillar]
    else:
        pool = COMMENT_TEMPLATES_FLAT
    return random.sample(pool, min(n, len(pool)))


def generate_smart_comments(hashtags, n=5):
    """Generate contextual comments using Claude (if available)."""
    if not HAS_ANTHROPIC:
        print("Anthropic SDK not available. Using template comments.")
        return get_random_comments(n)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system="""You write genuine Instagram comments for a wellness-focused account.
Rules:
- Each comment is 1-2 sentences MAX
- Sound like a real person, not a bot
- Show genuine interest or add a small insight
- No emojis (or max 1 subtle one)
- No hashtags
- Vary the style: some appreciative, some adding insight, some asking a question
- Never say "nice post", "love this", "great content" or generic phrases
- Be specific enough to seem genuine but general enough to work on different posts""",
        messages=[{
            "role": "user",
            "content": f"Generate {n} unique, genuine comments I could leave on posts about: {', '.join(hashtags)}. One per line, no numbering."
        }]
    )
    comments = [line.strip() for line in response.content[0].text.strip().split("\n") if line.strip()]
    return comments[:n]


def get_engagement_plan():
    """Generate today's engagement plan."""
    hashtags = get_todays_hashtags()
    day_of_year = datetime.now().timetuple().tm_yday
    group_idx = day_of_year % len(HASHTAG_GROUPS)
    pillar = GROUP_PILLAR.get(group_idx, "nourishment")
    comments = get_random_comments(LIMITS["comments"], pillar)

    plan = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "hashtags": hashtags,
        "limits": LIMITS,
        "comments": comments,
        "steps": [
            f"1. Open Instagram, log in to @oria_naturithm",
            f"2. Search hashtag: #{hashtags[0]}",
            f"   - Scroll through top/recent posts",
            f"   - Like {LIMITS['likes'] // len(hashtags)} posts",
            f"   - Follow {LIMITS['follows'] // len(hashtags)} relevant accounts",
            f"   - Leave 1-2 genuine comments",
            f"3. Search hashtag: #{hashtags[1]}",
            f"   - Repeat: like, follow, comment",
            f"4. Search hashtag: #{hashtags[2]}",
            f"   - Repeat: like, follow, comment",
            f"5. Check @oria_naturithm notifications",
            f"   - Reply to any DMs or comments",
            f"6. Total session: ~{LIMITS['session_duration_min']}-{LIMITS['session_duration_max']} minutes",
        ]
    }
    return plan


def log_engagement(actions):
    """Log engagement session."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    log = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            log = json.load(f)

    log.append({
        "date": datetime.now().isoformat(),
        "actions": actions,
    })

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

    print(f"Logged to {LOG_FILE}")


def print_plan():
    """Print today's engagement plan."""
    plan = get_engagement_plan()

    print(f"\n{'='*50}")
    print(f"  ENGAGEMENT PLAN — {plan['date']}")
    print(f"{'='*50}\n")

    print(f"Target hashtags: {', '.join('#' + h for h in plan['hashtags'])}\n")
    print(f"Limits: {plan['limits']['likes']} likes, {plan['limits']['follows']} follows, {plan['limits']['comments']} comments\n")

    print("Steps:")
    for step in plan["steps"]:
        print(f"  {step}")

    print(f"\nPrepared comments:")
    for i, comment in enumerate(plan["comments"], 1):
        print(f"  {i}. \"{comment}\"")

    print()


def print_smart_comments():
    """Generate and print smart comments."""
    hashtags = get_todays_hashtags()
    print(f"\nGenerating comments for: {', '.join('#' + h for h in hashtags)}\n")
    comments = generate_smart_comments(hashtags)
    for i, comment in enumerate(comments, 1):
        print(f"  {i}. \"{comment}\"")
    print()


def main():
    if "--plan" in sys.argv:
        print_plan()
    elif "--comments" in sys.argv:
        print_smart_comments()
    else:
        print_plan()
        print("Use --comments to generate AI-powered comments")
        print("Use Playwright MCP through Claude Code for automated engagement")


if __name__ == "__main__":
    main()
