"""Naturithm Content Approval Dashboard — clean rewrite.

Run: python3 dashboard/server.py
Open: http://localhost:8090
"""

import json, html, mimetypes
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8090
OUT_BASE = Path("/Users/kapi7/Naturithm/output")
DASH_DIR = Path("/Users/kapi7/Naturithm/dashboard")
REVIEWS_FILE = DASH_DIR / "reviews.json"

CONTENT = {
    "oria_naturithm": [
        {
            "id": "pancake_reel", "name": "Healthy Pancakes", "type": "Reel",
            "file": "pancake_reel/pancake_reel_v2.mp4", "schedule": "Day 1 \u2014 Mar 10",
            "caption": "Your kid doesn\u2019t know these are healthy. And that\u2019s the point.\n\n3 eggs. Almond flour. Half a banana. A pinch of baking soda. That\u2019s it.\n\nNo wheat. No sugar. No seed oils. No ingredients you can\u2019t pronounce.\n\nThey\u2019ll crack a little when you flip them \u2014 that\u2019s the almond flour. No gluten holding them together. That\u2019s a feature, not a bug.\n\nWhat your kid gets: protein, healthy fats, potassium, fiber. No blood sugar crash. No bloat. No \u201cI\u2019m hungry again\u201d 20 minutes later.\n\nWhat they think they\u2019re getting: pancakes.\n\nFeed them what their body recognizes. Not what a factory designed.\n\nRecipe:\n\u2014 3 eggs (your foundation)\n\u2014 2 tbsp almond flour\n\u2014 \u00bd banana, mashed\n\u2014 \u00bc tsp baking soda\n\u2014 Cook on medium. Flip gently. Serve with love.\n\nSave this for tomorrow morning.\n\n#healthypancakes #glutenfree #kidsbreakfast #cleanrecipe #realfood #nosugar #healthybreakfast #grainfree #oria #naturithm #feedthemwell #paleokids"
        },
        {
            "id": "garlic_reel", "name": "Fermented Garlic Honey", "type": "Reel",
            "file": "garlic_reel/garlic_reel_v2.mp4", "schedule": "Day 2 \u2014 Mar 11",
            "caption": "Two ingredients. One month. Ancient medicine on your shelf.\n\nHere\u2019s how to make fermented garlic honey \u2014 one of the most powerful natural remedies you can keep at home.\n\n\U0001f9c4 Crush (don\u2019t chop) fresh garlic cloves \u2014 this activates allicin, the compound that makes garlic a natural antibiotic.\n\n\U0001f36f Cover with raw honey only \u2014 not the processed kind. Raw honey has wild yeasts that make fermentation happen.\n\n\U0001f504 Seal the jar. Flip it daily. Wait one month.\n\nWhat you get: a living, antimicrobial, immune-boosting tonic. One spoonful when you feel something coming on. Or daily as prevention.\n\nNo pharmacy sells this. Nature already made the medicine. Be patient enough to let it work.\n\nSave this for when cold season hits.\n\n#fermentedgarlic #garlicinhoney #naturalmedicine #immuneboost #homeremedy #fermentation #rawgarlicbenefits #rawhoney #guthealth #oria #naturithm #ancestralhealth"
        },
        {
            "id": "carousel_running", "name": "Running Science", "type": "Carousel (8 slides)",
            "file": "carousel_running/slide_01_hook.png",
            "slides": [f"carousel_running/slide_{i:02d}_{s}.png" for i, s in enumerate(["hook","problem","science","body","high","born","start","cta"], 1)],
            "schedule": "Day 3 \u2014 Mar 12",
            "caption": "You\u2019re running too fast. Or not running at all. Both are the same mistake.\n\nHere\u2019s what nobody told you about running:\n\n1. Zone 2 training (60-70% max HR) is where the magic happens\n2. If you can\u2019t hold a conversation, slow down\n3. Your body makes its own bliss molecule after 30 min\n4. 2 million years of evolution designed you for this\n\nElite marathon runners train at easy pace 80% of the time. You should too.\n\nStart with 15 minutes. Walk if you need to. Just move.\n\nLace up. Go slow. Trust the process.\n\nSave this for your next run.\n\n#running #zone2training #runnersofinstagram #beginnerrunner #runningmotivation #slowrunning #endurance #borntorun #oria #naturithm #movement #runningtips"
        },
        {
            "id": "deodorant_reel", "name": "DIY Natural Deodorant", "type": "Reel",
            "file": "deodorant_reel/deodorant_reel_v2.mp4", "schedule": "Day 4 \u2014 Mar 13",
            "caption": "Aluminum. Parabens. Phthalates. You put this on your skin every single day.\n\nOr you could make your own.\n\nHere\u2019s the recipe:\n\U0001fad5 Melt: beeswax + coconut oil + shea butter\n\U0001f944 Mix in: arrowroot powder + pinch of baking soda\n\U0001f4a7 Add: tea tree + lavender oil (nature\u2019s antibacterials)\n\U0001fad9 Pour into jar. Let set 2 hours. Done.\n\n6 months of deodorant for less than one stick costs.\n\nIt won\u2019t stop you from sweating. Good. Your body sweats to cool itself and flush toxins. Aluminum stops that. This doesn\u2019t.\n\nYour skin absorbs what you put on it. Choose what nature made, not what a factory engineered.\n\n#naturaldeodorant #diyskincare #cleanbeauty #nontoxicliving #homemadedeodorant #naturalbeauty #zerowaste #oria #naturithm #skincare #toxinfree"
        },
        {
            "id": "addiction_reel", "name": "Understanding Addiction", "type": "Reel",
            "file": "addiction_reel/addiction_reel_v2.mp4", "schedule": "Day 5 \u2014 Mar 14",
            "caption": "Nobody chooses addiction. They choose relief.\n\nIt was never about the thing. It was about the feeling underneath.\n\nThe question isn\u2019t \u201cwhy the addiction.\u201d It\u2019s \u201cwhy the pain.\u201d\n\nWillpower doesn\u2019t fix a wound. You can\u2019t discipline your way out of something your nervous system chose to survive.\n\nThe opposite of addiction isn\u2019t sobriety. It\u2019s connection.\n\nYou are not your coping mechanism. You are the person underneath it. And that person deserves gentleness.\n\nIf this resonates, send it to someone who needs to hear it today.\n\n#addiction #mentalhealth #recovery #healing #gabormateé #connection #trauma #selfcompassion #oria #naturithm #innerwork #sobriety"
        },
    ],
    "naturithm7": [
        {
            "id": "naturithm_loop1", "name": "Wayne Dyer \u2014 Perspective", "type": "Loop (6s)",
            "file": "naturithm_loop1/naturithm_loop1_v2.mp4", "schedule": "Day 1 \u2014 Mar 10",
            "caption": "When you change the way you look at things, the things you look at change.\n\nRead that again.\n\nYour reality isn\u2019t fixed. It shifts the moment your perspective does.\n\nThe job you hate might be the lesson you needed.\nThe person who hurt you might be showing you where you\u2019re still wounded.\nThe obstacle in your way might be the way.\n\nNothing changed outside. Everything changed inside.\n\nThat\u2019s the shift.\n\nSave this. Come back when you forget.\n\n#perspective #mindshift #waynedyer #awakening #consciousness #selfrealization #innerwork #naturithm #presencematters #mindfulness"
        },
        {
            "id": "naturithm_duck", "name": "Duck Story \u2014 Let It Go", "type": "Story (39s)",
            "file": "naturithm_duck/naturithm_duck_v3.mp4", "schedule": "Day 2 \u2014 Mar 11",
            "caption": "Two ducks fight on a pond. Feathers fly. Water splashes.\n\nThen it\u2019s over. Each duck flaps its wings. Shakes off the energy. And floats away. Like nothing happened.\n\nNow imagine that duck had a human mind.\n\nIt would replay that fight for days. \u201cI can\u2019t believe he did that. He thinks he owns this pond.\u201d\n\nThe duck knew something we forgot:\n\nThe fight is over. Flap your wings. Let it go.\n\nBased on Eckhart Tolle \u2014 A New Earth\n\nIf you needed to hear this today, save it.\n\n#letitgo #eckharttolle #presence #mindfulness #innercalm #overthinking #consciousness #naturithm #anewearth #mentalhealth #healing"
        },
        {
            "id": "naturithm_loop3", "name": "Carl Jung \u2014 Shadow", "type": "Loop (6s)",
            "file": "naturithm_loop3/naturithm_loop3_v2.mp4", "schedule": "Day 3 \u2014 Mar 12",
            "caption": "What you see in others lives inside you.\n\nThe things that trigger you? They\u2019re mirrors.\n\nThe arrogance you can\u2019t stand in someone \u2014 is it because you\u2019ve buried your own?\nThe sensitivity you judge \u2014 is it because you were told yours was too much?\n\nJung called it the shadow. The parts of yourself you refuse to see.\n\nIt takes one to know one. Not as an insult. As a doorway.\n\nNext time someone triggers you, don\u2019t react. Ask: what in me is being reflected right now?\n\nThat question changes everything.\n\n#carljung #shadowwork #selfreflection #innerwork #projection #consciousness #personalgrowth #naturithm #healingjourney #knowthyself"
        },
        {
            "id": "naturithm_fence", "name": "Dog & Fence \u2014 Invisible Limits", "type": "Story (47s)",
            "file": "naturithm_fence/naturithm_fence_v3.mp4", "schedule": "Day 4 \u2014 Mar 13",
            "caption": "There\u2019s a dog wearing a collar. Around the yard, an invisible fence.\n\nEvery time it gets close \u2014 the collar buzzes. So the dog learns: don\u2019t go near the edge.\n\nOver time, it forgets there\u2019s even a world beyond the yard. Its whole life shrinks to the size of what doesn\u2019t hurt.\n\nOne day, the dog walks toward the edge. The collar buzzes. It keeps walking.\n\nThe buzz gets louder. The pain gets sharper. Every part says stop.\n\nBut it takes one more step. And then \u2014 silence.\n\nThe field was always there. The collar couldn\u2019t stop it. Only the dog\u2019s belief in the collar could.\n\nWhat invisible fence are you still obeying?\n\nInspired by Michael Singer \u2014 The Untethered Soul\n\n#innerwork #selflimitation #fearoffailure #letgo #michaelsinger #consciousness #breakfree #naturithm #courage #healing"
        },
        {
            "id": "naturithm_loop5", "name": "Meditation \u2014 I Am Not My Thoughts", "type": "Loop (6s)",
            "file": "naturithm_loop5/naturithm_loop5_v2.mp4", "schedule": "Day 5 \u2014 Mar 14",
            "caption": "I am not my thoughts. I am the one watching them.\n\nThis one sentence can change your entire relationship with anxiety, fear, and overthinking.\n\nYou are not the voice in your head.\nYou are the awareness behind it.\n\nWhen a thought comes \u2014 you don\u2019t have to follow it. You can watch it. Like a cloud passing.\n\nThe mind will wander. That\u2019s its nature.\nYour job isn\u2019t to stop thinking.\nYour job is to notice when you\u2019re lost \u2014 and come back.\n\nAgain. And again. And again.\n\nThat\u2019s the practice. That\u2019s the freedom.\n\nStart with 5 minutes. Eyes closed. Just breathe. Just watch.\n\n#meditation #mindfulness #presence #innercalm #awareness #consciousness #breathe #naturithm #mentalhealth #letgo"
        },
    ],
}


