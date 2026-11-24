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
    # 24 Nov 2026: the transition mix follows the world (the realtor reel's 3D-shake cut is energy, so it stays out of calm story reels):
    #   hype_hero  shake3d, whip h, shake3d, whip v       clean_pop  whip h, zoomBlur, shake3d, whip v       warm_cinema  whip h, zoomBlur, whip v, zoomBlur (unchanged)
    world = p.get("world")
    kinds = {"hype_hero": [("shake3d", None), ("whip", "h"), ("shake3d", None), ("whip", "v")],
             "clean_pop": [("whip", "h"), ("zoomBlur", None), ("shake3d", None), ("whip", "v")]}.get(world, [("whip", "h"), ("zoomBlur", None), ("whip", "v"), ("zoomBlur", None)])
    plan_t = [(t, *kinds[i % len(kinds)]) for i, t in enumerate(J)]
    signs = None
    ov = os.environ.get("TRANS_AT")     # per-reel curation (dialogue reel, 23 Nov 2026): "6.33:whip:h:-1,14.57:zoomBlur,20.5:whip:h:1" = time:kind[:dir[:sign]] — whips on speaker changes ping-pong left/right
    if ov:
        plan_t, signs = [], []
        for tok in ov.split(","):
            f = tok.strip().split(":"); k = f[1] if len(f) > 1 else "zoomBlur"
            plan_t.append((float(f[0]), k, (f[2] if len(f) > 2 else "h") if k == "whip" else None)); signs.append(int(f[3]) if len(f) > 3 else -1)
    p["fx"] = [f for f in p["fx"] if f["fn"] not in ("aperture", "whip", "shrink", "blurIn", "leak")]
    p["fx"] += [dict(fn="whip", a=[t, {"dir": d, "sign": (signs[i] if signs else (1 if i % 2 else -1))}]) for i, (t, k, d) in enumerate(plan_t) if k == "whip"]
    p["fx"].sort(key=lambda f: f["a"][0])
    if p.get("premium"):
        p["premium"]["trans"] = [dict(t=t, type=k) for t, k, _ in plan_t if k in ("zoomBlur", "shake3d")]
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
        p["sfx"].append(snd("whoosh_fast" if k in ("whip", "shake3d") else "whoosh_pass", t, 0.3 if k in ("whip", "shake3d") else 0.26, "cut"))
        if k == "shake3d": p["sfx"].append(snd("boom", t + 0.02, 0.2, "cut"))      # the hit that lands with the radial cut
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
        elif pr["kind"] == "flood":      # requests pile up (riser) and the IP-BLOCKED stamp lands on the boom
            p["sfx"] += [snd("riser", pr["block_t"], 0.26, "flood-rise"), snd("boom", pr["block_t"] + 0.02, 0.4, "block")]
        elif pr["kind"] == "urls":       # one key-click per URL row
            p["sfx"] += [snd("keys", pr["t0"] + 0.12 + i * pr.get("gap", 0.3), 0.18, "type") for i in range(4)]
        elif pr["kind"] == "queues":     # chips routed into lanes (pop), a blip per worker, a ding on the first two ticks
            nq = len(pr.get("order") or [0] * 16)
            p["sfx"] += [snd("pop", pr["route_t"] + 0.3 + j * pr.get("route_gap", 0.13), 0.12, "route") for j in range(0, nq, 2)]
            p["sfx"] += [snd("blip", pr["worker_t"] + i * 0.1 + 0.15, 0.16, "worker") for i in range(4)]
            p["sfx"] += [snd("ding", pr["pull_t"] + 0.62 + k * 0.8, 0.12, "done") for k in range(2)]
        elif pr["kind"] == "shards":     # three ID rows pop in, the collision lands on a riser -> boom
            p["sfx"] += [snd("pop", pr["t0"] + 0.5 + r * 0.3 + 0.05, 0.14, "shard-id") for r in range(3)]
            p["sfx"] += [snd("riser", pr["hit_t"], 0.22, "collide-rise"), snd("boom", pr["hit_t"] + 0.02, 0.36, "collide")]
        elif pr["kind"] == "pages":      # a soft blip per UUID landing (every other one), the SLOW WRITES stamp on a boom
            s, i = pr["t0"] + 0.5, 0
            stop = (pr.get("slow_t", pr["t1"] - 0.8)) - 0.25
            while s < stop:
                if i % 2 == 0:
                    p["sfx"].append(snd("blip", s + 0.3, 0.1, "page"))
                s += max(0.2, 0.44 - i * 0.03); i += 1
            if pr.get("slow_t") is not None:
                p["sfx"] += [snd("riser", pr["slow_t"], 0.2, "slow-rise"), snd("boom", pr["slow_t"] + 0.02, 0.34, "slow")]
        elif pr["kind"] == "idbits":     # one pop per ID part as it is spoken
            p["sfx"] += [snd("pop", pr[k], 0.16, "bits") for k in ("ts_t", "dc_t", "mc_t", "sq_t")]
        elif pr["kind"] == "idstream":   # coordinator crossed out (boom), a blip per ID for the first rows, a ding on SORTED
            p["sfx"] += [snd("boom", pr["x_t"] + 0.1, 0.3, "x"), snd("ding", pr["sorted_t"] + 0.05, 0.2, "sorted")]
            p["sfx"] += [snd("blip", pr["rows_t"] + i * 0.24, 0.1, "id") for i in range(8)]
        elif pr["kind"] == "clockback":  # clock ticks (keys), the rewind and the DUPLICATE stamp each on a riser -> boom
            p["sfx"] += [snd("keys", pr["tick_t"] + i * pr.get("step", 0.28), 0.12, "tick") for i in range(6)]
            p["sfx"] += [snd("riser", pr["rewind_t"], 0.2, "rewind-rise"), snd("boom", pr["rewind_t"] + 0.02, 0.3, "rewind"), snd("boom", pr["dup_t"] + 0.02, 0.38, "dup")]
        elif pr["kind"] == "jam":        # promo chips pop in (every 3rd), the OTP lands with a ding, STUCK and USER DROP-OFF each on a riser -> boom
            c, i = pr["flood_t"], 0
            while c < pr["otp_t"] - 0.2:
                if i % 3 == 0:
                    p["sfx"].append(snd("pop", c + 0.2, 0.1, "promo"))
                c += max(0.06, 0.32 - i * 0.03); i += 1
            p["sfx"] += [snd("ding", pr["otp_t"] + 0.3, 0.2, "otp"), snd("riser", pr["stuck_t"], 0.22, "stuck-rise"), snd("boom", pr["stuck_t"] + 0.02, 0.3, "stuck"), snd("boom", pr["drop_t"] + 0.02, 0.4, "drop")]
        elif pr["kind"] == "priority":   # a blip per lane, a ding per HIGH chip that arrives, a blip per worker bot
            p["sfx"] += [snd("blip", pr["t0"] + 0.15, 0.14, "lane"), snd("blip", pr["t0"] + 0.3, 0.12, "lane")]
            p["sfx"] += [snd("ding", pr["hi_t"] + i * 0.5 + 0.85, 0.12, "high-done") for i in range(4) if pr["hi_t"] + i * 0.5 + 0.85 < pr["t1"] - 0.3]
            p["sfx"] += [snd("blip", pt + 0.15, 0.16, "worker") for pt in (pr.get("pool_ts") or [pr["pool_t"] + i * 0.12 for i in range(3)])]
        elif pr["kind"] == "retry":      # a pop per failed attempt, a ding when it finally lands
            p["sfx"] += [snd("pop", h + 0.05, 0.16, "fail") for h in pr["hops"][:3]] + [snd("ding", pr["hops"][3] + 0.05, 0.26, "landed")]
        elif pr["kind"] == "dupe":       # the alert dings twice (that IS the bug), the timeout on a pop, SENT TWICE on a riser -> boom
            p["sfx"] += [snd("ding", pr["card1_t"] + 0.12, 0.26, "alert-1"), snd("pop", pr["timeout_t"] + 0.1, 0.16, "timeout"), snd("ding", pr["card2_t"] + 0.12, 0.26, "alert-2"),
                         snd("riser", pr["dup_t"], 0.22, "dup-rise"), snd("boom", pr["dup_t"] + 0.02, 0.38, "dup")]
    p["sfx"].sort(key=lambda s: s["t"])
    return f"v4: {len(plan_t)} transitions, earshot kit, {len(p['sfx'])} sfx"


if __name__ == "__main__":   # self-check: the join rule on the approved reel's joins keeps the 8 used in v4 (+ 9.66, 2.6 s after 7.03)
    js = [4.266, 7.025, 9.662, 12.741, 14.705, 18.322, 20.819, 24.234, 28.792, 31.003, 33.79]
    print(idea_joins(js, [dict(t0=t) for t in js], 35.85))
