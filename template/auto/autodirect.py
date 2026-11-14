#!/usr/bin/env python3
"""autodirect.py — the editor's brain. the creator pastes a SCRIPT (and later hands over footage); this decides everything else.

  python3 -I autodirect.py world --script script.md [--reel NAME]            → picks the world + grade BEFORE the cut (make_cut.py --look <grade>)
  python3 -I autodirect.py plan  --reel <reel dir> [--world ID] [--seed S]   → <reel>/edit_plan.json + EDIT_PLAN.md  (compose.py builds the reel from it)

`plan` reads <reel>/work/words_cut.json (islands of [text, start, end, tag?] on the CUT timeline; or transcribes assets/main.mp4 with whisper),
<reel>/segments.txt (the kept source ranges → the jump-cut times = where transitions can hide), <reel>/assets/main.mp4 (end time) and optionally
<reel>/script.md (the creator's words: used for the world + the yes/no CTA). Nothing is asked of the creator.

Decisions (rules come from the round-8 study of 63 reels, research/refs_<date>/REPORT.md, and the creator's hard notes in reel-edit/variety.md):
  world      script cues → clean_pop | warm_cinema | hype_hero (never the same as the last 2 reels when another fits)
  camera     alternate framing per shot (1.00 / 1.065) so jump cuts read as camera cuts, slow drift inside each shot, snap-in on the opening, punch-ins on the
             emphasis words (numbers, negations, contrast, stretched words), a push-in on the CTA — all kept ≥ 0.6 s apart
  transitions ≤ 1 per ~9 s, only at jump cuts that start a new idea (sentence start + connector word), types by world weights, never twice the same in a row
  sound      each transition / punch / number / negation / CTA gets a role sound (ROLES.json), one file per role per reel, levelled by peak, landing 40 ms early,
             spacing ≥ 0.35 s, density ≤ ~1 per 1.6 s, the last non-CTA sentence stays silent (the quiet beat)
  music      pick_music2.py: energetic from second 1, bar-aligned start, never the last 3 reels' tracks
  CTA        comment-YES card when the last sentence is a question, else follow; starts with that sentence
"""
import argparse, json, math, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def _cfg():
    p = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
    try:
        return json.load(open(p))
    except Exception:
        return {}
CFG = _cfg()

T = os.path.dirname(HERE)
ROOT = os.path.dirname(T)
SFX = os.path.join(T, "composition", "assets", "audio", "sfx")
WORLDS = json.load(open(os.path.join(HERE, "worlds.json"), encoding="utf-8"))
LOG = os.path.join(ROOT, "reels", "auto_style_log.json")

NEG = re.compile(r"^(nahi|nahin|never|not|no|don'?t|dont|kabhi|galat|wrong|bad|mat|na|zero|without|bina|worst|fail|failed|crash|crashes|slow|problem|dikkat|loss)$", re.I)
CONTRAST = re.compile(r"^(but|lekin|par|magar|actually|asli|asal|however|instead|real|sach|truth|surprise|twist|bas|sirf|only|sabse|best|fastest|biggest)$", re.I)
NUMBER = re.compile(r"^(\d[\d,.%x]*|one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|lakh|lakhs|crore|million|billion|percent|ek|do|teen|char|paanch|sau|hazaar)$", re.I)
GOOD = re.compile(r"^(fast|faster|instantly|free|sahi|win|works|solved|safe|success|better|best|easy|simple|smooth)$", re.I)
CONNECT = re.compile(r"^(ab|aur|toh|lekin|but|now|next|so|phir|pehle|dusra|teesra|sabse|finally|last|ek|dekho|samjho|imagine|socho|think|here|yahan|matlab|let'?s|suno)$", re.I)


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def duration(f):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]) or 0)


def pick_world(text, last, forced=None):
    if forced:
        return forced
    t = (text or "").lower()
    sel = WORLDS["_selection"]
    score = {k: sum(t.count(c) for c in sel[k + "_cues"]) for k in ("warm_cinema", "hype_hero")}
    score["clean_pop"] = sum(t.count(c) for c in sel["explainer_cues"]) + 1
    order = sorted(score, key=lambda k: -score[k])
    for w in order:
        if w not in last[-2:] or w == order[-1]:
            return w
    return order[0]


