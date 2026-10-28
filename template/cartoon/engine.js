/* Cartoon engine v1: SVG character + stage cards + word captions, driven by ONE paused GSAP timeline (HyperFrames clock).
   Input: window.CARTOON = {total, theme, character, words:[[start,end,text]], visemes:[[t,shape]], scenes:[...]}.
   Seek-safe: no repeat:-1, no random at runtime (blinks use a fixed schedule), mouth is a pure function of time. */
(function () {
  const C = window.CARTOON, root = document.getElementById("root"), tl = gsap.timeline({ paused: true });
  const T = C.total, ch = Object.assign({ skin: "#f6d2b0", shade: "#e6b78f", blush: "#f7a58e", hair: "#3f3532", hairHi: "#5f5552", beard: true, beardColor: "#3a2e2b", tee: "#853946", teeText: ["Ride the Wave.", "Obey the King."], teeInk: "#ee8574", ink: "#2b2321" }, C.character || {});
  const $ = (h) => { const d = document.createElement("div"); d.innerHTML = h.trim(); return d.firstChild; };
  const em = (s) => String(s).replace(/\*(.+?)\*/g, "<em>$1</em>");
  const add = (parent, node) => (parent.appendChild(node), node);

  /* ---------- character: the creator's own cartoon, rebuilt as a proper puppet ----------
     HEAD  = the traced original art (hair, face, ears, beard) with the eyes and brows redrawn on top so they can blink, look and lift.
     BODY  = drawn in code to match the cartoon: torso, collar, shirt text, two jointed arms (sleeve > forearm > wrist > hand), outline 9 u.
     All numbers are art units (the 760-wide trace; source px = units / 2 + (232,262)). Poses are joint angles, not pictures. */
  const SK = "#f6d2b0", TEE = "#853946", INK = "#2b2321", LW = 9, K = 0.72;
  const ol = `stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round" stroke-linecap="round"`, ol2 = `stroke="${INK}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"`;
  const cv = (str) => { let n = 0; return str.replace(/-?\d+(\.\d+)?/g, (m) => { const v = +m, i = n++; return +((i % 2 ? (v - 262) : (v - 232)) * 2).toFixed(1); }); };  // src px path -> art units
  const SH = { R: [554, 820], L: [154, 820] };                 // shoulder joints (art units)
  const EYE = { L: [235, 428], R: [469, 428] }, MOUTH = [352, 556], NECK = "372 676";
  const hand = (kind) => ({
    open: [-34, -62, -6, -12, -82, -6, 10, -76, -6, 30, -60, -6].reduce((h, _, i, arr) => (i % 3 ? h : h + `<rect x="${arr[i] - 9}" y="${arr[i + 1]}" width="18" height="${arr[i + 2] - arr[i + 1]}" rx="9" fill="${SK}" ${ol}/>`), "") + `<ellipse cx="0" cy="14" rx="46" ry="40" fill="${SK}" ${ol}/><ellipse cx="-52" cy="4" rx="14" ry="26" transform="rotate(-32 -52 4)" fill="${SK}" ${ol}/><ellipse cx="0" cy="14" rx="39" ry="33" fill="${SK}"/>`,
    point: `<rect x="-9" y="-100" width="18" height="96" rx="9" fill="${SK}" ${ol}/><ellipse cx="0" cy="16" rx="46" ry="40" fill="${SK}" ${ol}/><ellipse cx="-50" cy="8" rx="13" ry="22" transform="rotate(-32 -50 8)" fill="${SK}" ${ol}/><ellipse cx="0" cy="16" rx="39" ry="33" fill="${SK}"/><path d="M12 -2 q22 8 24 26 M10 18 q20 6 22 24" stroke="${INK}" stroke-width="6" fill="none" stroke-linecap="round"/>`,
    fist: `<ellipse cx="0" cy="12" rx="46" ry="42" fill="${SK}" ${ol}/><path d="M-20 -22 q-2 18 0 34 M0 -28 q-2 22 0 40 M20 -22 q2 18 0 34" stroke="${INK}" stroke-width="6" fill="none" stroke-linecap="round"/><ellipse cx="-22" cy="26" rx="22" ry="14" fill="${SK}" ${ol}/>`
  }[kind]);
  const arm = (side) => `<g id="arm${side}" class="armwrap" transform="translate(${SH[side][0]} ${SH[side][1]})${side === "L" ? " scale(-1 1)" : ""}"><g class="ua">
      <g transform="translate(0 100)"><g class="fa"><path d="M-38 -12 L-38 176 Q-38 200 0 200 Q38 200 38 176 L38 -12Z" fill="${SK}" ${ol}/>
        <g transform="translate(0 196)"><g class="hd"><g transform="scale(.82 -.82)">${["open", "point", "fist"].map((k) => `<g class="h-${k}" opacity="0">${hand(k)}</g>`).join("")}</g></g></g></g></g>
      <path d="M-52 10 C-52 -10 -46 -22 -32 -30 C-8 -44 22 -52 40 -46 C54 -40 56 -26 56 -10 L56 96 Q56 112 40 112 L-40 112 Q-52 112 -52 96Z" fill="${TEE}" ${ol}/></g></g>`;
  const eye = (side) => `<g class="eye" id="eye${side}" transform="translate(${EYE[side][0]} ${EYE[side][1]})"><g class="eyei"><ellipse rx="38" ry="48" fill="#171210"/><circle cx="-10" cy="-18" r="14" fill="#fff"/><circle cx="12" cy="22" r="7" fill="#fff"/></g></g>`;
  const lid = (side) => `<g class="lid" transform="translate(${EYE[side][0]} ${EYE[side][1]})" opacity="0"><ellipse rx="54" ry="60" fill="${SK}"/><path d="M-40 8 Q0 -24 40 8" stroke="#171210" stroke-width="10" fill="none" stroke-linecap="round"/></g>`;
  const SHAPES = {
    A: `<path d="M-34 0 Q0 7 34 0" stroke="${INK}" stroke-width="8" fill="none" stroke-linecap="round"/>`,
    B: `<path d="M-30 -2 Q0 -9 30 -2 Q0 15 -30 -2Z" fill="#5a1f1b" ${ol2}/>`,
    C: `<path d="M-32 -6 Q0 -14 32 -6 Q26 24 0 26 Q-26 24 -32 -6Z" fill="#5a1f1b" ${ol2}/><ellipse cx="0" cy="17" rx="13" ry="6" fill="#e0675f"/>`,
    D: `<path d="M-38 -10 Q0 -22 38 -10 Q36 40 0 42 Q-36 40 -38 -10Z" fill="#5a1f1b" ${ol2}/><path d="M-30 -9 Q0 -18 30 -9 L28 2 Q0 -5 -28 2Z" fill="#fff"/><ellipse cx="0" cy="27" rx="19" ry="9" fill="#e0675f"/>`,
    E: `<ellipse rx="20" ry="25" fill="#5a1f1b" ${ol2}/><ellipse cx="0" cy="12" rx="10" ry="6" fill="#e0675f"/>`,
    F: `<ellipse rx="13" ry="16" fill="#5a1f1b" ${ol2}/>`,
    G: `<path d="M-30 -4 Q0 -10 30 -4 L28 7 Q0 3 -28 7Z" fill="#fff" ${ol2}/><path d="M-26 14 Q0 22 26 14" stroke="${INK}" stroke-width="7" fill="none" stroke-linecap="round"/>`,
    H: `<path d="M-32 -6 Q0 -14 32 -6 Q26 24 0 26 Q-26 24 -32 -6Z" fill="#5a1f1b" ${ol2}/><ellipse cx="0" cy="-1" rx="12" ry="7" fill="#e0675f"/>`
  };
  const svg = `<svg id="avi" viewBox="0 0 760 2120" width="${760 * K}" height="${2120 * K}" style="position:absolute;left:${(1080 - 760 * K) / 2}px;top:${1060 - 20 * K}px;overflow:visible">
    <defs><clipPath id="cHead"><rect x="-400" y="-100" width="1560" height="782"/></clipPath></defs>
    <g id="torso">
      <path d="${cv("M 392 590 L 426 590 L 426 616 L 392 616 Z")}" fill="${SK}"/><path d="${cv("M 392 598 L 392 614 M 426 598 L 426 614")}" fill="none" ${ol}/>
      <path d="${cv("M 362 610 C 340 618 318 640 304 668 L 312 730 L 326 900 L 492 900 L 506 730 L 514 668 C 500 640 478 618 456 610 Q 409 630 362 610 Z")}" fill="${TEE}" ${ol}/>
      <path d="${cv("M 362 611 Q 409 644 456 611")}" fill="none" ${ol}/>
      <text x="${(409 - 232) * 2}" y="${(659 - 262) * 2}" text-anchor="middle" font-family="Caveat, 'Bradley Hand', cursive" font-weight="700" font-size="23" fill="#e5806f">Ride the Wave.</text>
      <text x="${(409 - 232) * 2}" y="${(676 - 262) * 2}" text-anchor="middle" font-family="Caveat, 'Bradley Hand', cursive" font-weight="700" font-size="23" fill="#e5806f">Obey the King.</text>
    </g>
    <g id="headg"><g id="hs"><g id="head"><use href="#avi-art" clip-path="url(#cHead)"/>
      <g id="brows"><path d="${cv("M 327 439 Q 350 424 374 436")}" stroke="#171210" stroke-width="18" fill="none" stroke-linecap="round"/><path d="${cv("M 443 436 Q 468 424 491 438")}" stroke="#171210" stroke-width="18" fill="none" stroke-linecap="round"/></g>
      <g id="eyes">${eye("L")}${eye("R")}</g>${lid("L")}${lid("R")}
      <g id="mouthov" style="display:none" transform="translate(${MOUTH[0]} ${MOUTH[1]})"><ellipse cx="0" cy="-3" rx="56" ry="24" fill="#f6d2b0"/>${Object.keys(SHAPES).map((k) => `<g class="m m-${k}" style="display:none">${SHAPES[k]}</g>`).join("")}</g>
    </g></g></g>
    <g class="armlift">${arm("L")}${arm("R")}</g></svg>`;
  add(root, $(svg));
  gsap.set(["#hs", "#head"], { svgOrigin: NECK });
  gsap.set([".ua", ".fa", ".hd"], { svgOrigin: "0 0" });
  /* ---- poses = joint angles (right arm; the left arm is the same rig mirrored, so the same numbers mirror automatically).
     [shoulder, elbow, wrist, hand]; 0 = hanging straight down, negative = swings out and up ---- */
  /* two-bone IK: aim the wrist at a point (art units) so hands land exactly where they should (chin, stage object) instead of guessing angles */
  const L1 = 100, L2 = 205;
  const ik = (side, tx, ty) => {
    const S = SH[side]; let dx = tx - S[0]; const dy = ty - S[1]; if (side === "L") dx = -dx;
    const r = Math.min(Math.hypot(dx, dy), L1 + L2 - 1), dir = Math.atan2(-dx, dy), a = Math.acos((L1 * L1 + r * r - L2 * L2) / (2 * L1 * r));
    let best = null;
    [1, -1].forEach((sg) => { const ts = dir + sg * a, ex = -Math.sin(ts) * L1, ey = Math.cos(ts) * L1, tf = Math.atan2(-(dx - ex), dy - ey); let te = tf - ts; te = Math.atan2(Math.sin(te), Math.cos(te)); if (!best || ey > best.ey) best = { s: ts, e: te, ey }; });
    return [+(best.s * 180 / Math.PI).toFixed(1), +(best.e * 180 / Math.PI).toFixed(1)];
  };
  const REST = [0, 22, 0, "open"];
  const POSES = {
    rest: { R: REST, head: 0, lift: 0 },
    explain: { R: [-58, -72, 8, "open"], L: [8, 24, 0, "open"], head: -2 },
    point: { R: [-112, -82, -6, "point"], L: REST, head: 2.5 },
    count: { R: [-84, -104, 0, "point"], L: REST, head: 1.5 },
    shrug: { R: [-40, -104, 12, "open"], head: 3, lift: -14 },
    think: { R: [...ik("R", 438, 648), 0, "fist"], L: REST, head: -3 },
    cheer: { R: [-150, -18, 10, "open"], head: 0, lift: -10 },
    both: { R: [-64, -78, 6, "open"], head: 0 },
    wave: { R: [-128, -52, 0, "open"], L: REST, head: 2, wave: true }
  };
  const ACC = new Set(C.scenes.flatMap((s) => s.accent || []).map((w) => w.toLowerCase().replace(/[^\w]/g, "")));
  const arms = { R: "#armR", L: "#armL" }, cur = { name: null };
  const pose = (name, t) => {
    const p = POSES[name] || POSES.rest, prev = POSES[cur.name] || POSES.rest; if (name === cur.name) return; cur.name = name;
    ["R", "L"].forEach((side) => {
      const to = side === "R" ? p.R : (p.L || p.R), id = arms[side], was = side === "R" ? prev.R : (prev.L || prev.R);
      const lag = side === "R" ? 0 : 0.04;
      ["open", "point", "fist"].forEach((k) => tl.set(`${id} .h-${k}`, { opacity: to[3] === k ? 1 : 0 }, t));
      /* anticipation (a small pull-back), then shoulder leads, elbow follows 0.06 s later, wrist 0.12 s later, each with a little overshoot */
      tl.to(`${id} .ua`, { rotation: was[0] * 0.9 + (to[0] < was[0] ? 5 : -5), duration: 0.09, ease: "power1.out" }, t + lag)
        .to(`${id} .ua`, { rotation: to[0], duration: 0.42, ease: "back.out(1.5)" }, t + lag + 0.09)
        .to(`${id} .fa`, { rotation: to[1], duration: 0.42, ease: "back.out(1.7)" }, t + lag + 0.15)
        .to(`${id} .hd`, { rotation: to[2], duration: 0.4, ease: "back.out(2)" }, t + lag + 0.21);
    });
    /* secondary motion: head tilts into the gesture a beat late, body lifts/drops, then settles */
    tl.to("#head", { rotation: p.head || 0, duration: 0.5, ease: "back.out(1.6)" }, t + 0.1)
      .to(["#torso", ".armlift"], { y: (p.lift || 0), duration: 0.35, ease: "power2.out" }, t)
      .to("#headg", { y: (p.lift || 0) * 0.6, duration: 0.45, ease: "power2.out" }, t + 0.05);
    if (p.wave) for (let k = 0; k < 4; k++) tl.to(`${arms.R} .hd`, { rotation: k % 2 ? 6 : 26, duration: 0.22, ease: "sine.inOut" }, t + 0.65 + k * 0.22);
  };
  /* ---- life: breathing, blinks (some double), moving holds, eye darts, emphasis nods ---- */
  for (let t = 0, k = 0; t < T; t += 1.8, k++) tl.to(["#torso"], { scaleY: k % 2 ? 1 : 1.012, svgOrigin: "372 1270", duration: 1.8, ease: "sine.inOut" }, t);
  for (let t = 1.9, k = 0; t < T; t += 2.4 + (k++ % 4) * 0.55) { const d = k % 4 === 3 ? 0.2 : 0; tl.set(".lid", { opacity: 1 }, t).set(".lid", { opacity: 0 }, t + 0.12); if (d) tl.set(".lid", { opacity: 1 }, t + d + 0.12).set(".lid", { opacity: 0 }, t + d + 0.24); }
  for (let t = 0, k = 0; t < T; t += 2.1, k++) tl.to("#hs", { rotation: k % 2 ? 1.1 : -1.1, duration: 2.1, ease: "sine.inOut" }, t);
  C.words.forEach((w) => { const key = w[2].toLowerCase().replace(/[^\w]/g, ""); if (ACC.has(key)) { tl.to("#headg", { y: "+=7", duration: 0.09, ease: "power2.out" }, w[0]).to("#headg", { y: "-=7", duration: 0.24, ease: "power2.inOut" }, w[0] + 0.09).to("#brows", { y: -8, duration: 0.1 }, w[0] - 0.05).to("#brows", { y: 0, duration: 0.3 }, w[0] + 0.3); } });
  C.scenes.forEach((sc) => { if (sc.stage) tl.to(".eyei", { y: -9, duration: 0.2, ease: "power2.out" }, sc.from + 0.1).to(".eyei", { y: 0, duration: 0.3, ease: "power2.inOut" }, sc.from + 0.9); });
  /* ---- mouth: Rhubarb-style shapes A-H, X = rest (the cartoon's own smile). Pure function of time. ---- */
  const LEG = { closed: "X", small: "B", mid: "C", wide: "D", round: "E" };
  const V = C.visemes.map((v) => [v[0], LEG[v[1]] || v[1]]); let last = "";
  const mouthAt = (t) => { let lo = 0, hi = V.length - 1, r = "X"; while (lo <= hi) { const m = (lo + hi) >> 1; if (V[m][0] <= t) { r = V[m][1]; lo = m + 1; } else hi = m - 1; } return r; };
  tl.to({}, { duration: T }, 0);
  tl.eventCallback("onUpdate", () => {
    const s = mouthAt(tl.time()); if (s === last) return; last = s;
    document.getElementById("mouthov").style.display = s === "X" ? "none" : "inline";
    document.querySelectorAll("#mouthov .m").forEach((g) => (g.style.display = g.classList.contains("m-" + s) ? "inline" : "none"));
  });

  /* ---------- stage components: each returns an element; entrance/exit timed by the scene ---------- */
  const S = {
    big: (o) => $(`<div class="big">${em(o.text)}</div>`),
    card: (o) => $(`<div class="card"><div class="ct">${em(o.title || "")}</div><div class="cb">${em(o.body || "")}</div></div>`),
    stamp: (o) => $(`<div class="stamp">${em(o.text)}</div>`),
    counter: (o) => $(`<div class="counter"><div class="num" data-from="${o.from || 0}" data-to="${o.to}" data-pre="${o.prefix || ""}" data-suf="${o.suffix || ""}">${o.prefix || ""}${o.from || 0}${o.suffix || ""}</div><div class="lab">${em(o.label || "")}</div></div>`),
    phone: (o) => $(`<div class="phone"><div class="notch"></div><div class="screen">${(o.lines || []).map((l) => `<div class="msg ${l.who === "me" ? "me" : "them"}">${em(l.text)}${l.tick ? `<span class="tk">${l.tick}</span>` : ""}</div>`).join("")}</div></div>`),
    terminal: (o) => $(`<div class="term"><div class="bar"><i></i><i></i><i></i></div><div class="tb">${(o.lines || []).map((l) => `<div class="tl">${String(l).replace(/</g, "&lt;")}</div>`).join("")}</div></div>`),
    checklist: (o) => $(`<div class="card"><div class="ct">${em(o.title || "")}</div>${(o.items || []).map((i) => `<div class="ck"><span class="bx"></span><span>${em(i)}</span></div>`).join("")}</div>`),
    flow: (o) => $(`<div class="flow">${(o.nodes || []).map((n, i) => `${i ? '<div class="ar">↓</div>' : ""}<div class="node">${em(n)}</div>`).join("")}</div>`)
  };
  const enter = {
    default: (e, t) => tl.fromTo(e, { opacity: 0, y: 60, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.5)" }, t),
    stamp: (e, t) => tl.fromTo(e, { opacity: 0, scale: 2.4, rotation: -18 }, { opacity: 1, scale: 1, rotation: -8, duration: 0.22, ease: "power4.in" }, t)
  };
  const inner = (el, type, sc, t0, t1) => {
    const kids = (sel) => [...el.querySelectorAll(sel)], span = Math.max(0.6, t1 - t0 - 0.9);
    if (type === "phone") kids(".msg").forEach((m, i, a) => tl.fromTo(m, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, t0 + 0.5 + (span * i) / Math.max(1, a.length)));
    if (type === "terminal") kids(".tl").forEach((m, i, a) => tl.fromTo(m, { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.2 }, t0 + 0.5 + (span * i) / Math.max(1, a.length)));
    if (type === "checklist") kids(".ck").forEach((m, i, a) => { const at = t0 + 0.5 + (span * i) / Math.max(1, a.length); tl.fromTo(m, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.25 }, at).to(m.querySelector(".bx"), { backgroundColor: "var(--ok)", duration: 0.12 }, at + 0.35); sfx("check-blip", at + 0.35, 0.3); });
    if (type === "flow") kids(".node,.ar").forEach((m, i, a) => tl.fromTo(m, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.28 }, t0 + 0.4 + (span * i) / Math.max(1, a.length)));
    if (type === "counter") { const n = el.querySelector(".num"), o = { v: +n.dataset.from }; tl.to(o, { v: +n.dataset.to, duration: Math.min(1.6, span), ease: "power2.out", onUpdate: () => (n.textContent = n.dataset.pre + Math.round(o.v).toLocaleString("en-IN") + n.dataset.suf) }, t0 + 0.4); }
  };
  const sfxList = [];
  const sfx = (name, t, vol) => sfxList.push([name, t, vol || 0.35]);

  /* ---------- scenes ---------- */
  const kick = add(root, $(`<div id="kick"></div>`)); add(root, $(`<div id="brand">${(C.brand || "").toUpperCase()}</div>`)); add(root, $(`<div id="pbar"></div>`));
  tl.fromTo("#pbar", { scaleX: 0 }, { scaleX: 1, duration: T, ease: "none" }, 0);
  C.scenes.forEach((sc, i) => {
    const t0 = sc.from, t1 = sc.to; pose(sc.pose || "rest", t0);
    if (sc.kicker) { tl.set(kick, { textContent: sc.kicker }, t0); }
    if (sc.stage) {
      const type = sc.stage.type, w = add(root, $('<div class="stg"></div>')), e = add(w, S[type](sc.stage)); w.id = "stg" + i;
      (enter[type] || enter.default)(w, t0 + 0.05);
      tl.to(w, { opacity: 0, y: -30, duration: 0.25, ease: "power2.in" }, t1 - 0.28);
      inner(e, type, sc, t0, t1); sfx(type === "stamp" ? "hit-heavy" : "pop", t0 + 0.05, type === "stamp" ? 0.5 : 0.3);
    }
    (sc.sfx || []).forEach((x) => sfx(x[0], x[1], x[2]));
    if (i) sfx("paper-slide", t0, 0.22);
  });

  /* ---------- captions: 3-4 word chunks; words go from grey to ink as spoken; accent words = serif italic ---------- */
  const acc = new Set(C.scenes.flatMap((s) => s.accent || []).map((w) => w.toLowerCase().replace(/[^\w]/g, "")));
  const W = C.words, chunks = []; let cur2 = [];
  W.forEach((w, i) => { cur2.push(w); if (cur2.length >= 4 || /[.?!,;:]$/.test(w[2]) || (W[i + 1] && W[i + 1][0] - w[1] > 0.5)) { chunks.push(cur2); cur2 = []; } }); if (cur2.length) chunks.push(cur2);
  chunks.forEach((c, ci) => {
    const e = add(root, $(`<div class="cap">${c.map((w, wi) => `<span class="w${acc.has(w[2].toLowerCase().replace(/[^\w]/g, "")) ? " a" : ""}" id="w${ci}_${wi}">${w[2]}</span>`).join(" ")}</div>`));
    const a = Math.max(0, c[0][0] - 0.05), b = chunks[ci + 1] ? chunks[ci + 1][0][0] - 0.05 : T;
    tl.fromTo(e, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.12 }, a).set(e, { opacity: 0 }, b);
    c.forEach((w, wi) => tl.to(`#w${ci}_${wi}`, { color: acc.has(w[2].toLowerCase().replace(/[^\w]/g, "")) ? "var(--accent)" : "var(--ink)", duration: 0.08 }, w[0]));
  });

  /* ---------- audio cues (sfx elements are added by the builder from this list) ---------- */
  window.__SFX = sfxList; window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl;
})();
