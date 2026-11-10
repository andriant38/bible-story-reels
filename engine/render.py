"""Render a Bible-story reel: story JSON + one narration clip per scene → 1080x1920 MP4.

Usage:
  python engine/render.py stories/<slug>.json --audio-dir work/<slug> --out videos/<file>.mp4

The audio dir must contain 01.mp3, 02.mp3, ... — one narration clip per scene, in order.
Each scene lasts exactly as long as its narration (plus small gaps), so voice and subtitles stay in sync.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from draw import H, W, render_background  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
MUSIC = os.path.join(ROOT, "assets", "music.m4a")
FPS = 30
LEAD = 0.5        # silence before first line
PRE = 0.35        # scene shows this long before its narration starts
POST = 0.45       # and stays this long after it ends
TAIL = 1.8        # extra hold on the final scene
FADE = 0.4        # cross-fade between scenes
CAMERAS = ["push", "pan_right", "pull", "pan_left"]


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Inter-{name}.otf"), size)


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def wrap(text, fnt, max_w, draw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def text_overlay(scene, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # ---- subtitle box
    sub = scene.get("subtitle", scene["text"])
    fnt = font("Bold", 46)
    lines = wrap(sub, fnt, 880, d)
    lh = 62
    pad_x, pad_y = 38, 30
    tw = max(d.textlength(l, font=fnt) for l in lines)
    bh = lh * len(lines) + pad_y * 2 - 8
    bw = tw + pad_x * 2
    bottom = 1795
    box = [W / 2 - bw / 2, bottom - bh, W / 2 + bw / 2, bottom]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([box[0] + 4, box[1] + 10, box[2] + 4, box[3] + 10], 30, fill=(0, 0, 0, 110))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle(box, 30, fill=(22, 13, 18, 205))
    y = box[1] + pad_y - 4
    for l in lines:
        d.text((W / 2, y), l, font=fnt, fill=(255, 255, 255, 255), anchor="ma")
        y += lh
    # ---- headline block (title card / closing card)
    head = scene.get("headline")
    if head:
        styles = {"big": ("ExtraBold", 132, (255, 255, 255)), "accent": ("ExtraBold", 132, (245, 163, 107)),
                  "small": ("Medium", 46, (255, 255, 255)), "ref": ("SemiBold", 34, (255, 255, 255)),
                  "statement": ("ExtraBold", 76, (255, 255, 255))}
        y = scene.get("headline_y", 230)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for item in head:
            name, size, rgb = styles.get(item.get("style", "big"), styles["big"])
            f = font(name, size)
            for l in wrap(item["text"], f, 940, ld):
                ld.text((W / 2, y), l, font=f, fill=rgb + (255,), anchor="ma")
                y += int(size * 1.12)
            y += 10
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 150), mask=layer.split()[3])
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
        img.alpha_composite(layer)
    img.save(path)


def render_scene_clip(i, scene, dur, tmp, seed):
    bg = os.path.join(tmp, f"bg{i:02d}.png")
    tx = os.path.join(tmp, f"tx{i:02d}.png")
    out = os.path.join(tmp, f"clip{i:02d}.mp4")
    render_background(scene, seed=seed + i).convert("RGB").save(bg)
    text_overlay(scene, tx)
    cam = scene.get("camera", CAMERAS[i % len(CAMERAS)])
    D = max(dur, 0.1)
    if cam == "push":
        v = f"scale=w='trunc(1080*(1.02+0.08*t/{D})/2)*2':h=-2:eval=frame,crop=1080:1920"
    elif cam == "pull":
        v = f"scale=w='trunc(1080*(1.10-0.08*t/{D})/2)*2':h=-2:eval=frame,crop=1080:1920"
    elif cam == "pan_left":
        v = f"scale=1188:-2,crop=1080:1920:x='(iw-1080)*(1-t/{D})':y='(ih-1920)/2'"
    elif cam == "pan_right":
        v = f"scale=1188:-2,crop=1080:1920:x='(iw-1080)*t/{D}':y='(ih-1920)/2'"
    else:
        v = "scale=1134:-2,crop=1080:1920"
    fc = (f"[0:v]{v},setsar=1,format=rgba[b];"
          f"[1:v]format=rgba,fade=in:st=0.1:d=0.35:alpha=1[t];"
          f"[b][t]overlay=0:0:format=auto,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", bg,
                    "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", tx,
                    "-filter_complex", fc, "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "19", "-pix_fmt", "yuv420p", out], check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story")
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--music-volume", type=float, default=0.16)
    args = ap.parse_args()

    story = json.load(open(args.story, encoding="utf-8"))
    scenes = story["scenes"]
    audio = [os.path.join(args.audio_dir, f"{i + 1:02d}.mp3") for i in range(len(scenes))]
    for a in audio:
        if not os.path.exists(a):
            sys.exit(f"missing narration clip: {a}")
    adur = [probe_duration(a) for a in audio]

    # timeline
    starts, durs, t = [], [], 0.0
    for i, a in enumerate(adur):
        pre = LEAD if i == 0 else PRE
        d = pre + a + POST + (TAIL if i == len(scenes) - 1 else 0)
        starts.append(t)
        durs.append(d)
        t += d
    total = t
    voice_at = [starts[i] + (LEAD if i == 0 else PRE) for i in range(len(scenes))]

    seed = abs(hash(story.get("slug", "x"))) % 10000
    with tempfile.TemporaryDirectory() as tmp:
        clips = []
        for i, sc in enumerate(scenes):
            L = durs[i] + (FADE if i < len(scenes) - 1 else 0)
            clips.append(render_scene_clip(i, sc, L, tmp, seed))
            print(f"scene {i + 1}/{len(scenes)} rendered ({durs[i]:.1f}s)", flush=True)

        inputs, fc = [], []
        for c in clips:
            inputs += ["-i", c]
        prev = "[0:v]"
        for k in range(1, len(clips)):
            lab = f"[x{k}]"
            fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={FADE}:offset={starts[k]:.3f}{lab}")
            prev = lab
        vlabel = prev
        n = len(clips)
        for i, a in enumerate(audio):
            inputs += ["-i", a]
            ms = int(voice_at[i] * 1000)
            fc.append(f"[{n + i}:a]aresample=44100,adelay={ms}:all=1[a{i}]")
        inputs += ["-stream_loop", "-1", "-i", MUSIC]
        m = n + len(audio)
        fc.append(f"[{m}:a]aresample=44100,atrim=0:{total:.3f},volume={args.music_volume},"
                  f"afade=t=in:d=1,afade=t=out:st={max(total - 2.5, 0):.3f}:d=2.5[mus]")
        fc.append("".join(f"[a{i}]" for i in range(len(audio))) + f"[mus]amix=inputs={len(audio) + 1}:normalize=0:duration=longest,"
                  f"atrim=0:{total:.3f},alimiter=limit=0.95[aout]")
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                        "-map", vlabel, "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                        "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", "-t", f"{total:.3f}", args.out], check=True)
    print(f"done: {args.out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
