#!/usr/bin/env python3
"""relight.py — the AUTOMATIC look for a reel (24 Nov 2026; study research/refs_<date>/REPORT.md).

  tools/.venv/bin/python template/auto/relight.py <project dir> [--look auto|<name>|off] [--world W] [--workers 4] [--force]
  <project dir> = reels/<reel>/videos/<reel> (same argument as person_matte.py); needs assets/main.mp4 + assets/fg.webm (person_matte.py).

What it does (no questions, the creator 24 Nov: "choose the best fit from the content, the frames and how it was shot"):
  1. MEASURE the footage: face / room brightness (L*), room colour cast (a*, b*), room saturation, how much of the frame is the person.
  2. PICK a look from the script's world + those numbers (+ never the same look as the last two reels):
       teal_amber  default for explainers / hype: deep teal room, amber practical glow behind him, orange rim; skin natural
       studio_key  neutral deep room with a soft light pool: when the room is already cool / blue (teal would turn to mush), or the footage is bright and clean
       golden_hour warm window light + shafts: story / career / opinion scripts in a neutral or warm room
     (spotlight, moonlight, high_key exist in lookstack.py but are never picked automatically; neon_night / lime_pop need LOOK=<name>.)
  3. CALIBRATE exposure per reel: the face lands at L* ~52 and the room at the look's target whatever the source brightness (dim phone room or bright window).
  4. RENDER assets/main_look.mp4 (room rebuilt behind him, skin natural) and assets/fg_look.webm (the same relit pixels + his matte), so the word-behind-the-head
     layer still sits between the room and a matching person. assets/fg_raw.webm keeps the untouched matte. compose.py / autodirect.py pick the *_look files when they exist.
  5. Write reels/<reel>/work/look.json (choice, reasons, numbers) — EDIT_PLAN.md prints it — and append reels/auto_look_log.json.
LOOK=off (or --look off) removes the *_look files: the reel renders exactly as before. A failure never breaks the edit: it logs and leaves the plain footage.
"""
import argparse, copy, hashlib, json, os, shutil, subprocess, sys, tempfile, time
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lookstack as LS

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
LOG = os.path.join(ROOT, "reels", "auto_look_log.json")
AUTO = ("teal_amber", "studio_key", "golden_hour")          # only these are ever picked automatically
W, H = LS.W, LS.H


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def duration(f):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout.strip() or 0)


def face_exe():
    exe = os.path.join(HERE, "face_boxes")
    if not os.path.exists(exe):
        sh(["swiftc", "-O", os.path.join(HERE, "face_boxes.swift"), "-o", exe])
    return exe


def sample(main, fgraw, n, lut=None):
    """n frames evenly spread over the cut -> [(rgb uint8, alpha float, t)]"""
    d = duration(main); out = []
    for i in range(n):
        t = round(d * (i + 0.5) / n, 2)
        vf = f"scale={W}:{H}" + (f",lut3d=file={lut}" if lut else "")
        a = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", main, "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        m = subprocess.run(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", str(t), "-i", fgraw, "-frames:v", "1", "-vf", "alphaextract,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(a) == W * H * 3 and len(m) == W * H:
            out.append((np.frombuffer(a, np.uint8).reshape(H, W, 3).copy(), np.frombuffer(m, np.uint8).reshape(H, W).astype(np.float32) / 255, t))
    return out


def boxes(frames):
    d = tempfile.mkdtemp(); ps = []
    for i, (rgb, _, _) in enumerate(frames):
        p = f"{d}/f{i}.png"; cv2.imwrite(p, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)); ps.append(p)
    j = json.loads(sh([face_exe()] + ps).stdout or "{}")
    shutil.rmtree(d, ignore_errors=True)
    return [j.get(p) for p in ps]


def analyse(frames, bxs):
    """numbers about how the footage was shot (raw cut, before any look)"""
    fl, rl, ra, rb, rs, ps = [], [], [], [], [], []
    for (rgb, al, _), bx in zip(frames, bxs):
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32); L = lab[..., 0] * 100 / 255
        room = al < 0.02; room[int(H * 0.6):, :] = False
        if bx:
            x, y, w, h = [int(v) for v in bx]; room[:, max(0, x - w):min(W, x + 2 * w)] = False
            fl.append(float(L[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4].mean()))
        if room.sum() > 2000:
            rl.append(float(L[room].mean())); ra.append(float(lab[..., 1][room].mean() - 128)); rb.append(float(lab[..., 2][room].mean() - 128))
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV); rs.append(float(hsv[..., 1][room].mean() / 255))
        ps.append(float(al.mean()))
    m = lambda v: round(float(np.mean(v)), 2) if v else None
    return dict(face_L=m(fl), room_L=m(rl), room_a=m(ra), room_b=m(rb), room_sat=m(rs), person_share=m(ps), frames=len(frames), faces=len(fl))


