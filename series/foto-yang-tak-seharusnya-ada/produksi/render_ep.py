#!/usr/bin/env python3
"""Render one episode of FOTO YANG TAK SEHARUSNYA ADA from a JSON spec.

Spec:
{
  "ep": 3, "music": "music_tense", "music_vol": 0.5,
  "scenes": [
    {"shots": [["img", z0, z1, x0, x1, y0, y1], ...],   # Ken Burns per shot, split evenly
     "min": 4.0,                                         # minimum scene length
     "lead": 0.25,                                       # delay before first line
     "events": [{"vo": "e3_nar_1", "sub": "text **key**", "gap": 0.35, "tempo": 1.0}],
     "big": "TEXT", "big_at": 0.0, "big_dur": null,      # big centre text (optional)
     "label": "RAKA", "label_dur": 2.5,                  # small lower-third (optional)
     "sfx": [["boom", 0.0, 1.0]],                        # file, offset in scene, volume
     "mvol": 1.0, "tail": 0.45, "dim": false}
  ],
  "end": {"dur": 5.5, "lines": [["SIAPA PRIA ITU?", 0.2, "Big"], ["EPISODE 4 BESOK.", 2.8, "Ep"]],
          "events": [...], "sfx": [["boom", 0.0, 1.2]], "mvol": 0.0},
  "beds": [["amb", 0.0, 6.0, 0.3]],                      # file, start, end, volume (looped)
  "tick": [6.0, 30.0]                                     # synthetic wall clock between t0 and t1
}
"""
import json, os, re, subprocess, sys

D = os.path.dirname(os.path.abspath(__file__))
FONTS = "/home/user/bible-story-reels/assets/fonts"
W, H, FPS = 1080, 1920, 30


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]))


def vo_path(name):
    for ext in (".wav", ".mp3"):
        p = f"{D}/vo/{name}{ext}"
        if os.path.exists(p):
            return p
    raise FileNotFoundError(name)


def img_path(name):
    for d in ("img",):
        for ext in (".png", ".jpg"):
            p = f"{D}/{d}/{name}{ext}"
            if os.path.exists(p):
                return p
    raise FileNotFoundError(name)


def shot_clip(img, d, z0, z1, x0, x1, y0, y1, out, dim=False):
    p = f"(t/{d:.3f})"
    z = f"({z0}+({z1}-{z0})*{p})"
    extra = ",eq=brightness=-0.06:saturation=0.85" if dim else ""
    vf = (f"scale=w='trunc({W}*{z}/2)*2':h=-2:eval=frame:flags=lanczos,"
          f"crop={W}:{H}:'(iw-{W})*({x0}+({x1}-{x0})*{p})':'(ih-{H})*({y0}+({y1}-{y0})*{p})',"
          f"setsar=1{extra},format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img_path(img),
         "-t", f"{d:.3f}", "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "17",
         "-r", str(FPS), out])


