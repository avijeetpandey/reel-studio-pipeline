#!/usr/bin/env python3
"""Deep reference-reel analysis (round 8, 14 Nov 2026) — video + audio + captions + comments in one pass.

  tools/.venv/bin/python template/scripts/analyze_ref2.py <dir with src/<id>.mp4 + <id>.info.json> [--only ID,ID] [--workers 4]

Writes <dir>/analysis/<id>/ :
  metrics.json   duration, fps, cuts, avg shot, first cut, flashes, whips, zooms (punch / push), shakes, colour grade
                 (Y, saturation, warmth, shadow/highlight tint, contrast), skin share (face-on-screen proxy), LUFS,
                 words, wpm, first word, tail, music bed, tempo, non-speech sound events per 10 s + their classes,
                 caption stats (hashtags, emoji, CTA keyword), top comments
  timeline.json  every detected event with its time (cut / flash / whip / zoom / shake / sfx:<class>)
  view.jpg       hook strip (8 frames, 0–2 s) + 24-frame overview — the thing to LOOK at
  events.jpg     6 consecutive frames around up to 12 transitions (frame-by-frame look at how they are built)
  audio.png      spectrogram with speech words and detected sound events marked
  transcript.txt word timings
Needs ffmpeg, whisper-cli (ggml-small), numpy, opencv, librosa, matplotlib (tools/.venv).
"""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import cv2

W_SMALL = 180
MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.bin")
PROMPT = "Hinglish in Roman script. English tech words stay English: Claude, AI, ChatGPT, Instagram, edit, reel."


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(f):
    o = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,bit_rate,codec_name:format=duration,bit_rate", "-of", "json", f]).stdout
    j = json.loads(o)
    s = j["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return dict(w=int(s["width"]), h=int(s["height"]), fps=float(n) / float(d), dur=float(j["format"]["duration"]),
                codec=s.get("codec_name"), kbps=int(float(j["format"].get("bit_rate", 0)) / 1000))


