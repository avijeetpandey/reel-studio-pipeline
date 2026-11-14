/* fx.js — camera-real effects for a talking-head reel (HyperFrames + GSAP). Round 8, 14 Nov 2026.
 *
 * Why it exists: the reference reels that feel "human" (celfstudies 157K, liveairprod 52K, messy_mummah, kienobifilms) get their energy from CAMERA
 * behaviour — punch-ins on words, whips and card-shrink moves that hide cuts, focus pulls, light leaks, a little handheld shake, shared grain —
 * not from overlays. Everything here moves the footage (#world / #cam) or adds one honest lens-style layer; nothing draws a panel, a glow or a
 * generic sticker. the creator's notes (variety.md §0, §7, §8) still apply: face on screen 100 %, no glass/console boxes, no white flash, no light streak.
 *
 * DOM contract (compose.py writes it):  #world > ( #cam > #bump > video#a-roll ) + #stage ;  #leak, #captions, #grain are siblings of #world.
 * Seek-safe: only fromTo/set with immediateRender:false, state kept in this closure and advanced in time order.
 *
 *   const fx = makeFX(tl, { end: 26.9 });
 *   fx.camTo(t0, t1, scale, y, ease)       sequential camera track (footage zoom + stage parallax); call in time order
 *   fx.punch(t, amt, hold)                 snap-in on a word, ease back to the current base
 *   fx.whip(J, {dir:'h'|'v', sign})        directional motion-blur smear across the cut at J  (+ its whoosh is added by the plan, not here)
 *   fx.shrink(J, {from:'down'|'up'})       the whole frame tilts, shrinks to a card and flies out; the next shot lands from the other side
 *   fx.blurIn(J, {px})                     focus pull: next shot arrives defocused and snaps sharp
 *   fx.leak(J, {tone:'amber'|'rose'|'teal'}) warm lens light-leak that swallows the cut (film worlds only, ≤ 2 per reel)
 *   fx.shake(t, {amp, dur})                handheld jolt (deterministic, decaying)
 *   fx.aperture(t0, t1)                    opener: the frame starts as a narrow strip and widens (hook, ≤ 0.5 s, face visible throughout)
 *   fx.rgb(t, {dur, px})                   3-frame chromatic split on a punch word (≤ 1 per reel)
 *   fx.grain(end)                          12 fps jittered grain over footage + graphics (one shared texture)
 *   fx.pulse(times, amt)                   tiny beat pulses on #bump
 */