def load_reviews():
    if REVIEWS_FILE.exists():
        try:
            return json.loads(REVIEWS_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_reviews(reviews):
    REVIEWS_FILE.write_text(json.dumps(reviews, indent=2))


def h(text):
    """HTML-escape text, but preserve newlines as <br>."""
    return html.escape(text).replace("\n", "<br>")


def build_card_html(item, reviews):
    """Build one content card as HTML string."""
    r = reviews.get(item["id"], {})
    vs = r.get("video_status", "pending")
    cs = r.get("caption_status", "pending")
    is_video = item["file"].endswith(".mp4")
    is_loop = "loop" in item.get("type", "").lower()
    has_slides = "slides" in item

    # Media section
    if has_slides:
        slides_html = ""
        for i, s in enumerate(item["slides"]):
            display = "block" if i == 0 else "none"
            slides_html += f'<img id="{item["id"]}-slide-{i}" src="/files/{s}" style="width:100%;height:100%;object-fit:contain;display:{display}">'
        dots = ""
        for i in range(len(item["slides"])):
            cls = " active" if i == 0 else ""
            dots += f'<button class="carousel-dot{cls}" onclick="event.stopPropagation();showSlide(\'{item["id"]}\',{i},{len(item["slides"])})">{i+1}</button>'
        media_inner = f'{slides_html}<div class="carousel-nav">{dots}</div>'
    elif is_video:
        loop_attr = ' loop' if is_loop else ''
        media_inner = f'''<video id="vid-{item["id"]}" preload="metadata" playsinline muted{loop_attr}>
            <source src="/files/{item["file"]}" type="video/mp4"></video>
            <div class="play-overlay" id="play-{item["id"]}" onclick="event.stopPropagation();playVideo('{item["id"]}')">&#9654;</div>'''
    else:
        media_inner = f'<img src="/files/{item["file"]}" style="width:100%;height:100%;object-fit:contain">'

    icon = {"approved": "\u2713", "rejected": "\u2717", "pending": "\u25cf"}
    preview = html.escape(item["caption"].split("\n")[0][:100]) + "..."

    return f'''<div class="card" id="card-{item["id"]}" onclick="selectItem('{item["id"]}')">
  <div class="card-media">
    {media_inner}
    <span class="type-badge">{html.escape(item["type"])}</span>
    <button class="expand-btn" onclick="event.stopPropagation();openLightbox('{item["id"]}')">\u26f6</button>
  </div>
  <div class="card-info">
    <div>
      <h3>{html.escape(item["name"])}</h3>
      <div class="schedule">{html.escape(item["schedule"])}</div>
      <div class="status-row" id="sr-{item["id"]}">
        <span class="status-tag {vs}"><span class="label">VIDEO</span> {icon[vs]} {vs}</span>
        <span class="status-tag {cs}"><span class="label">CAPTION</span> {icon[cs]} {cs}</span>
      </div>
      <div class="caption-preview">{preview}</div>
    </div>
  </div>
</div>'''


def generate_html():
    reviews = load_reviews()

    # Pre-build card HTML for each tab
    oria_cards = ""
    for item in CONTENT["oria_naturithm"]:
        oria_cards += build_card_html(item, reviews)

    nat_cards = ""
    for item in CONTENT["naturithm7"]:
        nat_cards += build_card_html(item, reviews)

    # Build JS data object (just id/caption/file/slides/type for lightbox + review)
    js_items = []
    for account, items in CONTENT.items():
        for item in items:
            r = reviews.get(item["id"], {})
            slides = "null"
            if item.get("slides"):
                slides = json.dumps(item["slides"])
            # Use JSON for caption to avoid any escaping issues
            caption_json = json.dumps(item["caption"])
            js_items.append(f'''"{item["id"]}":{{
                account:"{account}",
                name:{json.dumps(item["name"])},
                type:{json.dumps(item["type"])},
                file:{json.dumps(item["file"])},
                slides:{slides},
                caption:{caption_json},
                video_status:"{r.get("video_status","pending")}",
                caption_status:"{r.get("caption_status","pending")}",
                video_notes:{json.dumps(r.get("video_notes",""))},
                caption_notes:{json.dumps(r.get("caption_notes",""))}
            }}''')

    items_js = "{" + ",".join(js_items) + "}"

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Naturithm \u2014 Content Approval</title>
<style>
:root {{
    --sand: #c4956a; --sand-light: #d4a57a; --sand-dim: #9a7555;
    --bg: #1a1714; --bg-card: #2a2520; --border: #3a3530; --border-hover: #5a5550;
    --text: #e8e0d4; --text-dim: #8a7e72; --text-cap: #c8c0b4;
    --green: #5ab86a; --green-bg: rgba(90,184,106,.12); --green-border: rgba(90,184,106,.35);
    --red: #d45454; --red-bg: rgba(212,84,84,.12); --red-border: rgba(212,84,84,.35);
    --yellow: #dcaa40; --yellow-bg: rgba(220,170,64,.12); --yellow-border: rgba(220,170,64,.35);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Palatino',Georgia,serif; background:var(--bg); color:var(--text); min-height:100vh; }}
.header {{ background:var(--bg-card); padding:20px 40px; border-bottom:2px solid var(--sand); display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }}
.header h1 {{ font-size:26px; color:var(--sand); font-weight:400; letter-spacing:3px; text-transform:lowercase; }}
.stats {{ color:var(--text-dim); font-size:13px; display:flex; gap:12px; align-items:center; }}
.pill {{ padding:4px 10px; border-radius:12px; font-size:12px; font-weight:600; }}
.pill.approved {{ background:var(--green-bg); color:var(--green); border:1px solid var(--green-border); }}
.pill.pending {{ background:var(--yellow-bg); color:var(--yellow); border:1px solid var(--yellow-border); }}
.pill.rejected {{ background:var(--red-bg); color:var(--red); border:1px solid var(--red-border); }}
.tabs {{ display:flex; background:var(--bg-card); padding:0 40px; border-bottom:1px solid var(--border); }}
.tab {{ padding:14px 28px; cursor:pointer; color:var(--text-dim); border-bottom:3px solid transparent; font-size:15px; letter-spacing:.5px; user-select:none; }}
.tab:hover {{ color:var(--sand); }}
.tab.active {{ color:var(--sand); border-bottom-color:var(--sand); }}
.main {{ display:flex; height:calc(100vh - 110px); }}
.content-list {{ flex:1; overflow-y:auto; padding:24px 30px; }}
.tab-content {{ display:none; }}
.tab-content.active {{ display:block; }}
.review-panel {{ width:420px; min-width:420px; background:var(--bg-card); border-left:1px solid var(--border); overflow-y:auto; }}
.card {{ background:var(--bg-card); border-radius:10px; border:1px solid var(--border); margin-bottom:16px; cursor:pointer; display:flex; overflow:hidden; transition:border-color .2s; }}
.card:hover {{ border-color:var(--border-hover); }}
.card.selected {{ border-color:var(--sand); box-shadow:0 0 0 1px var(--sand); }}
.card-media {{ width:380px; min-width:380px; position:relative; background:#000; aspect-ratio:9/14; display:flex; align-items:center; justify-content:center; overflow:hidden; }}
.card-media video {{ width:100%; height:100%; object-fit:contain; cursor:pointer; }}
.card-media img {{ width:100%; height:100%; object-fit:contain; }}
.type-badge {{ position:absolute; top:10px; right:10px; background:rgba(196,149,106,.92); color:var(--bg); padding:3px 8px; border-radius:4px; font-size:11px; font-weight:700; }}
.expand-btn {{ position:absolute; bottom:10px; right:10px; background:rgba(0,0,0,.7); border:1px solid var(--border); color:var(--sand); width:32px; height:32px; border-radius:6px; cursor:pointer; font-size:16px; display:flex; align-items:center; justify-content:center; z-index:5; }}
.expand-btn:hover {{ background:var(--sand); color:var(--bg); }}
.play-overlay {{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,.35); cursor:pointer; z-index:4; font-size:48px; color:rgba(255,255,255,.85); }}
.play-overlay.hidden {{ display:none; }}
.card-info {{ flex:1; padding:18px 20px; display:flex; flex-direction:column; }}
.card-info h3 {{ color:var(--sand); font-size:17px; font-weight:400; margin-bottom:4px; }}
.schedule {{ color:var(--text-dim); font-size:13px; margin-bottom:14px; }}
.status-row {{ display:flex; gap:10px; flex-wrap:wrap; }}
.status-tag {{ display:inline-flex; align-items:center; gap:5px; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600; }}
.status-tag.approved {{ background:var(--green-bg); color:var(--green); border:1px solid var(--green-border); }}
.status-tag.pending {{ background:var(--yellow-bg); color:var(--yellow); border:1px solid var(--yellow-border); }}
.status-tag.rejected {{ background:var(--red-bg); color:var(--red); border:1px solid var(--red-border); }}
.status-tag .label {{ opacity:.7; text-transform:uppercase; font-size:10px; }}
.caption-preview {{ color:var(--text-dim); font-size:12px; line-height:1.5; margin-top:8px; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }}
.carousel-nav {{ position:absolute; bottom:10px; left:50%; transform:translateX(-50%); display:flex; gap:5px; z-index:5; }}
.carousel-dot {{ background:rgba(58,53,48,.8); border:none; color:var(--sand); width:24px; height:24px; border-radius:50%; cursor:pointer; font-size:11px; }}
.carousel-dot.active {{ background:var(--sand); color:var(--bg); }}
/* Review panel */
.rp-empty {{ display:flex; align-items:center; justify-content:center; height:100%; text-align:center; color:var(--text-dim); padding:40px; }}
.rp-header {{ padding:20px 24px; border-bottom:1px solid var(--border); }}
.rp-header h2 {{ color:var(--sand); font-size:18px; font-weight:400; }}
.rp-type {{ color:var(--text-dim); font-size:13px; margin-top:2px; }}
.rp-section {{ padding:20px 24px; border-bottom:1px solid var(--border); }}
.rp-section-title {{ color:var(--text-dim); font-size:11px; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:14px; }}
.rp-actions {{ display:flex; gap:10px; margin-bottom:10px; }}
.rp-btn {{ flex:1; padding:10px 14px; border-radius:8px; border:1px solid var(--border); background:transparent; color:var(--text); cursor:pointer; font-family:inherit; font-size:13px; display:flex; align-items:center; justify-content:center; gap:6px; }}
.rp-btn.approve {{ border-color:var(--green-border); color:var(--green); }}
.rp-btn.approve:hover,.rp-btn.approve.active {{ background:var(--green-bg); border-color:var(--green); }}
.rp-btn.reject {{ border-color:var(--red-border); color:var(--red); }}
.rp-btn.reject:hover,.rp-btn.reject.active {{ background:var(--red-bg); border-color:var(--red); }}
.rp-notes {{ margin-top:12px; display:none; }}
.rp-notes.visible {{ display:block; }}
.rp-notes textarea {{ width:100%; min-height:80px; background:var(--bg); border:1px solid var(--border); border-radius:8px; color:var(--text); padding:12px; font-family:inherit; font-size:13px; line-height:1.5; resize:vertical; }}
.rp-notes textarea:focus {{ outline:none; border-color:var(--sand-dim); }}
.rp-caption {{ background:var(--bg); border-radius:8px; padding:16px; font-size:13px; line-height:1.65; color:var(--text-cap); white-space:pre-wrap; max-height:280px; overflow-y:auto; border:1px solid var(--border); margin-bottom:12px; }}
.copy-btn {{ background:transparent; color:var(--sand); border:1px solid var(--sand-dim); padding:8px 16px; border-radius:6px; cursor:pointer; font-size:12px; font-family:inherit; font-weight:600; }}
.copy-btn:hover {{ background:var(--sand); color:var(--bg); }}
/* Lightbox */
.lightbox {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.92); z-index:1000; align-items:center; justify-content:center; cursor:pointer; }}
.lightbox.open {{ display:flex; }}
.lightbox video,.lightbox img {{ max-height:90vh; max-width:90vw; object-fit:contain; border-radius:8px; }}
.lightbox .close-lb {{ position:absolute; top:20px; right:30px; color:var(--text); font-size:32px; cursor:pointer; background:none; border:none; z-index:1001; }}
/* Toast */
.toast {{ position:fixed; bottom:30px; left:50%; transform:translateX(-50%) translateY(80px); background:var(--bg-card); border:1px solid var(--green-border); color:var(--green); padding:12px 24px; border-radius:8px; font-size:14px; z-index:999; transition:transform .3s; pointer-events:none; }}
.toast.show {{ transform:translateX(-50%) translateY(0); }}
/* Scrollbars */
.content-list::-webkit-scrollbar,.review-panel::-webkit-scrollbar {{ width:6px; }}
.content-list::-webkit-scrollbar-thumb,.review-panel::-webkit-scrollbar-thumb {{ background:var(--border); border-radius:3px; }}
@media (max-width:900px) {{
    .main {{ flex-direction:column; height:auto; }}
    .review-panel {{ width:100%; min-width:0; border-left:none; border-top:1px solid var(--border); }}
    .card {{ flex-direction:column; }}
    .card-media {{ width:100%; min-width:0; }}
}}
</style>
</head>
<body>

<div class="header">
    <h1>naturithm</h1>
    <div class="stats" id="stats-bar"></div>
</div>

<div class="tabs">
    <div class="tab active" id="tab-oria" onclick="switchTab('oria')">@oria_naturithm (5)</div>
    <div class="tab" id="tab-nat" onclick="switchTab('nat')">@naturithm7 (5)</div>
</div>

<div class="main">
    <div class="content-list">
        <div class="tab-content active" id="list-oria">{oria_cards}</div>
        <div class="tab-content" id="list-nat">{nat_cards}</div>
    </div>
    <div class="review-panel" id="review-panel">
        <div class="rp-empty"><p>Select a content piece<br>to begin reviewing</p></div>
    </div>
</div>

<div class="lightbox" id="lightbox" onclick="closeLightbox()">
    <button class="close-lb" onclick="closeLightbox()">&times;</button>
    <div id="lb-content"></div>
</div>
<div class="toast" id="toast"></div>

<script>
var DATA = {items_js};
var selected = null;

// --- Video: only one plays at a time ---
function pauseAll() {{
    document.querySelectorAll('video').forEach(function(v) {{ v.pause(); v.muted = true; }});
    document.querySelectorAll('.play-overlay').forEach(function(o) {{ o.classList.remove('hidden'); }});
}}

function playVideo(id) {{
    pauseAll();
    var v = document.getElementById('vid-' + id);
    var o = document.getElementById('play-' + id);
    if (v) {{ v.muted = false; v.play(); }}
    if (o) o.classList.add('hidden');
}}

// Sync play overlay with video state
document.addEventListener('DOMContentLoaded', function() {{
    document.querySelectorAll('.card-media video').forEach(function(v) {{
        var id = v.id.replace('vid-', '');
        v.addEventListener('click', function(e) {{
            e.stopPropagation();
            if (v.paused) {{ playVideo(id); }} else {{ v.pause(); v.muted = true; document.getElementById('play-' + id).classList.remove('hidden'); }}
        }});
        v.addEventListener('ended', function() {{
            var o = document.getElementById('play-' + id);
            if (o && !v.loop) o.classList.remove('hidden');
        }});
    }});
    updateStats();
}});

// --- Carousel ---
function showSlide(cardId, idx, total) {{
    for (var i = 0; i < total; i++) {{
        var s = document.getElementById(cardId + '-slide-' + i);
        if (s) s.style.display = i === idx ? 'block' : 'none';
    }}
    document.querySelectorAll('#card-' + cardId + ' .carousel-dot').forEach(function(d, i) {{
        d.className = 'carousel-dot' + (i === idx ? ' active' : '');
    }});
}}

// --- Tab switching ---
function switchTab(tab) {{
    pauseAll();
    document.getElementById('tab-oria').className = 'tab' + (tab === 'oria' ? ' active' : '');
    document.getElementById('tab-nat').className = 'tab' + (tab !== 'oria' ? ' active' : '');
    document.getElementById('list-oria').className = 'tab-content' + (tab === 'oria' ? ' active' : '');
    document.getElementById('list-nat').className = 'tab-content' + (tab !== 'oria' ? ' active' : '');
}}

// --- Select & Review ---
function selectItem(id) {{
    document.querySelectorAll('.card.selected').forEach(function(c) {{ c.classList.remove('selected'); }});
    var card = document.getElementById('card-' + id);
    if (card) card.classList.add('selected');
    selected = id;
    renderPanel();
}}

function renderPanel() {{
    var panel = document.getElementById('review-panel');
    var d = DATA[selected];
    if (!d) {{
        panel.innerHTML = '<div class="rp-empty"><p>Select a content piece<br>to begin reviewing</p></div>';
        return;
    }}

    var icon = {{approved:'\u2713', rejected:'\u2717', pending:'\u25cf'}};
    var vActive = d.video_status === 'approved' ? ' active' : '';
    var vRActive = d.video_status === 'rejected' ? ' active' : '';
    var cActive = d.caption_status === 'approved' ? ' active' : '';
    var cRActive = d.caption_status === 'rejected' ? ' active' : '';
    var vNotesVis = d.video_status === 'rejected' ? ' visible' : '';
    var cNotesVis = d.caption_status === 'rejected' ? ' visible' : '';

    panel.innerHTML =
        '<div class="rp-header"><h2 id="rp-name"></h2><div class="rp-type" id="rp-type"></div></div>' +
        '<div class="rp-section">' +
            '<div class="rp-section-title">VIDEO / VISUAL REVIEW</div>' +
            '<div class="rp-actions">' +
                '<button class="rp-btn approve' + vActive + '" onclick="setStatus(\'video\',\'approved\')">\u2713 Approve</button>' +
                '<button class="rp-btn reject' + vRActive + '" onclick="setStatus(\'video\',\'rejected\')">\u2717 Reject</button>' +
            '</div>' +
            '<div class="rp-notes' + vNotesVis + '" id="video-notes">' +
                '<textarea id="video-notes-input" placeholder="What needs to change?" onblur="saveNotes()">' +
                '</textarea>' +
            '</div>' +
        '</div>' +
        '<div class="rp-section">' +
            '<div class="rp-section-title">CAPTION REVIEW</div>' +
            '<div class="rp-caption" id="rp-caption"></div>' +
            '<button class="copy-btn" onclick="copyCaption()">Copy Caption</button>' +
            '<div style="margin-top:14px">' +
                '<div class="rp-actions">' +
                    '<button class="rp-btn approve' + cActive + '" onclick="setStatus(\'caption\',\'approved\')">\u2713 Approve</button>' +
                    '<button class="rp-btn reject' + cRActive + '" onclick="setStatus(\'caption\',\'rejected\')">\u2717 Reject</button>' +
                '</div>' +
                '<div class="rp-notes' + cNotesVis + '" id="caption-notes">' +
                    '<textarea id="caption-notes-input" placeholder="Caption feedback..." onblur="saveNotes()">' +
                    '</textarea>' +
                '</div>' +
            '</div>' +
        '</div>';

    // Set text via textContent to avoid HTML entity issues
    document.getElementById('rp-name').textContent = d.name;
    document.getElementById('rp-type').textContent = d.type + ' \u00b7 ' + (d.schedule || '');
    document.getElementById('rp-caption').textContent = d.caption;
    document.getElementById('video-notes-input').value = d.video_notes || '';
    document.getElementById('caption-notes-input').value = d.caption_notes || '';
}}

function setStatus(type, status) {{
    var d = DATA[selected];
    if (!d) return;
    var key = type + '_status';
    d[key] = d[key] === status ? 'pending' : status;
    updateCardStatus(selected);
    updateStats();
    renderPanel();
    autoSave();
}}

function updateCardStatus(id) {{
    var d = DATA[id];
    var icon = {{approved:'\u2713', rejected:'\u2717', pending:'\u25cf'}};
    var row = document.getElementById('sr-' + id);
    if (row) {{
        row.innerHTML =
            '<span class="status-tag ' + d.video_status + '"><span class="label">VIDEO</span> ' + icon[d.video_status] + ' ' + d.video_status + '</span>' +
            '<span class="status-tag ' + d.caption_status + '"><span class="label">CAPTION</span> ' + icon[d.caption_status] + ' ' + d.caption_status + '</span>';
    }}
}}

function updateStats() {{
    var a=0, p=0, r=0, total=0;
    for (var id in DATA) {{
        total += 2;
        ['video_status','caption_status'].forEach(function(k) {{
            if (DATA[id][k] === 'approved') a++;
            else if (DATA[id][k] === 'rejected') r++;
            else p++;
        }});
    }}
    var bar = document.getElementById('stats-bar');
    bar.innerHTML = '<span class="pill approved">' + a + '/' + total + ' approved</span>' +
        (p > 0 ? '<span class="pill pending">' + p + ' pending</span>' : '') +
        (r > 0 ? '<span class="pill rejected">' + r + ' needs revision</span>' : '');
}}

function saveNotes() {{
    var d = DATA[selected];
    if (!d) return;
    var vn = document.getElementById('video-notes-input');
    var cn = document.getElementById('caption-notes-input');
    if (vn) d.video_notes = vn.value;
    if (cn) d.caption_notes = cn.value;
    autoSave();
}}

function autoSave() {{
    var d = DATA[selected];
    if (!d) return;
    var vn = document.getElementById('video-notes-input');
    var cn = document.getElementById('caption-notes-input');
    fetch('/api/review', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            id: selected,
            video_status: d.video_status,
            caption_status: d.caption_status,
            video_notes: vn ? vn.value : d.video_notes,
            caption_notes: cn ? cn.value : d.caption_notes
        }})
    }}).then(function() {{
        showToast('Saved');
    }}).catch(function() {{
        showToast('Error saving');
    }});
}}

