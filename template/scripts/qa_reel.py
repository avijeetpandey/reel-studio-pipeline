#!/usr/bin/env python3
"""Self-check for a {brand} reel (see $PLUGIN/skills/reel-edit/qa.md).

Timeline checks (composition):
  python3 -I qa_reel.py <composition_dir> [--segments segments.txt] [--geometry geometry.json] [--no-face]
Transcript checks (cut or final video):
  python3 -I qa_reel.py --audio <file.mp4|wav>
Cover check (near-blank cover = ERROR):
  python3 -I qa_reel.py --cover cover_a.jpg --cover cover_b.jpg

Clips are read from index.html elements with class "clip" + data-start/data-duration.
Tag them for best results: data-role="graphic|broll|hook|cta|caption" and data-scene="T|TC|TL|SP|FG|TB".
Enhance-pass clips (reel-edit enhance.md) also carry data-component="roll-text|swing-window|pop-blur|code-window|<registry block>".
Exit code 1 when any ERROR is found.
"""
import argparse, json, os, re, subprocess, sys, tempfile
from html.parser import HTMLParser

FLASH_MIN = 0.8          # s, shortest a graphic/b-roll may stay on screen
FACE_FLASH = 0.6         # s, shortest face shot allowed between a b-roll edge and a jump cut
CANVAS_W, CANVAS_H = 1080, 1920
VOID = {"img", "br", "hr", "input", "meta", "link", "source", "area", "base", "col", "embed", "param", "track", "wbr"}

issues = []
def report(level, msg):
    issues.append((level, msg))


