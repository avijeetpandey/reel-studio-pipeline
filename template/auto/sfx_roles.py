#!/usr/bin/env python3
"""Build sfx/ROLES.json: every sound in the library filed under the JOB it does on screen (not under its filename).

  python3 -I sfx_roles.py            (re-run after fetch_free_audio.py adds sounds)

Roles (what autodirect.py asks for):  whip · whoosh · hit_soft · impact · riser · pop · tick · click · notif · success · error · negation · shutter
                                      · glitch · paper · scratch · sparkle
Candidates = the creator's approved synthesized originals first (they stay the defaults), then Mixkit sounds (free, no attribution) that fit the role's
duration window and keywords. Each candidate carries peak_db so the plan can level every sound to the same peak before applying the role volume.
A reel picks ONE candidate per role (seeded by the reel name) and uses it the same way all reel long (WINNING_PATTERNS §14: signature sounds).
"""
import json, os, re, subprocess

SFX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "composition", "assets", "audio", "sfx")
IDX = os.path.join(SFX, "mixkit", "mixkit_index.json")

# role: (categories, title keywords that help, title keywords that disqualify, min dur, max dur, synthesized defaults)
ROLES = {
    "whip":     (["whoosh", "woosh", "swoosh", "swish", "sweep", "sweeping", "slide"], ["fast", "swipe", "quick", "swish", "zoom", "transition"], ["long", "tunnel", "trailer", "ghost", "magic", "rocket", "cinematic", "epic"], 0.2, 0.9, ["whip", "whoosh-short"]),
    "whoosh":   (["whoosh", "woosh", "swoosh", "sweep", "sweeping", "spin"], ["air", "swoosh", "passing", "transition"], ["trailer", "epic", "stutter", "rocket", "ghost", "tunnel"], 0.7, 2.0, ["whoosh-air", "whoosh", "whoosh-cinematic"]),
    "hit_soft": (["hit", "thud", "stomp", "punch", "tap", "drop"], ["soft", "light", "thud", "tap", "low", "bass", "wood", "punch"], ["metal", "gun", "explosion", "sword", "scream", "glass", "crash", "cymbal"], 0.1, 0.8, ["soft-hit", "soft-pluck"]),
    "impact":   (["impact", "boom", "drop", "crash", "bass", "cinematic", "hit"], ["impact", "boom", "bass", "deep", "drop", "cinematic", "hit"], ["gun", "scream", "sword", "metal", "car", "thunder", "bomb", "explosion", "glass"], 0.5, 2.6, ["impact-bass-1", "impact-bass-2", "hit-heavy", "bass-drop"]),
    "riser":    (["swell", "cinematic", "whoosh", "intro", "sci-fi"], ["swell", "riser", "build", "rise", "reverse", "tension", "suspense"], ["trailer", "epic", "horror", "scream"], 0.8, 3.2, ["riser", "reverse-swell", "riser-metal"]),
    "pop":      (["pop", "bubbles", "bleep", "cartoon", "cute", "squeak"], ["pop", "bubble", "blip", "bloop", "light", "ui"], ["fart", "scream", "cry", "laugh", "horse", "cow"], 0.04, 0.45, ["pop", "soft-pluck", "digital-tick"]),
    "tick":     (["click", "tap", "keyboard", "key", "mouse", "clock", "interface", "high-tech"], ["click", "tick", "key", "tap", "mouse", "button", "interface"], ["door", "lock", "camera", "typewriter"], 0.02, 0.25, ["digital-tick", "tick", "click-soft"]),
    "click":    (["click", "mouse", "tap", "interface", "keyboard"], ["click", "mouse", "tap", "button"], ["door", "lock"], 0.02, 0.3, ["mouse-click", "click", "click-soft"]),
    "notif":    (["notification", "alerts", "ding", "bell", "chimes", "alarm"], ["notification", "alert", "message", "ding", "bell", "chime", "ping"], ["church", "doorbell", "fire", "siren", "alarm", "police", "emergency"], 0.15, 1.4, ["notif-pop", "notification", "ping", "ding"]),
    "success":  (["correct", "ding", "coin", "arcade", "game-show", "magic", "sparkle"], ["correct", "success", "win", "coin", "bonus", "achievement", "level", "positive", "ding"], ["horror", "scary", "lose", "fail"], 0.3, 1.8, ["ui-success", "check-blip", "ding", "chime"]),
    "error":    (["error", "buzzer", "lose", "beep", "bleep", "alarm"], ["error", "wrong", "fail", "negative", "buzzer", "lose", "incorrect"], ["fire", "police", "siren"], 0.2, 1.2, ["error", "negation", "glitch-negative"]),
    "negation": (["error", "buzzer", "lose", "bleep", "glitch"], ["wrong", "negative", "fail", "bad", "buzz", "no"], ["fire", "siren", "police"], 0.15, 0.8, ["negation", "glitch-negative", "error"]),
    "shutter":  (["camera"], ["shutter", "photo", "click", "flash", "snap"], ["video", "movie", "projector"], 0.08, 0.7, ["camera-shutter", "camera-flash"]),
    "glitch":   (["glitch", "static", "interface", "high-tech", "technology", "rewind", "sci-fi"], ["glitch", "digital", "static", "data", "error", "tech", "robot"], ["engine", "horror"], 0.1, 1.2, ["glitch", "zap", "slice"]),
    "paper":    (["paper", "page"], ["paper", "page", "slide", "flip", "turn", "swipe"], [], 0.1, 1.2, ["paper-slide", "pen-scribble", "line-draw"]),
    "scratch":  (["dj-record-scratch", "rewind"], ["scratch", "record", "rewind", "tape"], [], 0.15, 2.0, []),
    "sparkle":  (["sparkle", "magic", "fairy", "chimes"], ["sparkle", "magic", "twinkle", "shine"], ["horror", "scary"], 0.3, 2.0, ["sparkle", "chime"]),
}


def probe(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r); m = re.search(r"max_volume: (-?[\d.]+) dB", r)
    return (int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0, float(m[1]) if m else -3.0)


def main():
    idx = json.load(open(IDX)) if os.path.exists(IDX) else {}
    os.makedirs(SFX, exist_ok=True)
    out = {}
    for role, (cats, good, bad, lo, hi, defaults) in ROLES.items():
        cands = []
        for name in defaults:
            f = os.path.join(SFX, name + ".mp3")
            if os.path.exists(f):
                d, pk = probe(f)
                cands.append(dict(file=name + ".mp3", dur=round(d, 2), peak_db=pk, src="original", score=100))
        scored = []
        for v in idx.values():
            if v["cat"] not in cats and not set(v.get("tags", [])) & set(cats):
                continue
            t = v["title"].lower()
            if any(b in t for b in bad) or not (lo <= v["duration"] <= hi):
                continue
            if v.get("lufs") is not None and v["lufs"] < -45:      # near-silent preview
                continue
            s = sum(2 for g in good if g in t) + (1 if v["cat"] == cats[0] else 0)
            scored.append((s, v))
        scored.sort(key=lambda x: (-x[0], x[1]["duration"]))
        for s, v in scored[:14]:
            cands.append(dict(file="mixkit/" + v["file"], dur=v["duration"], peak_db=v["peak_db"], src="mixkit", title=v["title"], score=s))
        out[role] = cands
    json.dump(out, open(os.path.join(SFX, "ROLES.json"), "w"), indent=1, ensure_ascii=False)
    for r, c in out.items():
        print(f"{r:9} {len(c):2} candidates · " + ", ".join(x["file"].replace("mixkit/", "")[:26] for x in c[:4]))


if __name__ == "__main__":
    main()
