#!/usr/bin/env python3
"""premium.py — the "premium" half of the auto-director (Round 14, 22 Nov 2026; study research/refs_<date>/REPORT.md).

autodirect.py calls  premium.plan(...)  after the camera/transition pass. It reads the script's sentences and decides, with no input from the creator:
  theme        a colour "set" (themes.json), rotated so the last two reels differ
  room/depth   room tint + glossy orbs + glass ribbon (behind / in front of the person; the person is the cut-out from person_matte.py)
  behind       the big WORD BEHIND THE HEAD: the frame-0 claim (replaces the old headline), numbers (outline), defined terms ("X ... phonebook hai")
  tier         two-tier captions (pill lead-in + hero line, key words in serif italic)
  cards        light frosted cards picked by what the sentence DOES:
                 question (not the CTA) -> search bar typing it · sequence ("phir / milte hi / convert / hit") -> node timeline of its tech terms
                 comparison ("nahi ... sirf", "ki jagah", "vs") -> checklist ✕/✓ · "kis par / kahan kam / sabse kam" (choosing) -> 3-stop slider
                 a big count ("hazaaron", "1000s", "lakhs") -> counter · "load / ho jaati / ready" -> loading bar · CTA "A ya B?" -> DM bubble with reply chips
  trans        shrink -> zoomBlur (no black void), one theme-coloured streak at the main idea change
  sfx          riser -> impact on every premium transition, whoosh on each word, typing ticks, check pops, DM tap
Every decision can be overridden by hand in <reel>/work/beats.json (same shape as plan["premium"]; keys given there replace the auto ones).
Density caps (from the study, scaled from 10 s demos to 30-40 s explainers): one card on screen at a time, cards >= 1.2 s apart,
words behind the head 3-5, at least two sentences left plain.
"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SI = os.path.expanduser("~/.cache/reel-studio/simple-icons/package/icons")
BRANDS = json.load(open(os.path.join(os.path.dirname(HERE), "brands.json"), encoding="utf-8"))
THEMES = {k: v for k, v in json.load(open(os.path.join(HERE, "themes.json"), encoding="utf-8")).items() if not k.startswith("_")}

TECH = re.compile(r"^(dns|ip|ips|server|servers|load|balancer|browser|api|apis|cache|cdn|database|db|request|requests|response|packet|packets|router|tcp|http|https|url|domain|"
                  r"website|internet|cloud|kafka|redis|queue|token|tokens|model|agent|ai|llm|gpu|cpu|ram|code|app|apps|data|network|wifi|chrome|brave|google|"
                  r"netflix|swiggy|zomato|amazon|youtube|instagram|whatsapp|backend|frontend|latency|bandwidth|key|hash|index|shard|replica|node|cluster)$", re.I)
NUMTOK = re.compile(r"^\d[\d,.]*%?$")
BIGCOUNT = re.compile(r"\b(hazaar\w*|hazaron|thousands?|lakhs?|crores?|millions?|billions?)\b", re.I)
SEQ = re.compile(r"\b(phir|milte hi|convert|hit|bhej\w*|forward|then|after|uske baad|pehle)\b", re.I)
CMP = re.compile(r"(\bnahi\b.*\bsirf\b|\bki jagah\b|\bvs\b|\bversus\b|\binstead\b|\bnot\b.*\bbut\b)", re.I)
CHOOSE = re.compile(r"\b(kis par|kis server|kahan kam|sabse kam|least|kam hai|choose|chun\w*|best one)\b", re.I)
LOADED = re.compile(r"\b(load ho|ho jaati|ho jata|ready|open ho|khul)\w*", re.I)
DEFINE = re.compile(r"\b(samjho|matlab|yaani|ki tarah|jaisa|jaise|is like|means)\b", re.I)
OPTS = re.compile(r"\b([A-Z][\w+#.]*)\s+(?:ya|or|vs)\s+([A-Z][\w+#.]*)\b")
FILL = {"tumhe", "tumhein", "pata", "hai", "dekho", "samjho", "toh", "aur", "ki", "ka", "ke", "ko", "mein", "se", "hi", "ye", "yeh", "jo", "basically", "phir", "ek"}


GENERIC = {"internet", "website", "websites", "request", "computer", "basically", "actually", "matlab", "cheez", "cheezein", "system", "logon", "logo", "tumhari", "humare"}


def clean(t):
    return re.sub(r"[^\w%+#.'-]", "", t).strip(".'")


def terms(words):
    """tech terms of a sentence in spoken order, multi-word ones merged ("Load Balancer")"""
    out, prev = [], None
    for w in words:
        c = clean(w[0])
        if not c:
            prev = None; continue
        if TECH.match(c) or (c[:1].isupper() and c.lower() not in FILL and w is not words[0] and len(c) > 1):
            if prev is not None and out and prev == len(out) - 1 and len(out[-1]["text"].split()) < 2 and c[:1].isupper() and out[-1]["text"][:1].isupper() and not out[-1]["text"].isupper():
                out[-1] = dict(text=out[-1]["text"] + " " + c, t=out[-1]["t"])
            else:
                out.append(dict(text=c, t=w[1]))
            prev = len(out) - 1
        else:
            prev = None
    seen, uniq = set(), []
    for x in out:
        k = x["text"].lower()
        if k not in seen:
            seen.add(k); uniq.append(x)
    return uniq


ICONS = {"website": "www", "web": "www", "browser": "⌘", "dns": "DNS", "ip": "IP", "server": "▤", "servers": "▤", "load balancer": "⚖", "balancer": "⚖", "cache": "⚡", "database": "DB", "request": "→", "data": "{}", "api": "API", "cdn": "CDN", "user": "☺"}


def cap1(t):
    return t[:1].upper() + t[1:] if t and not t[:1].isupper() else t


def icon(t):
    return ICONS.get(t.lower(), t.upper() if len(t) <= 3 else t[:1].upper())


def brand(word):
    """brands.json word -> {slug, hex, label, d (svg path)} or None"""
    b = BRANDS.get(re.sub(r"[^a-z0-9]", "", word.lower()))
    f = os.path.join(SI, b[0] + ".svg") if b else ""
    if not b or not os.path.exists(f):
        return None
    m = re.search(r' d="([^"]+)"', open(f, encoding="utf-8").read())
    return dict(slug=b[0], hex=b[1].lstrip("#"), label=b[2], d=m.group(1)) if m else None


def pick_theme(script, recent, forced=None):
    if forced in THEMES:
        return forced
    warm = re.search(r"\b(career|job|salary|manager|interview|resign|story|zindagi|mistake|lesson|mentor|burnout)\b", script, re.I)
    order = ["violet_studio", "chrome_night", "lime_studio"] + (["warm_gold"] if warm else [])
    if warm and not re.search(r"\b(server|dns|api|database|cache|request)\b", script, re.I):
        order = ["warm_gold"] + order[:-1]
    return next((t for t in order if t not in recent[-2:]), order[0])


# energetic accents (the creator 22 Nov 2026: "every video its own colour, based on the script and the video; mostly energetic; not purple everywhere")
ACCENTS = {"yellow": ("#ffd23f", 47), "lime": ("#c6ff3d", 78), "cyan": ("#2fd8ff", 193), "coral": ("#ff5a36", 11),
           "orange": ("#ff8a1f", 28), "pink": ("#ff3d8b", 336), "mint": ("#2de2a6", 160), "violet": ("#9b7bff", 258)}
MOOD = [(r"\b(galat|mistake|wrong|danger|hack|scam|risk|fail|crash|warning|stop|mat karo|bug|leak|attack)\b", ("coral", "orange", "pink")),
        (r"\b(ai|model|agent|llm|future|gpt|claude|robot|automation)\b", ("cyan", "lime", "violet")),
        (r"\b(money|salary|paisa|rupees?|crore|lakh|growth|career|job|interview|hike)\b", ("lime", "mint", "yellow")),
        (r"\b(server|dns|database|api|cache|request|network|internet|website|browser|code|system)\b", ("yellow", "cyan", "lime"))]


def hue_dist(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def footage_palette(video, hair=850):
    """3 frames of the cut -> the room's mean hue/saturation/luma (rows above the hair) and the hues of its saturated details (lights, chair trim)"""
    import colorsys, subprocess
    out = []
    try:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip() or 10)
        for f in (0.2, 0.5, 0.8):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{dur * f:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=54:96", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            out.append(raw)
    except Exception:
        return None
    rows = max(1, int(96 * hair / 1920))
    sx = sy = sat_sum = lum = n = 0
    hot = {}
    import math
    for raw in out:
        for i in range(0, min(len(raw), 54 * rows * 3), 3):
            r, g, b = raw[i] / 255, raw[i + 1] / 255, raw[i + 2] / 255
            h, l, sa = colorsys.rgb_to_hls(r, g, b)
            sx += math.cos(2 * math.pi * h) * sa; sy += math.sin(2 * math.pi * h) * sa; sat_sum += sa; lum += l; n += 1
            if sa > 0.45 and 0.25 < l < 0.85:
                k = int(h * 360) // 30 * 30; hot[k] = hot.get(k, 0) + 1
    if not n:
        return None
    return dict(hue=round((math.degrees(math.atan2(sy, sx)) + 360) % 360), sat=round(sat_sum / n, 3), luma=round(lum / n, 3),
                details=[k + 15 for k, c in sorted(hot.items(), key=lambda x: -x[1]) if c >= 3][:4])


def pick_accent(pal, script, recent=()):
    """score every energetic accent: contrast with the room hue (counts more when the room is colourful), harmony with the room's own saturated details,
    the script's mood, and a small penalty for the last two reels' accents"""
    mood = []
    for rx, names in MOOD:
        if re.search(rx, script, re.I):
            mood += [n for n in names if n not in mood]
    best = None
    for name, (hexv, h) in ACCENTS.items():
        sc = 0.0
        if pal:
            sc += (0.25 + 1.2 * min(0.4, pal["sat"])) * hue_dist(h, pal["hue"]) / 180
            sc += 0.25 * any(hue_dist(h, d) <= 25 for d in pal["details"])
        sc += 0.4 * (1 - mood.index(name) / 3) if name in mood[:3] else 0
        sc -= 0.35 if name in list(recent)[-2:] else 0
        sc -= 0.3 if name == "violet" else 0          # the creator 22 Nov 2026: not purple by default
        if best is None or sc > best[0]:
            best = (round(sc, 3), name)
    return best[1]


def theme_from(accent_name):
    hexv, h = ACCENTS[accent_name]
    r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
    return dict(label=f"{accent_name} accent (from the footage + script)", accent=hexv, word=hexv, glow=f"rgba({r},{g},{b},.35)",
                tint_top="rgba(0,0,0,0)", tint_bot="rgba(0,0,0,0)", orb=hexv, orb2=hexv, rib1=hexv, rib2="#ffffff", ring=f"rgba({r},{g},{b},.28)",
                ok="#2de2a6", ink2="#14121f", word_style="block", music_moods=["upbeat", "bright", "funky"])


def layout(geo):
    """1080x1920 canvas rows. Face sits low in the creator's framing (hair top ~850), so the ceiling band holds cards, captions and the word."""
    hair = int(geo["hair_top_min"]) if geo else 800
    hair = max(560, min(1000, hair))
    cap_y = max(300, hair - 300)                 # two-tier caption block (pill + hero ~170 px) sits just above the hair
    card_top, card_bot = 285, cap_y - 16         # cards live above the captions, below the IG top UI zone
    return dict(hair=hair, cap_y=cap_y, card_top=card_top, card_h=max(160, card_bot - card_top))


def word_size(text, style):
    n = max(2, len(text))
    k = 0.47 if style in ("block", "chrome", "outline") else 0.46     # Anton glyph width / size
    return int(max(150, min(430, 840 / (k * n))))   # <= ~840 px wide: 60 px margins + room for the 6 % drift (PHONEBOOK clipped at 960)   # fills ~90 % of the width: the head has to cover part of it, or it reads as a caption


def plan(sents, words, geo, end, joins, trans, script, recent_themes, add_sfx, rnd, override=None, headline=None, forced=None, broll=None, video=None, graphics=False, beats=()):
    gtxt = re.sub(r"/\*.*?\*/|<!--.*?-->|//[^\n]*|<[^>]+>", " ", graphics, flags=re.S) if isinstance(graphics, str) else ""   # visible text only (no comments, no tags)
    shown = set(re.findall(r"[a-z0-9%]+", gtxt.lower()))   # words the scene graphics already draw
    CARDS = os.environ.get("PREMIUM_CARDS") == "1"     # 22 Nov 2026: generic frosted cards are OFF by default (the creator: "ugly"); the reel's own Sticker Pop scene tells the story
    L0 = layout(geo)
    pal = footage_palette(video, L0["hair"]) if video else None
    theme_id = forced if forced in ACCENTS else (forced if forced in THEMES else pick_accent(pal, script, recent_themes))
    T = THEMES[theme_id] if theme_id in THEMES else theme_from(theme_id)
    L = L0
    cta_q = next((s for s in reversed(sents[-3:]) if s["q"]), None)
    body = [s for s in sents if s is not cta_q and s["t1"] < end - 1.0]
    behind, cards, keys = [], [], []

    def add_word(t0, t1, text, style=None, kick=None):
        style = style or T["word_style"]
        if any(not (t1 <= b["t0"] + 0.1 or t0 >= b["t1"] - 0.1) for b in behind) or len(behind) >= 3:
            return False
        size = word_size(text, style)
        y = int(L["hair"] - size * 0.74)          # Anton caps fill ~0.72 em from ~0.1 em: the head covers only the lower ~25 % of the middle letters (0.58 hid "CO" in "1 SECOND")
        behind.append(dict(t0=round(t0, 2), t1=round(t1, 2), text=text if style == "serif" else text.upper(), style=style, kick=kick, y=y, size=size))
        add_sfx("whoosh", t0 - 0.12, 0.2, "word", True); add_sfx("impact", t0 + 0.08, 0.24, "word-hit", True)
        return True

    # 1) frame-0 claim as the word behind the head (replaces the old above-the-head headline)
    hook_end = min(2.6, (sents[1]["t1"] if len(sents) > 1 and sents[0]["t1"] < 1.2 else sents[0]["t1"]) + 0.2) if sents else 2.4
    if headline and headline.get("lines") and not headline.get("auto"):
        l1, l2 = (headline["lines"] + [""])[:2]
        if l2:
            add_word(0.0, hook_end, l2.rstrip("?!."), kick=l1)
    elif sents:
        hw = [w for s in sents[:2] for w in s["words"] if w[1] < 3.5]
        tm = next((w for w in hw if NUMTOK.match(clean(w[0]))), None) or next((dict(t=x["t"], text=x["text"]) for x in terms(hw)), None)
        if tm:
            txt0 = clean(tm[0]) if isinstance(tm, list) else tm["text"]
            add_word(0.0, hook_end, txt0, kick=" ".join(clean(w[0]) for w in sents[0]["words"][:4]) if len(sents[0]["words"]) <= 4 else None)
    # 2) per sentence: numbers / definitions -> word; what the sentence does -> card
    last_card_end = -9
    for s in body:
        ws, txt, tms = s["words"], s["text"], terms(s["words"])
        dur = s["t1"] - s["t0"]
        nums = [w for w in ws if NUMTOK.match(clean(w[0]))]
        card = None
        used = [c["kind"] for c in cards]
        ok = lambda k: used.count(k) < (2 if k == "nodes" else 1)
        first_q = s["q"] and s["t0"] > 3.0 and not any(c["kind"] == "circle" for c in cards) and dur >= 2.0
        t0c = max(s["t0"] - 0.05, last_card_end + (0.3 if first_q else 1.2))   # the iris is a full-frame move, not another card: a short gap is enough
        if t0c > s["t1"] - 1.2 or s["t0"] < 2.4:
            t0c = None
        brs = []
        for w in ws:
            b = brand(clean(w[0]))
            if b and b["slug"] not in [x["slug"] for x in brs]:
                brs.append(dict(b, t=round(w[1] - 0.05, 2)))
        if t0c is not None and CARDS:
            if len(brs) >= 2 and ok("logos"):
                card = dict(kind="logos", items=brs[:4])
            elif broll and ok("photos") and re.search(r"\b(dekho|example|jaise|ye|yeh|look|see)\b", txt, re.I):
                card = dict(kind="photos", items=broll[:3])
            elif first_q and geo and not nums:
                card = dict(kind="circle", cy=int(geo["target"]["center"]), r=int(geo["target"]["face_h"] * 0.62),
                            text=" ".join(clean(w[0]) for w in ws)[:44].upper())
            elif CMP.search(txt) and len(tms) >= 1 and ok("checklist"):
                cw = [clean(w[0]) for w in ws]
                lo = [c.lower() for c in cw]
                ni, si = (lo.index("nahi") if "nahi" in lo else -1), (lo.index("sirf") if "sirf" in lo else -1)
                neg = cw[ni - 1] if ni > 0 else (tms[0]["text"] if len(tms) > 1 else "")
                pos = " ".join(cw[si + 1: si + 3]) if si >= 0 else tms[-1]["text"]
                head = [c for c in cw[:max(0, ni - 1)] if c and c.lower() not in FILL][:2]
                if neg and pos:
                    card = dict(kind="checklist", title=(" ".join(head).capitalize() + " <em>samajhta</em>") if head else "Asli <em>sach</em>",
                                items=[dict(text=neg.capitalize(), ok=False, t=None), dict(text=pos, ok=True, t=None)])
            elif LOADED.search(txt) and ok("load") and not ok("slider"):
                card = dict(kind="load", title=f"{cap1(tms[0]['text'] if tms else 'Page')} <em>loading</em>", label="", done="Loaded")
            elif CHOOSE.search(txt) and ok("slider"):
                noun = next((x["text"].rstrip("s") for x in tms if x["text"].lower().startswith(("server", "node", "replica", "shard"))), tms[0]["text"].rstrip("s") if tms else "Option")
                ask = " ".join(clean(w) for w in txt[CHOOSE.search(txt).start():].split()[:5])
                card = dict(kind="slider", title=ask.capitalize().replace(noun.lower(), f"<em>{noun.lower()}</em>", 1) + "?", items=[cap1(f"{noun} 1"), cap1(f"{noun} 2"), cap1(f"{noun} 3")], pick=2)
            elif SEQ.search(txt) and len(tms) >= 2 and ok("nodes"):
                items = [dict(text=cap1(x["text"]), t=round(max(t0c + 0.1, x["t"] - 0.05), 2), icon=icon(x["text"])) for x in tms[:3]]
                card = dict(kind="nodes", items=items)
            elif BIGCOUNT.search(txt) and ok("counter"):
                card = dict(kind="counter", to=1000, suffix="+", label=BIGCOUNT.search(txt).group(0).capitalize() + " servers" if "server" in txt.lower() else "")
            elif LOADED.search(txt) and ok("load"):
                card = dict(kind="load", title=f"{cap1(tms[0]['text'] if tms else 'Page')} <em>loading</em>", label="", done="Loaded")
            elif s["q"] and tms and ok("search"):
                q = " ".join(x["text"] for x in tms[:3])
                card = dict(kind="search", query=(q + " kaise?")[:30])
        if card and card["kind"] == "nodes" and not any(c["kind"] == "split" for c in cards) and dur >= 3.0:
            card = dict(kind="split", inner=card, panel_h=L["cap_y"] - 20)
        if card:
            t1c = round(min(s["t1"] + 0.25, t0c + max(1.8, min(4.6, dur + 0.3)), end - 0.5), 2)
            card.update(t0=round(t0c, 2), t1=t1c, y=L["card_top"], h=L["card_h"])
            cards.append(card); last_card_end = t1c
            add_sfx("pop", t0c - 0.03, 0.18, "card", False)
            if card["kind"] == "logos":
                for it in card["items"][1:]:
                    add_sfx("pop", it["t"], 0.16, "logo", False)
            if card["kind"] == "circle":
                add_sfx("whoosh", card["t0"] - 0.05, 0.18, "iris", True)
            if card["kind"] == "search":
                for k in range(0, min(len(card["query"]), 24), 3):
                    add_sfx("tick", t0c + 0.35 + k / 18 - 0.02, 0.1, "type", True)
            if card["kind"] == "checklist":
                for i in range(len(card["items"])):
                    add_sfx("success" if card["items"][i]["ok"] else "negation", t0c + 0.5 + i * 0.45, 0.14, "check", False)
            if card["kind"] in ("nodes", "split"):
                for it in (card.get("inner") or card)["items"][1:]:
                    add_sfx("tick", it["t"] + 0.15, 0.14, "node", False)
        # words behind the head: numbers anywhere, defined terms ("Samjho, DNS ... phonebook hai")
        if nums and not graphics:
            w = nums[0]; add_word(w[1] - 0.05, min(s["t1"] + 0.1, w[1] + 2.2), clean(w[0]))
        elif DEFINE.search(txt) and (tms or ws):
            fresh = [x for x in tms if x["text"].lower() not in shown and x["text"].lower() not in GENERIC]
            if not fresh:            # the scene already draws the term: promote the strongest other noun of the sentence (longest non-filler word)
                cand = [w for w in ws if len(clean(w[0])) >= 5 and clean(w[0]).lower() not in FILL and clean(w[0]).lower() not in GENERIC and clean(w[0]).lower() not in shown and not DEFINE.search(w[0])]
                fresh = [dict(text=clean(max(cand, key=lambda w: len(clean(w[0])))[0]), t=max(cand, key=lambda w: len(clean(w[0])))[1])] if cand else []
            if fresh:
                add_word(fresh[0]["t"] - 0.05, max(fresh[0]["t"] + 1.4, min(s["t1"] + 0.1, fresh[0]["t"] + 2.4)), fresh[0]["text"])   # >= 1.4 s on screen
        for x in tms[:2]:
            keys.append([round(x["t"], 2), round(x["t"] + 0.6, 2)])
    # 3) CTA question -> DM bubble with the options he names ("Chrome ya Brave")
    cta_card = None
    if cta_q and CARDS:
        m = OPTS.search(cta_q["text"])
        opts = [m.group(1), m.group(2)] if m else ["YES", "NO"]
        icons = [brand(o) for o in opts]
        cta_card = dict(kind="dm", question=re.sub(r"^(ab\s+)?comments?\s+mein\s+batao,?\s*", "", cta_q["text"], flags=re.I)[:60], options=opts, icons=[dict(d=i["d"], hex=i["hex"]) if i else None for i in icons], pick=0,
                        t0=round(cta_q["t0"] - 0.1, 2), t1=round(min(end, cta_q["t1"] + 0.6), 2), y=L["card_top"], h=L["card_h"] + 60)
        cta_card["t_tap"] = round(min(cta_card["t1"] - 0.4, cta_card["t0"] + 1.6), 2)
        cards.append(cta_card)
        add_sfx("notif", cta_card["t0"], 0.2, "dm", True); add_sfx("click", cta_card["t_tap"] - 0.03, 0.24, "dm-tap", True); add_sfx("success", cta_card["t_tap"] + 0.08, 0.2, "dm-done", True)
    hero = next((b for b in behind if b["style"] == "outline"), None) or (behind[1] if len(behind) > 1 else None)
    if hero and os.environ.get("PREMIUM_PARTICLES") == "1":   # off by default (22 Nov 2026: read as flashy)
        hero["particles"] = True
    # 4) transitions: shrink -> zoomBlur; the join nearest the "solution" start (first definition / 'samjho') becomes one streak
    ptrans = []
    sol = next((s["t0"] for s in sents if DEFINE.search(s["text"])), None)
    streak_j = min((t["t"] for t in trans), key=lambda j: abs(j - sol)) if sol and trans else None
    for t in trans:
        if t["type"] == "shrink":
            t["type"] = "zoomBlur"
        if t["type"] in ("zoomBlur", "streak"):
            ptrans.append(dict(t=t["t"], type=t["type"]))
            add_sfx("riser", t["t"] - 0.55, 0.16, "rise", True); add_sfx("impact", t["t"] - 0.02, 0.2, "impact", True)
    KIN = os.environ.get("KINETIC", "1") != "0"
    kin = None
    if KIN:                                          # Round 15: the kinetic track replaces the single words + captions
        cta_t0 = cta_q["t0"] - 0.1 if cta_q else end
        face = dict(cx=540, cy=int(geo["target"]["center"]), r=int(geo["target"]["face_h"] * 0.55)) if geo else None
        kin = kinetic(sents, words, L, end, cta_t0, add_sfx, beats=beats, face=face)
        kin.update(dark=0.42, hair=L["hair"])
        sfx_word = [b for b in behind]
        behind = []
        if cta_q:                                    # "Chrome ya Brave?" -> the two logos flank the head, VS above
            m = OPTS.search(cta_q["text"])
            its = [dict(brand(m.group(i)) or {}, label=m.group(i), t=round(next((w[1] for w in cta_q["words"] if clean(w[0]) == m.group(i)), cta_q["t0"]) - 0.05, 2)) for i in (1, 2)] if m else []
            if its and all(x.get("d") for x in its):
                kin["props"].append(dict(kind="versus", t0=its[0]["t"], t1=round(min(end - 0.1, cta_q["t1"] + 0.4), 2), items=its, vs_t=round(its[1]["t"] - 0.2, 2)))
                add_sfx("pop", its[0]["t"], 0.18, "vs", True); add_sfx("pop", its[1]["t"], 0.18, "vs2", True); add_sfx("impact", its[1]["t"] - 0.2, 0.18, "vs-hit", True)
    P = dict(theme=theme_id, theme_vars=T, palette=pal, layout=L, room=None, depth=None, glow=True, kinetic=kin,
             behind=behind, tier=None, cards=cards, trans=ptrans, music_moods=T["music_moods"])
    if override:
        P.update({k: v for k, v in override.items() if not k.startswith("_")})
    return P, (cta_card is not None)


# ======================= Round 15: kinetic depth track (the creator 22 Nov 2026: "learn what the references do") =======================
HSTOP = {"nahi", "nahin", "kam", "zyada", "sirf", "bas", "sabse", "bahut", "kabhi", "phir", "turant", "asli", "magic", "raaz", "basically"}
HINDI_NUM = {"ek": "1", "do": "2", "teen": "3", "char": "4", "chaar": "4", "paanch": "5", "das": "10", "sau": "100"}
UNITS = re.compile(r"^(second|seconds|sec|minute|minutes|ms|percent|gb|mb|lakh|crore|hazaar|million|billion|x)$", re.I)
MAPCUE = re.compile(r"\b(duniya|world|globe|country|desh|videsh|us|usa|america|india|europe|london)\b", re.I)
RACKCUE = re.compile(r"\b(servers?|hazaar\w*|load balancer|bheed)\b", re.I)
LOADCUE = re.compile(r"\b(load ho\w*|loading|screen par|khul)\b", re.I)
CONVCUE = re.compile(r"\b(naam|name)\b.*\b(ip|number)\b", re.I)
PLACES = {"us": ([-98, 39], "US"), "usa": ([-98, 39], "US"), "america": ([-98, 39], "US"), "europe": ([10, 50], "Europe"), "london": ([-0.1, 51.5], "London"),
          "india": ([78.9, 22], "India"), "japan": ([139, 36], "Japan"), "singapore": ([103.8, 1.3], "Singapore"), "dubai": ([55.3, 25.2], "Dubai")}   # lon, lat


def phrases_of(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        if (len(w) > 4 and w[4] == "/") or re.search(r"[.?!,]$", w[0]) or len(cur) >= 4 or i == len(words) - 1:
            out.append(cur); cur = []
    return out


def keyword(ph):
    """the phrase's big word: number (+ unit) > tech/brand pair ('Load Balancer', 'IP address') > tech/brand > tagged word"""
    cw = [clean(w[0]) for w in ph]
    for i, c in enumerate(cw):
        n = HINDI_NUM.get(c.lower()) if i + 1 < len(cw) and UNITS.match(cw[i + 1]) else None
        if NUMTOK.match(c) or n:
            txt = (n or c) + (" " + cw[i + 1] if i + 1 < len(cw) and UNITS.match(cw[i + 1]) else "")
            return txt, ph[i][1], i
    for i, c in enumerate(cw):
        if (TECH.match(c) or brand(c)) and c.lower() not in GENERIC:
            if i + 1 < len(cw) and (TECH.match(cw[i + 1]) or cw[i + 1].lower() in ("address", "balancer", "number")) and cw[i + 1].lower() not in GENERIC:
                return c + " " + cw[i + 1], ph[i][1], i
            return c, ph[i][1], i
    for i, w in enumerate(ph):
        if len(w) > 3 and w[3] and len(cw[i]) >= 4 and cw[i].lower() not in HSTOP and cw[i].lower() not in GENERIC:
            return cw[i], w[1], i
    return None, None, None


def kinetic(sents, words, L, end, cta_t0, add_sfx, beats=(), face=None):
    """the whole-reel word track + props. Bigs hold until the next big (<= 2.8 s), >= 0.9 s each; leads change per phrase."""
    phs = phrases_of(words)
    lines, bigs = [], []
    for ph in phs:
        if ph[0][1] >= cta_t0 - 0.05:
            break
        k, kt, ki = keyword(ph)
        root = lambda x: re.sub(r"s$", "", x.lower())
        if k and bigs and root(k) == root(bigs[-1]["big"]) and kt - bigs[-1]["t0"] < 4:
            k = None
        if k and (not bigs or kt - bigs[-1]["t0"] >= 0.9) and len(k) <= 14:
            if bigs:
                bigs[-1]["t1"] = round(min(bigs[-1]["t1"], kt - 0.06), 2)
            size = word_size(k, "block")
            bigs.append(dict(big=k.upper(), t0=round(kt - 0.04, 2), t1=round(min(kt + 2.0, cta_t0 - 0.1), 2), size=size, y=int(L["hair"] - size * 0.74), style="block"))
            bt = next((b for b in beats if kt - 0.1 <= b <= kt + 0.04), None)   # land on the music's beat when it is that close (speech still leads)
            if bt is not None:
                bigs[-1]["t0"] = round(bt - 0.02, 2)
            strong = bool(NUMTOK.match(k.split()[0]) or len(bigs) == 1)
            add_sfx("riser", bigs[-1]["t0"] - 0.34, 0.12, "kin-rise", False)
            add_sfx("impact" if strong else "hit_soft", bigs[-1]["t0"] + 0.02, 0.22 if strong else 0.18, "kin-hit", True)
    for b in bigs:                                   # strike: "X nahi, sirf Y" -> X struck right before Y lands
        pass
    for i, ph in enumerate(phs):
        t0 = ph[0][1]
        if t0 >= cta_t0 - 0.05:
            break
        t1 = phs[i + 1][0][1] - 0.03 if i + 1 < len(phs) else end
        big = next((b for b in bigs if b["t0"] - 0.1 <= t0 < b["t1"]), None)
        txt = " ".join(clean(w[0]) for w in ph if not (big and clean(w[0]).upper() in big["big"].split()) and not (big and HINDI_NUM.get(clean(w[0]).lower()) and HINDI_NUM[clean(w[0]).lower()] in big["big"]))
        if len(txt.split()) <= 1 and big:
            continue
        if lines and t0 - lines[-1]["t0"] < 0.5 and len(lines[-1]["lead"].split()) <= 2 and lines[-1]["lead_y"] == (int(big["y"] - 64) if big else int(L["hair"] - 210)):
            lines[-1]["lead"] += " " + txt; lines[-1]["t1"] = round(min(t1, cta_t0 - 0.05), 2)
            lines[-1]["words"] += [[clean(w[0]), round(w[1], 2)] for w in ph if clean(w[0]) and clean(w[0]) in txt.split()]; continue
        kept = [[clean(w[0]), round(w[1], 2)] for w in ph if clean(w[0]) and clean(w[0]) in txt.split()]
        lines.append(dict(lead=txt, words=kept, t0=round(t0 - 0.03, 2), t1=round(min(t1, cta_t0 - 0.05), 2), lead_y=int(big["y"] - 64) if big else int(L["hair"] - 210)))
    # strike pairs
    for s in sents:
        m = re.search(r"\b(\w+)\s+nahi\b.*\bsirf\b", s["text"], re.I)
        if m:
            neg = next((b for b in bigs if s["t0"] <= b["t0"] <= s["t1"]), None)
            w = next((w for w in s["words"] if clean(w[0]).lower() == m.group(1).lower()), None)
            if w and not (neg and neg["big"].lower().startswith(m.group(1).lower())):
                size = word_size(m.group(1), "block")
                nxt = next((b for b in bigs if b["t0"] > w[1]), None)
                bigs.append(dict(big=m.group(1).upper(), t0=round(w[1] - 0.04, 2), t1=round(nxt["t0"] - 0.02 if nxt else w[1] + 1.0, 2), size=size,
                                 y=int(L["hair"] - size * 0.74), style="block", strike=dict(t=round(w[1] + 0.22, 2))))
                add_sfx("scratch", w[1] + 0.2, 0.18, "strike", True)
    bigs.sort(key=lambda b: b["t0"])
    for a, b in zip(bigs, bigs[1:]):                 # one big word on screen at a time
        a["t1"] = round(min(a["t1"], b["t0"] - 0.06), 2)
    props = []
    for s in sents:
        if s["t0"] >= cta_t0 - 0.05:
            continue
        txt = s["text"]
        if MAPCUE.search(txt) and not any(p["kind"] == "map" and p["t1"] > s["t0"] for p in props):
            dest = next((PLACES[clean(w[0]).lower()] for w in s["words"] if clean(w[0]).lower() in PLACES and clean(w[0]).lower() != "india"), None)
            cue = next((w[1] for w in s["words"] if MAPCUE.search(clean(w[0]))), s["t0"] + 0.8)   # the arc launches ON the place / "duniya" word
            props.append(dict(kind="map", t0=round(max(s["t0"], cue - 0.6), 2), t1=round(s["t1"] + 0.1, 2), arc_t=round(cue - 0.05, 2), arc_d=1.0,
                              **({"to": dest[0], "labels": ["India", dest[1]]} if dest else {})))
            add_sfx("sparkle", s["t0"] + 0.35, 0.14, "map", False); add_sfx("whoosh", s["t0"] + 0.8, 0.14, "arc", False)
        if CONVCUE.search(txt) and not any(p["kind"] == "search" for p in props) and re.search(r"\b(website|site|convert)\b", txt, re.I):
            props.append(dict(kind="search", t0=round(s["t0"], 2), t1=round(s["t1"] + 0.3, 2), query="website.com", result="142.250.183.14", result_t=round(s["t1"] - 1.0, 2)))
            for k in range(0, 11, 2):
                add_sfx("tick", s["t0"] + 0.35 + k * 0.07, 0.1, "type", True)
            add_sfx("success", s["t1"] - 1.0, 0.16, "resolve", True)
        elif re.search(r"\bip\b", txt, re.I) and not any(p["kind"] in ("digits", "search") for p in props):
            w = next(w for w in s["words"] if clean(w[0]).lower() == "ip")
            ob = next((b for b in bigs if b["t0"] <= w[1] + 0.3 < b["t1"]), None)
            props.append(dict(kind="digits", t0=round(w[1] + 0.3, 2), t1=round(min(s["t1"] + 0.15, ob["t1"] if ob else 99), 2), text="142.250.183.14",
                              y=int((ob["y"] - 250) if ob else L["hair"] - 300)))   # above the word's lead line   # above the word's lead line, never behind the hair
        if RACKCUE.search(txt) and re.search(r"\b(kis|kahan|kam|which|least)\b", txt, re.I) and not any(p["kind"] == "racks" for p in props):
            nxt = next((x for x in sents if x["t0"] > s["t0"] and re.search(r"\b(kam|least|empty|khaali)\b", x["text"], re.I)), None)
            kw = next((w for w in (nxt or s)["words"] if clean(w[0]).lower() in ("kam", "least", "khaali")), None)
            props.append(dict(kind="racks", t0=round(s["t0"] + 0.6, 2), t1=round(((nxt or s)["t1"]) - 3.0 if nxt and nxt["t1"] - nxt["t0"] > 4 else (nxt or s)["t1"], 2),
                              pick=2, pick_t=round(kw[1] if kw else s["t1"] - 0.5, 2)))
            add_sfx("tick", s["t0"] + 0.6, 0.14, "racks", False)
            if kw:
                add_sfx("success", kw[1] - 0.02, 0.18, "pick", True)
        if LOADCUE.search(txt) and not any(p["kind"] == "load" for p in props):
            w = next((w for w in s["words"] if re.match(r"load|khul|screen", clean(w[0]), re.I)), s["words"][-1])
            props.append(dict(kind="load", t0=round(w[1] - 0.6, 2), t1=round(s["t1"] + 0.2, 2), dur=0.9))
            add_sfx("riser", w[1] - 0.7, 0.14, "load", False); add_sfx("success", w[1] + 0.3, 0.16, "loaded", True)
    for b in bigs:
        m = re.match(r"^(\d+)\s+(SECOND|SECONDS|SEC)$", b["big"])
        if m and not any(p["t0"] < b["t1"] and p["t1"] > b["t0"] for p in props) and not any(p["kind"] == "ring" for p in props):
            props.append(dict(kind="ring", t0=b["t0"], t1=round(b["t1"] + 0.05, 2), value=int(m.group(1)), unit="s", dur=1.0))
            for k in range(4):
                add_sfx("tick", b["t0"] + 0.1 + k * 0.25, 0.12, "ring", True)
    for p in props:
        if p["kind"] == "map":
            add_sfx("notif", p["arc_t"] + p.get("arc_d", 1.0), 0.14, "arrive", True)
        if p["kind"] == "digits":
            for k in range(0, len(p["text"]), 3):
                add_sfx("tick", p["t0"] + 0.08 + k * 0.05, 0.08, "digit", True)
    lights = []
    if os.environ.get("KINETIC_V", "4") == "4":      # Round 17 (default since 22 Nov 2026; KINETIC_V=3 = the Round 16 look) (22 Nov 2026): emphasis budget + role styles + room lighting (motionmaxxing: "emphasis is spent, not spread")
        hook = next((b for b in sorted(bigs, key=lambda b: b["t0"]) if b["t0"] < 4.5 and re.match(r"^\d", b["big"])), None) or (sorted(bigs, key=lambda b: b["t0"])[0] if bigs else None)
        def score(i, b):
            w = b["big"]
            sc = 7 if b is hook else 0
            sc += 5 if b.get("strike") else 0
            sc += 4 if NUMTOK.match(w.split()[0]) and b is not hook else 0
            sc += 4 if any(DEFINE.search(s["text"]) and s["t0"] - 0.2 <= b["t0"] <= s["t1"] for s in sents) else 0
            sc += 3 if len(w.split()) == 2 and not w.split()[0].isdigit() else 0
            sc += 1 if TECH.match(w.split()[0].lower()) else 0
            sc -= 6 if any(o["big"] == w and o["t0"] < b["t0"] for o in bigs) else 0   # a repeat of an earlier big word is not new emphasis
            return sc
        bigs.sort(key=lambda b: b["t0"])
        ranked = sorted(enumerate(bigs), key=lambda x: -score(*x))
        budget = max(4, min(7, round(len(phs) * 0.2)))
        keep = []
        for i, b in ranked:
            if len(keep) >= budget:
                break
            if all(abs(b["t0"] - k["t0"]) >= 1.8 or b.get("strike") or k.get("strike") for k in keep):
                keep.append(b)
        keep.sort(key=lambda b: b["t0"])
        hero = max((b for b in keep[1:] if len(b["big"].split()) == 2 and not b.get("strike")), key=lambda b: b["t0"], default=None)
        if hook is not None and hook in keep and hook["t0"] > 0.7:   # frame-0 claim (Round 12): the hook word is up from the first phrase
            hook["t0"] = 0.6
        for i, b in enumerate(keep):
            if b is hook:
                b["style"] = "neon"; lights.append(dict(kind="spot", t0=b["t0"], t1=b["t1"]))
            elif b.get("strike"):
                b["style"] = "serif"
            elif b is hero:
                b["style"] = "block"; lights.append(dict(kind="rays", t0=b["t0"], t1=b["t1"]))
                add_sfx("impact", b["t0"] + 0.02, 0.26, "hero-boom", True)
            elif any(DEFINE.search(s["text"]) and s["t0"] - 0.2 <= b["t0"] <= s["t1"] for s in sents):
                b["style"] = "chrome"
            elif NUMTOK.match(b["big"].split()[0]):
                b["style"] = "block"; lights.append(dict(kind="spot", t0=b["t0"], t1=b["t1"]))
        dropped = [b for b in bigs if b not in keep]
        bigs[:] = keep
        INV = {v: k for k, v in HINDI_NUM.items()}
        for b in dropped:                             # a dropped word goes back into the ONE lead line spoken over it, unless that line already says it
            toks = set(b["big"].lower().split()) | {INV[t] for t in b["big"].lower().split() if t in INV}
            ln = next((x for x in lines if x["t0"] <= b["t0"] + 0.06 <= x["t1"]), None)
            if ln and not toks & set(ln["lead"].lower().split()) and not any(toks & set(x["lead"].lower().split()) for x in lines if abs(x["t0"] - b["t0"]) < 1.2):
                ln["words"].append([b["big"].lower(), round(b["t0"] + 0.04, 2)]); ln["words"].sort(key=lambda x: x[1]); ln["lead"] = " ".join(w[0] for w in ln["words"])
    racks = [p for p in props if p["kind"] in ("racks", "load")]   # racks / the load sweep ARE the visual: no big word fighting them
    for b in bigs:                                    # a word running into the racks / a map ends where the prop starts (dropped only if < 0.8 s would be left)
        for r in racks:
            if b["t0"] < r["t0"] < b["t1"]:
                b["t1"] = round(r["t0"] - 0.05, 2)
    bigs = [b for b in bigs if (b.get("strike") or b["t1"] - b["t0"] >= 0.8) and not any(r["t0"] - 0.05 <= b["t0"] < r["t1"] for r in racks)]
    for ln in lines:                                  # place every lead against the big word actually on screen at its start (after strikes / trims)
        on = next((b for b in bigs if b["t0"] - 0.1 <= ln["t0"] < b["t1"]), None)
        ln["lead_y"] = int(on["y"] - 64) if on else int(L["hair"] - 210)
        if any(r["t0"] <= ln["t0"] < r["t1"] for r in racks):
            ln["lead_y"] = int(L["hair"] - 210); ln["narrow"] = True
    return dict(lines=sorted(bigs + lines, key=lambda x: x["t0"]), props=props, beats=[round(b, 3) for b in beats], face=face, lights=lights, v=4 if lights else 3)
