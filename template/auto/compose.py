#!/usr/bin/env python3
"""compose.py — turn an edit plan into a complete, renderable HyperFrames reel (no hand-coded index.html).

  python3 -I compose.py <edit_plan.json> <project dir containing assets/>  [--graphics g.html --graphics-js g.js --graphics-css g.css --overlay o.html] [--platform ig|yt]
  --platform yt swaps the Instagram "Follow" end card for a YouTube "Subscribe" card (everything else identical).

The plan (written by autodirect.py, or edited by hand) carries every decision: words, joins, grade world, caption style, camera + effect list,
SFX list, music, hook, CTA. This script only assembles: footage + voice stem, captions, `fx.js` effects, SFX tags, music bed (carve with
carve.mjs afterwards), grain, progress bar, CTA card. A reel with no graphics is still a finished reel (captions + camera + sound + grade);
illustrations (sticker scenes) are optional and go in the `#stage` slot via --graphics / --graphics-js.

Plan keys (all optional except end, words):
  end, words (flat or islands [[text,start,end,tag?]]), caption {style: pop|serif|hero, y, accent, hero_until, size},
  hook {text, t0, t1}, fx [{fn, a:[...]}] sorted by time, sfx [{id,file,t,vol,ms}], music {file,vol,fade}, voice, video,
  headline {lines:[l1,l2], strike, t0, t1, y, size, style: stack|band} — the claim burned in from frame 0 (above the head; 18 Nov 2026),
  chips [{t0,t1,slug,hex,label,y}] — brand-logo badge that pops when the brand word is spoken (simple-icons),
  cta {variant: follow|save|comment|subscribe, t0, y, promise, answer, handle} — a dict, or a list (comment card for the question, then a follow card: each card ends when the next starts), progress {color}, grain (opacity), accent, bg
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
SFX_DIR = os.path.join(T, "composition", "assets", "audio", "sfx")
CTA = os.path.join(T, "composition", "components", "cta-card.html")
SI_ICONS = os.path.expanduser("~/.cache/reel-studio/simple-icons/package/icons")
def _cfg():
    p = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
    try:
        return json.load(open(p))
    except Exception:
        return {}
CFG = _cfg()


SFX_GROUP = ('<hf-audio-group id="sfx" data-label="SFX" data-volume="1" data-fx-chain="{&quot;version&quot;:1,&quot;nodes&quot;:[{&quot;type&quot;:&quot;highpass&quot;,&quot;id&quot;:&quot;s1&quot;,'
             '&quot;label&quot;:&quot;Keep SFX off the voice low end&quot;,&quot;params&quot;:{&quot;frequency&quot;:160,&quot;q&quot;:0.707,&quot;poles&quot;:&quot;2&quot;}},{&quot;type&quot;:&quot;reverb&quot;,'
             '&quot;id&quot;:&quot;s2&quot;,&quot;label&quot;:&quot;Shared room glue&quot;,&quot;params&quot;:{&quot;size&quot;:0.3,&quot;damping&quot;:0.6,&quot;wet&quot;:0.1,&quot;dry&quot;:1}}]}"></hf-audio-group>')


def sfx_path(name):
    """a bare name, 'mixkit/<file>', or a path; returns (abs path, name inside assets/audio/sfx/)"""
    for cand in (name, name + ".mp3", os.path.join(SFX_DIR, name), os.path.join(SFX_DIR, name + ".mp3")):
        if os.path.isfile(cand):
            return cand, os.path.relpath(cand, SFX_DIR) if cand.startswith(SFX_DIR) else os.path.basename(cand)
    raise SystemExit(f"SFX not found: {name}")


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    proj = os.path.abspath(sys.argv[2])
    gh = open(sys.argv[sys.argv.index("--graphics") + 1], encoding="utf-8").read() if "--graphics" in sys.argv else ""
    gj = open(sys.argv[sys.argv.index("--graphics-js") + 1], encoding="utf-8").read() if "--graphics-js" in sys.argv else ""
    gc = open(sys.argv[sys.argv.index("--graphics-css") + 1], encoding="utf-8").read() if "--graphics-css" in sys.argv else ""
    ov = open(sys.argv[sys.argv.index("--overlay") + 1], encoding="utf-8").read() if "--overlay" in sys.argv else ""   # static overlays outside the camera (CTA cards that carry their own animation)
    platform = sys.argv[sys.argv.index("--platform") + 1] if "--platform" in sys.argv else "ig"
    END = round(float(plan["end"]), 2)
    words = plan["words"]
    flat = [w for isl in words for w in isl] if words and isinstance(words[0][0], list) else words
    cap = {"style": "pop", "y": 1230, "accent": plan.get("accent", "#ffd23f"), "hero_until": 2.0, "size": 76}
    cap.update(plan.get("caption", {}))
    accent = plan.get("accent", cap["accent"])
    video = plan.get("video", "assets/main.mp4")
    voice = plan.get("voice", "assets/audio/voice.wav")
    music = plan.get("music")
    os.makedirs(os.path.join(proj, "assets", "audio", "sfx"), exist_ok=True)
    os.makedirs(os.path.join(proj, "assets", "img"), exist_ok=True)
    # grain tile (one shared texture)
    g = os.path.join(proj, "assets", "img", "grain.jpg")
    if not os.path.exists(g):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=1200x2100", "-vf", "noise=alls=46:allf=t+u,format=gray", "-frames:v", "1", g], check=True)
    av = os.path.join(proj, "assets", "img", "avatar.png")         # approved cartoon avatar for the CTA cards
    for cand in (os.path.join(T, "carousel", "assets", "avatar-cartoon.png"), os.path.join(T, "carousel", "assets", "avatar.png")):
        if not os.path.exists(av) and os.path.exists(cand):
            shutil.copy(cand, av)
    # voice stem from the cut
    vp = os.path.join(proj, voice)
    if not os.path.exists(vp):
        os.makedirs(os.path.dirname(vp), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(proj, video), "-vn", "-ac", "2", "-ar", "48000", vp], check=True)
    # SFX tags
    tags, tr = [], 40
    for s in plan.get("sfx", []):
        src, rel = sfx_path(s["file"])
        dst = os.path.join(proj, "assets", "audio", "sfx", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        ms = float(s.get("ms", 0)); t = max(0.0, float(s["t"]))
        d = round(min(dur(src) - ms, END - t) - 0.002, 3)   # 22 Nov 2026: the 30 ms digital-tick was dropped by a 0.03 s floor (typing ticks were silent)
        if d <= 0.01:
            continue
        m = f' data-media-start="{ms}"' if ms else ""
        tags.append(f'      <audio id="sfx-{s["id"]}" src="assets/audio/sfx/{rel}" data-start="{t:.2f}" data-duration="{d}"{m} data-track-index="{tr}" data-audio-group="sfx" data-volume="{round(min(float(s.get("vol", 0.25)), 1.0), 2)}"></audio>')
        tr += 1
    # CTA component pieces
    cta_css = cta_html = cta_js = cta_style = cta_calls = ""
    ctas = plan.get("cta") or []
    if isinstance(ctas, dict):
        ctas = [ctas]
    if ctas:
        raw = open(CTA, encoding="utf-8").read()
        cta_css = re.search(r"<style>(.*?)</style>", raw, re.S).group(1)
        cta_js = re.search(r"<script>(.*?)</script>", raw, re.S).group(1)
        base = raw[raw.index("</style>") + 8: raw.index("<!-- JS -->")]
        base = re.sub(r"<!--.*?-->", "", base, flags=re.S).strip()
        for i, c in enumerate(ctas):                      # e.g. a comment card for the question, then a follow card for the sign-off
            nxt = ctas[i + 1]["t0"] if i + 1 < len(ctas) else END
            cta_html += (f'<div id="g-cta{i}" class="clip" data-start="{c["t0"]}" data-duration="{round(nxt - c["t0"], 2)}" data-track-index="{15 + i}" data-role="cta" data-component="cta-card">'
                         + base.replace('id="cta"', f'id="cta{i}"') + '</div>')
            cta_style += f'      #g-cta{i} {{ position: absolute; inset: 0; pointer-events: none; }}\n      #g-cta{i} .cta {{ top: {c.get("y", 1010)}px; }}\n'
            cta_calls += "buildCtaCard(tl, " + json.dumps({"el": f"#cta{i}", "variant": "subscribe" if platform == "yt" and c.get("variant", "follow") == "follow" else c.get("variant", "follow"), "start": round(c["t0"] + 0.1, 2),
                         "promise": c.get("promise", CFG.get("promise", "one useful idea every day")), "answer": c.get("answer", "YES").replace(" ", "\u00a0"), "handle": c.get("handle", CFG.get("handle", "yourhandle")), "avatar": c.get("avatar") or "assets/img/avatar.png"}) + ");\n        "
    # music bed
    music_tag = ""
    if music:
        fade = float(music.get("fade", 0.28))
        auto = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": 0, "v": 1}, {"t": round(END - fade - 0.05, 2), "v": 1}, {"t": round(END - 0.03, 2), "v": 0}]}]}).replace('"', "&quot;")
        music_tag = (f'      <audio id="music" src="{music["file"]}" data-start="0" data-duration="{END}" data-track-index="31" data-audio-group="music" '
                     f'data-volume="{music.get("vol", 0.2)}" data-automation="{auto}"></audio>')
    hook = plan.get("hook")
    hook_html = ""
    if hook:
        hook_html = f'<div id="hook" class="clip" data-start="{hook.get("t0", 0)}" data-duration="{round(hook.get("t1", 0.6) - hook.get("t0", 0), 2)}" data-track-index="22" data-role="hook"><div class="hk">{hook["text"]}</div></div>'
    hl = plan.get("headline")
    hl_html = hl_css = hl_js = ""
    if hl and hl.get("lines"):
        esc = lambda x: x.replace("&", "&amp;").replace("<", "&lt;")
        strike, t1h = hl.get("strike"), float(hl.get("t1", 2.4))
        struck = []
        def line(t, cls):
            t = esc(t)
            if strike and not struck and re.search(r"\b" + re.escape(esc(strike)) + r"\b", t, re.I):
                t = re.sub(r"\b(" + re.escape(esc(strike)) + r")\b", r'<span class="st">\1<i></i></span>', t, count=1, flags=re.I)
                struck.append(1)
            return f'<div class="hl {cls}">{t}</div>'
        body = "".join(line(l, "hl1" if i == 0 else "hl2") for i, l in enumerate(hl["lines"][:2]))
        hl_html = (f'<div id="headline" class="clip {hl.get("style", "stack")}" data-start="{hl.get("t0", 0)}" data-duration="{t1h}" data-track-index="23" data-role="headline" '
                   f'style="top:{int(hl.get("y", 330))}px">{body}</div>')
        hl_css = (f'#headline {{ position: absolute; left: 50px; right: 50px; text-align: center; pointer-events: none; }}\n'
                  f'      #headline .hl {{ font: 900 {int(hl.get("size", 104))}px/1.05 Montserrat, sans-serif; color: #fff; -webkit-text-stroke: 12px rgba(14,16,24,.92); paint-order: stroke fill; text-shadow: 0 8px 0 rgba(14,16,24,.28); letter-spacing: -0.01em; }}\n'
                  f'      #headline .hl2 {{ font-family: "Playfair Display", serif; font-style: italic; font-weight: 900; color: {hl.get("accent", accent)}; }}\n'
                  f'      #headline .st {{ position: relative; display: inline-block; }}\n'
                  f'      #headline .st i {{ position: absolute; left: -8px; right: -8px; top: 50%; height: 13px; margin-top: -6px; background: #ff2d55; border-radius: 7px; transform-origin: 0 50%; transform: scaleX(0); }}\n'
                  f'      #headline.band .hl {{ display: inline-block; background: {hl.get("accent", accent)}; color: #0b0d12; -webkit-text-stroke: 0; text-shadow: none; padding: 4px 28px 8px; border-radius: 16px; margin: 7px 0; }}\n'
                  f'      #headline.band .hl2 {{ font-style: normal; font-family: Montserrat, sans-serif; background: #fff; color: #0b0d12; }}\n')
        hl_js = (f'tl.fromTo("#headline", {{ scale: 1.07 }}, {{ scale: 1, duration: 0.28, ease: "power3.out", ...IM }}, 0);\n'
                 f'        if (document.querySelector("#headline .st i")) tl.to("#headline .st i", {{ scaleX: 1, duration: 0.22, ease: "power2.out", ...IM }}, {float(hl.get("strike_t", 0.55))});\n'
                 f'        tl.to("#headline", {{ opacity: 0, y: -14, duration: 0.22, ease: "power2.in", ...IM }}, {round(t1h - 0.24, 2)});')
    chips_html = chips_css = chips_js = ""
    for i, ch in enumerate(plan.get("chips") or []):
        f = os.path.join(SI_ICONS, ch["slug"] + ".svg")
        if not os.path.exists(f):
            print(f"warn: no simple-icons logo '{ch['slug']}' — chip skipped"); continue
        d = re.search(r' d="([^"]+)"', open(f, encoding="utf-8").read()).group(1)
        t0c, t1c = float(ch["t0"]), float(ch["t1"])
        chips_html += (f'<div id="chip{i}" class="chip clip" data-start="{t0c}" data-duration="{round(t1c - t0c, 2)}" data-track-index="{24 + i}" data-role="logo-chip" style="top:{int(ch.get("y", 330))}px">'
                       f'<div class="cb"><svg viewBox="0 0 24 24"><path d="{d}" fill="#{ch["hex"].lstrip("#")}"/></svg></div><div class="cl">{ch.get("label", ch["slug"]).upper()}</div></div>')
        chips_js += (f'tl.fromTo("#chip{i}", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.28, ease: "back.out(1.8)", ...IM }}, {t0c});\n        '
                     f'tl.to("#chip{i}", {{ opacity: 0, scale: 0.92, duration: 0.2, ...IM }}, {round(t1c - 0.22, 2)});\n        ')
    if chips_html:
        chips_css = ('#chips { position: absolute; inset: 0; pointer-events: none; }\n      .chip { position: absolute; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; gap: 14px; pointer-events: none; }\n'
                     '      .chip .cb { width: 210px; height: 210px; border-radius: 46px; background: #fff; display: grid; place-items: center; box-shadow: 0 22px 50px rgba(0,0,0,.4); }\n'
                     '      .chip .cb svg { width: 128px; height: 128px; }\n'
                     '      .chip .cl { font: 800 34px Montserrat, sans-serif; color: #fff; -webkit-text-stroke: 8px rgba(14,16,24,.9); paint-order: stroke fill; letter-spacing: .04em; }\n')
    # ---- premium layer (Round 14, 22 Nov 2026): depth stack + two-tier captions + cards; see premium/premium.py ----
    P = plan.get("premium")
    pr_css = pr_js = pr_call = pr_behind = pr_front = pr_over = ""
    if P:
        PD = os.path.join(HERE, "premium")
        fdir = os.path.join(proj, "assets", "fonts"); os.makedirs(fdir, exist_ok=True)
        fsrc = os.path.join(PD, "fonts")
        if not os.path.exists(os.path.join(fsrc, "Anton-Regular.ttf")):
            print("WARN: premium fonts missing: run template/auto/premium/fetch_fonts.sh once (type falls back to system fonts)")
        for f in (os.listdir(fsrc) if os.path.isdir(fsrc) else []):
            if not os.path.exists(os.path.join(fdir, f)):
                shutil.copy(os.path.join(fsrc, f), fdir)
        tv = P["theme_vars"]
        pr_css = (":root { " + " ".join(f"--p-{k.replace('_', '-')}: {tv[k]};" for k in ("accent", "word", "glow", "tint_top", "tint_bot", "orb", "orb2", "rib1", "rib2", "ring", "ok", "ink2"))
                  + " --avatar-img: url(assets/img/avatar.png); }\n" + open(os.path.join(PD, "premium.css"), encoding="utf-8").read())
        pr_js = open(os.path.join(PD, "premium.js"), encoding="utf-8").read() + "\n" + open(os.path.join(PD, "kinetic.js"), encoding="utf-8").read()
        has_fg = os.path.exists(os.path.join(proj, "assets", "fg.webm"))
        if not has_fg:
            print("WARN: no assets/fg.webm — run person_matte.py first; words behind the head and the room tint are dropped (they would cover the face)")
            P = dict(P, behind=[], room=None, depth=dict(P.get("depth") or {}, ribbon=False))
        pr_behind = ('<div id="behind"><div id="room"></div><div id="dots"></div><svg id="ribbonB" class="ribbon" viewBox="0 0 1080 1920"></svg><div id="wb"></div></div>'
                     + (f'<div id="fgw"><video id="fg" class="clip" src="assets/fg.webm" data-start="0" data-duration="{END}" data-media-start="0" data-track-index="1" muted playsinline></video></div>' if has_fg else "")
                     + '<div id="ribbonF"><svg class="ribbon" viewBox="0 0 1080 1920"></svg></div>')
        pr_front = '<div id="tier"></div><div id="cards"></div><div id="streak"></div>'
        pr_call = "makePremium(tl, " + json.dumps(P, ensure_ascii=False) + ", { end: END, words: WORDS });"
        if P.get("kinetic"):
            if not has_fg:
                print("WARN: kinetic track without fg.webm — words would cover the face; run person_matte.py")
            if any(q.get("kind") == "map" for q in P["kinetic"].get("props", [])):
                pr_js = "const WORLDDOTS = " + open(os.path.join(PD, "worlddots.json"), encoding="utf-8").read() + ";\n" + pr_js
            pr_call += "\n        makeKinetic(tl, " + json.dumps(P["kinetic"], ensure_ascii=False) + ", { end: END, accent: " + json.dumps(tv["accent"]) + " });"
            cap["style"] = "kinetic"
        if P.get("tier"):
            cap["style"] = "tier"
    scene_cls = "pop"
    world_open = '<div id="splitBg"></div><div id="world">' if P else '<div id="world">'
    html = TEMPLATE
    rep = {
        "{{END}}": str(END), "{{ACCENT}}": accent, "{{BG}}": plan.get("bg", "#05070f"),
        "{{CAPY}}": str(cap["y"]), "{{CAPSIZE}}": str(cap["size"]), "{{GRAIN}}": str(plan.get("grain", 0.1)),
        "{{VIDEO}}": video, "{{VOICE}}": voice, "{{CTA_CSS}}": cta_css, "{{CTA_HTML}}": cta_html,
        "{{CTA_JS}}": cta_js, "{{HOOK}}": hook_html, "{{HEADLINE}}": hl_html + chips_html, "{{HEADLINE_CSS}}": hl_css + chips_css, "{{HEADLINE_JS}}": hl_js + "\n        " + chips_js, "{{GRAPHICS}}": gh, "{{GRAPHICS_JS}}": gj, "{{GRAPHICS_CSS}}": gc, "{{OVERLAY}}": ov, "{{MUSIC}}": music_tag, "{{SFX_GROUP}}": SFX_GROUP if tags else "", "{{SFX}}": "\n".join(tags),
        "{{FXJS}}": open(os.path.join(HERE, "fx.js"), encoding="utf-8").read(),
        "{{WORDS}}": json.dumps(flat, ensure_ascii=False), "{{CAP}}": json.dumps(cap), "{{FX}}": json.dumps(plan.get("fx", [])),
        "{{CTA_CALL}}": cta_calls,
        "{{CTA_STYLE}}": cta_style,
        "{{PROGRESS}}": f'<div id="g-progress"><div id="pg-bar"></div></div>' if plan.get("progress", True) else "",
        "{{PROGRESS_JS}}": f'tl.fromTo("#pg-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {round(END - 0.1, 2)}, ease: "none", ...IM }}, 0);' if plan.get("progress", True) else "",
        "{{PREMIUM_CSS}}": pr_css, "{{PREMIUM_JS}}": pr_js, "{{PREMIUM_CALL}}": pr_call, "{{PREMIUM_BEHIND}}": pr_behind, "{{PREMIUM_FRONT}}": pr_front,
        "{{LEAK}}": '<div id="leak"></div>' if any(f.get("fn") == "leak" for f in plan.get("fx", [])) else '<div id="leak"></div>',
    }
    for k, v in rep.items():
        html = html.replace(k, v)
    html = html.replace('<div id="world">', world_open, 1)
    open(os.path.join(proj, "index.html"), "w", encoding="utf-8").write(html)
    print(f"wrote {proj}/index.html — {len(flat)} words, {len(plan.get('fx', []))} fx, {len(tags)} sfx, end {END}s")


TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: {{BG}}; }
      :root { --accent: {{ACCENT}}; --avatar: none; }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; font-family: Montserrat, sans-serif; background: {{BG}}; }
      #world { position: absolute; inset: 0; overflow: hidden; }
      #cam { position: absolute; inset: 0; overflow: hidden; transform-origin: 50% 44%; }
      #bump { position: absolute; inset: 0; transform-origin: 50% 44%; }
      #a-roll { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      #stage { position: absolute; inset: 0; transform-origin: 50% 44%; pointer-events: none; }
      #leak { position: absolute; inset: -60px; opacity: 0; mix-blend-mode: screen; pointer-events: none; }
      #captions, #hook { position: absolute; inset: 0; pointer-events: none; }
      /* captions: pop (default) · serif (warm, above the hair) · hero (giant opening words) */
      .cap { position: absolute; left: 70px; right: 70px; top: {{CAPY}}px; display: flex; justify-content: center; flex-wrap: nowrap; gap: 0 30px; opacity: 0; }
      .cw { display: inline-block; font-size: {{CAPSIZE}}px; font-weight: 900; line-height: 1.1; color: #fff; -webkit-text-stroke: 10px rgba(14, 16, 24, 0.92); paint-order: stroke fill; text-shadow: 0 6px 0 rgba(14, 16, 24, 0.3); white-space: nowrap; }
      .serif .cw { font-family: "Playfair Display", serif; font-weight: 600; font-size: 70px; -webkit-text-stroke: 0; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6), 0 2px 8px rgba(0, 0, 0, 0.45), 0 2px 22px rgba(0, 0, 0, 0.55); letter-spacing: 0.01em; }  /* 21 Nov 2026: cream serif vanished on a light wall (a test reel): a tight dark core under the soft glow keeps it readable */
      .serif .cw.em { font-style: italic; font-weight: 700; }
      .hero .cw { font-size: 150px; text-transform: uppercase; letter-spacing: -0.01em; -webkit-text-stroke: 14px rgba(14, 16, 24, 0.9); }
      .hk { position: absolute; left: 60px; right: 60px; top: 300px; text-align: center; font: 900 120px/1.02 Montserrat, sans-serif; color: #fff; -webkit-text-stroke: 14px rgba(14,16,24,.9); paint-order: stroke fill; text-transform: uppercase; }
      {{HEADLINE_CSS}}
      #grain { position: absolute; left: -60px; top: -60px; width: 1200px; height: 2100px; background: url(assets/img/grain.jpg) 0 0 / 1200px 2100px; mix-blend-mode: overlay; opacity: {{GRAIN}}; pointer-events: none; }
      #g-progress { position: absolute; left: 0; top: 0; width: 1080px; height: 8px; pointer-events: none; }
      #pg-bar { width: 100%; height: 8px; background: var(--accent); transform-origin: 0 50%; }
{{CTA_STYLE}}{{CTA_CSS}}
{{GRAPHICS_CSS}}
{{PREMIUM_CSS}}
    </style>
  </head>
  <body>
    <svg width="0" height="0" style="position:absolute" aria-hidden="true">
      <defs>
        <filter id="mbH" x="-25%" y="-5%" width="150%" height="110%"><feGaussianBlur stdDeviation="0 0"/></filter>
        <filter id="mbV" x="-5%" y="-25%" width="110%" height="150%"><feGaussianBlur stdDeviation="0 0"/></filter>
        <filter id="rgb" color-interpolation-filters="sRGB">
          <feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>
          <feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>
          <feOffset in="r" id="rgbR" dx="0" dy="0" result="r2"/><feOffset in="b" id="rgbB" dx="0" dy="0" result="b2"/>
          <feBlend in="r2" in2="g" mode="screen" result="rg"/><feBlend in="rg" in2="b2" mode="screen"/>
        </filter>
      </defs>
    </svg>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{END}}" data-width="1080" data-height="1920">
      <div id="world">
        <div id="cam"><div id="bump"><video id="a-roll" class="clip" src="{{VIDEO}}" data-start="0" data-duration="{{END}}" data-track-index="0" muted playsinline></video>{{PREMIUM_BEHIND}}</div></div>
        <div id="stage" data-role="graphics">
{{GRAPHICS}}
        </div>
      </div>
      {{LEAK}}
      <div id="captions" class="clip" data-start="0" data-duration="{{END}}" data-track-index="20" data-role="caption"></div>
      {{PREMIUM_FRONT}}
      {{HOOK}}
      {{HEADLINE}}
      {{CTA_HTML}}
{{OVERLAY}}
      <div id="grain"></div>
      {{PROGRESS}}

      <audio id="voice" src="{{VOICE}}" data-start="0" data-duration="{{END}}" data-track-index="30" data-audio-group="voiceover" data-volume="1"></audio>
{{MUSIC}}
      {{SFX_GROUP}}
{{SFX}}
    </div>
    <script>
{{CTA_JS}}
    </script>
    <script>
{{FXJS}}
    </script>
    <script>
{{PREMIUM_JS}}
    </script>
    <script>
      (function () {
        const tl = gsap.timeline({ paused: true });
        const IM = { immediateRender: false };
        const END = {{END}};
        const WORDS = {{WORDS}};
        const CAP = {{CAP}};
        const COL = { r: "#ff5470", y: CAP.accent, g: "#2de2a6" };
        const WEAK = /^(a|an|the|to|of|and|or|but|in|on|at|for|is|it|ka|ke|ki|se|ko|na|ek|hi|ye|toh|mein|pe|par|hai|aur|ho|tum|ya|bhi)$/i;
        const bare = (t) => t.replace(/(?<!\d),|,(?!\d)|[.?!;:"“”]/g, "");   // keeps the comma inside numbers (50,000)
        const fx = makeFX(tl, { end: END });

        /* ---------- captions ---------- */
        const chunks = [];
        let cur = [];
        const HINTED = WORDS.some((w) => w[4] === "/");   // phrase mode: the script author marks where a caption chunk ends (a person phrases by meaning, not by word count)
        WORDS.forEach((w, i) => {
          cur.push(w);
          if (HINTED) { if (w[4] === "/" || i === WORDS.length - 1 || cur.length >= 4) { chunks.push(cur); cur = []; } return; }
          const punct = /[.,?!]$/.test(w[0]), last = i === WORDS.length - 1;
          const chars = cur.reduce((a, x) => a + bare(x[0]).length, 0);
          const hero = CAP.style === "hero" && w[1] < CAP.hero_until;
          const nl = WORDS[i + 1] ? bare(WORDS[i + 1][0]).length : 0;   // 16 Nov 2026: "a long three-word phrase" (18 chars) ran past the safe margins
          const weakEnd = !punct && !last && WEAK.test(bare(w[0])) && chars < 11 && chars + nl <= 16;
          const maxw = hero ? 1 : CAP.style === "serif" ? 3 : 2;
          if (!weakEnd && (punct || cur.length >= maxw || chars >= (hero ? 8 : 14) || last)) { chunks.push(cur); cur = []; }
        });
        const capRoot = document.getElementById("captions");
        if (CAP.style !== "tier" && CAP.style !== "kinetic") chunks.forEach((c, ci) => {
          if ((CAP.skip || []).some((r) => c[0][1] >= r[0] && c[0][1] < r[1])) return;   // optional: a word the scene already shows as hero lettering is not captioned twice
          const el = document.createElement("div");
          const isHero = CAP.style === "hero" && c[0][1] < CAP.hero_until;
          el.className = "cap" + (CAP.style === "serif" ? " serif" : isHero ? " hero" : "");
          el.id = "cap-" + ci;
          if (isHero) el.style.top = "430px";
          const ysr = (CAP.ys || []).find((r) => c[0][1] >= r[0] && c[0][1] < r[1]);   // optional per-shot caption rows [[t0, t1, y], …]: a lean-in shot raises its hair line
          if (ysr) el.style.top = ysr[2] + "px";
          c.forEach((w, wi) => {
            const s = document.createElement("span");
            s.className = "cw" + (CAP.style === "serif" && w[3] ? " em" : "");
            s.id = "cap-" + ci + "-" + wi;
            s.textContent = bare(w[0]);
            el.appendChild(s);
          });
          capRoot.appendChild(el);
          const start = Math.max(0.02, c[0][1] - 0.04), next = chunks[ci + 1];
          const end = next ? Math.max(start + 0.2, next[0][1] - 0.04) : END;
          tl.fromTo(el, { opacity: 0, y: isHero ? 0 : 10, scale: isHero ? 1.12 : 0.95 }, { opacity: 1, y: 0, scale: 1, duration: isHero ? 0.1 : 0.12, ease: "power2.out", ...IM }, start);
          tl.set(el, { opacity: 0 }, end);
          c.forEach((w, wi) => {
            const hot = w[3] ? COL[w[3]] || CAP.accent : isHero ? "#fff" : "#ffffff";
            tl.fromTo("#cap-" + ci + "-" + wi, { color: "#ffffff", scale: 1 }, { color: hot, scale: 1.08, duration: 0.08, ease: "power1.out", ...IM }, w[1]);
            tl.to("#cap-" + ci + "-" + wi, { scale: 1, duration: 0.1 }, w[2]);
          });
        });

        /* ---------- effects from the plan (camera track, whips, shrinks, leaks, shakes…) in time order ---------- */
        {{FX}}.forEach((e) => fx[e.fn](...e.a));
        {{PROGRESS_JS}}
        {{HEADLINE_JS}}
        fx.grain(END);
        {{PREMIUM_CALL}}
        {{CTA_CALL}}
{{GRAPHICS_JS}}
        window.__timelines = window.__timelines || {};
        window.__timelines["main"] = tl;
        tl.seek(0);
      })();
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    main()