def recent_looks(exclude):
    try:
        return [r["look"] for r in json.load(open(LOG)) if r["reel"] != exclude][-2:]
    except Exception:
        return []


def choose(world, f, last):
    """-> (look, scores, reasons). Plain rules on purpose: the creator can read why."""
    sc = {k: 0.0 for k in AUTO}; why = []
    cue = {"clean_pop": {"teal_amber": 2.0, "studio_key": 1.0}, "hype_hero": {"teal_amber": 2.2, "studio_key": 0.6}, "warm_cinema": {"golden_hour": 2.2, "teal_amber": 1.2}}.get(world, {"teal_amber": 1.5, "studio_key": 1.0})
    for k, v in cue.items(): sc[k] += v
    why.append(f"world {world}: " + ", ".join(f"{k} +{v}" for k, v in cue.items()))
    b = f.get("room_b"); a = f.get("room_a"); rl = f.get("room_L"); rs = f.get("room_sat")
    if b is not None:
        if b < -4:
            sc["teal_amber"] -= 1.6; sc["studio_key"] += 1.2; why.append(f"room already cool (b* {b}): teal on blue turns to mush, so studio_key +1.2, teal_amber -1.6")
        elif b > 8:
            sc["teal_amber"] += 0.8; sc["golden_hour"] -= 0.6; why.append(f"yellow / olive room (b* {b}): teal is its complement (teal_amber +0.8), more gold would stack (golden_hour -0.6)")
        elif b > 2:
            sc["golden_hour"] += 0.3; why.append(f"slightly warm room (b* {b}): golden_hour +0.3")
    if rl is not None and rl > 62:
        sc["studio_key"] += 0.7; why.append(f"bright room (L* {rl}): a neutral deep room reads cleanest, studio_key +0.7")
    if rs is not None and rs > 0.45:
        sc["studio_key"] += 0.5; why.append(f"already colourful room (sat {rs}): studio_key +0.5")
    for i, l in enumerate(reversed(last)):                      # variety: never the same look as the last two reels when another fits
        pen = 1.4 if i == 0 else 0.7
        if l in sc: sc[l] -= pen; why.append(f"used {i + 1} reel{'s' if i else ''} ago: {l} -{pen}")
    best = max(sc, key=lambda k: (sc[k], k == "teal_amber"))
    return best, {k: round(v, 2) for k, v in sc.items()}, why


def calibrate(look, cal, bxs):
    """secant steps so the face lands at the look's face L* and the room at its room L* (L* moves ~15 per stop around mid grey)"""
    P = copy.deepcopy(LS.LOOKS[look]); tf, tr = LS.TARGETS[look]
    base_e, base_x = P["room"]["exp"], P["subj"]["expo"]
    trace = []
    for it in range(3):
        fs, rs = [], []
        for (rgb, al, _), bx in zip(cal, bxs):
            if not bx: continue
            f, r = LS.measure(LS.apply_look(rgb, al, P), al, bx); fs.append(f); rs.append(r)
        if not fs: break
        fl, rl = float(np.mean(fs)), float(np.mean(rs)); trace.append((round(fl, 1), round(rl, 1)))
        if abs(fl - tf) < 2 and abs(rl - tr) < 2.5: break
        P["subj"]["expo"] = float(np.clip(P["subj"]["expo"] + (tf - fl) / 15, base_x - 0.9, base_x + 0.9))
        P["room"]["exp"] = float(np.clip(P["room"]["exp"] + (tr - rl) / 15, base_e - 1.3, base_e + 1.3))
    return P, trace


