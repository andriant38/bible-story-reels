"""Split one narration file that covers several scenes into per-scene clips.

Use this when ElevenLabs keeps answering "busy": send several scenes in ONE speech call,
with a blank line between scenes, then split the result here.

  python engine/split_audio.py combo.mp3 work/<slug> 4 5 9 11 --story stories/<slug>.json

The numbers are the scene numbers the file covers, in order. Each cut is placed at the pause
closest to where it is expected, estimated from the scene text lengths.
"""
import argparse
import json
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("outdir")
ap.add_argument("scenes", nargs="+", type=int)
ap.add_argument("--story", required=True)
a = ap.parse_args()

texts = [json.load(open(a.story, encoding="utf-8"))["scenes"][n - 1]["text"] for n in a.scenes]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.audio],
                           capture_output=True, text=True).stdout)
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.audio, "-af", "silencedetect=n=-40dB:d=0.3", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
sil = [(s, e) for s, e in zip(st, en) if e - s >= 0.45]

total = sum(len(t) for t in texts)
cuts, acc, used = [], 0, set()
for t in texts[:-1]:
    acc += len(t)
    expect = acc / total * dur
    best = min((i for i in range(len(sil)) if i not in used),
               key=lambda i: abs((sil[i][0] + sil[i][1]) / 2 - expect) - 1.5 * (sil[i][1] - sil[i][0]))
    used.add(best)
    cuts.append(sil[best])
cuts.sort()
starts = [0.0] + [e - 0.1 for _, e in cuts]
ends = [s + 0.1 for s, _ in cuts] + [dur]
for n, s, e in zip(a.scenes, starts, ends):
    out = f"{a.outdir}/{n:02d}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
                    "-c:a", "libmp3lame", "-q:a", "2", out], check=True)
    print(f"scene {n}: {s:.2f}-{e:.2f}s -> {out}")