function makeFX(tl, o) {
  o = o || {};
  const IM = { immediateRender: false };
  const W = "#world", C = "#cam", S = "#stage", B = "#bump", CAP = "#captions";
  const PAR = o.par == null ? 0.45 : o.par; // graphics follow the camera at 45 % so they sit in the shot
  const st = { s: 1, y: 0 };
  const api = {};
  const blurH = document.querySelector("#mbH feGaussianBlur"), blurV = document.querySelector("#mbV feGaussianBlur");
  const rgbR = document.querySelector("#rgbR"), rgbB = document.querySelector("#rgbB");

  // ---- camera track (footage + stage parallax) -------------------------------------------------
  api.camTo = (t0, t1, s, y, ease) => {
    y = y || 0;
    if (t1 <= t0 + 1e-3) {
      tl.set(C, { scale: s, y }, t0);
      tl.set(S, { scale: 1 + (s - 1) * PAR, y: y * PAR }, t0);
    } else {
      tl.fromTo(C, { scale: st.s, y: st.y }, { scale: s, y, duration: t1 - t0, ease: ease || "power2.out", ...IM }, t0);
      tl.fromTo(S, { scale: 1 + (st.s - 1) * PAR, y: st.y * PAR }, { scale: 1 + (s - 1) * PAR, y: y * PAR, duration: t1 - t0, ease: ease || "power2.out", ...IM }, t0);
    }
    st.s = s; st.y = y;
  };
  api.state = () => ({ s: st.s, y: st.y });
  api.punch = (t, amt, hold) => {
    const base = st.s, by = st.y, up = 0.09, down = hold || 0.5;
    api.camTo(t, t + up, base * (amt || 1.07), by, "power3.out");
    api.camTo(t + up, t + up + down, base, by, "power2.out");
  };

  // ---- directional motion blur (SVG filter on #world, only attached while a whip runs) -------------
  const blurTween = (el, axis, t, dur, from, to, ease) => {
    const p = { v: from };
    tl.fromTo(p, { v: from }, { v: to, duration: dur, ease: ease || "none", ...IM,
      onUpdate() { el.setAttribute("stdDeviation", axis === "h" ? p.v.toFixed(2) + " 0" : "0 " + p.v.toFixed(2)); } }, t);
  };
  api.whip = (J, d) => {
    d = d || {};
    const dir = d.dir || "h", amt = d.amt == null ? 90 : d.amt, bl = d.blur == null ? 34 : d.blur, tin = d.out == null ? 0.1 : d.out, tout = d.in == null ? 0.2 : d.in, sg = d.sign || 1;
    const ax = dir === "h" ? "x" : "y", el = dir === "h" ? blurH : blurV, f = dir === "h" ? "url(#mbH)" : "url(#mbV)", ov = 1 + amt / (dir === "h" ? 480 : 900); // overscale > the slide, so no edge ever shows
    tl.set(W, { filter: f }, J - tin - 0.02);
    tl.fromTo(W, { [ax]: 0, scale: 1 }, { [ax]: -amt * sg, scale: ov, duration: tin, ease: "power2.in", ...IM }, J - tin); 
    blurTween(el, dir, J - tin, tin, 0, bl, "power2.in");
    tl.fromTo(W, { [ax]: amt * sg, scale: ov }, { [ax]: 0, scale: 1, duration: tout, ease: "power3.out", ...IM }, J);
    blurTween(el, dir, J, tout, bl, 0, "power3.out");
    tl.set(W, { filter: "none" }, J + tout + 0.01);
  };

  // ---- frame-as-object transition (messy_mummah): tilt + shrink + fly, next shot lands from the other side ------
  api.shrink = (J, d) => {
    d = d || {};
    const sg = d.from === "up" ? -1 : 1, tout = d.out == null ? 0.17 : d.out, tin = d.in == null ? 0.26 : d.in;
    tl.set(W, { transformPerspective: 1500 }, 0);
    tl.fromTo(W, { scale: 1, y: 0, rotationX: 0, rotationZ: 0 }, { scale: 0.7, y: 560 * sg, rotationX: -13 * sg, rotationZ: 3 * sg, duration: tout, ease: "power2.in", ...IM }, J - tout);
    tl.fromTo(W, { scale: 0.7, y: -560 * sg, rotationX: 13 * sg, rotationZ: -3 * sg }, { scale: 1, y: 0, rotationX: 0, rotationZ: 0, duration: tin, ease: "power3.out", ...IM }, J);
    tl.fromTo(CAP, { opacity: 1 }, { opacity: 0, duration: 0.06, ...IM }, J - tout);
    tl.fromTo(CAP, { opacity: 0 }, { opacity: 1, duration: 0.12, ...IM }, J + 0.1);
    tl.set(W, { filter: "url(#mbV)" }, J - tout - 0.02);
    blurTween(blurV, "v", J - tout, tout, 0, 24, "power2.in");
    blurTween(blurV, "v", J, tin * 0.8, 24, 0, "power3.out");
    tl.set(W, { filter: "none" }, J + tin + 0.01);
  };

  // ---- focus pull ---------------------------------------------------------------------------------
  api.blurIn = (J, d) => {
    d = d || {};
    const px = d.px == null ? 13 : d.px, dur = d.dur == null ? 0.24 : d.dur;
    tl.fromTo(W, { filter: "blur(" + px + "px)", scale: 1.035 }, { filter: "blur(0px)", scale: 1, duration: dur, ease: "power2.out", ...IM }, J);
    tl.set(W, { filter: "none" }, J + dur + 0.01);
  };

  // ---- light leak that hides the cut (kienobifilms, liveairprod) ------------------------------------
  const TONES = {
    amber: ["rgba(255,196,84,1)", "rgba(255,120,40,0.95)", "rgba(255,245,200,1)"],
    rose: ["rgba(255,150,120,1)", "rgba(255,70,110,0.9)", "rgba(255,236,224,1)"],
    teal: ["rgba(120,230,220,1)", "rgba(40,150,200,0.9)", "rgba(230,255,250,1)"],
  };
  api.leak = (J, d) => {
    d = d || {};
    const tone = TONES[d.tone || "amber"], up = d.up == null ? 0.2 : d.up, down = d.down == null ? 0.38 : d.down, el = document.getElementById("leak");
    el.style.background =
      "radial-gradient(ellipse 85% 55% at 18% 8%," + tone[2] + " 0%," + tone[0] + " 38%,rgba(0,0,0,0) 72%)," +
      "radial-gradient(ellipse 60% 70% at 100% 55%," + tone[1] + " 0%,rgba(0,0,0,0) 70%)," +
      "linear-gradient(115deg," + tone[0].replace(/[\d.]+\)$/, "0.55)") + " 0%,rgba(0,0,0,0) 55%)";
    tl.fromTo("#leak", { opacity: 0, x: -140, scale: 1.1 }, { opacity: 0.96, x: 0, scale: 1.0, duration: up, ease: "power2.in", ...IM }, J - up);
    tl.fromTo("#leak", { opacity: 0.96, x: 0, scale: 1.0 }, { opacity: 0, x: 120, scale: 1.12, duration: down, ease: "power2.out", ...IM }, J);
  };

  // ---- handheld jolt ----------------------------------------------------------------------------
  let seed = o.seed || 7;
  const rnd = () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  api.shake = (t, d) => {
    d = d || {};
    const amp = d.amp == null ? 9 : d.amp, dur = d.dur == null ? 0.32 : d.dur, n = Math.max(3, Math.round(dur * 30)), dt = dur / n;
    let px = 0, py = 0, pr = 0;
    for (let i = 1; i <= n; i++) {
      const k = Math.pow(1 - i / n, 1.4), nx = (rnd() * 2 - 1) * amp * k, ny = (rnd() * 2 - 1) * amp * k * 0.8, nr = (rnd() * 2 - 1) * 0.6 * k;
      tl.fromTo(B, { x: px, y: py, rotation: pr }, { x: nx, y: ny, rotation: nr, duration: dt, ease: "none", ...IM }, t + (i - 1) * dt);
      px = nx; py = ny; pr = nr;
    }
    tl.set(B, { x: 0, y: 0, rotation: 0 }, t + dur + 0.01);
  };

  // ---- aperture opener ------------------------------------------------------------------------
  api.aperture = (t0, t1, d) => {
    d = d || {};
    const side = d.side == null ? 34 : d.side;
    tl.fromTo(W, { clipPath: "inset(0% " + side + "% 0% " + side + "%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: t1 - t0, ease: "power3.out", ...IM }, t0);
    tl.set(W, { clipPath: "none" }, t1 + 0.01);
  };

  // ---- chromatic split on a punch word -------------------------------------------------------------
  api.rgb = (t, d) => {
    d = d || {};
    const px = d.px == null ? 9 : d.px, dur = d.dur == null ? 0.12 : d.dur;
    const p = { v: 0 };
    tl.set(W, { filter: "url(#rgb)" }, t - 0.01);
    tl.fromTo(p, { v: px }, { v: 0, duration: dur, ease: "power2.out", ...IM, onUpdate() { rgbR.setAttribute("dx", p.v.toFixed(2)); rgbB.setAttribute("dx", (-p.v).toFixed(2)); } }, t);
    tl.set(W, { filter: "none" }, t + dur + 0.01);
  };

  // ---- shared texture ---------------------------------------------------------------------------
  api.grain = (end) => tl.fromTo("#grain", { x: 0, y: 0 }, { x: -40, y: -50, duration: end, ease: "steps(" + Math.round(end * 12) + ")", ...IM }, 0);
  api.pulse = (times, amt) => times.forEach((t) => {
    tl.fromTo(B, { scale: 1 }, { scale: amt || 1.02, duration: 0.07, ease: "power2.out", ...IM }, t);
    tl.to(B, { scale: 1, duration: 0.16, ease: "power2.out" }, t + 0.07);
  });
  return api;
}