function copyCaption() {{
    var d = DATA[selected];
    if (d) navigator.clipboard.writeText(d.caption).then(function() {{ showToast('Caption copied'); }});
}}

// --- Lightbox ---
function openLightbox(id) {{
    pauseAll();
    var d = DATA[id];
    var lb = document.getElementById('lightbox');
    var content = document.getElementById('lb-content');
    if (d.file.endsWith('.mp4')) {{
        var loop = d.type.toLowerCase().indexOf('loop') !== -1 ? ' loop' : '';
        content.innerHTML = '<video controls autoplay playsinline' + loop + ' onclick="event.stopPropagation()"><source src="/files/' + d.file + '" type="video/mp4"></video>';
    }} else if (d.slides) {{
        var idx = 0;
        var slides = d.slides;
        content.innerHTML = '<img id="lb-img" src="/files/' + slides[0] + '" onclick="event.stopPropagation()">';
        document.getElementById('lb-img').addEventListener('click', function() {{
            idx = (idx + 1) % slides.length;
            this.src = '/files/' + slides[idx];
        }});
    }} else {{
        content.innerHTML = '<img src="/files/' + d.file + '">';
    }}
    lb.classList.add('open');
    selectItem(id);
}}

function closeLightbox() {{
    var lb = document.getElementById('lightbox');
    var v = lb.querySelector('video');
    if (v) v.pause();
    lb.classList.remove('open');
}}