def read_frames(f, w, h, fps=30):
    cmd = ["ffmpeg", "-v", "error", "-i", f, "-an", "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    p = subprocess.run(cmd, capture_output=True)
    a = np.frombuffer(p.stdout, np.uint8)
    n = len(a) // (w * h * 3)
    return a[: n * w * h * 3].reshape(n, h, w, 3)


def video_metrics(fr, fps):
    n, h, w, _ = fr.shape
    gray = np.array([cv2.cvtColor(x, cv2.COLOR_BGR2GRAY) for x in fr]).astype(np.float32)
    hsv = np.array([cv2.cvtColor(x, cv2.COLOR_BGR2HSV) for x in fr])
    Y = gray.mean((1, 2))
    S = hsv[..., 1].astype(np.float32).mean((1, 2)) / 255
    B, G, R = [fr[..., i].astype(np.float32).mean((1, 2)) for i in range(3)]
    sharp = np.array([cv2.Laplacian(g, cv2.CV_32F).var() for g in gray])
    d = np.r_[0, np.abs(np.diff(gray, axis=0)).mean((1, 2))]
    # histogram distance
    hist = np.array([cv2.calcHist([x], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3).flatten() for x in fr])
    hist /= hist.sum(1, keepdims=True)
    hd = np.r_[0, 0.5 * np.abs(np.diff(hist, axis=0)).sum(1)]
    # skin share (face-on-screen proxy): YCrCb range
    ycc = np.array([cv2.cvtColor(x, cv2.COLOR_BGR2YCrCb) for x in fr])
    skin = ((ycc[..., 1] > 135) & (ycc[..., 1] < 175) & (ycc[..., 2] > 85) & (ycc[..., 2] < 127)).mean((1, 2))
    # global flow on the border band (ignores the face): translation + zoom rate per frame
    yy, xx = np.mgrid[0:h, 0:w]
    border = ((xx < w * 0.22) | (xx > w * 0.78) | (yy < h * 0.18) | (yy > h * 0.82))
    cx, cy = w / 2, h / 2
    gs = [cv2.resize(g.astype(np.uint8), (w // 2, h // 2)) for g in gray]
    bm = cv2.resize(border.astype(np.uint8), (w // 2, h // 2)).astype(bool)
    hh, ww = gs[0].shape
    y2, x2 = np.mgrid[0:hh, 0:ww]
    X = np.c_[np.ones(bm.sum()), (x2[bm] - ww / 2) / ww, (y2[bm] - hh / 2) / hh]
    dx = np.zeros(n); dy = np.zeros(n); kz = np.zeros(n); mag = np.zeros(n)
    for i in range(1, n):
        fl = cv2.calcOpticalFlowFarneback(gs[i - 1], gs[i], None, 0.5, 2, 13, 2, 5, 1.1, 0)
        fx, fy = fl[..., 0][bm], fl[..., 1][bm]
        # fx ≈ tx + k*(x-cx)  → k from the x-gradient; fy likewise
        bx = np.linalg.lstsq(X, fx, rcond=None)[0]; by = np.linalg.lstsq(X, fy, rcond=None)[0]
        dx[i], dy[i] = bx[0] * 2, by[0] * 2                       # px at 180-wide scale
        kz[i] = (bx[1] / ww + by[2] / hh) / 2                      # scale change per frame (+ = zoom in)
        mag[i] = np.hypot(fl[..., 0], fl[..., 1]).mean() * 2
    return dict(Y=Y, S=S, R=R, G=G, B=B, sharp=sharp, d=d, hd=hd, skin=skin, dx=dx, dy=dy, kz=kz, mag=mag, hsv=hsv, fr=fr)


def local_med(a, i, r=8):
    lo, hi = max(0, i - r), min(len(a), i + r + 1)
    seg = np.r_[a[lo:i], a[i + 1:hi]]
    return float(np.median(seg)) if len(seg) else 0.0


def detect_events(m, fps):
    n = len(m["Y"])
    ev = []
    cut_frames = []
    for i in range(2, n - 1):
        lm = local_med(m["d"], i)
        if m["hd"][i] > 0.28 and m["d"][i] > max(10, 3.0 * lm):
            cut_frames.append(i)
    # drop adjacent duplicates
    cuts = []
    for i in cut_frames:
        if not cuts or i - cuts[-1] > 3:
            cuts.append(i)
    for i in cuts:
        ev.append(dict(t=round(i / fps, 2), type="cut"))
    # flash: brightness spike vs the 6 frames before, decays soon after
    Y = m["Y"]
    for i in range(6, n - 4):
        base = np.median(Y[i - 6:i - 2])
        if Y[i] - base > 22 and np.min(Y[i + 1:i + 5]) < Y[i] - 12:
            if not ev or ev[-1]["type"] != "flash" or i / fps - ev[-1]["t"] > 0.3:
                ev.append(dict(t=round(i / fps, 2), type="flash", dY=round(float(Y[i] - base), 1)))
    # whip / smear: strong global motion + sharpness collapse
    sh = m["sharp"]
    i = 3
    while i < n - 3:
        if m["mag"][i] > 9 and sh[i] < 0.55 * max(1e-3, local_med(sh, i, 10)):
            j = i
            while j < n - 1 and m["mag"][j + 1] > 6:
                j += 1
            ev.append(dict(t=round(i / fps, 2), type="whip", dur=round((j - i + 1) / fps, 2), dir=("h" if abs(m["dx"][i:j + 1].sum()) > abs(m["dy"][i:j + 1].sum()) else "v")))
            i = j + 2
        else:
            i += 1
    # zoom / punch: cumulative scale over a sliding 0.35 s window (not across a cut)
    win = max(3, int(0.35 * fps)); cutset = set(cuts)
    i = 0
    zooms = []
    while i < n - win:
        if any((i + k) in cutset or (i + k + 1) in cutset for k in range(win)):
            i += 1; continue
        z = float(m["kz"][i + 1:i + win + 1].sum())
        if abs(z) > 0.04:
            j = i + win
            while j < n - 1 and (j + 1) not in cutset and abs(m["kz"][j + 1]) > 0.0012 and np.sign(m["kz"][j + 1]) == np.sign(z):
                j += 1
            tot = float(m["kz"][i + 1:j + 1].sum())
            zooms.append(dict(t=round(i / fps, 2), type="punch_in" if tot > 0 else "punch_out", dur=round((j - i + 1) / fps, 2), amt=round(abs(tot), 3)))
            i = j + 1
        else:
            i += 1
    ev += zooms
    # shake: high-frequency translation energy
    hp = m["dx"] - np.convolve(m["dx"], np.ones(5) / 5, "same"); hq = m["dy"] - np.convolve(m["dy"], np.ones(5) / 5, "same")
    en = np.hypot(hp, hq)
    for i in range(3, n - 3):
        if en[i - 2:i + 3].mean() > 3.2 and m["mag"][i] < 14:
            if not ev or ev[-1]["type"] != "shake" or i / fps - ev[-1]["t"] > 0.5:
                ev.append(dict(t=round(i / fps, 2), type="shake"))
    ev.sort(key=lambda e: e["t"])
    return cuts, ev


def grade_stats(m):
    fr = m["fr"]
    idx = np.linspace(0, len(fr) - 1, min(30, len(fr))).astype(int)
    lab = np.array([cv2.cvtColor(fr[i], cv2.COLOR_BGR2LAB) for i in idx]).astype(np.float32)
    L = lab[..., 0] * 100 / 255; a = lab[..., 1] - 128; b = lab[..., 2] - 128
    sh = L < 35; hi = L > 65
    def mean(x, mk): return float(x[mk].mean()) if mk.any() else 0.0
    Yv = m["Y"]
    return dict(Y_mean=round(float(Yv.mean()), 1), Y_p5=round(float(np.percentile(Yv, 5)), 1), Y_p95=round(float(np.percentile(Yv, 95)), 1),
                sat=round(float(m["S"].mean()), 3), warm_RB=round(float((m["R"] - m["B"]).mean()), 1),
                shadow_ab=[round(mean(a, sh), 1), round(mean(b, sh), 1)], high_ab=[round(mean(a, hi), 1), round(mean(b, hi), 1)],
                contrast=round(float(L.std()), 1), skin=round(float(np.median(m["skin"])), 3), sharp=round(float(np.median(m["sharp"])), 1))


def palette(m, k=5):
    idx = np.linspace(0, len(m["fr"]) - 1, min(40, len(m["fr"]))).astype(int)
    px = np.concatenate([cv2.resize(m["fr"][i], (30, 54)).reshape(-1, 3) for i in idx]).astype(np.float32)
    _, lab, c = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0), 2, cv2.KMEANS_PP_CENTERS)
    cnt = np.bincount(lab.flatten(), minlength=k)
    o = np.argsort(-cnt)
    return ["#%02x%02x%02x" % tuple(int(v) for v in c[j][::-1]) + f":{cnt[j] / cnt.sum():.2f}" for j in o]


def whisper_words(wav):
    out = run(["whisper-cli", "-m", MODEL, "-f", wav, "-l", "auto", "-ml", "1", "-sow", "-np", "--prompt", PROMPT]).stdout
    ws = []
    for l in out.splitlines():
        mm = re.match(r"\[(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)\]\s+(.*)", l)
        if mm and mm.group(7).strip() and not mm.group(7).strip().startswith("["):
            a = int(mm[1]) * 3600 + int(mm[2]) * 60 + float(mm[3]); b = int(mm[4]) * 3600 + int(mm[5]) * 60 + float(mm[6])
            ws.append((round(a, 2), round(b, 2), mm.group(7).strip()))
    clean = []
    for w in ws:
        if len(clean) >= 6 and all(clean[-k][2] == w[2] for k in (1, 2, 3)):
            continue
        clean.append(w)
    return clean


def audio_metrics(f, dur, od, ws):
    import librosa
    wav = os.path.join(od, "a22.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "22050", "-ac", "1", wav])
    y, sr = librosa.load(wav, sr=22050, mono=True)
    out = {}
    e = run(["ffmpeg", "-i", f, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", e); out["lufs"] = float(m[-1]) if m else None
    hop = 512
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    speech = np.zeros(len(t), bool)
    for a, b, _ in ws:
        speech[(t >= a - 0.03) & (t <= b + 0.05)] = True
    db = 20 * np.log10(rms + 1e-6)
    out["speech_db"] = round(float(db[speech].mean()), 1) if speech.any() else None
    gap = ~speech
    if gap.sum() > 5:
        out["gap_db_p50"] = round(float(np.median(db[gap])), 1); out["gap_db_p10"] = round(float(np.percentile(db[gap], 10)), 1)
    out["bed_below_voice_db"] = round(out["speech_db"] - out["gap_db_p10"], 1) if out.get("speech_db") is not None and out.get("gap_db_p10") is not None else None
    out["music_bed"] = bool(out.get("gap_db_p10") is not None and out["gap_db_p10"] > -48)
    # tempo of the whole mix
    try:
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
        out["tempo"] = round(float(np.atleast_1d(tempo)[0]), 0)
        beat_t = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
    except Exception:
        out["tempo"] = None; beat_t = np.array([])
    # sound events outside speech: spectral-flux onsets, classified by band / noise-ness / decay
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=1024)
    low = S[freqs < 150].sum(0); mid = S[(freqs >= 150) & (freqs < 3000)].sum(0); hi = S[freqs >= 3000].sum(0)
    tot = low + mid + hi + 1e-9
    flat = librosa.feature.spectral_flatness(S=S)[0]
    cent = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
    onset = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S), sr=sr, hop_length=hop)
    thr = np.median(onset) + 2.2 * np.std(onset)
    peaks = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=8, post_avg=8, delta=thr * 0.35, wait=int(0.12 * sr / hop))
    events = []
    for p in peaks:
        if p >= len(t) or onset[p] < thr:
            continue
        tt = float(t[p])
        if speech[min(p, len(speech) - 1)]:
            continue          # inside a word: skip (voice onsets)
        seg = slice(p, min(len(t), p + int(0.35 * sr / hop)))
        pre = slice(max(0, p - 6), p)
        lowr = float(low[seg].mean() / tot[seg].mean()); hir = float(hi[seg].mean() / tot[seg].mean())
        fl = float(flat[seg].mean()); ce = float(cent[seg].mean())
        env = rms[p:min(len(rms), p + int(0.7 * sr / hop))]
        decay = float((env > env.max() * 0.35).sum() * hop / sr) if len(env) else 0
        rise = float(np.argmax(rms[max(0, p - int(0.6 * sr / hop)):p + 1]) if p else 0)
        if lowr > 0.45 and decay < 0.45: cls = "impact"
        elif fl > 0.12 and decay >= 0.18: cls = "whoosh"
        elif hir > 0.35 and decay < 0.18: cls = "click"
        elif ce > 2500 and decay < 0.3: cls = "pop/ding"
        else: cls = "hit/other"
        on_beat = bool(len(beat_t) and np.min(np.abs(beat_t - tt)) < 0.04)
        events.append(dict(t=round(tt, 2), type="sfx:" + cls, on_beat=on_beat, strength=round(float(onset[p] / thr), 1)))
    out["sfx_events"] = len(events)
    out["sfx_per_10s"] = round(len(events) / max(dur, 1) * 10, 1)
    cl = {}
    for e_ in events:
        cl[e_["type"]] = cl.get(e_["type"], 0) + 1
    out["sfx_classes"] = cl
    # tail after last word
    out["tail_s"] = round(dur - ws[-1][1], 2) if ws else None
    return out, events, (y, sr, t, db, speech, beat_t)


def spectrogram_png(path, y, sr, ws, evs, cuts, dur):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt, librosa
    S = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=1024, hop_length=256)), ref=np.max)
    fig, ax = plt.subplots(figsize=(14, 3.2))
    ax.imshow(S, origin="lower", aspect="auto", extent=[0, len(y) / sr, 0, sr / 2], cmap="magma", vmin=-70, vmax=0)
    ax.set_ylim(0, 8000)
    for a, b, w in ws:
        ax.axvspan(a, b, ymin=0.95, ymax=1, color="#7fdc7f")
    for e in evs:
        ax.axvline(e["t"], color="#46d0ff", lw=0.8, alpha=0.8)
    for c in cuts:
        ax.axvline(c, color="#ffd23f", lw=0.6, alpha=0.5, ls=":")
    ax.set_xlim(0, dur); ax.set_xlabel("s  (green = speech, cyan = non-speech sound event, yellow dotted = video cut)")
    fig.tight_layout(); fig.savefig(path, dpi=70); plt.close(fig)


