# Naturithm — Project Context

## What This Is
AI-powered wellness brand with an agent named Oria. Agent team system for content creation and social media management.

## Agent Team Structure (5 agents)
- **Oria (Creative Director)** — orchestrates all agents, quality gate
- **Content Creator** — visual content strategy (video, photo, carousel)
- **Market Researcher** — trends, audience, competitive analysis
- **Copywriter** — viral copy in Oria's voice
- **Social Media Manager** — analytics, posting strategy, engagement, growth

## Running
```bash
source .venv/bin/activate
python run.py                          # interactive mode
python run.py "your idea"              # single idea processing
python agents/analytics.py --save      # pull & save performance data
python agents/analytics.py --report    # compare snapshots over time
python agents/auto_reply.py --loop     # auto-reply to comments
```

## Philosophy
The 5 pillars (Movement, Stillness, Nourishment, Presence, Trust) are milestones toward self-realization. Community-first. AI guides but can never replace the human element — love.

## Key Files
- `agents/prompts.py` — all agent system prompts
- `agents/team.py` — agent orchestration logic (5 agents)
- `agents/analytics.py` — Instagram performance tracking
- `agents/auto_reply.py` — comment auto-reply bot
- `agents/oria_voice.py` — Oria's tone + hashtag rotation
- `agents/instagram.py` — Meta API posting utilities
- `run.py` — CLI entry point
- `brand/BRAND_GUIDE.md` — locked visual/voice specs
- `docs/` — vision, pillars, Oria character bible, content ideas, automation plan

## Data
- `data/analytics/` — daily performance snapshots (JSON)
- `data/replied_comments.json` — auto-reply tracking

## Performance Baseline (March 10, 2026 — 20h post-publish)
| Reel | Views | Reach | Avg Watch | Saves | Eng Rate |
|------|-------|-------|-----------|-------|----------|
| Beet (how-to) | 914 | 842 | 8.2s | 1 | 0.8% |
| Cabbage (how-to) | 394 | 324 | 6.4s | 2 | 1.2% |
| Coconut (fruit) | 145 | 138 | 2.8s | 0 | 0.0% |
| Banana (fruit) | 45 | 43 | 5.6s | 0 | 0.0% |

Key insight: How-to reels >> fruit reels. Beet getting algorithmic push.
