#!/usr/bin/env node
// Build a YouTube/Instagram .srt from the WORDS caption array inside a reel's index.html.
// Usage: node make_srt.js <index.html> <out.srt>
const fs = require("fs");
const [, , html, out] = process.argv;
const src = fs.readFileSync(html, "utf8");
const m = src.match(/const WORDS = (\[[\s\S]*?\n\s*\]);/);
if (!m) throw new Error("WORDS array not found in " + html);
const W = JSON.parse(m[1].replace(/,\s*\]$/, "]").replace(/\]\s*,\s*\n\s*\]/, "]]"));
const fmt = (t) => {
  const ms = Math.round(t * 1000);
  const p = (n, w = 2) => String(n).padStart(w, "0");
  return `${p(Math.floor(ms / 3600000))}:${p(Math.floor(ms / 60000) % 60)}:${p(Math.floor(ms / 1000) % 60)},${p(ms % 1000, 3)}`;
};
const cues = [];
let cur = [];
W.forEach((w, i) => {
  cur.push(w);
  const end = /[.,?!]$/.test(w[0]);
  if ((end && cur.length >= 3) || cur.length >= 7 || i === W.length - 1) { cues.push(cur); cur = []; }
});
fs.writeFileSync(out, cues.map((c, i) => `${i + 1}\n${fmt(c[0][1])} --> ${fmt(c[c.length - 1][2])}\n${c.map((w) => w[0]).join(" ")}\n`).join("\n"));
console.log(`${cues.length} cues → ${out}`);