def tile(imgs, cols, pad=4, bg=(18, 18, 18)):
    h, w = imgs[0].shape[:2]
    rows = (len(imgs) + cols - 1) // cols
    out = np.full((rows * (h + pad) + pad, cols * (w + pad) + pad, 3), bg, np.uint8)
    for k, im in enumerate(imgs):
        r, c = divmod(k, cols)
        out[pad + r * (h + pad):pad + r * (h + pad) + h, pad + c * (w + pad):pad + c * (w + pad) + w] = cv2.resize(im, (w, h))
    return out


def label(im, text):
    im = im.copy()
    cv2.putText(im, text, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 3, cv2.LINE_AA)
    cv2.putText(im, text, (4, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
    return im


def hires_frames(f, times, w=190):
    out = []
    for t in times:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, t):.3f}", "-i", f, "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "mjpeg", "-"], capture_output=True)
        im = cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR) if p.stdout else None
        out.append(im)
    h0 = next((x.shape[0] for x in out if x is not None), 338)
    return [x if x is not None else np.zeros((h0, w, 3), np.uint8) for x in out]


def caption_stats(info):
    cap = info.get("description") or ""
    tags = re.findall(r"#(\w+)", cap)
    emoji = len(re.findall(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", cap))
    kw = re.search(r"comment\s+[\"“']?([A-Za-z0-9_ ]{2,20}?)[\"”']?(?:\s|$|[.,!])", cap, re.I)
    first = cap.strip().split("\n")[0][:140]
    comments = info.get("comments") or []
    cm = [dict(a=c.get("author"), t=(c.get("text") or "")[:120], likes=c.get("like_count")) for c in comments[:12]]
    # keyword-comment pattern: many comments that are one identical short word
    words = [re.sub(r"\W", "", (c.get("text") or "").lower()) for c in comments]
    top = max(set(words), key=words.count) if words else ""
    kwshare = round(words.count(top) / len(words), 2) if words and top else 0
    likes = info.get("like_count") or 0; cc = info.get("comment_count") or 0
    ts = info.get("timestamp") or 0
    import time
    return dict(user=info.get("channel") or info.get("uploader"), likes=likes, comments=cc, cm_per_like=round(cc / likes, 3) if likes else None,
                age_days=round((time.time() - ts) / 86400, 1) if ts else None, caption_len=len(cap), hashtags=tags, n_tags=len(tags), emoji=emoji,
                first_line=first, cta_keyword=(kw.group(1).strip() if kw else None), keyword_comment_share=kwshare, keyword_comment_top=top, top_comments=cm)


def analyze(args):
    d, rid = args
    f = os.path.join(d, "src", rid + ".mp4")
    od = os.path.join(d, "analysis", rid); os.makedirs(od, exist_ok=True)
    if os.path.exists(os.path.join(od, "metrics.json")):
        return rid, "cached"
    info = json.load(open(os.path.join(d, "src", rid + ".info.json")))
    pr = probe(f); fps = 30.0
    w = W_SMALL; h = int(round(pr["h"] * w / pr["w"] / 2) * 2)
    fr = read_frames(f, w, h, int(fps))
    m = video_metrics(fr, fps)
    cuts, ev = detect_events(m, fps)
    dur = pr["dur"]
    # speech
    wav = os.path.join(od, "a16.wav"); run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "16000", "-ac", "1", wav])
    ws = whisper_words(wav); os.remove(wav)
    with open(os.path.join(od, "transcript.txt"), "w") as t:
        t.write(" ".join(x[2] for x in ws) + "\n\n" + "\n".join(f"{x[0]:.2f}-{x[1]:.2f} {x[2]}" for x in ws))
    am, aev, (y, sr, tt, db, speech, beat_t) = audio_metrics(f, dur, od, ws)
    os.remove(os.path.join(od, "a22.wav"))
    allev = sorted(ev + aev, key=lambda e: e["t"])
    kinds = {}
    for e in ev:
        kinds[e["type"]] = kinds.get(e["type"], 0) + 1
    shots = np.diff([0] + [c / fps for c in cuts] + [dur])
    row = dict(id=rid, duration=round(dur, 1), w=pr["w"], h=pr["h"], src_fps=round(pr["fps"], 1), kbps=pr["kbps"], codec=pr["codec"],
               cuts=len(cuts), cuts_per_10s=round(len(cuts) / dur * 10, 1), avg_shot_s=round(float(shots.mean()), 2), median_shot_s=round(float(np.median(shots)), 2),
               first_cut_s=round(cuts[0] / fps, 2) if cuts else None, events=kinds, flash=kinds.get("flash", 0), whip=kinds.get("whip", 0),
               punch_in=kinds.get("punch_in", 0), punch_out=kinds.get("punch_out", 0), shake=kinds.get("shake", 0),
               grade=grade_stats(m), palette=palette(m), words=len(ws), wpm=round(len(ws) / (dur / 60)) if dur else 0,
               first_word_s=ws[0][0] if ws else None, speech_share=round(sum(x[1] - x[0] for x in ws) / dur, 2) if ws else 0,
               hook_text=" ".join(x[2] for x in ws if x[0] < 3.0), text=" ".join(x[2] for x in ws)[:700], audio=am, caption=caption_stats(info))
    json.dump(row, open(os.path.join(od, "metrics.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(allev, open(os.path.join(od, "timeline.json"), "w"), indent=0)
    # ---- pictures
    hook_t = [0, 0.15, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]
    ov_t = [dur * (i + 0.5) / 24 for i in range(24)]
    hk = [label(x, f"{t:.2f}") for x, t in zip(hires_frames(f, hook_t), hook_t)]
    ov = [label(x, f"{t:.1f}") for x, t in zip(hires_frames(f, ov_t), ov_t)]
    cv2.imwrite(os.path.join(od, "view.jpg"), np.vstack([tile(hk, 8), tile(ov, 8)]), [cv2.IMWRITE_JPEG_QUALITY, 82])
    tr = [e for e in ev if e["type"] in ("flash", "whip", "punch_in", "punch_out", "shake")]
    ct = [e for e in ev if e["type"] == "cut"]
    pick = tr[:8] + ct[:max(0, 12 - len(tr[:8]))]
    pick.sort(key=lambda e: e["t"])
    cells = []
    for e in pick[:12]:
        times = [e["t"] + k / fps for k in (-2, -1, 0, 1, 2, 4)]
        row_ = [label(x, f"{e['type'][:5]} {e['t']:.1f}s{'' if k != 0 else ''}") if j == 0 else x for j, (x, k) in enumerate(zip(hires_frames(f, times, 110), (-2, -1, 0, 1, 2, 4)))]
        cells.append(tile(row_, 6, pad=2))
    if cells:
        wmax = max(c.shape[1] for c in cells)
        cells = [np.pad(c, ((0, 0), (0, wmax - c.shape[1]), (0, 0))) for c in cells]
        half = (len(cells) + 1) // 2
        a = np.vstack(cells[:half]); b = np.vstack(cells[half:]) if cells[half:] else np.zeros_like(a)
        if b.shape[0] < a.shape[0]: b = np.pad(b, ((0, a.shape[0] - b.shape[0]), (0, 0), (0, 0)))
        cv2.imwrite(os.path.join(od, "events.jpg"), np.hstack([a, b]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    spectrogram_png(os.path.join(od, "audio.png"), y, sr, ws, aev, [c / fps for c in cuts], dur)
    return rid, "ok"


def main():
    d = sys.argv[1]
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    ids = sorted(x[:-4] for x in os.listdir(os.path.join(d, "src")) if x.endswith(".mp4") and "." not in x[:-4].replace("-", "").replace("_", "") and os.path.exists(os.path.join(d, "src", x[:-4] + ".info.json")))
    if only:
        ids = [i for i in ids if i in only]
    with ProcessPoolExecutor(workers) as ex:
        for rid, st in ex.map(analyze, [(d, i) for i in ids]):
            print(rid, st, flush=True)
    rows = [json.load(open(os.path.join(d, "analysis", i, "metrics.json"))) for i in ids if os.path.exists(os.path.join(d, "analysis", i, "metrics.json"))]
    json.dump(rows, open(os.path.join(d, "analysis", "all_metrics.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
