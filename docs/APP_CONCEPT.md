# Naturithm App — Product Concept

## Overview

A wellness app built around the 5 pillars, powered by Oria (AI agent). Free to start, premium for depth.

## User Journey

### First Open
1. Welcome from Oria — introduces herself honestly ("I'm an AI wellness guide")
2. Quick assessment — NOT a quiz, more like a conversation:
   - "Which pillar speaks to you most right now?"
   - "What brought you here today?"
   - "How much time can you realistically give this per day?"
3. Personalized starting path based on answers
4. No account required to browse — account for saving progress

### Daily Experience

**Morning**: Oria's daily insight (push notification, optional)
- One thought related to today's pillar focus
- Example: "🧘 Stillness day: Before you check your phone, take 3 breaths. That's it. That's the practice."

**During Day**: Content library available
- Articles, audio guides, short exercises
- Filtered by pillar, difficulty, time available

**Anytime**: Chat with Oria
- Free tier: Limited conversations per day
- Premium: Unlimited, deeper conversations

**Evening**: Optional reflection
- "How was your day through the lens of the 5 pillars?"
- Quick journal entry (text or voice)

### Progression
- No gamification for its own sake (no streaks that create anxiety)
- Gentle tracking: "You've been consistent with movement this month"
- Milestones are internal, not badges: "You told me last week you couldn't sit still for 2 minutes. Today you did 10."
- Oria adapts content based on your journey

## Feature Set

### Free Tier
- Daily Oria insight (1 per day)
- Pillar explorer (browse content by pillar)
- 3 Oria conversations per day
- Basic habit tracking (did you move today? Y/N style)
- Community feed (read-only)

### Premium Tier ($9.99/month or $79.99/year)
- Unlimited Oria conversations
- Personalized wellness plan
- Structured courses:
  - "30 Days of Stillness"
  - "Movement Discovery"
  - "Nourish: Back to Basics"
  - "Digital Presence Reset"
  - "Trust Yourself: 21 Days"
- Audio content (guided meditations, movement guides)
- Journal with AI insights ("Here's what I notice about your patterns...")
- Progress analytics (gentle, not obsessive)

## Technical Architecture (Planned)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│   API Layer   │────▶│  AI Engine   │
│  (React/PWA) │     │  (Node/Python)│     │  (LLM/Oria)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   Database   │
                    │  (Postgres)  │
                    └─────────────┘
                           │
                    ┌──────┴──────┐
                    │  Content CMS │
                    │ (Headless)   │
                    └─────────────┘
```

### Stack Options
- **Frontend**: Next.js (PWA) → Native (React Native) later
- **Backend**: Node.js or Python FastAPI
- **AI**: OpenAI/Anthropic API with Oria system prompt + RAG for wellness content
- **Database**: PostgreSQL
- **Content**: Sanity.io or Strapi
- **Hosting**: Vercel (frontend) + Railway/Render (backend)

## Content Strategy

### Phase 1: Instagram (Now)
- Build Oria's voice and audience
- Test what resonates
- Gather early community

### Phase 2: Web MVP
- Landing page + waitlist
- Blog with pillar content
- Oria chatbot (web widget)

### Phase 3: App Launch
- PWA first (works on all devices)
- Core features: daily content, Oria chat, basic tracking

### Phase 4: Premium + Courses
- Structured programs
- Advanced Oria personalization
- Community features

---

*Build small, learn fast, stay honest.*
