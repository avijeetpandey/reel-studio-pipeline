#!/usr/bin/env python3
"""Build a cartoon Short from a voiceover + a scene list, all open source (ffmpeg, whisper.cpp, HyperFrames, SVG).

  python3 -I build_cartoon.py <project dir> [--transcribe] [--music]      # --transcribe = print word times only. project/ has voice.(wav|m4a|mp3|aiff) + scenes.json

scenes.json = {"title": "...", "character": {"skin","hair","tee","beard"}, "scenes": [
   {"from": 0.0, "to": 3.1, "kicker": "// 01 · the hook", "pose": "point",
    "stage": {"type": "big|card|phone|terminal|checklist|flow|counter|stamp", ...}, "accent": ["word", ...]}, ...]}
Writes index.html + HyperFrames scaffold + assets/ (voice.wav, words.json, visemes.json, sfx, optional bgm).
Then: cd <project> && npx --yes hyperframes@0.8.209 check && npx --yes hyperframes@0.8.209 render -o renders/draft.mp4 -q draft
"""
import array, json, math, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..")
SFX = os.path.join(TPL, "composition", "assets", "audio", "sfx")
MODEL = os.path.expanduser("~/.cache/hyperframes/whisper/models/ggml-small.en.bin")


def run(*a):
    return subprocess.run(a, capture_output=True, text=True)


def to_wav(src, dst):
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-ar", "16000", "-ac", "1", dst)


def transcribe(wav):
    out = run("whisper-cli", "-m", MODEL, "-f", wav, "-ml", "1", "-sow", "-np").stdout
    ws = []
    for l in out.splitlines():
        m = re.match(r"\[(\d+):(\d+):([\d.]+) --> (\d+):(\d+):([\d.]+)\]\s+(.*)", l)
        if m and m.group(7).strip() and not m.group(7).strip().startswith("["):
            ws.append([round(int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), 2), round(int(m[4]) * 3600 + int(m[5]) * 60 + float(m[6]), 2), m.group(7).strip()])
    return ws


VOW = {"a": "D", "e": "C", "i": "B", "o": "E", "u": "C", "y": "B"}
DIG = {"th": "H", "sh": "B", "ch": "B", "ng": "B", "ee": "B", "oo": "F", "ou": "E", "ow": "E", "oa": "E", "ai": "C", "ay": "C", "ea": "B", "ie": "B", "oi": "E", "ph": "G", "wh": "F", "qu": "F"}
CON = {"m": "A", "b": "A", "p": "A", "f": "G", "v": "G", "l": "H", "w": "F", "r": "B", "s": "B", "z": "B", "t": "B", "d": "B", "n": "B", "k": "B", "g": "B", "j": "B", "c": "B", "q": "B", "x": "B"}


def word_shapes(word):
    """Letters -> mouth shapes (A closed, B slit, C mid, D wide, E round, F pucker, G teeth-on-lip, H tongue) with weights."""
    w = re.sub(r"[^a-z]", "", word.lower())
    if w.endswith("e") and len(w) > 2 and w[-2] not in "aeiou":
        w = w[:-1]
    out, i = [], 0
    while i < len(w):
        d = w[i:i + 2]
        if d in DIG: out.append((DIG[d], 2.4 if d[0] in "aeiou" else 1.0)); i += 2; continue
        c = w[i]
        if c in VOW: out.append((VOW[c], 2.0))
        elif c in CON: out.append((CON[c], 0.9 if CON[c] in "AGFH" else 0.7))
        i += 1
    merged = []
    for s, wt in out:
        if merged and merged[-1][0] == s: merged[-1][1] += wt
        else: merged.append([s, wt])
    return merged or [["B", 1.0]]


