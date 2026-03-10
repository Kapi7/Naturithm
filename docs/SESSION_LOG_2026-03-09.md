# Session Log — March 9, 2026

## What We Built Today

### Brand Foundation (from earlier session)
- Set up Meta Business Manager with system user token (never-expires)
- Created Facebook pages for both accounts
- Linked Instagram accounts via API
- Set bios and profile pictures manually
- Built posting utilities (`agents/instagram.py`)
- Published 5 still photos to @naturithm7 (movement, god/nature, family, food, presence)
- Privacy policy page live via GitHub Pages

### Today's Session

#### 1. Improved Reel Production Pipeline
- **Text overlays**: Matched still photo style — Palatino font, white regular + sand bold italic for key lines, semi-transparent gradient band, subtle text shadow
- **Saved reusable compilation tool**: `tools/compile_reel.py`

#### 2. Chose Oria's Voice (LOCKED)
- Tested 20 Google Cloud TTS voices
- **Selected: en-US-Studio-O** — calm, clear, confident, good English
- Speaking rate: 0.92, pitch: -1.0
- Locked in `brand/BRAND_GUIDE.md`

#### 3. Audio Mixing System
- Background music from **Mixkit** (royalty-free, no attribution)
- **FFmpeg sidechain compression** for auto-ducking music under voice
- Settings: ratio 2.5:1, attack 500ms, release 1500ms, music volume 0.35
- Music fades in 1.5s, fades out 3s

#### 4. Produced & Published 4 Reels to @oria_naturithm

**Reel 1: Coconut** (Fruit Series)
- Music: Forest Treasure (Mixkit #138)
- Theme: "Nature designed the perfect hydration"
- IG: 18058363322413954 | FB: 697070580093975

**Reel 2: Fermented Cabbage** (How-To Series)
- Music: Serene View (Mixkit #443)
- Theme: "One ingredient. Four weeks. Billions of probiotics."
- Key point: cabbage releases its OWN water, no outside water needed
- IG: 18097052491956256 | FB: 796977939596605

**Reel 3: Banana** (Fruit Series)
- Music: Sleepy Cat (Mixkit #135)
- Theme: "You think you know the banana. You don't."
- IG: 18081764837197619 | FB: 1546716599745172

**Reel 4: Fermented Beet** (How-To Series)
- Music: Hope and Kindness (Mixkit #534)
- Theme: "Ancient medicine. In a jar."
- Recipe: Himalayan/Atlantic salt + apple cider vinegar brine, 3 weeks
- IG: 18099403187485937 | FB: 1457094279349273

#### 5. Brand Rules Locked
- Oria's voice: Studio O (Google TTS)
- Salt: always "Himalayan or Atlantic salt" — never generic
- Text overlays: white + sand bold italic, no green
- Music: sidechain ducked, Mixkit royalty-free
- All reel specs: 720x1280, 30fps, H.264, AAC, faststart

---

## Content Strategy Going Forward
- **Fruit Series** (@oria_naturithm): coconut ✓, banana ✓ → next fruits TBD
- **Fermentation How-To Series** (@oria_naturithm): cabbage ✓, beet ✓ → more fermentation recipes
- **@naturithm7**: brand/platform content (5 still photos posted)
- Let data from these 4 reels inform next content decisions

---

## Cost Breakdown — March 9, 2026

### Google Cloud — Veo 2.0 (Video Generation)
- ~31 video generations (5-6 seconds each)
- Veo pricing: ~$0.35 per second of generated video
- Total seconds: ~31 × 5.5s avg = ~170 seconds
- **Estimated: ~$60**

### Google Cloud — Text-to-Speech (Studio voices)
- ~44 synthesis calls
- Studio voices: $0.016 per 100 characters
- ~44 clips × ~80 chars avg = ~3,500 characters
- **Estimated: ~$0.56**

### Google Cloud — Imagen (Still photos, previous session)
- ~15 image generations (including regenerations)
- Imagen pricing: ~$0.04 per image
- **Estimated: ~$0.60**

### Mixkit Music
- **Free** (royalty-free, no attribution required)

### Meta API
- **Free** (posting to own accounts)

### Total Estimated Cost
| Service | Cost |
|---------|------|
| Veo 2.0 (video gen) | ~$60 |
| Text-to-Speech | ~$0.56 |
| Imagen (images) | ~$0.60 |
| Music | $0 |
| Meta API | $0 |
| **TOTAL** | **~$61** |

*Note: Veo pricing may vary. Check Google Cloud billing console for actual charges.*

## Cost Optimization Plan (for next sessions)
- Use FREE stock video (Pexels/Pixabay) for generic shots (food, nature, spices)
- Only use Veo for unique Oria character shots (~1-2 per reel)
- Target: ~$2-4 per reel instead of ~$12
- Write better prompts to avoid re-generations
- Batch of 4 reels should cost ~$8-12 instead of ~$60
