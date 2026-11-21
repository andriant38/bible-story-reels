"""Split one narration file (all scenes, blank line between them) into per-scene clips.

  python3 konstruksi/engine/split_audio.py combo.mp3 work/k-<slug> --story konstruksi/stories/<slug>.json [--scenes 2-14]

Unlike engine/split_audio.py (greedy, one cut at a time), this picks ALL cut points together:
it chooses, in order, the pauses that best match where each scene should end
(from the scene text lengths), preferring longer pauses. Check the printed durations.
"""
import argparse
import json
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("outdir")
ap.add_argument("--story", required=True)
ap.add_argument("--scenes", default=None, help="range of scene numbers the file covers, e.g. 2-14 (default: all)")
a = ap.parse_args()

scenes = json.load(open(a.story, encoding="utf-8"))["scenes"]
if a.scenes:
    lo, hi = map(int, a.scenes.split("-"))
    nums = list(range(lo, hi + 1))
else:
    nums = list(range(1, len(scenes) + 1))
texts = [scenes[n - 1]["text"] for n in nums]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio],
                           capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.audio, "-af", "silencedetect=n=-40dB:d=0.25", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
sil = [(s, e) for s, e in zip(st, en) if e < dur - 0.05]

# expected end time of each scene, proportional to characters (+ a fixed pause per scene)
w = [len(t) + 25 for t in texts]
tot = sum(w)
expect, acc = [], 0
for x in w[:-1]:
    acc += x
    expect.append(acc / tot * dur)

K, M = len(expect), len(sil)
if M < K:
    raise SystemExit(f"only {M} pauses found for {K} cuts")


def cost(k, i):
    s, e = sil[i]
    mid = (s + e) / 2
    return (mid - expect[k]) ** 2 - 6.0 * (e - s)  # reward longer pauses


INF = float("inf")
best = [[INF] * M for _ in range(K)]
back = [[-1] * M for _ in range(K)]
for i in range(M):
    best[0][i] = cost(0, i)
for k in range(1, K):
    run, arg = INF, -1
    for i in range(M):
        if i - 1 >= 0 and best[k - 1][i - 1] < run:
            run, arg = best[k - 1][i - 1], i - 1
        if arg >= 0:
            best[k][i] = run + cost(k, i)
            back[k][i] = arg
i = min(range(M), key=lambda j: best[K - 1][j])
pick = [i]
for k in range(K - 1, 0, -1):
    i = back[k][i]
    pick.append(i)
cuts = [sil[j] for j in reversed(pick)]

starts = [0.0] + [e - 0.1 for _, e in cuts]
ends = [s + 0.1 for s, _ in cuts] + [dur]
for n, s, e, t in zip(nums, starts, ends, texts):
    out = f"{a.outdir}/{n:02d}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                    "-c:a", "libmp3lame", "-q:a", "2", out], check=True)
    print(f"scene {n:2d}: {s:6.2f}-{e:6.2f}s ({e - s:4.1f}s, {len(t):3d} chars) {t[:40]}")
