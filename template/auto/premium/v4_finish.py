"""v4_finish.py — Round 17 finishing pass, default since 22 Nov 2026 (approved on the first test reel).

autodirect.py calls finish(plan, joins, sents, end) after the premium plan is built (KINETIC_V=3 skips it):
  transitions  one at every idea change: a join that starts a sentence, >= 2.2 s after the last one, none in the first 3 s or last 4 s;
               alternating whip (h/v) and zoomBlur
  sound        a shared earshot kit (MIT, Leonxlnx/earshot; rendered once into composition/assets/audio/sfx/earshot/, CPU, offline),
               every cue placed by the sound's PEAK so the hit lands on the frame: whoosh per cut, blip per big word, boom on a spotlight,
               riser -> boom -> shine on the hero word, keystrokes + a knock on the search card
Falls back to the plan's own ROLES.json sounds when earshot is not installed (tools/ext/earshot/.venv).
"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(HERE))
KIT = os.path.join(T, "composition", "assets", "audio", "sfx", "earshot")
EARSHOT = os.path.join(os.path.dirname(T), "tools", "ext", "earshot", ".venv", "bin", "earshot")
# name -> earshot design (pinned so every reel has the same palette); peak times are read back from earshot's report
SOUNDS = {"whoosh_fast": "sound=whoosh/fast", "whoosh_pass": "sound=whoosh/pass", "boom": "sound=boom/deep", "riser": "sound=riser/dark",
          "pop": "sound=pop/soft", "keys": "sound=keyboard/mechanical", "ding": "sound=notify/single", "shine": "sound=shine/sweep", "blip": "sound=blip/soft"}


def kit():
    """render the kit once; returns {name: peak_s} or None when earshot is unavailable"""
    pk_file = os.path.join(KIT, "peaks.json")
    peaks = json.load(open(pk_file)) if os.path.exists(pk_file) else {}
    if all(n in peaks and os.path.exists(os.path.join(KIT, n + ".wav")) for n in SOUNDS):
        return peaks
    if not os.path.exists(EARSHOT):
        return None
    os.makedirs(KIT, exist_ok=True)
    for n, q in SOUNDS.items():
        if n in peaks and os.path.exists(os.path.join(KIT, n + ".wav")):
            continue
        r = subprocess.run([EARSHOT, "make", q, "-o", os.path.join(KIT, n + ".wav")], capture_output=True, text=True)
        line = (r.stdout or "").splitlines()[0] if r.stdout else ""
        try:
            peaks[n] = float(line.split("peak at ")[1].split(" s")[0])
        except Exception:
            print("earshot failed for", n, r.stderr[-300:]); return None
    json.dump(peaks, open(pk_file, "w"), indent=1)
    return peaks


def idea_joins(joins, sents, end):
    starts = [s["t0"] for s in sents]
    out = []
    for J in joins:
        if J < 3.0 or J > end - 4.0 or (out and J - out[-1] < 2.2):
            continue
        if any(abs(J - t) < 0.35 for t in starts):
            out.append(J)
    return out


def finish(p, joins, sents, end):
    J = idea_joins(joins, sents, end)
    kinds = [("whip", "h"), ("zoomBlur", None), ("whip", "v"), ("zoomBlur", None)]
    plan_t = [(t, *kinds[i % len(kinds)]) for i, t in enumerate(J)]
    p["fx"] = [f for f in p["fx"] if f["fn"] not in ("aperture", "whip", "shrink", "blurIn", "leak")]
    p["fx"] += [dict(fn="whip", a=[t, {"dir": d, "sign": 1 if i % 2 else -1}]) for i, (t, k, d) in enumerate(plan_t) if k == "whip"]
    p["fx"].sort(key=lambda f: f["a"][0])
    if p.get("premium"):
        p["premium"]["trans"] = [dict(t=t, type=k) for t, k, _ in plan_t if k == "zoomBlur"]
    p["transitions"] = [dict(t=t, type=k) for t, k, _ in plan_t]
    peaks = kit()
    if not peaks:
        return "earshot kit unavailable: kept ROLES.json sounds"
    n = [0]
    def snd(name, at, vol, why):
        n[0] += 1
        return dict(id=f"es{n[0]}-{why}", file="earshot/" + name + ".wav", t=round(max(0, at - peaks[name]), 3), vol=vol, role=why, why=why)
    drop = ("whip", "shrink", "focus", "leak", "leak-hit", "rise", "impact", "kin-rise", "kin-hit", "hero-boom", "cut", "word-land", "hero-rise", "hero-shine", "spot", "type", "resolve")
    p["sfx"] = [s for s in p["sfx"] if s.get("why") not in drop]
    for t, k, _ in plan_t:
        p["sfx"].append(snd("whoosh_fast" if k == "whip" else "whoosh_pass", t, 0.3 if k == "whip" else 0.26, "cut"))
    K = (p.get("premium") or {}).get("kinetic") or {}
    for ln in K.get("lines", []):
        if ln.get("big"):
            p["sfx"].append(snd("blip", ln["t0"] + 0.02, 0.18, "word-land"))
    for Lt in K.get("lights", []):
        if Lt["kind"] == "rays":
            p["sfx"] += [snd("riser", Lt["t0"], 0.3, "hero-rise"), snd("boom", Lt["t0"] + 0.02, 0.38, "hero-boom"), snd("shine", Lt["t0"] + 0.5, 0.22, "hero-shine")]
        elif Lt["kind"] == "spot":
            p["sfx"].append(snd("boom", Lt["t0"] + 0.02, 0.35, "spot"))
    for pr in K.get("props", []):
        if pr["kind"] == "search":
            p["sfx"] += [snd("keys", pr["t0"] + 0.38 + k * 0.095, 0.2, "type") for k in range(8)]
            p["sfx"].append(snd("ding", pr.get("result_t", pr["t0"] + 1.4), 0.3, "resolve"))
    p["sfx"].sort(key=lambda s: s["t"])
    return f"v4: {len(plan_t)} transitions, earshot kit, {len(p['sfx'])} sfx"


if __name__ == "__main__":   # self-check: the join rule on the approved reel's joins keeps the 8 used in v4 (+ 9.66, 2.6 s after 7.03)
    js = [4.266, 7.025, 9.662, 12.741, 14.705, 18.322, 20.819, 24.234, 28.792, 31.003, 33.79]
    print(idea_joins(js, [dict(t0=t) for t in js], 35.85))