def recent_worlds(exclude=None):
    try:
        return [r["world"] for r in json.load(open(LOG)) if r["reel"] != exclude][-3:]
    except Exception:
        return []


def transcribe(video, work):
    wav = os.path.join(work, "a16.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ar", "16000", "-ac", "1", wav], check=True)
    langs = (CFG.get("languages") or "English").lower()
    code_mixed = "hindi" in langs or "hinglish" in langs
    base = os.path.expanduser(CFG.get("whisper_model", "~/.cache/hyperframes/whisper/models/ggml-small.en.bin"))
    multi = os.path.join(os.path.dirname(base), "ggml-small.bin")      # code-mixed scripts need the multilingual model (setup.sh --install fetches it)
    model = multi if (code_mixed and os.path.exists(multi)) else base
    cmd = ["whisper-cli", "-m", model, "-f", wav, "-ml", "1", "-sow", "-np"]
    cmd += ["-l", "hi", "--prompt", "Hinglish in Roman script. English tech words stay English."] if code_mixed and model == multi else ["-l", "en"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    ws = []
    for l in out.splitlines():
        m = re.match(r"\[(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)\]\s+(.*)", l)
        if m and m.group(7).strip() and not m.group(7).strip().startswith("["):
            a = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]); b = int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6])
            ws.append([m.group(7).strip(), round(a, 2), round(b, 2)])
    return [ws]


def sentences(words):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if re.search(r"[.?!]$", w[0]) or nxt is None or nxt[1] - w[2] > 0.45:
            out.append(dict(t0=cur[0][1], t1=cur[-1][2], text=" ".join(x[0] for x in cur), words=cur, q=cur[-1][0].endswith("?")))
            cur = []
    return out


def emphasis(words, end):
    """score every word; return picks [(t, score, kind)] spaced ≥ 1.4 s"""
    cands = []
    for i, w in enumerate(words):
        b = re.sub(r"[^\w%]", "", w[0])
        s, kind = 0.0, None
        if NUMBER.match(b):
            s, kind = 3.0, "number"
        elif NEG.match(b):
            s, kind = 2.6, "negation"
        elif CONTRAST.match(b):
            s, kind = 2.4, "contrast"
        elif GOOD.match(b):
            s, kind = 1.6, "good"
        if w[2] - w[1] >= 0.38:
            s += 1.0; kind = kind or "stretch"
        if i == 0 or re.search(r"[.?!]$", words[i - 1][0]):
            s += 0.4
        if s >= 1.6 and 0.5 < w[1] < end - 3.0:
            cands.append((w[1], s, kind, i))
    cands.sort(key=lambda x: -x[1])
    picks = []
    for c in cands:
        if all(abs(c[0] - p[0]) >= 1.4 for p in picks):
            picks.append(c)
    return sorted(picks)


def tag_words(words):
    for w in words:
        if len(w) > 3:
            continue
        b = re.sub(r"[^\w%]", "", w[0])
        if NEG.match(b):
            w.append("r")
        elif NUMBER.match(b) or CONTRAST.match(b):
            w.append("y")
        elif GOOD.match(b):
            w.append("g")
    return words


def joins_from(segfile):
    t, js = 0.0, []
    for ln in open(segfile):
        if ln.strip():
            a, b = map(float, ln.strip().split("-"))
            t += b - a
            js.append(round(t, 3))
    return js[:-1]


def choose_transitions(joins, sents, words, W, end, rnd):
    """score each join as an 'idea change'; keep ≤ max, ≥ 4.5 s apart, none in the first 3 s / last 4 s"""
    nmax = max(1, round(end / 9.0)) if end > 14 else 1
    nmax = min(nmax, W.get("max_transitions_per_30s", 3) + 1)
    starts = {round(s["t0"], 1) for s in sents}
    cands = []
    for k, J in enumerate(joins):
        if J < 3.0 or J > end - 4.0:
            continue
        nxt = next((w for w in words if w[1] >= J - 0.05), None)
        prv = [w for w in words if w[2] <= J + 0.05]
        sc = 0.0
        if prv and re.search(r"[.?!]$", prv[-1][0]):
            sc += 2.0
        if nxt and CONNECT.match(re.sub(r"[^\w']", "", nxt[0])):
            sc += 1.5
        if any(abs(J - s) < 0.25 for s in starts):
            sc += 1.0
        prev_j = joins[k - 1] if k else 0
        if J - prev_j >= 2.0:
            sc += 1.0
        cands.append((sc + rnd.random() * 0.3, J))
    cands.sort(reverse=True)
    pick = []
    for sc, J in cands:
        if sc < 1.5 and pick:
            break
        if all(abs(J - p) >= 4.5 for p in pick):
            pick.append(J)
        if len(pick) >= nmax:
            break
    return sorted(pick)


