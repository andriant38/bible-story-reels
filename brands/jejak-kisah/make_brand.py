"""Brand images for 'Jejak Kisah': profile photo, YouTube banner, Facebook cover.

Run: python3 brands/jejak-kisah/make_brand.py  (writes PNGs next to this file)
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "..", "assets", "fonts")
GOLD = (242, 184, 92)
GOLD_LIGHT = (255, 226, 160)
BG_IN = (58, 34, 24)
BG_OUT = (10, 8, 10)


def font(name, size):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def radial_bg(w, h, cx, cy, r):
    img = Image.new("RGB", (w, h), BG_OUT)
    d = ImageDraw.Draw(img)
    steps = 120
    for i in range(steps, 0, -1):
        t = i / steps
        rr = r * t
        c = tuple(int(BG_OUT[k] + (BG_IN[k] - BG_OUT[k]) * (1 - t) ** 1.4) for k in range(3))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    return img.filter(ImageFilter.GaussianBlur(r * 0.02)).convert("RGBA")


def glow(img, cx, cy, r, color, alpha=170):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(50, 0, -1):
        rr = r * i / 50
        a = int(alpha * (1 - i / 50) ** 2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(r * 0.12)))


def flame(d, cx, base_y, h, w, color):
    pts = []
    for i in range(61):
        t = i / 60  # 0 bottom-left -> top -> bottom-right
        a = t * math.pi
        y = base_y - h * (math.sin(a / 2) ** 1.0 if t <= 0.5 else math.sin((math.pi - a) / 2))
        # teardrop: widest near bottom, pointed at top
        u = 1 - abs(t - 0.5) * 2  # 0 at sides, 1 at tip
        x = cx + (-1 if t < 0.5 else 1) * w * (1 - u) ** 0.6 * (1 - u ** 3) ** 0.5
        y = base_y - h * u
        pts.append((x, y))
    d.polygon(pts, fill=color)
    d.ellipse([cx - w, base_y - w * 0.9, cx + w, base_y + w * 0.9], fill=color)


def torch(img, cx, cy, s):
    """Torch centered around (cx, cy); s = overall height."""
    glow(img, cx, cy - s * 0.28, s * 0.55, (255, 170, 70), 200)
    d = ImageDraw.Draw(img)
    # flame layers
    fb = cy - s * 0.08
    flame(d, cx, fb, s * 0.42, s * 0.13, (214, 96, 38))
    flame(d, cx + s * 0.01, fb, s * 0.32, s * 0.095, GOLD)
    flame(d, cx + s * 0.015, fb + s * 0.01, s * 0.2, s * 0.055, GOLD_LIGHT)
    # cup
    top, bot = cy - s * 0.04, cy + s * 0.09
    d.polygon([(cx - s * 0.17, top), (cx + s * 0.17, top), (cx + s * 0.1, bot), (cx - s * 0.1, bot)], fill=GOLD)
    d.rectangle([cx - s * 0.19, top - s * 0.025, cx + s * 0.19, top + s * 0.01], fill=GOLD_LIGHT)
    for k in (0.33, 0.66):
        y = top + (bot - top) * k
        d.line([(cx - s * 0.16, y), (cx + s * 0.16, y)], fill=(150, 98, 44), width=max(2, int(s * 0.012)))
    # handle
    d.polygon([(cx - s * 0.065, bot), (cx + s * 0.065, bot), (cx + s * 0.035, cy + s * 0.5), (cx - s * 0.035, cy + s * 0.5)],
              fill=(196, 140, 70))
    d.line([(cx + s * 0.03, bot), (cx + s * 0.012, cy + s * 0.5)], fill=(120, 80, 40), width=max(2, int(s * 0.015)))


def footprints(img, x0, y0, x1, y1, n, size, alpha=70):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(n):
        t = i / max(1, n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        off = size * 0.45 * (1 if i % 2 else -1)
        a = int(alpha * (0.35 + 0.65 * t))
        d.ellipse([x - size * 0.28, y + off - size * 0.5, x + size * 0.28, y + off + size * 0.2], fill=GOLD + (a,))
        d.ellipse([x - size * 0.2, y + off + size * 0.28, x + size * 0.2, y + off + size * 0.6], fill=GOLD + (a,))
    img.alpha_composite(layer)


def dust(img, n, seed=3, avoid=None):
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(n):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(0.8, 2.4) * min(w, h) / 1080
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        d.ellipse([x - r, y - r, x + r, y + r], fill=GOLD_LIGHT + (rng.randint(30, 110),))


def text_center(d, cx, y, s, f, fill, spacing=0):
    if spacing:
        widths = [d.textlength(ch, font=f) + spacing for ch in s]
        x = cx - (sum(widths) - spacing) / 2
        for ch, wd in zip(s, widths):
            d.text((x, y), ch, font=f, fill=fill)
            x += wd
    else:
        d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def profile():
    S = 1080
    img = radial_bg(S, S, S / 2, S * 0.45, S * 0.75)
    dust(img, 60)
    torch(img, S / 2, S * 0.5, S * 0.62)
    # thin gold ring inside the circular crop area
    d = ImageDraw.Draw(img)
    m = S * 0.06
    d.ellipse([m, m, S - m, S - m], outline=GOLD + (150,), width=6)
    img.convert("RGB").save(os.path.join(HERE, "profile.png"))


def wide(w, h, name, safe_w, safe_h, tag):
    img = radial_bg(w, h, w / 2, h / 2, w * 0.45)
    cx, cy = w / 2, h / 2
    dust(img, 110, seed=7, avoid=(cx - safe_w * 0.2, cy - safe_h * 0.4, cx + safe_w * 0.5, cy + safe_h * 0.4))
    footprints(img, cx - safe_w * 0.9, cy + safe_h * 0.62, cx - safe_w * 0.4, cy + safe_h * 0.45, 6, safe_h * 0.06, alpha=120)
    torch(img, cx - safe_w * 0.3, cy - safe_h * 0.04, safe_h * 0.95)
    d = ImageDraw.Draw(img)
    tx = cx + safe_w * 0.12
    text_center(d, tx, cy - safe_h * 0.26, "JEJAK KISAH", font("Inter-ExtraBold.otf", int(safe_h * 0.2)), GOLD_LIGHT, spacing=int(safe_h * 0.012))
    text_center(d, tx, cy + safe_h * 0.02, "Kisah nyata yang jarang diceritakan", font("Inter-Medium.otf", int(safe_h * 0.085)), (235, 220, 200))
    text_center(d, tx, cy + safe_h * 0.2, tag, font("Inter-SemiBold.otf", int(safe_h * 0.07)), GOLD)
    img.convert("RGB").save(os.path.join(HERE, name))


if __name__ == "__main__":
    profile()
    # YouTube banner 2560x1440; text-and-logo safe area 1546x423
    wide(2560, 1440, "youtube-banner.png", 1546, 423, "Video baru setiap hari · 12.00 & 19.00 WIB")
    # Facebook cover 1640x624 (mobile crops sides) -> keep content central
    wide(1640, 624, "facebook-cover.png", 1150, 430, "Video baru setiap hari · 12.00 & 19.00 WIB")
    print("ok")
