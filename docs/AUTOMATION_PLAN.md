# Naturithm Automation Plan

## 1. Auto-Reply to Comments ✅ BUILT
**File:** `agents/auto_reply.py`
**How:** Polls Oria's recent posts every 30 min, generates replies in her voice using Claude Sonnet, posts via Meta API.
**Cost:** ~$0.001 per reply (Claude Sonnet)
**Run:** `python agents/auto_reply.py --loop` (or `--dry-run` to preview)

## 2. Optimal Posting Schedule (LATER)
- Pull follower activity data via IG Insights API
- Determine best posting windows
- Build scheduler that queues posts

## 3. Story Teasers for Every Reel (PLAN)
**Flow:**
1. After each Reel is published, auto-generate a Story teaser
2. Use the Reel's first frame or cover image
3. Add branded overlay: "New reel ↑" in Palatino
4. Post as Story via Meta API (Stories API supports images)
5. Story disappears after 24h = urgency

**Implementation:**
- Extract first frame from reel with ffmpeg
- Add branded text overlay with PIL
- Post via `POST /{ig_id}/media` with `media_type=STORIES`
- Can be added to the posting pipeline after each reel

## 4. Hashtag Rotation ✅ BUILT
**File:** `agents/oria_voice.py` → `HASHTAG_SETS` + `get_hashtag_set()`
**6 rotating sets:**
- A: Wellness broad
- B: Food / Nutrition
- C: Fermentation
- D: Nature / Mindfulness
- E: Movement / Body
- F: AI / Unique angle
Each set keeps `#naturithm #oria` as anchor tags.
Auto-rotates based on post number to avoid shadowban.

## 5. Engagement with Target Hashtags — HONEST ASSESSMENT
**Reality check:** The Instagram Graph API does NOT allow:
- Searching other users' posts
- Liking other users' posts
- Commenting on other users' posts
- Following/unfollowing

This can ONLY be done:
- **Manually** through the Instagram app
- **Third-party tools** (risk of ban — NOT recommended)

**What we CAN do instead:**
- Auto-reply to our own comments (builds engagement signals) ✅
- Use Instagram's native "suggested reels" by posting at peak times
- Encourage saves/shares in captions (algorithmic boost)
- Use the "share to story" CTA
- Engage manually 15 min/day on target hashtag posts (human touch)

**Recommended manual routine (15 min/day):**
1. Search 3 target hashtags on Instagram app
2. Like 10 recent posts per hashtag
3. Leave 3-5 genuine comments on posts that resonate
4. Follow 5-10 creators in the niche
5. Reply to any DMs

## 6. Analytics Tracker (LATER)
- Daily pull: reach, impressions, saves, shares, comments per post
- Weekly report auto-generated
- Track: fruit reels vs how-to reels performance
- Build with IG Insights API → save to JSON → generate summary