document.addEventListener('keydown', function(e) {{ if (e.key === 'Escape') closeLightbox(); }});

function showToast(msg) {{
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(function() {{ t.classList.remove('show'); }}, 2000);
}}
</script>
</body>
</html>'''


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html_content = generate_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode())

        elif self.path == "/api/reviews":
            reviews = load_reviews()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(reviews).encode())

        elif self.path.startswith("/files/"):
            file_path = OUT_BASE / self.path[7:]
            if file_path.exists():
                mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
                size = file_path.stat().st_size
                range_header = self.headers.get("Range")
                if range_header and mime and mime.startswith("video/"):
                    self._serve_range(file_path, mime, size, range_header)
                else:
                    self.send_response(200)
                    self.send_header("Content-Type", mime)
                    self.send_header("Content-Length", str(size))
                    if mime and mime.startswith("video/"):
                        self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            self.send_error(404)

    def _serve_range(self, file_path, mime, size, range_header):
        try:
            parts = range_header.replace("bytes=", "").strip().split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else size - 1
            end = min(end, size - 1)
            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(file_path, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(length))
        except Exception:
            self.send_error(416)

    def do_POST(self):
        if self.path == "/api/review":
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            try:
                data = json.loads(body)
                reviews = load_reviews()
                reviews[data["id"]] = {
                    "video_status": data.get("video_status", "pending"),
                    "caption_status": data.get("caption_status", "pending"),
                    "video_notes": data.get("video_notes", ""),
                    "caption_notes": data.get("caption_notes", ""),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
                save_reviews(reviews)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": True}).encode())
            except (json.JSONDecodeError, KeyError) as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    if not REVIEWS_FILE.exists():
        save_reviews({})
    server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print(f"\n  Naturithm Content Approval Dashboard")
    print(f"  http://localhost:{PORT}")
    print(f"  Press Ctrl+C to stop\n")
    server.serve_forever()