def ass_text(t):
    t = t.replace("{", "(").replace("}", ")")
    return re.sub(r"\*\*(.+?)\*\*", r"{\\c&H0030C8FF&}\1{\\c&H00FFFFFF&}", t)


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def main(spec_path):
    S = json.load(open(spec_path))
    ep = S["ep"]
    work = f"{D}/out/ep{ep:02d}"
    os.makedirs(work, exist_ok=True)

    # ---------- timeline ----------
    t = 0.0
    voice, subs, sfx, clips, mvols = [], [], [], [], []
    for si, sc in enumerate(S["scenes"]):
        start = t
        cur = start + sc.get("lead", 0.25)
        last_end = start
        for ev in sc.get("events", []):
            cur += ev.get("pre", 0.0)
            tempo = ev.get("tempo", 1.0)
            d = dur(vo_path(ev["vo"])) / tempo
            voice.append((ev["vo"], cur, tempo, ev.get("vol", 1.0)))
            if ev.get("sub"):
                subs.append((cur, cur + d + 0.15, "Sub", ev["sub"]))
            last_end = cur + d
            cur = last_end + ev.get("gap", 0.35)
        length = max(sc.get("min", 4.0), last_end - start + sc.get("tail", 0.45))
        if sc.get("big"):
            b0 = start + sc.get("big_at", 0.0)
            subs.append((b0, b0 + (sc.get("big_dur") or length - sc.get("big_at", 0.0)), "Big", sc["big"]))
        if sc.get("label"):
            subs.append((start + 0.3, start + 0.3 + sc.get("label_dur", 2.6), "Label", sc["label"]))
        for f, off, v in sc.get("sfx", []):
            sfx.append((f, start + off, v))
        mvols.append((start, start + length, sc.get("mvol", 1.0)))
        shots = sc["shots"]
        n = len(shots)
        weights = sc.get("weights", [1] * n)
        acc = start
        for k, sh in enumerate(shots):
            d = length * weights[k] / sum(weights)
            clips.append((sh, d, sc.get("dim", False)))
            acc += d
        t = start + length

    end = S.get("end", {})
    end_start = t
    cur = end_start + end.get("lead", 0.3)
    for ev in end.get("events", []):
        tempo = ev.get("tempo", 1.0)
        d = dur(vo_path(ev["vo"])) / tempo
        voice.append((ev["vo"], cur, tempo, ev.get("vol", 1.0)))
        if ev.get("sub"):
            subs.append((cur, cur + d + 0.15, "SubLow", ev["sub"]))
        cur += d + ev.get("gap", 0.35)
    end_len = max(end.get("dur", 5.0), cur - end_start + 0.6)
    TOTAL = end_start + end_len
    for line in end.get("lines", []):
        txt, off = line[0], line[1]
        style = line[2] if len(line) > 2 else "Big"
        subs.append((end_start + off, TOTAL, style, txt))
    for f, off, v in end.get("sfx", []):
        sfx.append((f, end_start + off, v))
    mvols.append((end_start, TOTAL, end.get("mvol", 0.0)))

    # ---------- video ----------
    lst = []
    for i, (sh, d, dim) in enumerate(clips):
        out = f"{work}/c{i:02d}.mp4"
        shot_clip(sh[0], d, *sh[1:7], out, dim=dim)
        lst.append(out)
    blk = f"{work}/black.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}",
         "-t", f"{end_len:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", blk])
    lst.append(blk)
    with open(f"{work}/list.txt", "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in lst)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt",
         "-c", "copy", f"{work}/base.mp4"])

    # ---------- subtitles ----------
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter ExtraBold,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,4,2,2,90,90,560,1
Style: SubLow,Inter ExtraBold,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,4,2,2,90,90,640,1
Style: Big,Inter ExtraBold,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,5,3,5,70,70,0,1
Style: Big2,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,5,3,8,70,70,1010,1
Style: Ep,Inter ExtraBold,66,&H0030C8FF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,4,2,2,70,70,700,1
Style: Small,Inter SemiBold,48,&H00E6E6E6,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,3,2,2,90,90,560,1
Style: Label,Inter ExtraBold,40,&H0030C8FF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,3,0,1,3,2,1,80,80,360,1
Style: Tag,Inter SemiBold,34,&H00E6E6E6,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,3,0,1,2,1,8,60,60,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    tag = S.get("tag", f"FOTO YANG TAK SEHARUSNYA ADA  •  EP {ep}")
    ass += f"Dialogue: 0,{ts(0)},{ts(end_start)},Tag,,0,0,0,,{tag}\n"
    for a, b, st, tx in subs:
        fade = r"{\fad(80,220)}" if st in ("Big", "Big2", "Ep") else r"{\fad(120,120)}"
        ass += f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{fade}{ass_text(tx)}\n"
    with open(f"{work}/subs.ass", "w") as fh:
        fh.write(ass)

    # ---------- audio ----------
    inputs, parts, vl, sl = [], [], [], []
    k = 0
    def add(p):
        nonlocal k
        inputs.extend(["-i", p]); k += 1; return k
    for name, st, tempo, v in voice:
        i = add(vo_path(name))
        tp = f"atempo={tempo}," if abs(tempo - 1) > 1e-3 else ""
        parts.append(f"[{i}:a]aresample=44100,{tp}volume={v},adelay={int(st*1000)}:all=1,apad=whole_dur={TOTAL:.3f}[v{i}]")
        vl.append(f"[v{i}]")
    for name, st, v in sfx:
        i = add(f"{D}/sfx/n/{name}.wav")
        parts.append(f"[{i}:a]volume={v},adelay={int(st*1000)}:all=1,apad=whole_dur={TOTAL:.3f}[s{i}]")
        sl.append(f"[s{i}]")
    for name, a, b, v in S.get("beds", []):
        i = add(f"{D}/sfx/n/{name}.wav")
        L = b - a
        parts.append(f"[{i}:a]aloop=loop=-1:size=2e9,atrim=0:{L:.3f},volume={v},afade=t=in:d=0.6,"
                     f"afade=t=out:st={max(L-0.8,0):.3f}:d=0.8,adelay={int(a*1000)}:all=1,apad=whole_dur={TOTAL:.3f}[s{i}]")
        sl.append(f"[s{i}]")
    if S.get("tick"):
        a, b = S["tick"]
        L = b - a
        parts.append(f"aevalsrc='0.35*exp(-90*mod(t,1))*sin(2*PI*2200*t)':s=44100:d={L:.3f},highpass=f=900,"
                     f"volume=0.16,afade=t=in:d=1,afade=t=out:st={max(L-1.5,0):.3f}:d=1.5,"
                     f"adelay={int(a*1000)}:all=1,apad=whole_dur={TOTAL:.3f}[tick]")
        sl.append("[tick]")
    if not sl:
        parts.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{TOTAL:.3f}[s0]"); sl.append("[s0]")
    i = add(f"{D}/sfx/n/{S.get('music', 'music_tense')}.wav")
    expr = "1"
    for a, b, v in reversed(mvols):
        expr = f"if(between(t,{a:.2f},{b:.2f}),{v},{expr})"
    mv = S.get("music_vol", 0.5)
    parts.append(f"[{i}:a]atrim=0:{TOTAL:.3f},volume='{mv}*({expr})':eval=frame,"
                 f"afade=t=out:st={TOTAL-1.2:.3f}:d=1.2,apad=whole_dur={TOTAL:.3f}[mus]")
    parts.append("".join(vl) + f"amix=inputs={len(vl)}:normalize=0,atrim=0:{TOTAL:.3f},asplit=2[vo1][vo2]")
    parts.append("".join(sl) + f"amix=inputs={len(sl)}:normalize=0,atrim=0:{TOTAL:.3f}[fx]")
    parts.append("[mus][vo1]sidechaincompress=threshold=0.02:ratio=8:attack=15:release=350[mud]")
    parts.append("[vo2][fx][mud]amix=inputs=3:normalize=0,loudnorm=I=-12:TP=-1.5:LRA=11[aout]")
    vf = (f"[0:v]vignette=angle=PI/5,noise=alls=3:allf=t,"
          f"ass={work}/subs.ass:fontsdir={FONTS},format=yuv420p[vout]")
    out = f"{D}/Foto30Tahun_Ep{ep}.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/base.mp4", *inputs,
         "-filter_complex", vf + ";" + ";".join(parts), "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "12M", "-bufsize", "24M",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", out])
    print(f"EP{ep}: {TOTAL:.1f}s -> {out}")
    for a, b, st, tx in subs:
        if st in ("Sub", "SubLow"):
            pass
    json.dump({"total": TOTAL, "scenes": mvols}, open(f"{work}/timeline.json", "w"))


if __name__ == "__main__":
    main(sys.argv[1])
