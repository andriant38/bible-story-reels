#!/usr/bin/env python3
"""split.py file.mp3 N -> file_1.wav..file_N.wav cut at the N-1 longest silences; also trims each piece."""
import sys, subprocess, re
f, n = sys.argv[1], int(sys.argv[2])
base = f.rsplit('.', 1)[0]
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
out = subprocess.run(["ffmpeg","-i",f,"-af","silencedetect=n=-42dB:d=0.25","-f","null","-"],capture_output=True,text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
sil = list(zip(st, en))
inner = [s for s in sil if s[0] > 0.05 and s[1] < dur - 0.05]
cuts = sorted(sorted(inner, key=lambda s: s[1]-s[0], reverse=True)[:n-1])
if len(cuts) < n-1: sys.exit(f"only {len(cuts)} gaps in {f}")
bounds = [0.0] + [ (a+b)/2 for a,b in cuts ] + [dur]
for i in range(n):
    a, b = bounds[i], bounds[i+1]
    o = f"{base}_{i+1}.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-ss",f"{a:.3f}","-to",f"{b:.3f}","-af",
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,apad=pad_dur=0.05",
        "-ar","44100","-ac","2",o],check=True)
    d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",o]))
    print(f"{o} {d:.2f}s (gap {b-a:.2f})")
print("gaps used:", [round(b-a,2) for a,b in cuts])
