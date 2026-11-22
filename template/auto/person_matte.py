#!/usr/bin/env python3
"""person_matte.py — cut the speaker out of the cut once per reel (Round 14, 22 Nov 2026).

  python3 -I person_matte.py <project dir>  [--quality accurate|balanced|fast] [--size 1080x1920] [--force]

Reads <project>/assets/main.mp4, writes <project>/assets/fg.webm: the same frames with the PERSON opaque and the room transparent
(VP9 + alpha, Chrome-native). compose.py stacks:  room video -> #behind (big word, ribbon, orbs, room tint) -> fg.webm -> captions/cards.
Both videos start at 0, so they decode in sync (HyperFrames text-behind-subject rule). Cached: skipped when fg.webm is newer than main.mp4.
Engine: Apple Vision VNGeneratePersonSegmentationRequest (person_matte.swift); fallback `npx hyperframes remove-background` (u2net, 320 px input).
Cost on an M-series Mac: ~0.4 s/frame accurate, roughly 4x faster at balanced; the matte is cached so re-composes after notes are free.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def fps_of(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    n, d = r.split("/")
    return float(n) / float(d)


def main():
    proj = os.path.abspath(sys.argv[1])
    q = sys.argv[sys.argv.index("--quality") + 1] if "--quality" in sys.argv else os.environ.get("MATTE_QUALITY", "balanced")
    W, H = map(int, (sys.argv[sys.argv.index("--size") + 1] if "--size" in sys.argv else "1080x1920").split("x"))
    src = os.path.realpath(os.path.join(proj, "assets", "main.mp4"))
    dst = os.path.join(proj, "assets", "fg.webm")
    if os.path.exists(dst) and os.path.getmtime(dst) > os.path.getmtime(src) and "--force" not in sys.argv:
        print(f"matte cached: {dst}"); return
    exe = os.path.join(HERE, "person_matte")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(os.path.join(HERE, "person_matte.swift")):
        r = subprocess.run(["swiftc", "-O", os.path.join(HERE, "person_matte.swift"), "-o", exe], capture_output=True, text=True)
        if r.returncode:
            print("swift build failed, falling back to hyperframes remove-background:", r.stderr[-400:], file=sys.stderr)
            subprocess.run(["npx", "--yes", "hyperframes", "remove-background", src, "-o", dst, "--quality", "best"], check=True)
            return
    fps = fps_of(src); t0 = time.time()
    tmp = dst + ".part.webm"
    m = subprocess.Popen([exe, src, str(W), str(H), q], stdout=subprocess.PIPE)
    # mask: light feather (1.2 px) so hair edges don't stair-step; colour comes from the same cut, so the overlap is invisible
    ff = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                         "-filter_complex", f"[0:v]scale={W}:{H}:flags=lanczos,format=yuva420p[c];[1:v]gblur=sigma=1.2,format=gray[m];[c][m]alphamerge,format=yuva420p[o]",
                         "-map", "[o]", "-an", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8",
                         "-row-mt", "1", "-auto-alt-ref", "0", tmp], stdin=m.stdout)
    m.stdout.close(); m.wait()
    if ff.returncode or m.returncode:
        raise SystemExit(f"matte failed (vision {m.returncode}, ffmpeg {ff.returncode})")
    os.replace(tmp, dst)
    print(f"matte: {dst} ({q}, {time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