def weighted(w, avoid, rnd, leaks_left):
    pool = [(k, v) for k, v in w.items() if k != avoid and (k != "leak" or leaks_left > 0)] or list(w.items())
    tot = sum(v for _, v in pool); r = rnd.random() * tot
    for k, v in pool:
        r -= v
        if r <= 0:
            return k
    return pool[-1][0]


def role_pick(roles, role, rnd):
    c = roles.get(role) or []
    if not c:
        return None
    originals = [x for x in c if x["src"] == "original"]
    pool = originals[:2] + c[2:6] if originals else c[:4]
    return rnd.choice(pool)


def level(c, base):
    """level every sound to the same peak (-10 dBFS) before the role volume"""
    return round(max(0.04, min(1.0, base * 10 ** ((-10 - c["peak_db"]) / 20))), 2)


def face_layout(video, joins, end, W):
    """Apple Vision face boxes per shot -> (1) a per-shot reframe so the face is the same size and height in every shot (the v2 hand-tuning, now automatic),
    (2) caption row + CTA row that never touch a face AFTER that reframe (1080x1920 space, with alt-scale + punch margin)."""
    exe = os.path.join(HERE, "face_boxes")
    if not os.path.exists(exe):
        try:
            r = subprocess.run(["swiftc", "-O", os.path.join(HERE, "face_boxes.swift"), "-o", exe], capture_output=True, text=True)
        except FileNotFoundError:   # no Swift toolchain (Linux / no Xcode CLT): captions use the world defaults
            return None
        if r.returncode:
            return None
    bounds = [0.0] + list(joins) + [end]
    tmp = os.path.join(os.path.dirname(video), "_geo"); os.makedirs(tmp, exist_ok=True)
    files = []
    for i in range(len(bounds) - 1):
        for k, fr in enumerate((0.3, 0.75)):
            t = bounds[i] + (bounds[i + 1] - bounds[i]) * fr
            f = os.path.join(tmp, f"s{i}_{k}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=540:960", f], capture_output=True)
            files.append((i, f))
    out = json.loads(subprocess.run([exe] + [f for _, f in files], capture_output=True, text=True).stdout or "{}")
    per = {}
    for i, f in files:
        b = out.get(f)
        if b:
            x, y, w, h = [v * 2 for v in b]                                  # 540 -> 1080 canvas
            per.setdefault(i, []).append((y - 0.45 * h, y + 1.12 * h))        # Vision box covers brow-to-chin: add hair + jaw
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    if not per:
        return None
    n = len(bounds) - 1
    raw = [(sum(t for t, _ in per[i]) / len(per[i]), sum(c for _, c in per[i]) / len(per[i])) if i in per else None for i in range(n)]
    hs = sorted(c - t for t, c in (r for r in raw if r)); cs = sorted((t + c) / 2 for t, c in (r for r in raw if r))
    h_t = hs[int(len(hs) * 0.75)] if hs else 600; c_t = cs[len(cs) // 2] if cs else 1100
    shots = []
    for i in range(n):
        if raw[i] is None:
            shots.append(dict(m=1.0, c=c_t, top=None, chin=None)); continue
        t, c = raw[i]
        m = max(1.0, min(1.32, h_t / max(1.0, c - t)))                        # never zoom out; wide shots zoom in (headroom: main.mp4 is 1440x2560)
        shots.append(dict(m=round(m, 3), c=round((t + c) / 2, 1), top=round(t, 1), chin=round(c, 1)))
    def y_for(sh, s):
        return int(max(-190, min(190, c_t - (845 + (sh["c"] - 845) * s))))
    faces = []
    for i, sh in enumerate(shots):
        if sh["top"] is None:
            continue
        se = sh["m"] * 1.1                                                    # alt-scale + punch margin
        yy = y_for(sh, se)
        faces.append((845 + (sh["top"] - 845) * se + yy, 845 + (sh["chin"] - 845) * se + yy, i))
    ok = lambda y0, y1: all(y1 <= tp - 25 or y0 >= ch + 25 for tp, ch, _ in faces)
    top_min = min(f[0] for f in faces)
    dyn = int(top_min - 25 - 125)
    order = [dyn, W["caption"]["y"], 640, 360, 1230, 1330] if W["caption"]["y"] < 700 else [W["caption"]["y"], 1230, dyn, 640, 360, 1330]
    cap = next((y for y in order if 250 <= y and y + 120 <= 1420 and ok(y, y + 120)), None)
    if cap is None:
        cap = max(250, int(min(f[0] for f in faces) - 150))
    cta = next((y for y in [1010, 470, 290, 1250] if 250 <= y and y + 190 <= 1420 and ok(y, y + 190) and (y + 190 <= cap - 15 or y >= cap + 135)), 290)
    return dict(caption_y=int(cap), cta_y=int(cta), hair_top_min=int(min(f[0] for f in faces)), chin_max=int(max(f[1] for f in faces)),
                target=dict(face_h=round(h_t), center=round(c_t)), shots=shots, faces=[[round(a), round(b), i] for a, b, i in faces])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["world", "plan"])
    ap.add_argument("--script"); ap.add_argument("--reel"); ap.add_argument("--world"); ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    last = recent_worlds(os.path.basename(os.path.abspath(a.reel)) if a.reel else None)
    if a.cmd == "world":
        txt = open(a.script, encoding="utf-8").read() if a.script and os.path.exists(a.script) else ""
        w = pick_world(txt, last, a.world)
        print(json.dumps(dict(world=w, grade=WORLDS[w]["grade"], label=WORLDS[w]["label"], recent=last)))
        return
    R = os.path.abspath(a.reel)
    name = os.path.basename(R.rstrip("/"))
    seed = a.seed if a.seed is not None else sum(ord(c) for c in name)
    rnd = random.Random(seed)
    work = os.path.join(R, "work"); os.makedirs(work, exist_ok=True)
    proj_assets = os.path.join(R, "videos", name, "assets")
    video = os.path.join(proj_assets, "main.mp4")
    if not os.path.exists(video) and os.path.exists(os.path.join(R, "assets", "main.mp4")):
        os.makedirs(proj_assets, exist_ok=True)                       # the cut may have been written to <reel>/assets: bring it into the project
        os.symlink(os.path.abspath(os.path.join(R, "assets", "main.mp4")), video)
    end = round(duration(video), 2)
    wj = os.path.join(work, "words_cut.json")
    islands = json.load(open(wj, encoding="utf-8")) if os.path.exists(wj) else transcribe(video, work)
    if not os.path.exists(wj):
        json.dump(islands, open(wj, "w", encoding="utf-8"), ensure_ascii=False)
    words = tag_words([w for isl in islands for w in isl])
    script = open(os.path.join(R, "script.md"), encoding="utf-8").read() if os.path.exists(os.path.join(R, "script.md")) else " ".join(w[0] for w in words)
    wid = pick_world(script, last, a.world)
    W = WORLDS[wid]
    sents = sentences(words)
    joins = joins_from(os.path.join(R, "segments.txt")) if os.path.exists(os.path.join(R, "segments.txt")) else []
    speech_end = words[-1][2]
    rp = os.path.join(SFX, "ROLES.json")
    if not os.path.exists(rp):
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "sfx_roles.py")], capture_output=True)
    roles = json.load(open(rp)) if os.path.exists(rp) else {}
    pal = {r: role_pick(roles, r, rnd) for r in roles}

    geo = face_layout(video, joins, end, W)
    if geo:
        json.dump(geo, open(os.path.join(work, "geometry_auto.json"), "w"), indent=1)
        W = dict(W, caption=dict(W["caption"], y=geo["caption_y"]))
    # ---- transitions -------------------------------------------------------------------
    tj = choose_transitions(joins, sents, words, W, end, rnd)
    trans, prev, leaks = [], None, W.get("max_leaks", 0)
    for J in tj:
        k = weighted(W["transitions"], prev, rnd, leaks)
        if k == "leak":
            leaks -= 1
        trans.append(dict(t=J, type=k)); prev = k
    # ---- music (picked first: punches snap to its beats) ------------------------------------------
    mus = None
    try:
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "pick_music2.py"), "--len", str(end), "--moods", ",".join(W["music_moods"]), "--reel", name, "--out", os.path.join(os.path.dirname(video), "audio", "bgm.mp3")], capture_output=True, text=True)
        mus = json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
        if r.returncode:
            print(r.stderr, file=sys.stderr)
    except Exception as e:
        print("music pick failed:", e, file=sys.stderr)
    beats = (mus or {}).get("beats", [])
    # ---- camera ------------------------------------------------------------------------
    A, B = W["alt_scales"]
    bounds = [0.0] + joins + [end]
    puncts = emphasis(words, end)
    # keep punches off transition joins and cap by density
    cap_n = max(1, round(end / 10 * W["punch"]["per_10s"]))
    puncts = [p for p in puncts if all(abs(p[0] - J) > 0.5 for J in joins)][:cap_n]
    def snap_b(t):
        c = [b for b in beats if t - 0.12 <= b <= t + 0.03]
        return round(c[-1], 3) if c else t
    puncts = [(snap_b(p[0]),) + tuple(p[1:]) for p in puncts]
    ops = []
    st_s = A
    def SH(si):
        return geo["shots"][si] if geo and si < len(geo["shots"]) else None
    def SY(si, s):                      # y shift that keeps this shot's face at the target height after scaling about the origin (540, 845)
        sh = SH(si)
        if not sh:
            return 0
        return int(max(-190, min(190, geo["target"]["center"] - (845 + (sh["c"] - 845) * s))))
    for si in range(len(bounds) - 1):
        t0, t1 = bounds[si], bounds[si + 1]
        m = SH(si)["m"] if SH(si) else 1.0
        base = (A if si % 2 == 0 else B) * m
        drift = 0.025 if (t1 - t0) > 1.6 else 0.01
        if si == 0:
            s_hook = round(base * W["hook_snap"] / A, 4)
            ops.append(("camTo", [0.0, 0.0, s_hook, SY(si, s_hook), "none"], 0.0))
            ops.append(("camTo", [0.0, 0.45, round(base, 4), SY(si, base), "power3.out"], 0.0))
            t_cur = 0.45
        else:
            ops.append(("camTo", [t0, t0, round(base, 4), SY(si, base), "none"], t0))
            t_cur = t0
        ps = [p for p in puncts if t0 + 0.45 < p[0] < t1 - 0.3]
        bs = lambda t: base * (1 + drift * (t - t0) / max(0.2, t1 - t0))
        for p in ps:
            tp = max(t_cur, p[0] - 0.05)
            s_a, s_b, s_c = round(bs(tp), 4), round(bs(tp) * W["punch"]["amt"], 4), round(bs(tp + 0.6), 4)
            ops.append(("camTo", [t_cur, tp, s_a, SY(si, s_a), "none"], t_cur))
            ops.append(("camTo", [tp, tp + 0.09, s_b, SY(si, s_b), "power3.out"], tp))
            ops.append(("camTo", [tp + 0.09, tp + 0.6, s_c, SY(si, s_c), "power2.out"], tp + 0.09))
            t_cur = tp + 0.6
        tend = t1 - 0.02
        if tend > t_cur:
            s_e = round(base * (1 + drift), 4)
            ops.append(("camTo", [t_cur, tend, s_e, SY(si, s_e), "none"], t_cur))
    # ---- effects at transitions + shakes ------------------------------------------------
    sfx = []
    fx_ops = list(ops)
    sp = {}  # sfx spacing guard
    def add_sfx(role, t, base, tag, force=False):
        c = pal.get(role)
        if not c or t < 0:
            return
        if not force and any(abs(t - s["t"]) < 0.35 for s in sfx):
            return
        sfx.append(dict(id=f"{tag}{len(sfx)}", file=c["file"], t=round(t, 2), vol=level(c, base), role=role, why=tag))
    for tr in trans:
        J, k = tr["t"], tr["type"]
        if k == "whip":
            d = dict(dir=rnd.choice(["h", "h", "v"]), sign=rnd.choice([1, -1]))
            fx_ops.append(("whip", [J, d], J - 0.1)); add_sfx("whip", J - 0.13, 0.30, "whip")
        elif k == "shrink":
            fx_ops.append(("shrink", [J, dict(**{"from": rnd.choice(["down", "up"])})], J - 0.17)); add_sfx("whip", J - 0.17, 0.28, "shrink")
        elif k == "blurIn":
            fx_ops.append(("blurIn", [J, {}], J)); add_sfx("shutter" if W["sfx_palette"] != "soft" else "whoosh", J - 0.04, 0.2, "focus")
        elif k == "leak":
            fx_ops.append(("leak", [J, {"tone": "amber"}], J - 0.2)); add_sfx("riser", J - 0.5, 0.18, "leak"); add_sfx("hit_soft", J - 0.03, 0.22, "leak-hit", True)
    shakes = [p for i, p in enumerate(puncts) if W["punch"]["shake_every"] and i % W["punch"]["shake_every"] == 0 and p[2] in ("number", "negation", "contrast")]
    for p in shakes[:3]:
        fx_ops.append(("shake", [round(p[0] - 0.02, 2), {"amp": 9 if W["punch"]["amt"] > 1.06 else 6, "dur": 0.3}], p[0]))
    if W["rgb"] and puncts:
        p = max(puncts, key=lambda x: x[1])
        fx_ops.append(("rgb", [round(p[0], 2), {}], p[0]))
    # opening: aperture reveal only in hype world (face stays visible in the strip)
    if wid == "hype_hero":
        fx_ops.insert(0, ("aperture", [0.0, 0.32, {"side": 30}], 0.0))
    # ---- SFX for the words ----------------------------------------------------------------
    quiet = sents[-2] if len(sents) >= 2 and not sents[-1]["q"] else sents[-2] if len(sents) >= 2 else None
    quiet_rng = (quiet["t0"], quiet["t1"]) if quiet else (999, 999)
    nsfx = 0
    for p in puncts:
        if quiet_rng[0] <= p[0] <= quiet_rng[1]:
            continue
        if p[2] == "number" and nsfx < 3:
            add_sfx("tick", p[0] - 0.04, 0.22, "num"); nsfx += 1
        elif p[2] == "negation" and nsfx < 3:
            add_sfx("negation", p[0] - 0.04, 0.2, "neg"); nsfx += 1
        elif p[2] in ("contrast", "stretch") and nsfx < 4:
            add_sfx("hit_soft", p[0] - 0.04, 0.2, "hit"); nsfx += 1
    if W["sfx_palette"] in ("pop", "hit"):
        add_sfx("notif" if W["sfx_palette"] == "pop" else "impact", 0.0, 0.26, "open", True)
    # ---- CTA -----------------------------------------------------------------------------------
    OPEN_Q = re.compile(r"\b(kitna|kitne|kitni|kaun|kaunsa|kaunse|kab|kahan|kyun|kaise|how|what|which|when|where|why)\b", re.I)
    qs = [x for x in sents[-3:] if x["q"]]
    fol = [x for x in sents[-2:] if re.search(r"follow|subscribe", x["text"], re.I) and (not qs or x["t0"] > qs[-1]["t1"] - 0.2)]
    ctas = []
    y_cta = geo["cta_y"] if geo else (470 if W["caption"]["y"] > 1000 else 1010)
    if qs:                                   # comment card while the question is spoken
        q = qs[-1]
        t0q = round(max(q["t0"] - 0.1, end - 4.2), 2) if q["t1"] - q["t0"] > 4.2 else round(q["t0"] - 0.1, 2)
        ctas.append(dict(variant="comment", t0=t0q, y=y_cta, answer=("Mera answer" if "hinglish" in (CFG.get("languages") or "").lower() or "hindi" in (CFG.get("languages") or "").lower() else "My answer") if OPEN_Q.search(q["text"]) else "YES"))
    if fol or not ctas:                      # follow card with the sign-off line (or alone when there is no question)
        f = fol[-1] if fol else sents[-1]
        tf = round(max(f["t0"] - 0.1, end - 4.2), 2) if (f["t1"] - f["t0"] > 4.2 and not ctas) else round(f["t0"] - 0.1, 2)
        ctas.append(dict(variant="follow", t0=tf, y=y_cta))
    cta = ctas
    for ci, c in enumerate(ctas):
        s0 = c["t0"] + 0.1
        add_sfx("notif", c["t0"], 0.22, "cta", True)
        if c["variant"] == "comment":
            n = len(c["answer"])
            for i in range(n):
                add_sfx("tick", s0 + 0.5 + i * 0.12 - 0.03, 0.14, "cta-key", True)
            press = s0 + 0.6 + n * 0.12 + 0.3
        else:
            press = s0 + 1.2
        add_sfx("click", press - 0.03, 0.26, "cta-click", True); add_sfx("success", press + 0.06, 0.24, "cta-done", True)
    fx_ops.sort(key=lambda x: x[2])
    plan = dict(reel=name, end=end, world=wid, layout=geo, grade=W["grade"], accent=W["accent"], seed=seed,
                words=islands if isinstance(islands[0][0], list) else [islands],
                caption=W["caption"], fx=[dict(fn=f[0], a=f[1]) for f in fx_ops], sfx=sorted(sfx, key=lambda s: s["t"]),
                music=dict(file="assets/audio/bgm.mp3", vol=0.38, fade=0.28, meta=mus) if mus else None, cta=cta, progress=True, grain=0.1,
                transitions=trans, punches=[dict(t=round(p[0], 2), kind=p[2], score=p[1]) for p in puncts], joins=joins, sentences=[dict(t0=s["t0"], t1=s["t1"], text=s["text"], q=s["q"]) for s in sents])
    json.dump(plan, open(os.path.join(R, "edit_plan.json"), "w"), indent=1, ensure_ascii=False)
    # human-readable plan
    md = [f"# EDIT_PLAN — {name} (autodirect, seed {seed})", f"World **{wid}** — {W['label']}  ·  grade `{W['grade']}`  ·  captions `{W['caption']['style']}`  ·  end {end}s",
          f"Music: {mus['file'] if mus else '—'} (start {mus['start'] if mus else '-'} s, {mus['bpm'] if mus else '-'} bpm)" if mus else "Music: none picked", "",
          "| t | what | sound |", "|---|---|---|"]
    for f in sorted(fx_ops, key=lambda x: x[2]):
        if f[0] == "camTo" and f[1][3:] and f[1][4] != "power3.out":
            continue
        md.append(f"| {f[2]:.2f} | {f[0]} {json.dumps(f[1][1:] if f[0]=='camTo' else f[1][1:] or '')[:60]} | |")
    md += ["", "Sound:"] + [f"- {s['t']:.2f}s `{s['file']}` vol {s['vol']} ({s['why']})" for s in plan["sfx"]]
    pick = [x for x in sents if any(NUMBER.match(re.sub(r"[^\w%]", "", w[0])) for w in x["words"])][:1] or sents[1:2]
    mid = sents[len(sents) // 2] if sents else None
    md += ["", "Pickup shots (suggestions for the next shoot — the edit never waits for them):"]
    if pick:
        md.append(f"- Overhead shot of hands doing/holding the thing for: \"{pick[0]['text'][:70]}\"")
    if mid:
        md.append(f"- Change shirt or location at: \"{mid['text'][:70]}\" (the strongest 'a person made this' tell in the study)")
    md.append("- A prop held up to camera as the proof object for the claim in the opening line")
    md += ["", "Sentences:"] + [f"- {s['t0']:.1f}–{s['t1']:.1f}{' ?' if s['q'] else ''} {s['text']}" for s in sents]
    open(os.path.join(R, "EDIT_PLAN.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    # log the world so the next reel varies
    try:
        L = json.load(open(LOG)) if os.path.exists(LOG) else []
    except Exception:
        L = []
    if not name.startswith("_"):   # test reels (_autotest …) never touch the variety log
        L = [r for r in L if r["reel"] != name] + [dict(reel=name, world=wid, grade=W["grade"], music=(mus or {}).get("file"))]
        json.dump(L, open(LOG, "w"), indent=1)
    print(json.dumps(dict(world=wid, transitions=trans, punches=len(puncts), sfx=len(sfx), fx=len(fx_ops), music=(mus or {}).get("file"), end=end)))


if __name__ == "__main__":
    main()