class Clips(HTMLParser):
    """Collects class="clip" elements with timing, role, scene and visible text."""
    def __init__(self):
        super().__init__()
        self.stack, self.clips, self.root_dur, self.skip = [], [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        if a.get("data-composition-id") is not None and a.get("data-duration") and self.root_dur is None:
            self.root_dur = float(a["data-duration"])
        clip = None
        if "clip" in (a.get("class") or "").split() and a.get("data-start") is not None:
            clip = {"tag": tag, "id": a.get("id") or "", "cls": a.get("class") or "",
                    "start": float(a["data-start"]), "dur": float(a.get("data-duration") or 0),
                    "role": a.get("data-role"), "scene": a.get("data-scene"),
                    "comp": a.get("data-component"), "text": ""}
            self.clips.append(clip)
        if tag not in VOID:
            self.stack.append(clip)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag not in VOID and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.skip:
            return
        for c in reversed(self.stack):
            if c is not None:
                c["text"] += " " + data
                break


def infer_role(c):
    if c["role"]:
        return c["role"]
    key = (c["id"] + " " + c["cls"]).lower()
    if c["tag"] in ("audio",) or "sfx" in key or "music" in key:
        return "audio"
    if c["tag"] == "video" and ("main" in key or "a-roll" in key or "aroll" in key):
        return "video"
    if "caption" in key:
        return "caption"
    if "flash" in key or "hook" in key:
        return "hook"
    if "cta" in key:
        return "cta"
    if "broll" in key or "b-roll" in key or "screen" in key or c["tag"] == "video":
        return "broll"
    return "graphic"


def cut_points(path):
    """Jump-cut times on the output timeline, from segments.txt ("start-end" per line, source seconds)."""
    t, pts = 0.0, []
    for line in open(path):
        m = re.match(r"\s*([\d.]+)\s*-\s*([\d.]+)", line)
        if m:
            t += float(m.group(2)) - float(m.group(1))
            pts.append(round(t, 3))
    return pts[:-1]


def face_rect(cells):
    """Face box as a fractional rect. Prefers exact pixels written in the face field ("x 400-800, y 430-850"),
    else 'C2:D3' on the 6×6 face-map grid (columns A–F × 180 px, rows 1–6 × 320 px)."""
    px = re.search(r"x\s*(\d+)\s*-\s*(\d+).*?y\s*(\d+)\s*-\s*(\d+)", cells)
    if px:
        x0, x1, y0, y1 = (int(v) for v in px.groups())
        return (x0 / CANVAS_W, y0 / CANVAS_H, x1 / CANVAS_W, y1 / CANVAS_H)
    m = re.match(r"([A-F])(\d):([A-F])(\d)", cells.upper().replace(" ", ""))
    if not m:
        return None
    c0, r0, c1, r1 = "ABCDEF".index(m.group(1)), int(m.group(2)) - 1, "ABCDEF".index(m.group(3)), int(m.group(4)) - 1
    c0, c1 = min(c0, c1), max(c0, c1)
    r0, r1 = min(r0, r1), max(r0, r1)
    return (c0 * 180 / CANVAS_W, r0 * 320 / CANVAS_H, (c1 + 1) * 180 / CANVAS_W, (r1 + 1) * 320 / CANVAS_H)


def timeline_checks(comp, segments, geometry, face):
    p = Clips()
    p.feed(open(os.path.join(comp, "index.html"), encoding="utf-8").read())
    total = p.root_dur or max((c["start"] + c["dur"] for c in p.clips), default=0)
    vis = []
    for c in p.clips:
        c["role"] = infer_role(c)
        c["words"] = len(re.findall(r"[A-Za-z0-9₹$%]+", c["text"]))
        if c["role"] in ("graphic", "broll"):
            if c["words"] > 25:
                report("WARN", f"{c['id'] or c['cls']} holds {c['words']} words — if it's a group of cards, tag it data-role=\"group\" and tag each card; a single card should carry ≤ 6 words")
                continue
            vis.append(c)
    vis.sort(key=lambda c: c["start"])
    name = lambda c: c["id"] or c["cls"]

    for c in vis:
        if c["dur"] < FLASH_MIN:
            report("ERROR", f"flash: {name(c)} is on screen {c['dur']:.2f}s at {c['start']:.2f}s (min {FLASH_MIN}s)")
        need = 0.3 * c["words"] + 0.6
        if c["words"] and c["dur"] < need:
            report("ERROR", f"read time: {name(c)} has {c['words']} words for {c['dur']:.2f}s (needs ≥ {need:.1f}s)")

    if segments and os.path.exists(segments):
        cuts = cut_points(segments)
        for c in (x for x in vis if x["role"] == "broll"):
            s, e = c["start"], c["start"] + c["dur"]
            for k in cuts:
                if 0 < k - e < FACE_FLASH:
                    report("ERROR", f"face flash: b-roll {name(c)} ends {k - e:.2f}s before the cut at {k:.2f}s — extend it to {k:.2f}s")
                if 0 < s - k < FACE_FLASH:
                    report("ERROR", f"face flash: cut at {k:.2f}s only {s - k:.2f}s before b-roll {name(c)} — start the b-roll at {k:.2f}s")

    scenes = [c["scene"] for c in sorted(p.clips, key=lambda c: c["start"]) if c["scene"]]
    if scenes:
        run = 1
        for a, b in zip(scenes, scenes[1:]):
            run = run + 1 if a == b else 1
            if run > 2:
                report("WARN", f"variety: scene type {b} used more than 2 times in a row")
        if len(set(scenes)) < 3:
            report("WARN", f"variety: only {len(set(scenes))} scene types ({', '.join(sorted(set(scenes)))}); aim for 3+")
        if scenes.count("TB") > 1:
            report("WARN", "variety: more than one text-behind-head (TB) moment")
    else:
        report("INFO", "no data-scene attributes — tag clips so scene variety can be checked")

    # life in the frame (WINNING_PATTERNS §3): something new should appear every few seconds
    events = sorted({round(x, 2) for c in p.clips if infer_role(c) in ("graphic", "broll", "hook", "cta")
                     for x in (c["start"], c["start"] + c["dur"])})
    if segments and os.path.exists(segments):
        events = sorted(set(events) | {round(k, 2) for k in cut_points(segments)})
    events = [0.0] + [e for e in events if 0 < e < total] + [total]
    for a_, b_ in zip(events, events[1:]):
        if b_ - a_ > 4.0:
            report("WARN", f"static: nothing new on screen for {b_ - a_:.1f}s ({a_:.1f}–{b_:.1f}s) — add a state change, a cut or a camera move")

    # enhance-pass budget (enhance.md): heavy moves are signature-level, roll-text stays short, and a reel gets some motion
    comps = sorted((c for c in p.clips if c["comp"]), key=lambda c: c["start"])
    heavy = [c for c in comps if c["comp"] in ("swing-window", "code-window")]
    if len(heavy) > 2:
        report("ERROR", f"enhance: {len(heavy)} heavy components (swing-window/code-window) — max 2 per reel")
    for a_, b_ in zip(heavy, heavy[1:]):
        if b_["start"] < a_["start"] + a_["dur"]:
            report("ERROR", f"enhance: {name(a_)} and {name(b_)} overlap — never two cards at once")
    for c in comps:
        if c["comp"] == "roll-text":
            n = len(re.findall(r"[A-Za-z0-9₹$%]+", c["text"]))
            if n > 5:
                report("WARN", f"enhance: roll-text {name(c)} has {n} words — keep it ≤ 4")
    if total >= 20 and not comps:
        report("INFO", "enhance: no data-component clips — run the enhance pass (enhance.md) or note why the reel stays plain")

    if face and geometry and os.path.exists(geometry):
        g = json.load(open(geometry))
        shots = g if isinstance(g, list) else g.get("shots", [])
        for sh in shots:
            r = face_rect(str(sh.get("face", "")))
            if not r or not total:
                continue
            a, b = float(sh.get("from", 0)), float(sh.get("to", total))
            seeks = ",".join(f"{min(0.999, max(0.001, (a + (b - a) * q) / total)):.3f}" for q in (0.25, 0.5, 0.75))
            zone = f"x0={r[0]:.3f};y0={r[1]:.3f};x1={r[2]:.3f};y1={r[3]:.3f};severity=error;seek={seeks}"
            res = subprocess.run(["npx", "--yes", "hyperframes", "check", comp, "--json", "--no-contrast", "--caption-zone", zone],
                                 capture_output=True, text=True)
            try:
                out = json.loads(res.stdout[res.stdout.index("{"):])
            except Exception:
                report("WARN", f"face box: could not read check output for shot {a:.1f}–{b:.1f}s")
                continue
            for f in out.get("layout", {}).get("findings", []) if isinstance(out.get("layout"), dict) else out.get("layout", []) or []:
                if "caption_zone" in str(f.get("code", "")):
                    report("ERROR", f"face box: text over the face at {f.get('time', '?')}s — {f.get('selector', '')}")


FILLERS = {"um", "uh", "erm", "hmm", "basically", "actually", "literally", "like", "so"}
BRANDS = re.compile(r"\b(chat ?gpt|claude|gemini|llm|upi|openai|anthropic|nvidia|gpu|rag|agi)\b", re.I)


def cover_check(path):
    """Fail a near-blank cover (WINNING_PATTERNS §7: the flop's cover was an empty grey frame)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=72:128,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    if not raw:
        report("ERROR", f"cover: could not read {path}")
        return
    px = list(raw)
    mean = sum(px) / len(px)
    sd = (sum((x - mean) ** 2 for x in px) / len(px)) ** 0.5
    edges = sum(1 for i in range(1, len(px)) if i % 72 and abs(px[i] - px[i - 1]) > 40) / len(px)
    if sd < 18 or edges < 0.01:
        report("ERROR", f"cover: {os.path.basename(path)} looks near-blank (contrast {sd:.0f}, detail {edges:.3f}) — it needs a headline and a face/hero visual")
    else:
        report("INFO", f"cover: {os.path.basename(path)} ok (contrast {sd:.0f}, detail {edges:.3f})")


def transcript_checks(media):
    model = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.en.bin")
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", media, "-ar", "16000", "-ac", "1", wav], check=True)
        subprocess.run(["whisper-cli", "-m", model, "-f", wav, "-ml", "1", "-sow", "-oj", "-of", os.path.join(d, "t"), "-np"],
                       check=True, capture_output=True)
        data = json.load(open(os.path.join(d, "t.json")))
    words = []
    for seg in data.get("transcription", []):
        w = seg.get("text", "").strip()
        if w:
            words.append((w, seg["offsets"]["from"] / 1000, seg["offsets"]["to"] / 1000))
    norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower())
    toks = [(norm(w), s, e) for w, s, e in words if norm(w)]
    if toks and toks[0][1] > 0.15:
        report("WARN", f"first word starts at {toks[0][1]:.2f}s — the hook should start ≤ 0.1s")
    if len(toks) > 10:  # speech density (WINNING_PATTERNS §11: proven reels run 167–246 WPM)
        span = toks[-1][2] - toks[0][1]
        wpm = len(toks) / max(span, 1) * 60
        report("WARN" if wpm < 180 else "INFO", f"pace: {wpm:.0f} words/min over {span:.1f}s of speech — target ≥ 190 (cut more pauses / tighten the script)" if wpm < 180 else f"pace: {wpm:.0f} words/min")
    for n in (4, 3, 2, 1):
        for i in range(len(toks) - 2 * n + 1):
            a, b = [t[0] for t in toks[i:i + n]], [t[0] for t in toks[i + n:i + 2 * n]]
            if a == b and toks[i + 2 * n - 1][2] - toks[i][1] < 3.0:
                report("ERROR", f"repeat: \"{' '.join(a)}\" said twice at {toks[i][1]:.2f}s")
    for i, (w, s, e) in enumerate(toks):
        if w in FILLERS and w not in ("like", "so", "actually"):
            report("WARN", f"filler: \"{w}\" at {s:.2f}s")
        if w == "so" and (i == 0 or s - toks[i - 1][2] > 0.25):
            report("WARN", f"filler: sentence-opening \"so\" at {s:.2f}s")
        if i and s - toks[i - 1][2] > 0.25:  # round 3: proven reels have no gap ≥ 0.12 s in 15/19
            report("WARN", f"pause: {s - toks[i - 1][2]:.2f}s gap before \"{w}\" at {s:.2f}s")
    if toks:  # round 3: 13/19 proven reels end ≤ 0.4 s after the last word, so the loop restarts straight into the hook
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", media],
                                   capture_output=True, text=True).stdout.strip() or 0)
        tail = dur - toks[-1][2]
        if tail > 0.8:
            report("WARN", f"tail: video runs {tail:.2f}s after the last word — end ≤ 0.5 s after it (no outro hold, the CTA card shows while the question is spoken)")
        else:
            report("INFO", f"tail: {tail:.2f}s after the last word")
    brands = sorted({m.group(0) for w, _, _ in words for m in [BRANDS.search(w)] if m})
    report("INFO", "transcript: " + " ".join(w for w, _, _ in words))
    if brands:
        report("INFO", "check spelling in captions: " + ", ".join(brands))


ap = argparse.ArgumentParser()
ap.add_argument("composition", nargs="?")
ap.add_argument("--segments")
ap.add_argument("--geometry")
ap.add_argument("--no-face", action="store_true")
ap.add_argument("--audio")
ap.add_argument("--cover", action="append", default=[], help="cover image(s) to check for a near-blank frame")
a = ap.parse_args()
if a.composition:
    timeline_checks(a.composition, a.segments, a.geometry, not a.no_face)
if a.audio:
    transcript_checks(a.audio)
for cv in a.cover:
    cover_check(cv)
order = {"ERROR": 0, "WARN": 1, "INFO": 2}
for lvl, msg in sorted(issues, key=lambda x: order[x[0]]):
    print(f"{lvl:5} {msg}")
errs = sum(1 for l, _ in issues if l == "ERROR")
print(f"\n{errs} error(s), {sum(1 for l, _ in issues if l == 'WARN')} warning(s)")
sys.exit(1 if errs else 0)
