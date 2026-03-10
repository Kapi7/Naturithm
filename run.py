#!/usr/bin/env python3
"""Naturithm Agent Team — Interactive CLI.

Usage:
    python run.py                    # Interactive mode
    python run.py "your idea here"   # Process a single idea
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agents.team import NaturithmTeam


def save_output(result: dict, output_dir: Path = Path("output")):
    """Save the team's output to a timestamped file."""
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = result["idea"][:40].lower().replace(" ", "_").replace("/", "-")
    filename = output_dir / f"{timestamp}_{slug}.md"

    with open(filename, "w") as f:
        f.write(f"# Naturithm Content Plan\n\n")
        f.write(f"**Idea:** {result['idea']}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Director's Brief\n\n{result['director_brief']}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Content Creator Output\n\n{result['content']}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Market Research\n\n{result['research']}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Copywriter Output\n\n{result['copy']}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Social Media Manager Output\n\n{result['social']}\n\n")
        f.write(f"---\n\n")
        f.write(f"## Final Plan (Oria's Synthesis)\n\n{result['final_plan']}\n")

    print(f"\nSaved to: {filename}")
    return filename


def interactive_mode(team: NaturithmTeam):
    """Run the interactive CLI."""
    print("""
╔══════════════════════════════════════════════════════╗
║           NATURITHM — Creative Agent Team            ║
║                   Directed by Oria                   ║
╚══════════════════════════════════════════════════════╝

Commands:
  idea <text>     — Process an idea through the full team
  ask <agent> <q> — Talk to a specific agent
                    (director, content, research, copy)
  reset           — Clear all conversation history
  quit            — Exit

""")

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        if user_input.lower() == "reset":
            team.reset_all()
            print("All agents reset.\n")
            continue

        if user_input.lower().startswith("ask "):
            parts = user_input[4:].split(" ", 1)
            if len(parts) < 2:
                print("Usage: ask <agent> <message>")
                continue
            agent_name, message = parts
            print(f"\n{team.ask_agent(agent_name, message)}\n")
            continue

        if user_input.lower().startswith("idea "):
            idea = user_input[5:]
        else:
            idea = user_input

        result = team.process_idea(idea)
        print(f"\n{'='*60}")
        print("  FINAL PLAN")
        print(f"{'='*60}\n")
        print(result["final_plan"])

        save = input("\nSave this plan? (y/n) > ").strip().lower()
        if save in ("y", "yes"):
            save_output(result)
        print()


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.")
        print("Create a .env file with: ANTHROPIC_API_KEY=your-key-here")
        sys.exit(1)

    team = NaturithmTeam(api_key)

    if len(sys.argv) > 1:
        idea = " ".join(sys.argv[1:])
        result = team.process_idea(idea)
        print(f"\n{'='*60}")
        print("  FINAL PLAN")
        print(f"{'='*60}\n")
        print(result["final_plan"])
        save_output(result)
    else:
        interactive_mode(team)


if __name__ == "__main__":
    main()