def levels(wav, hop=0.04):
    pcm = array.array("h", run_bytes("ffmpeg", "-v", "error", "-i", wav, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"))
    n = int(16000 * hop); db = []
    for k in range(len(pcm) // n):
        seg = pcm[k * n:(k + 1) * n]
        db.append(20 * math.log10(math.sqrt(sum(x * x for x in seg) / n) / 32768 + 1e-9))
    top = sorted(db)[int(len(db) * 0.95)]
    return [d - top for d in db], hop


def lipsync(words, wav):
    """Word timings (whisper) + letter->shape mapping + loudness correction -> [[t, shape]] (X = rest). Rhubarb would be more exact; this needs no download."""
    rel, hop = levels(wav)
    lvl = lambda t: rel[min(len(rel) - 1, max(0, int(t / hop)))]
    cues = []
    for wi, (a, b, text) in enumerate(words):
        sh = word_shapes(text); tot = sum(w for _, w in sh); b = max(b - 0.02, a + 0.05); t = a
        for s, wt in sh:
            d = (b - a) * wt / tot; mid = lvl(t + d / 2)
            if mid < -34: s = "X"
            elif mid < -26 and s in "DCEFH": s = "B"
            elif mid < -20 and s == "D": s = "C"
            cues.append([round(t, 3), s]); t += d
        nxt = words[wi + 1][0] if wi + 1 < len(words) else 1e9
        if nxt - b > 0.12 or re.search(r"[.?!]$", text): cues.append([round(b, 3), "X"])
    out = []
    for t, s in cues:                              # drop shapes shorter than 50 ms (except the closed A) and repeats
        if out and out[-1][1] == s: continue
        if out and t - out[-1][0] < 0.05 and out[-1][1] != "A" and s != "X": out[-1][1] = s; continue
        out.append([t, s])
    return [[0.0, "X"]] + out


def run_bytes(*a):
    return subprocess.run(a, capture_output=True).stdout


CSS = """
:root{--paper:#e8ecef;--ink:#12171c;--accent:#ee4b2b;--hi:#ffd84a;--ok:#1f9d63;--mute:#a3acb3}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--paper)}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Archivo,"Helvetica Neue",Arial,sans-serif;color:var(--ink);
  background:var(--paper) radial-gradient(rgba(18,23,28,.07) 2px,transparent 2.5px) 0 0/34px 34px}
#kick,#brand{position:absolute;top:64px;font:600 26px "JetBrains Mono",ui-monospace,monospace;color:#7d8890;letter-spacing:.04em}
#kick{left:70px}#brand{right:70px}
#pbar{position:absolute;left:0;top:0;width:1080px;height:9px;background:var(--accent);transform-origin:0 50%}
.cap{position:absolute;left:70px;right:70px;top:130px;font-weight:800;font-size:88px;line-height:1.08;letter-spacing:-.015em;text-wrap:balance}
.cap .w{color:var(--mute)}
.cap .a{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;font-size:108px}
.stg{position:absolute;left:90px;right:90px;top:400px;height:610px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px}
em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-weight:400;color:var(--accent)}
.big{font-weight:900;font-size:200px;line-height:.94;letter-spacing:-.035em;text-align:center}
.big em{font-size:236px}
.card{width:100%;background:#fff;border:5px solid var(--ink);border-radius:28px;box-shadow:12px 12px 0 var(--ink);padding:44px 50px}
.ct{font-weight:800;font-size:62px;line-height:1.1}
.cb{font-weight:500;font-size:44px;line-height:1.3;margin-top:16px;color:#3a444c}
.ck{display:flex;align-items:center;gap:26px;font-weight:700;font-size:48px;margin-top:26px}
.bx{width:48px;height:48px;border:5px solid var(--ink);border-radius:12px;background:#fff;flex:none}
.stamp{font-weight:900;font-size:112px;line-height:1;color:var(--accent);border:12px solid var(--accent);border-radius:20px;padding:10px 40px;text-transform:uppercase;letter-spacing:.02em;transform:rotate(-8deg)}
.counter{text-align:center}.num{font-weight:900;font-size:270px;line-height:1;letter-spacing:-.04em}.lab{font-weight:700;font-size:56px;color:#3a444c;margin-top:6px}
.phone{width:340px;height:500px;border:14px solid var(--ink);border-radius:64px;background:#fff;position:relative;overflow:hidden;box-shadow:12px 12px 0 var(--ink)}
.notch{position:absolute;left:50%;top:10px;width:120px;height:26px;margin-left:-60px;background:var(--ink);border-radius:20px}
.screen{padding:70px 18px 18px;display:flex;flex-direction:column;gap:14px}
.msg{max-width:80%;padding:14px 20px;border-radius:26px;font-weight:600;font-size:32px;line-height:1.2}
.msg.me{align-self:flex-end;background:#1f9d63;color:#fff;border-bottom-right-radius:8px}.msg.them{align-self:flex-start;background:#e7ebee;border-bottom-left-radius:8px}
.tk{display:block;font-size:24px;opacity:.85;margin-top:4px;text-align:right}
.term{width:100%;background:#12171c;border-radius:26px;box-shadow:12px 12px 0 var(--accent);overflow:hidden}
.bar{height:52px;background:#232b33;display:flex;gap:12px;align-items:center;padding-left:22px}.bar i{width:18px;height:18px;border-radius:50%;background:#56626b}
.tb{padding:30px 34px;display:flex;flex-direction:column;gap:14px}.tl{font:500 38px/1.25 "JetBrains Mono",ui-monospace,monospace;color:#cfe9d8;white-space:pre-wrap;word-break:break-word}
.flow{display:flex;flex-direction:column;align-items:center;gap:6px;width:100%}.node{width:100%;text-align:center;background:#fff;border:5px solid var(--ink);border-radius:22px;padding:22px;font-weight:800;font-size:52px;box-shadow:8px 8px 0 var(--ink)}
.ar{font-size:54px;font-weight:900;color:var(--accent);line-height:1}
#avi{filter:drop-shadow(0 10px 0 rgba(18,23,28,.0))}
"""

HTML = """<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Archivo:wght@500;700;800;900&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@500;600&display=swap">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>/*CSS*/</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="/*TOTAL*/" data-width="1080" data-height="1920">
<audio id="voice" src="assets/audio/voice.wav" data-start="0" data-duration="/*TOTAL*/" data-track-index="1" data-volume="1"></audio>
/*AUDIO*/
</div>
<svg width="0" height="0" style="position:absolute"><defs><g id="avi-art">/*ART*/</g></defs></svg>
<script>window.CARTOON=/*DATA*/;</script>
<script>/*ENGINE*/</script>
</body></html>
"""


def art():
    """Traced vector of the creator's own cartoon (rig/avi_art.svg): paths only, numbers rounded to 1 decimal to keep the page light."""
    s = open(os.path.join(HERE, "rig", "avi_art.svg"), encoding="utf-8").read()
    s = re.sub(r"</?svg[^>]*>|<\?xml[^>]*\?>|<!--.*?-->", "", s, flags=re.S)
    return re.sub(r"(\d+\.\d)\d+", r"\1", s)


def sfx_cues(scenes):
    cues = []
    for i, sc in enumerate(scenes):
        t0, t1, st = sc["from"], sc["to"], sc.get("stage")
        if st:
            cues.append(("hit-heavy" if st["type"] == "stamp" else "pop", t0 + 0.05, 0.5 if st["type"] == "stamp" else 0.3))
            if st["type"] == "checklist":
                n, span = len(st.get("items", [])), max(0.6, t1 - t0 - 0.9)
                cues += [("check-blip", t0 + 0.5 + span * k / max(1, n) + 0.35, 0.3) for k in range(n)]
        cues += [tuple(x) + (0.35,) * (3 - len(x)) for x in sc.get("sfx", [])]
        if i:
            cues.append(("paper-slide", t0, 0.22))
    return cues


def main():
    proj = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(proj, "assets", "audio", "sfx"), exist_ok=True)
    voice = next(os.path.join(proj, f) for f in sorted(os.listdir(proj)) if f.startswith("voice.") and not f.endswith(".json"))
    wav = os.path.join(proj, "assets", "audio", "voice.wav")
    run("ffmpeg", "-v", "error", "-y", "-i", voice, "-ar", "48000", "-ac", "1", wav)
    w16 = os.path.join(proj, "assets", "voice16.wav"); to_wav(voice, w16)
    dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav).stdout.strip())
    total = round(dur + 0.4, 2)
    words = transcribe(w16)
    if "--transcribe" in sys.argv:          # step 3 of the skill: print word times to write scenes.json from
        json.dump(words, open(os.path.join(proj, "assets", "words.json"), "w"))
        print(f"{dur:.2f}s  " + " ".join(f"{a}:{t}" for a, _, t in words)); return
    spec = json.load(open(os.path.join(proj, "scenes.json"), encoding="utf-8"))
    vis = lipsync(words, w16)
    json.dump(words, open(os.path.join(proj, "assets", "words.json"), "w")); json.dump(vis, open(os.path.join(proj, "assets", "visemes.json"), "w"))
    scenes = spec["scenes"]; scenes[-1]["to"] = max(scenes[-1]["to"], total)
    cues, audio = sfx_cues(scenes), []
    for k, (name, t, vol) in enumerate(cues):
        if not os.path.exists(os.path.join(SFX, name + ".mp3")): print("warning: missing sfx", name, "- run template/scripts/make_sfx.py", file=sys.stderr); continue
        shutil.copy(os.path.join(SFX, name + ".mp3"), os.path.join(proj, "assets", "audio", "sfx", name + ".mp3"))
        audio.append(f'<audio id="sfx{k}" src="assets/audio/sfx/{name}.mp3" data-start="{t:.2f}" data-duration="1.2" data-track-index="{10 + k % 6}" data-volume="{vol}"></audio>')
    if "--music" in sys.argv:
        subprocess.run([sys.executable, "-I", os.path.join(TPL, "scripts", "pick_music.py"), "--len", str(total), "--out", os.path.join(proj, "assets", "audio", "bgm.mp3")], check=True)
        audio.append(f'<audio id="bgm" src="assets/audio/bgm.mp3" data-start="0" data-duration="{total}" data-track-index="2" data-volume="0.14" data-fx-carve=\'{{"enabled":true,"sources":["voice"],"strength":0.8}}\'></audio>')
    data = {"brand": spec.get("brand", ""), "total": total, "character": spec.get("character", {}), "words": words, "visemes": vis, "scenes": scenes}
    html = (HTML.replace("/*CSS*/", CSS).replace("/*TOTAL*/", str(total)).replace("/*AUDIO*/", "\n".join(audio))
            .replace("/*DATA*/", json.dumps(data, ensure_ascii=False)).replace("/*ART*/", art()).replace("/*ENGINE*/", open(os.path.join(HERE, "engine.js"), encoding="utf-8").read()))
    open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(html)
    for f, body in {"hyperframes.json": {"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry", "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}},
                    "meta.json": {"id": os.path.basename(proj), "name": spec.get("title", os.path.basename(proj))},
                    "package.json": {"name": os.path.basename(proj).replace("_", "-"), "private": True, "type": "module"}}.items():
        if not os.path.exists(os.path.join(proj, f)):
            json.dump(body, open(os.path.join(proj, f), "w"), indent=2)
    print(f"{proj}/index.html  {total}s  {len(words)} words  {len(vis)} mouth changes  {len(cues)} sfx")


if __name__ == "__main__":
    main()
