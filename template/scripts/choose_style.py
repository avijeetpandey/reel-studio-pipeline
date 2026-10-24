#!/usr/bin/env python3
"""Pick the treatment, signature move, music mood and per-line components for a reel — no human input.

  python3 -I choose_style.py <lines.txt> [--script script.md] [--log reels/style_log.md]
                             [--treatments <plugin>/skills/reel-edit/treatments.md] [--force "Notebook"] [--out style_plan.json]

lines.txt: one spoken sentence per line, optionally "start-end | text" (seconds) — the cut's transcript.
Writes style_plan.json and prints an EDIT_PLAN.md-ready table. Deterministic: same input -> same plan.
Rules it enforces (see reel-edit treatments.md / enhance.md): never the treatment of either of the last 2 reels,
Cinematic Cutout at most once per 4 reels, a frequency penalty so one look can't dominate, a signature move that
differs from the last reel, <= 2 heavy components, quiet twist + pre-CTA beats, no heavy move in the first 2 s / last 4 s,
and a breather after every 2 upgraded lines.
Also picks the in-video CTA card variant (follow / save), the list device for list reels (step-progress for 2–3 items,
list-header for 4+), a count-roll for big numbers, hand-annotate when a line points at a real object, and a 1 s literal
hook image when the hook has a strong verb (WINNING_PATTERNS.md §16–18, round 3), and a check-card for a line that
lists 3–5 short items (§23, round 4).
"""
import argparse, json, os, re, sys
CFG_PATH = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
CFG = json.load(open(CFG_PATH)) if os.path.exists(CFG_PATH) else {}
STUDIO = os.path.expanduser(CFG.get("studio_dir", "~/Documents/reel-studio"))
PLUGIN = os.path.expanduser(CFG.get("plugin_root", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

HOME = os.path.expanduser("~")
NAMES = ["Clean Tech", "Notebook", "Newsroom", "Terminal", "Data", "Cinematic Cutout", "Editorial Split", "Studio Kinetic", "Fact-or-Hype Reaction", "Halftone Collage"]
MUSIC = {"Clean Tech": "light electronic, low", "Notebook": "warm lo-fi / acoustic, very low",
         "Newsroom": "minimal pulse, tense but quiet", "Terminal": "minimal electronic",
         "Data": "modern, steady", "Cinematic Cutout": "cinematic pad, swell into the twist",
         "Editorial Split": "funky (pick_music.py --mood funky)",
         "Studio Kinetic": "dramatic or funky bed, low (pick_music.py)", "Fact-or-Hype Reaction": "funky/bright (pick_music.py)",
         "Halftone Collage": "punchy hip-hop / funk, cuts on the beat (pick_music.py --mood funky)"}
SIGNALS = {
    "mechanism": r"\b(how|works?|token|tokens|embedding|vector|model|pipeline|layers?|attention|context|step|inside|under the hood|architecture|train(ed|ing)?|neural)\b",
    "analogy": r"\b(like|imagine|think of|it'?s as|similar to|autocomplete|recipe|kitchen|library|child|five|explain|everyday|just a|basically a|picture)\b",
    "news": r"\b(openai|google|anthropic|meta|microsoft|nvidia|announced?|launch(ed)?|released?|report(s|ed)?|study|breaking|new model|claims?|just|this week|today)\b",
    "terminal": r"\b(prompt|prompts|agent|agents|claude code|command|terminal|code|coding|tool|tools|api|cursor|script|cli|repo|debug)\b",
    "list": r"\b(number (one|two|three|four|five)|first|second|third|the best (one|part)|\d+ (things|tools|ways|skills|mistakes|types|steps|agents|prompts|apps|settings|features|connectors|servers))\b",
    "demo": r"\b(watch|here'?s how|set (it )?up|install|connect(ed)?|type|click|open|step)\b",
    "factcheck": r"\b(fact|hype|claim|claims|tested|test it|tried|really works|actually works|verdict|is it real|viral)\b",
    "identity": r"\b(you are|you're too|you talk|you overthink|you ask|career|superpower|go all in|stop|start|nobody tells you)\b",
    "strategy": r"\b(strategy|plan|random(ly)?|consisten(t|cy)|growth|ignored|results|direction|mindset|habits?|discipline|why most|most people|algorithm)\b",
    "emotion": r"\b(job|jobs|replace[ds]?|fear|laid off|career|scared|nobody|lie|truth|wrong|quit|salary|fired|worth|dead|dying|stop)\b",
}
NUM = re.compile(r"\d|\b(percent|million|billion|trillion|lakh|crore|thousand)\b|[%₹$]", re.I)
APP = re.compile(r"\b(chatgpt|claude|gemini|google|linkedin|youtube|instagram|app|website|page|screen|dashboard|settings|docs?|sheet|browser|notification)\b", re.I)
CODE = re.compile(r"\b(prompt|command|type[sd]?|code|script|terminal|query|config|sql|regex)\b", re.I)
TWIST = re.compile(r"\b(but|actually|the truth|here'?s the thing|turns out|the catch|except|in reality|surprise)\b", re.I)
QUESTION = re.compile(r"\?\s*$")
BIGNUM = re.compile(r"\b\d{1,3}(,\d{3})+\b|\b\d{4,}\b|\b\d+(\.\d+)?\s*(k|m|million|billion|lakh|crore|stars|installs|downloads|users)\b", re.I)
POINT = re.compile(r"\b(this (light|lamp|lens|mic|camera|setup|button|line|part|corner|tab|icon)|look at (this|that)|right here|see this|over here|behind me)\b", re.I)
HOOK_VERB = re.compile(r"\b(murder(ed|s)?|kill(ed|s)?|dead|died|stole|steal(s|ing)?|replac(ed|es|ing)|broke|break(s|ing)?|destroy(ed|s)?|ended|exposed|leaked|banned|wrong|lied|lying|fired|hacked|cheat(ed|ing)?)\b", re.I)


def listy(t):
    """3–5 short comma/and-separated items ("it added the zooms, the sound effects, the text and the captions") -> items."""
    body = re.split(r"\b(added|adds|does|do|gives|handles|cuts|includes|is|are|:)\b", t, maxsplit=1)[-1]
    parts = [p.strip(" .!?") for p in re.split(r",\s*(?:and\s+)?|\s+and\s+", body) if p.strip(" .!?")]
    if 3 <= len(parts) <= 5 and all(1 <= len(p.split()) <= 3 for p in parts):
        return parts
    return []


def parse_lines(path):
    out = []
    for raw in open(path, encoding="utf-8"):
        raw = raw.strip()
        if not raw:
            continue
        m = re.match(r"^([\d.]+)\s*-\s*([\d.]+)\s*\|\s*(.+)$", raw)
        out.append({"start": float(m[1]), "end": float(m[2]), "text": m[3]} if m
                   else {"start": None, "end": None, "text": raw})
    t = 0.0
    for l in out:  # no timestamps: estimate at ~2.8 words/s
        if l["start"] is None:
            d = max(1.2, len(l["text"].split()) / 2.8)
            l["start"], l["end"] = round(t, 2), round(t + d, 2)
        t = l["end"]
    return out


def read_log(path):
    rows = []
    if path and os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            if ln.startswith("## ") and "carousel" in ln.lower():
                break  # only the reels table drives the reel rotation
            if ln.startswith("| 20"):
                c = [x.strip() for x in ln.strip().strip("|").split("|")]
                if len(c) >= 4:
                    rows.append({"treatment": c[2], "move": c[3]})
    return rows


def treatments_of(row_text):
    return [n for n in NAMES if n.lower() in row_text.lower()]


def signature_moves(path):
    moves, cur = {}, None
    if path and os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            m = re.match(r"### \d+\. ([A-Za-z\- ]+?)(?: \(|$)", ln.strip())
            if m:
                cur = m[1].strip()
            m = re.match(r"- \*\*Signature moves.*?:\*\*\s*(.+)$", ln.strip())
            if m and cur:
                moves[cur] = [x.strip(" .") for x in re.split(r";", m[1]) if x.strip()]
    return moves


def choose(text, script_text, log, force):
    low = text.lower()
    counts = {k: len(re.findall(p, low)) for k, p in SIGNALS.items()}
    nums = len(NUM.findall(text))
    score = {
        "Clean Tech": 0.8 + counts["mechanism"] * 1.0,
        "Notebook": 0.4 + counts["analogy"] * 1.5,
        "Newsroom": counts["news"] * 1.5,
        "Terminal": counts["terminal"] * 1.3,
        "Data": (nums * 1.2) if nums >= 2 else 0.0,
        "Cinematic Cutout": counts["emotion"] * 1.4,
        "Editorial Split": counts["list"] * 1.6 + counts["demo"] * 0.6,  # lists + tool demos (WINNING_PATTERNS.md)
        "Studio Kinetic": counts["identity"] * 1.5 + counts["emotion"] * 0.6,  # opinion / career / mantra (round 2)
        "Fact-or-Hype Reaction": counts["factcheck"] * 2.0,  # test a viral claim (round 2)
        "Halftone Collage": counts["strategy"] * 1.4 + counts["identity"] * 0.4,  # opinion / strategy (round 3)
    }
    fmt = re.search(r"format[^\n]*", script_text or "", re.I)
    if fmt:  # the script's own format label is a strong hint
        f = fmt[0].lower()
        for key, name, bonus in [("news", "Newsroom", 3), ("myth", "Notebook", 2), ("analog", "Notebook", 2), ("explain", "Notebook", 1),
                                 ("hot take", "Cinematic Cutout", 2), ("story", "Cinematic Cutout", 2), ("experiment", "Terminal", 2),
                                 ("list", "Editorial Split", 3), ("story-demo", "Editorial Split", 2),
                                 ("fact or hype", "Fact-or-Hype Reaction", 6), ("reframe", "Studio Kinetic", 3), ("mantra", "Studio Kinetic", 3),
                                 ("opinion", "Halftone Collage", 2), ("strategy", "Halftone Collage", 3), ("collage", "Halftone Collage", 6)]:
            if key in f:
                score[name] += bonus
    hist = [treatments_of(r["treatment"]) for r in log]
    last2 = {n for h in hist[-2:] for n in h}
    recent = [n for h in hist[-6:] for n in h]
    for n in NAMES:
        score[n] -= 1.5 * recent.count(n)  # frequency penalty: stop one look from dominating
    banned = set(last2)
    if any("Cinematic Cutout" in h for h in hist[-4:]):
        banned.add("Cinematic Cutout")
    if force and force in NAMES:
        pick, why = force, "forced by the creator"
    else:
        ok = [n for n in NAMES if n not in banned] or NAMES
        pick = max(ok, key=lambda n: (score[n], -NAMES.index(n)))
        why = f"best score among allowed ({', '.join(f'{n} {score[n]:.1f}' for n in NAMES)}); banned (last 2 / cooldown): {', '.join(sorted(banned)) or 'none'}"
    return pick, why, counts, nums, score


def plan_components(lines, treatment):
    total = lines[-1]["end"] if lines else 0
    n = len(lines)
    plan = []
    for i, l in enumerate(lines):
        t, comp, why = l["text"], "-", "no upgrade (default)"
        quiet = None
        if i == 0:
            quiet = "hook: hook words own this line"
        elif i == n - 1:
            quiet = "CTA question stays on the face"
        elif i == n - 2 or (TWIST.search(t) and i >= n - 3):
            quiet = "twist stays on the face (quiet moment)"
        if quiet:
            plan.append({**l, "i": i, "comp": "-", "why": quiet, "quiet": True})
            continue
        words = len(t.split())
        if CODE.search(t) and re.search(r"[\"'“”`]|/|\bprompt|command|code\b", t, re.I):
            comp, why = "code-window", "line quotes a prompt/command/code -> typed card"
        elif listy(t):
            comp, why = "check-card", f"lists {len(listy(t))} short things -> live checklist that ticks as each is said"
        elif BIGNUM.search(t):
            comp, why = "count-roll", "says a big/growing number -> rolling counter (real figure only)"
        elif NUM.search(t) and words <= 14:
            comp, why = "roll-text", "carries the key number -> headline roll"
        elif POINT.search(t) and treatment != "Halftone Collage":
            comp, why = "hand-annotate", "points at a real object -> hand-drawn circle + arrow on the frame (place it from a frame grab)"
        elif APP.search(t) and treatment != "Cinematic Cutout":
            comp, why = "swing-window", f"names {APP.search(t)[0]} -> screen card (needs a REAL capture/screenshot of it)"
        elif re.search(r"\b(called|term|known as|is a|means)\b", t, re.I) or re.findall(r"(?<!^)\b[A-Z][a-zA-Z]{3,}\b", t):
            comp, why = "pop-blur", "names a term -> calm card entrance"
        plan.append({**l, "i": i, "comp": comp, "why": why, "quiet": False})

    heavy = [p for p in plan if p["comp"] in ("code-window", "swing-window")]
    pref = "code-window" if treatment in ("Terminal", "Clean Tech") else "swing-window"
    heavy.sort(key=lambda p: (p["comp"] != pref, p["i"]))
    for p in heavy[2:]:
        p["comp"], p["why"] = "pop-blur", p["why"] + " (heavy budget full -> pop-blur)"
    for p in plan:
        if p["comp"] in ("code-window", "swing-window") and (p["start"] < 2.0 or p["end"] > total - 4.0):
            p["comp"], p["why"] = "pop-blur", p["why"] + " (heavy move not allowed in first 2 s / last 4 s)"
    for name, cap in (("roll-text", 2), ("count-roll", 2), ("hand-annotate", 3), ("check-card", 1)):
        for p in [p for p in plan if p["comp"] == name][cap:]:
            p["comp"], p["why"] = "pop-blur", p["why"] + f" (max {cap} {name})"
    run = 0  # breather after every 2 upgraded lines
    for p in plan:
        if p["comp"] != "-":
            run += 1
            if run > 2:
                p["comp"], p["why"], run = "-", "breather after 2 upgraded lines", 0
        else:
            run = 0
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines")
    ap.add_argument("--script")
    ap.add_argument("--log", default=os.path.join(STUDIO, "reels/style_log.md"))
    ap.add_argument("--treatments", default=os.path.join(PLUGIN, "skills/reel-edit/treatments.md"))
    ap.add_argument("--force")
    ap.add_argument("--out", default="style_plan.json")
    a = ap.parse_args()

    lines = parse_lines(a.lines)
    if not lines:
        sys.exit("no lines")
    text = " ".join(l["text"] for l in lines)
    script_text = open(a.script, encoding="utf-8").read() if a.script and os.path.exists(a.script) else ""
    log = read_log(a.log)
    pick, why, counts, nums, score = choose(text + " " + script_text, script_text, log, a.force)
    moves = signature_moves(a.treatments).get(pick, [])
    last_move = log[-1]["move"].lower() if log else ""
    move = next((m for m in moves if m.split(";")[0].lower()[:24] not in last_move), moves[0] if moves else "")
    plan = plan_components(lines, pick)
    item_re = re.compile(r"\b((rule|tip|step|tool|skill) )?number (one|two|three|four|five|six|seven|eight|nine|ten)|\b(first|second|third|fourth|fifth)\b|the best (one|part)|last one|#\d+|\b(day|step|rule|tip) \d+\b", re.I)
    items = [l["start"] for l in lines if item_re.search(l["text"])]
    listed = re.search(r"\b(\d+|three|four|five|six|seven|eight|nine|ten) (things|tools|ways|skills|mistakes|steps|rules|systems|apps|settings|tips|effects|prompts|habits|signs)\b", lines[0]["text"], re.I)
    progress = None
    if len(items) >= 4 or (listed and len(items) >= 2 and not re.match(r"(two|three|2|3)\b", listed[1], re.I)):
        progress = {"component": "list-header", "mode": "chip", "items": items, "total": len(items),
                    "title": (listed[0] if listed else lines[0]["text"][:40]), "note": "title pinned from frame 0 (doubles as cover text)"}
    elif len(items) >= 2:
        progress = {"component": "step-progress", "steps": items, "total": len(items)}
    hv = HOOK_VERB.search(lines[0]["text"])
    hook_image = {"verb": hv[0], "at": lines[0]["start"], "brief": f"1 s literal image of \"{hv[0]}\" (e.g. tape across a logo, a struck-through word), then back to the face"} if hv else None
    cta = "save" if re.search(r"\b(framework|structure|checklist|template|cheat ?sheet|steps|save this)\b", text, re.I) else "follow"
    out = {"treatment": pick, "list_progress": progress, "hook_image": hook_image, "cta_variant": cta, "why": why, "signals": counts, "numbers": nums, "signature_move": move,
           "music_mood": MUSIC[pick], "last_treatments": [r["treatment"] for r in log[-2:]],
           "heavy_count": sum(p["comp"] in ("code-window", "swing-window") for p in plan),
           "lines": [{k: p[k] for k in ("i", "start", "end", "text", "comp", "why", "quiet")} for p in plan]}
    json.dump(out, open(a.out, "w"), indent=2, ensure_ascii=False)

    print(f"Treatment: {pick}   Signature move: {move}\nMusic mood: {MUSIC[pick]}\nWhy: {why}")
    print(f"CTA card: {cta}   List device: {progress['component'] + ' at ' + ', '.join(f'{t:.1f}s' for t in items) if progress else 'none'}")
    print(f"Hook image: {hook_image['brief'] if hook_image else 'none'}\n")
    print("| # | Time | Line | Component | Why |\n|---|---|---|---|---|")
    for p in plan:
        print(f"| {p['i'] + 1} | {p['start']:.1f}–{p['end']:.1f} | {p['text'][:60]} | {p['comp']} | {p['why']} |")


if __name__ == "__main__":
    main()
