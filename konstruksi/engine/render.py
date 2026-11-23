"""Render a construction/mining reel: story JSON + one narration clip per scene -> 1080x1920 MP4.

Usage:
  python3 konstruksi/engine/render.py konstruksi/stories/<slug>.json --audio-dir work/k-<slug> --out konstruksi/videos/<file>.mp4
  python3 konstruksi/engine/render.py konstruksi/stories/<slug>.json --sheet work/k-<slug>/sheet.jpg
      (no audio needed: one still per scene with its text, tiled into a contact sheet, to check the visuals first)

The audio dir must contain 01.mp3, 02.mp3, ... one narration clip per scene. Each scene lasts as long as its narration.
The 3D backgrounds are rendered by render3d.cjs (three.js in headless Chromium).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FONTS = os.path.join(REPO, "assets", "fonts")
MUSIC = os.path.join(REPO, "konstruksi", "assets", "music.mp3")
W, H, FPS = 1080, 1920, 30
LEAD, PRE, POST, TAIL, FADE = 0.4, 0.25, 0.35, 1.6, 0.3
YELLOW = (255, 196, 0)


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


STYLES = {
    "hook": ("ExtraBold", 96, (255, 255, 255)), "hook_accent": ("ExtraBold", 96, YELLOW),
    "big": ("ExtraBold", 124, (255, 255, 255)), "accent": ("ExtraBold", 124, YELLOW),
    "small": ("Bold", 46, (255, 255, 255)), "ref": ("SemiBold", 34, (255, 255, 255)),
    "stat": ("ExtraBold", 190, YELLOW), "unit": ("ExtraBold", 64, (255, 255, 255)),
    "label": ("Bold", 40, YELLOW), "point": ("Bold", 60, (255, 255, 255)),
    "statement": ("ExtraBold", 74, (255, 255, 255)),
}


SERIES = None  # e.g. "HITUNGAN PROYEK #3" (story["series"]), drawn as a badge on every scene
HANDLE = "@ant_proyek"  # the owner's account name, drawn top-right on every scene (story["handle"] overrides)


def draw_handle(img, handle):
    """Account watermark: dark pill, yellow @, top-right (clear of the platforms' right-side buttons)."""
    d = ImageDraw.Draw(img)
    f = font("ExtraBold", 36)
    at, name = handle[:1], handle[1:]
    w_at, w_name = d.textlength(at, font=f), d.textlength(name, font=f)
    tw = w_at + w_name
    x1, y0 = W - 48, 132
    x0 = x1 - tw - 48
    d.rounded_rectangle([x0, y0, x1, y0 + 58], 29, fill=(18, 18, 20, 190))
    d.text((x0 + 24, y0 + 9), at, font=f, fill=YELLOW + (255,))
    d.text((x0 + 24 + w_at, y0 + 9), name, font=f, fill=(255, 255, 255, 240))


def text_overlay(scene, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if SERIES:
        f = font("ExtraBold", 34)
        tw = d.textlength(SERIES, font=f)
        x0, y0 = 48, 132
        d.rounded_rectangle([x0, y0, x0 + tw + 44, y0 + 58], 12, fill=(18, 18, 20, 215))
        d.rounded_rectangle([x0, y0, x0 + 12, y0 + 58], 6, fill=YELLOW + (255,))
        d.text((x0 + 28, y0 + 11), SERIES, font=f, fill=YELLOW + (255,))
    if HANDLE:
        draw_handle(img, HANDLE)
    # subtitle: dark box with a yellow hazard edge on the left
    sub = scene.get("subtitle", scene["text"])
    if sub:
        fnt = font("Bold", 46)
        lines = wrap(sub, fnt, 860, d)
        lh, pad_x, pad_y = 62, 40, 30
        tw = max(d.textlength(l, font=fnt) for l in lines)
        bh, bw = lh * len(lines) + pad_y * 2 - 8, tw + pad_x * 2
        bottom = 1780
        box = [W / 2 - bw / 2, bottom - bh, W / 2 + bw / 2, bottom]
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([box[0] + 4, box[1] + 10, box[2] + 4, box[3] + 10], 18, fill=(0, 0, 0, 120))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        d.rounded_rectangle(box, 18, fill=(18, 18, 20, 215))
        d.rounded_rectangle([box[0], box[1], box[0] + 12, box[3]], 6, fill=YELLOW + (255,))
        y = box[1] + pad_y - 4
        for l in lines:
            d.text((W / 2 + 6, y), l, font=fnt, fill=(255, 255, 255, 255), anchor="ma")
            y += lh
    head = scene.get("headline")
    if head:
        y = scene.get("headline_y", 220)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for item in head:
            style = item.get("style", "big")
            name, size, rgb = STYLES.get(style, STYLES["big"])
            f = font(name, size)
            lines = wrap(item["text"], f, 960, ld)
            for l in lines:
                if style == "label":  # yellow tag with dark text
                    tw = ld.textlength(l, font=f)
                    ld.rounded_rectangle([W / 2 - tw / 2 - 24, y - 10, W / 2 + tw / 2 + 24, y + size + 12], 10, fill=YELLOW + (255,))
                    ld.text((W / 2, y), l, font=f, fill=(20, 20, 20, 255), anchor="ma")
                    y += size + 34
                    continue
                ld.text((W / 2, y), l, font=f, fill=rgb + (255,), anchor="ma")
                y += int(size * (1.0 if style == "stat" else 1.12))
            y += 10
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.paste((0, 0, 0, 170), mask=layer.split()[3])
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        img.alpha_composite(layer)
    img.save(path)


def render3d(story_path, durs, out_dir, extra=()):
    subprocess.run(["node", os.path.join(HERE, "render3d.cjs"), story_path, "--durs", ",".join(f"{x:.3f}" for x in durs),
                    *extra, *(["--out-dir", out_dir] if out_dir else [])], check=True)


def sheet(story_path, story, out):
    with tempfile.TemporaryDirectory() as tmp:
        durs = [max(3.0, len(s["text"].split()) / 2.6) for s in story["scenes"]]
        render3d(story_path, durs, None, ["--stills", tmp, "--at", "0.6"])
        tiles = []
        for i, sc in enumerate(story["scenes"]):
            bg = Image.open(os.path.join(tmp, f"s{i + 1:02d}_a.jpg")).convert("RGBA")
            tx = os.path.join(tmp, f"tx{i:02d}.png")
            text_overlay(sc, tx)
            bg.alpha_composite(Image.open(tx))
            tiles.append(bg.convert("RGB").resize((270, 480)))
        cols = 6
        rows = (len(tiles) + cols - 1) // cols
        S = Image.new("RGB", (270 * cols, 480 * rows), (0, 0, 0))
        for i, t in enumerate(tiles):
            S.paste(t, ((i % cols) * 270, (i // cols) * 480))
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        S.save(out, quality=88)
    print(f"sheet: {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story")
    ap.add_argument("--audio-dir")
    ap.add_argument("--out")
    ap.add_argument("--sheet")
    ap.add_argument("--stamp", help="only add the account watermark to an existing finished video (--out is the result)")
    ap.add_argument("--music", default=MUSIC)
    ap.add_argument("--music-volume", type=float, default=0.14)
    args = ap.parse_args()
    story = json.load(open(args.story, encoding="utf-8"))
    scenes = story["scenes"]
    global SERIES, HANDLE
    SERIES = story.get("series")
    HANDLE = story.get("handle", HANDLE)
    if args.sheet:
        return sheet(args.story, story, args.sheet)
    if args.stamp:
        with tempfile.TemporaryDirectory() as tmp:
            png = os.path.join(tmp, "handle.png")
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_handle(img, HANDLE)
            img.save(png)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", args.stamp, "-i", png, "-filter_complex",
                            "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-map", "0:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-c:a", "copy",
                            "-movflags", "+faststart", args.out], check=True)
        return print(f"stamped: {args.out}")
    if not (args.audio_dir and args.out):
        sys.exit("need --audio-dir and --out (or --sheet)")

    audio = [os.path.join(args.audio_dir, f"{i + 1:02d}.mp3") for i in range(len(scenes))]
    for a in audio:
        if not os.path.exists(a):
            sys.exit(f"missing narration clip: {a}")
    adur = [probe_duration(a) for a in audio]
    starts, durs, t = [], [], 0.0
    for i, a in enumerate(adur):
        d = (LEAD if i == 0 else PRE) + a + POST + (TAIL if i == len(scenes) - 1 else 0)
        starts.append(t)
        durs.append(d)
        t += d
    total = t
    voice_at = [starts[i] + (LEAD if i == 0 else PRE) for i in range(len(scenes))]
    clip_len = [durs[i] + (FADE if i < len(scenes) - 1 else 0) for i in range(len(scenes))]

    with tempfile.TemporaryDirectory() as tmp:
        render3d(args.story, clip_len, tmp)
        clips = []
        for i, sc in enumerate(scenes):
            tx = os.path.join(tmp, f"tx{i:02d}.png")
            text_overlay(sc, tx)
            out = os.path.join(tmp, f"clip{i:02d}.mp4")
            fc = "[1:v]format=rgba,fade=in:st=0.05:d=0.25:alpha=1[t];[0:v][t]overlay=0:0:format=auto,format=yuv420p[v]"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, f"bg{i + 1:02d}.mp4"),
                            "-loop", "1", "-framerate", str(FPS), "-t", f"{clip_len[i]:.3f}", "-i", tx,
                            "-filter_complex", fc, "-map", "[v]", "-t", f"{clip_len[i]:.3f}", "-r", str(FPS),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out], check=True)
            clips.append(out)

        inputs, fc = [], []
        for c in clips:
            inputs += ["-i", c]
        prev = "[0:v]"
        for k in range(1, len(clips)):
            lab = f"[x{k}]"
            fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={FADE}:offset={starts[k]:.3f}{lab}")
            prev = lab
        n = len(clips)
        for i, a in enumerate(audio):
            inputs += ["-i", a]
            fc.append(f"[{n + i}:a]aresample=44100,adelay={int(voice_at[i] * 1000)}:all=1[a{i}]")
        mix = [f"[a{i}]" for i in range(len(audio))]
        if args.music and os.path.exists(args.music):
            inputs += ["-stream_loop", "-1", "-i", args.music]
            m = n + len(audio)
            fc.append(f"[{m}:a]aresample=44100,atrim=0:{total:.3f},volume={args.music_volume},"
                      f"afade=t=in:d=0.5,afade=t=out:st={max(total - 2.0, 0):.3f}:d=2.0[mus]")
            mix.append("[mus]")
        fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{total:.3f},alimiter=limit=0.95[aout]")
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                        "-map", prev, "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                        "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-t", f"{total:.3f}", args.out], check=True)
    print(f"done: {args.out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
