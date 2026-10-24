#!/usr/bin/env python3
"""Measure reference reels: pacing, speech, hook, sound — so the pipeline learns from numbers, not vibes.

  python3 -I analyze_reference.py <dir with *.mp4> [--meta meta.json]

Per reel it writes <dir>/<code>/ : transcript.txt (word timings), sheet.jpg (16 evenly spaced frames),
hook.jpg (0, 0.4, 0.8, 1.2, 1.6, 2.0 s), and appends one row to <dir>/metrics.json:
  duration, cuts, cuts_per_min, avg_shot_s, first_cut_s, first_word_s, wpm, words, hook_text (first 2.5 s),
  first_sentence, loudness LUFS, speech_db vs gap_db (music level under the voice), music_bed (yes/no), gaps_over_0_5s.
Needs ffmpeg + whisper-cli (ggml-small.en). Pure python, no numpy.
"""
import json, os, re, subprocess, sys

MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.en.bin")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def duration(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).stdout.strip() or 0)


def cuts(f):
    out = run(["ffmpeg", "-i", f, "-vf", "scale=270:-2,select='gt(scene,0.28)',showinfo", "-an", "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"pts_time:([0-9.]+)", out)]


def words(f, wav):
    run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "16000", "-ac", "1", wav])
    out = run(["whisper-cli", "-m", MODEL, "-f", wav, "-ml", "1", "-sow", "-np"]).stdout
    ws = []
    for l in out.splitlines():
        m = re.match(r"\[(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)\]\s+(.*)", l)
        if m and m.group(7).strip() and not m.group(7).strip().startswith("["):
            a = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]); b = int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6])
            ws.append((round(a, 2), round(b, 2), m.group(7).strip()))
    # drop whisper loops (same phrase repeated back-to-back many times)
    clean = []
    for w in ws:
        if len(clean) >= 6 and all(clean[-k][2] == w[2] for k in (1, 2, 3)):
            continue
        clean.append(w)
    return clean


def level(f, a, b):
    if b - a < 0.08:
        return None
    out = run(["ffmpeg", "-v", "info", "-ss", f"{a:.2f}", "-t", f"{b - a:.2f}", "-i", f, "-af", "volumedetect", "-f", "null", "-"]).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", out)
    return float(m[1]) if m else None


def loudness(f):
    out = run(["ffmpeg", "-i", f, "-af", "ebur128", "-f", "null", "-"]).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else None


def sheets(f, d, dur, outdir):
    os.makedirs(outdir, exist_ok=True)
    ts = [round(dur * (i + 0.5) / 16, 2) for i in range(16)]
    sel = "+".join(f"between(t,{t},{t + 0.04})" for t in ts)
    run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", f"select='{sel}',scale=240:-2,tile=8x2:padding=4", "-frames:v", "1", "-fps_mode", "passthrough", os.path.join(outdir, "sheet.jpg")])
    hs = [0, 0.4, 0.8, 1.2, 1.6, 2.0]
    sel = "+".join(f"between(t,{t},{t + 0.04})" for t in hs)
    run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", f"select='{sel}',scale=300:-2,tile=6x1:padding=4", "-frames:v", "1", "-fps_mode", "passthrough", os.path.join(outdir, "hook.jpg")])


def main():
    d = sys.argv[1]
    meta = {}
    if "--meta" in sys.argv:
        meta = {m["c"]: m for m in json.load(open(sys.argv[sys.argv.index("--meta") + 1]))}
    rows = []
    for fn in sorted(x for x in os.listdir(d) if x.endswith(".mp4")):
        code = fn[:-4]; f = os.path.join(d, fn); od = os.path.join(d, code)
        os.makedirs(od, exist_ok=True)
        dur = duration(f); cs = [c for c in cuts(f) if 0.15 < c < dur - 0.1]
        ws = words(f, os.path.join(od, "a.wav"))
        with open(os.path.join(od, "transcript.txt"), "w") as t:
            t.write(" ".join(w[2] for w in ws) + "\n\n")
            for w in ws:
                t.write(f"{w[0]:.2f}-{w[1]:.2f} {w[2]}\n")
        text = " ".join(w[2] for w in ws)
        speech = sum(w[1] - w[0] for w in ws)
        gaps = [(ws[i][1], ws[i + 1][0]) for i in range(len(ws) - 1) if ws[i + 1][0] - ws[i][1] > 0.25]
        sp = [level(f, w[0], w[1]) for w in ws[:: max(1, len(ws) // 25)]]
        gp = [level(f, a + 0.05, b - 0.05) for a, b in gaps[:25]]
        sp = [x for x in sp if x is not None]; gp = [x for x in gp if x is not None]
        sdb = sum(sp) / len(sp) if sp else None; gdb = sum(gp) / len(gp) if gp else None
        first_sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0] if text else ""
        row = {
            "code": code, "user": meta.get(code, {}).get("u"), "likes": meta.get(code, {}).get("l"), "comments": meta.get(code, {}).get("cm"),
            "duration": round(dur, 1), "cuts": len(cs), "cuts_per_min": round(len(cs) / dur * 60, 1) if dur else 0,
            "avg_shot_s": round(dur / (len(cs) + 1), 2), "first_cut_s": cs[0] if cs else None,
            "first_word_s": ws[0][0] if ws else None, "words": len(ws), "wpm": round(len(ws) / (dur / 60), 0) if dur else 0,
            "speech_share": round(speech / dur, 2) if dur else 0,
            "hook_text": " ".join(w[2] for w in ws if w[0] < 2.5), "first_sentence": first_sentence[:160],
            "lufs": loudness(f), "speech_db": round(sdb, 1) if sdb is not None else None, "gap_db": round(gdb, 1) if gdb is not None else None,
            "music_bed": (gdb is not None and gdb > -42), "gaps_over_0_5s": sum(1 for a, b in gaps if b - a > 0.5),
        }
        if row["speech_db"] is not None and row["gap_db"] is not None:
            row["bed_below_voice_db"] = round(row["speech_db"] - row["gap_db"], 1)
        sheets(f, d, dur, od)
        os.remove(os.path.join(od, "a.wav"))
        rows.append(row)
        print(json.dumps(row), flush=True)
    json.dump(rows, open(os.path.join(d, "metrics.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