def run(a):
    proj = os.path.abspath(a.project); assets = os.path.join(proj, "assets")
    reel_dir = os.path.abspath(os.path.join(proj, "..", ".."))
    name = os.path.basename(reel_dir)
    main = os.path.realpath(os.path.join(assets, "main.mp4")); fg = os.path.join(assets, "fg.webm"); fgraw = os.path.join(assets, "fg_raw.webm")
    out_v, out_fg = os.path.join(assets, "main_look.mp4"), os.path.join(assets, "fg_look.webm")
    work = os.path.join(reel_dir, "work"); os.makedirs(work, exist_ok=True); info_p = os.path.join(work, "look.json")
    mode = (a.look or os.environ.get("LOOK") or "auto").lower()
    if os.environ.get("RELIGHT") == "0": mode = "off"
    if mode == "off":
        for f in (out_v, out_fg, info_p):
            if os.path.exists(f): os.remove(f)
        print(json.dumps(dict(look="off"))); return 0
    if not os.path.exists(main): sys.exit(f"relight: no {main}")
    if not os.path.exists(fgraw):
        if not os.path.exists(fg): print("relight: no assets/fg.webm (run person_matte.py first): skipped, the reel keeps its plain footage", file=sys.stderr); return 0
        shutil.copy(fg, fgraw)                                   # keep the untouched Vision matte; fg.webm stays as is, fg_look.webm is the relit twin
    t0 = time.time()
    world = a.world
    if not world:
        sc = os.path.join(reel_dir, "script.md")
        r = sh([sys.executable, "-I", os.path.join(HERE, "autodirect.py"), "world", "--reel", reel_dir] + (["--script", sc] if os.path.exists(sc) else []))
        try: world = json.loads(r.stdout.strip().splitlines()[-1])["world"]
        except Exception: world = "clean_pop"
    raw = sample(main, fgraw, 6)
    if len(raw) < 3: print("relight: could not sample the footage: skipped", file=sys.stderr); return 0
    bx = boxes(raw); feats = analyse(raw, bx)
    last = recent_looks(name)
    if mode == "auto":
        look, scores, why = choose(world, feats, last)
    else:
        if mode not in LS.LOOKS: sys.exit(f"relight: unknown look {mode}: {' '.join(LS.LOOKS)}")
        look, scores, why = mode, {}, [f"forced by LOOK={mode}"]
    tone = LS.LOOKS[look]["subj"]["tone"]
    cube = os.path.join(work, f"tone_{tone}.cube")
    sh([sys.executable, os.path.join(ROOT, "template", "scripts", "make_look.py"), tone, cube])
    cal = sample(main, fgraw, 4, lut=cube); cbx = boxes(cal)
    P, trace = calibrate(look, cal, cbx)
    key = hashlib.sha1(json.dumps([look, P, os.path.getmtime(main), os.path.getsize(main), os.path.getmtime(fgraw)], sort_keys=True, default=str).encode()).hexdigest()[:12]
    prev = json.load(open(info_p)) if os.path.exists(info_p) else {}
    info = dict(reel=name, look=look, world=world, features=feats, scores=scores, reasons=why, calibration=dict(face_room_L_trace=trace, targets=list(LS.TARGETS[look]), room_exp=round(P["room"]["exp"], 2), subj_expo=round(P["subj"]["expo"], 2)), key=key, auto=(mode == "auto"))
    if not a.force and prev.get("key") == key and os.path.exists(out_v) and os.path.exists(out_fg):
        print(json.dumps(dict(look=look, cached=True))); return 0
    LS.video(main, fgraw, out_v, P, workers=a.workers, tone=tone)
    if abs(duration(out_v) - duration(main)) > 0.15:
        os.remove(out_v); sys.exit(f"relight: rendered {duration(out_v):.2f}s vs cut {duration(main):.2f}s: removed, the reel keeps its plain footage")
    r = sh(["ffmpeg", "-v", "error", "-y", "-i", out_v, "-c:v", "libvpx-vp9", "-i", fgraw, "-filter_complex",
            f"[0:v]scale={W}:{H}:flags=lanczos,format=yuva420p[c];[1:v]alphaextract,scale={W}:{H},format=gray[m];[c][m]alphamerge,format=yuva420p[o]", "-map", "[o]", "-an",
            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8", "-row-mt", "1", "-auto-alt-ref", "0", out_fg])
    if r.returncode: os.remove(out_v); sys.exit("relight: fg_look.webm failed: " + r.stderr[-300:])
    info["seconds"] = round(time.time() - t0)
    json.dump(info, open(info_p, "w"), indent=1)
    try: log = [x for x in json.load(open(LOG)) if x["reel"] != name]
    except Exception: log = []
    log.append(dict(reel=name, look=look, world=world, at=time.strftime("%Y-%m-%d %H:%M"))); json.dump(log, open(LOG, "w"), indent=1)
    print(json.dumps(dict(look=look, world=world, reasons=why, calibration=info["calibration"], seconds=info["seconds"])))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("project"); ap.add_argument("--look"); ap.add_argument("--world"); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--force", action="store_true")
    sys.exit(run(ap.parse_args()))
