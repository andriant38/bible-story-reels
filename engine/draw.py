"""Silhouette scene drawing for Bible-story reels (1080x1920 portrait)."""
import math
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
GROUND_Y = 1330  # where figures stand

PALETTES = {
    # sky top, sky mid, horizon, sun, far→near terrain, figure
    "dusk":   dict(sky=["#2a1b3d", "#7a3b4a", "#f0a35e"], sun="#ffd08a", terrain=["#6b3a48", "#4a2836", "#2e1a26", "#1d1119"], fig="#120a10"),
    "night":  dict(sky=["#070b1c", "#18224a", "#35507e"], sun="#e8eefc", terrain=["#202c52", "#172040", "#10172e", "#0a0f1f"], fig="#05070f"),
    "dawn":   dict(sky=["#3b4f7a", "#d98f7a", "#ffe0a8"], sun="#fff3d6", terrain=["#9a6a6a", "#704a52", "#4a3038", "#2c1c22"], fig="#1a1014"),
    "desert": dict(sky=["#e8925a", "#f6c88a", "#fff0cc"], sun="#fffbe8", terrain=["#d49a62", "#b97a48", "#8a5432", "#5a3420"], fig="#2a160c"),
    "sea":    dict(sky=["#0f2c44", "#2f6b84", "#a7d6dc"], sun="#f4fbff", terrain=["#2a5a70", "#1c465c", "#123447", "#0a2433"], fig="#04121b"),
    "storm":  dict(sky=["#14161c", "#30364a", "#5e6880"], sun="#c9d2e6", terrain=["#3a4152", "#2a3040", "#1c212d", "#11141c"], fig="#07080b"),
    "golden": dict(sky=["#8a4a3a", "#e9a865", "#fff1c9"], sun="#fffdf2", terrain=["#b07a5a", "#8a5a44", "#5e3a2e", "#3a2420"], fig="#1e120e"),
}


def hexrgb(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient(w, h, stops):
    cols = [hexrgb(c) for c in stops]
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    n = len(cols) - 1
    for y in range(h):
        t = y / (h - 1) * n
        i = min(int(t), n - 1)
        d.line([(0, y), (w, y)], fill=lerp(cols[i], cols[i + 1], t - i))
    return img


def glow(img, cx, cy, r, color, strength=1.0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = hexrgb(color)
    steps = 40
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(255 * strength * (1 - i / steps) ** 2 * 0.35)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c[:3] + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.08))
    img.alpha_composite(layer)


def ridge(rng, w, base, amp, freq, rough=0.35):
    phases = [rng.uniform(0, 6.28) for _ in range(4)]
    pts = []
    for x in range(0, w + 8, 8):
        u = x / w
        y = base
        y -= amp * math.sin(u * freq * 6.28 + phases[0])
        y -= amp * 0.5 * math.sin(u * freq * 2.3 * 6.28 + phases[1])
        y -= amp * rough * math.sin(u * freq * 5.1 * 6.28 + phases[2])
        pts.append((x, y))
    return pts


def fill_below(d, pts, h, color):
    d.polygon(pts + [(pts[-1][0], h), (pts[0][0], h)], fill=color)


# ---------------------------------------------------------------- terrain
def draw_terrain(img, kind, pal, rng):
    w, h = img.size
    d = ImageDraw.Draw(img)
    t = [hexrgb(c) for c in pal["terrain"]]
    gy = GROUND_Y
    if kind == "sea":
        d.rectangle([0, gy - 140, w, h], fill=t[1])
        for i in range(26):
            y = gy - 130 + i * i * 1.6
            if y > h:
                break
            for x0 in range(-60, w, 140):
                xo = x0 + (i * 47) % 140
                d.line([(xo, y), (xo + 50 + i * 2, y)], fill=lerp(t[0], hexrgb(pal["sky"][2]), 0.35)[:3] + (120,), width=2 + i // 6)
        fill_below(d, ridge(rng, w, gy + 120, 15, 0.8), h, t[3])
        return
    if kind == "desert":
        fill_below(d, ridge(rng, w, gy - 160, 40, 0.6, 0.1), h, t[0])
        fill_below(d, ridge(rng, w, gy - 70, 50, 0.8, 0.1), h, t[1])
        fill_below(d, ridge(rng, w, gy + 10, 30, 0.5, 0.05), h, t[3])
        return
    if kind == "plain":
        fill_below(d, ridge(rng, w, gy - 120, 25, 0.7), h, t[1])
        fill_below(d, ridge(rng, w, gy + 5, 18, 0.5, 0.1), h, t[3])
        return
    if kind == "hill":  # single hill in the centre (e.g. Golgotha, Mount Sinai)
        fill_below(d, ridge(rng, w, gy - 260, 70, 1.4), h, t[0])
        cx = w / 2
        pts = [(x, gy + 10 - 260 * math.exp(-((x - cx) / 260) ** 2)) for x in range(0, w + 8, 8)]
        fill_below(d, pts, h, t[3])
        return
    # default: mountains / valley
    fill_below(d, ridge(rng, w, gy - 330, 90, 1.6), h, t[0])
    fill_below(d, ridge(rng, w, gy - 210, 70, 1.2), h, t[1])
    fill_below(d, ridge(rng, w, gy - 90, 45, 0.9), h, t[2])
    fill_below(d, ridge(rng, w, gy + 10, 20, 0.6, 0.1), h, t[3])


def draw_stars(img, rng, n=160):
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rng.uniform(0, img.width), rng.uniform(0, GROUND_Y - 400)
        r = rng.choice([1, 1, 1.5, 2])
        a = rng.randint(90, 230)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))


def draw_rays(img, cx, cy, color, n=22):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = hexrgb(color)
    R = 2600
    for i in range(n):
        a0 = i / n * 2 * math.pi
        a1 = a0 + math.pi / n * 0.55
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=c[:3] + (55,))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(layer)


def draw_clouds(img, rng, color, n=5, dark=False):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = hexrgb(color, 150 if dark else 90)
    for _ in range(n):
        cx, cy = rng.uniform(0, img.width), rng.uniform(150, 700)
        for _ in range(7):
            rx, ry = rng.uniform(80, 180), rng.uniform(35, 70)
            ox, oy = rng.uniform(-150, 150), rng.uniform(-25, 25)
            d.ellipse([cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry], fill=c)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(10)))


# ---------------------------------------------------------------- figures
def person(d, x, gy, s, col, pose="stand", props=(), facing=1, giant=False):
    """Stylised silhouette person. s = scale (1.0 → ~300px tall)."""
    hh = 300 * s
    head_r = hh * 0.075
    body_top = gy - hh * 0.80
    shoulder_w = hh * (0.15 if giant else 0.11)
    hip_w = hh * 0.09
    if pose == "kneel":
        gy_k = gy - hh * 0.0
        body_top = gy - hh * 0.55
    hy = body_top - head_r * 1.15
    d.ellipse([x - head_r, hy - head_r, x + head_r, hy + head_r], fill=col)
    # robe / torso
    bot = gy - (hh * 0.05 if pose != "kneel" else 0)
    hem = hh * (0.14 if not giant else 0.12)
    d.polygon([(x - shoulder_w, body_top), (x + shoulder_w, body_top), (x + hem, bot - hh * 0.25 if giant else bot), (x - hem, bot - hh * 0.25 if giant else bot)], fill=col)
    if giant:  # legs + armour skirt
        lw = hh * 0.035
        for sx in (-1, 1):
            d.rectangle([x + sx * hh * 0.07 - lw, bot - hh * 0.27, x + sx * hh * 0.07 + lw, gy], fill=col)
        d.polygon([(x - shoulder_w * 1.15, body_top - 4), (x + shoulder_w * 1.15, body_top - 4), (x + shoulder_w * 0.9, body_top + hh * 0.12), (x - shoulder_w * 0.9, body_top + hh * 0.12)], fill=col)
        # helmet crest
        d.polygon([(x - head_r * 1.1, hy - head_r * 0.2), (x + head_r * 1.1, hy - head_r * 0.2), (x, hy - head_r * 1.9)], fill=col)
    elif pose != "kneel":
        lw = hh * 0.025
        d.rectangle([x - hh * 0.05 - lw, bot - 6, x - hh * 0.05 + lw, gy], fill=col)
        d.rectangle([x + hh * 0.05 - lw, bot - 6, x + hh * 0.05 + lw, gy], fill=col)
    # arms
    aw = max(4, int(hh * 0.035))
    sh_y = body_top + hh * 0.03
    lx, rx = x - shoulder_w * 0.9, x + shoulder_w * 0.9
    if pose in ("arms_up", "praise"):
        ends = [(lx - hh * 0.10, sh_y - hh * 0.30), (rx + hh * 0.10, sh_y - hh * 0.30)]
    elif pose == "pray":
        ends = [(x - hh * 0.01, sh_y + hh * 0.12), (x + hh * 0.01, sh_y + hh * 0.12)]
    elif pose == "point":
        ends = [(lx - hh * 0.02, sh_y + hh * 0.28), (x + facing * hh * 0.42, sh_y - hh * 0.05)] if facing > 0 else [(x + facing * hh * 0.42, sh_y - hh * 0.05), (rx + hh * 0.02, sh_y + hh * 0.28)]
    elif pose == "sling":
        ends = [(lx - hh * 0.05, sh_y + hh * 0.25), (rx + hh * 0.05, sh_y - hh * 0.33)]
    else:
        ends = [(lx - hh * 0.04, sh_y + hh * 0.30), (rx + hh * 0.04, sh_y + hh * 0.30)]
    d.line([(lx, sh_y), ends[0]], fill=col, width=aw)
    d.line([(rx, sh_y), ends[1]], fill=col, width=aw)
    hand_r, hand_l = ends[1], ends[0]
    hand = hand_r if facing > 0 else hand_l
    for p in props:
        if p == "staff":
            d.line([(hand[0], hand[1] - hh * 0.35), (hand[0], gy)], fill=col, width=max(3, aw - 2))
            d.arc([hand[0] - hh * 0.06, hand[1] - hh * 0.42, hand[0] + hh * 0.06, hand[1] - hh * 0.30], 180, 360, fill=col, width=max(3, aw - 2))
        elif p == "spear":
            d.line([(hand[0], hand[1] - hh * 0.65), (hand[0], gy)], fill=col, width=max(3, aw - 1))
            tip = hand[1] - hh * 0.65
            d.polygon([(hand[0] - hh * 0.03, tip), (hand[0] + hh * 0.03, tip), (hand[0], tip - hh * 0.12)], fill=col)
        elif p == "sword":
            d.line([hand, (hand[0] + facing * hh * 0.05, hand[1] - hh * 0.38)], fill=col, width=max(3, aw - 1))
        elif p == "shield":
            o = hand_l if facing > 0 else hand_r
            d.ellipse([o[0] - hh * 0.12, o[1] - hh * 0.2, o[0] + hh * 0.12, o[1] + hh * 0.12], fill=col)
        elif p == "crown":
            cy = hy - head_r * 0.9
            d.polygon([(x - head_r, cy), (x - head_r * 0.6, cy - head_r * 0.8), (x - head_r * 0.2, cy - head_r * 0.2), (x, cy - head_r), (x + head_r * 0.2, cy - head_r * 0.2), (x + head_r * 0.6, cy - head_r * 0.8), (x + head_r, cy)], fill=col)
        elif p == "sling":
            d.arc([hand_r[0] - hh * 0.2, hand_r[1] - hh * 0.2, hand_r[0] + hh * 0.2, hand_r[1] + hh * 0.2], 200, 330, fill=(255, 255, 255, 140), width=3)
        elif p == "tablets":
            for k in (-1, 1):
                bx = x + k * hh * 0.07
                d.rounded_rectangle([bx - hh * 0.06, sh_y - hh * 0.40, bx + hh * 0.06, sh_y - hh * 0.22], radius=int(hh * 0.05), fill=col)
        elif p == "basket":
            d.ellipse([hand[0] - hh * 0.07, hand[1] - hh * 0.04, hand[0] + hh * 0.07, hand[1] + hh * 0.08], fill=col)
        elif p == "child":
            person(d, x + facing * hh * 0.22, gy, s * 0.45, col)
        elif p == "beard":
            d.polygon([(x - head_r * 0.7, hy + head_r * 0.3), (x + head_r * 0.7, hy + head_r * 0.3), (x, hy + head_r * 1.6)], fill=col)


def sheep(d, x, gy, s, col):
    w, h = 70 * s, 42 * s
    d.ellipse([x - w / 2, gy - h - 16 * s, x + w / 2, gy - 16 * s], fill=col)
    d.ellipse([x + w * 0.35, gy - h - 6 * s, x + w * 0.62, gy - h * 0.45], fill=col)
    for k in (-0.3, 0.25):
        d.rectangle([x + w * k - 3 * s, gy - 20 * s, x + w * k + 3 * s, gy], fill=col)


def tent(d, x, gy, s, col):
    d.polygon([(x - 120 * s, gy), (x, gy - 140 * s), (x + 120 * s, gy)], fill=col)
    d.line([(x, gy - 140 * s), (x, gy - 175 * s)], fill=col, width=max(2, int(4 * s)))


def palm(d, x, gy, s, col):
    for i in range(14):
        t = i / 14
        cx = x + 30 * s * math.sin(t * 2)
        d.ellipse([cx - 9 * s, gy - t * 360 * s - 9 * s, cx + 9 * s, gy - t * 360 * s + 9 * s], fill=col)
    top = (x + 30 * s * math.sin(2), gy - 360 * s)
    for a in (-160, -130, -100, -70, -40, -15):
        r = math.radians(a)
        end = (top[0] + 150 * s * math.cos(r), top[1] + 150 * s * math.sin(r) + 60 * s)
        mid = (top[0] + 80 * s * math.cos(r), top[1] + 80 * s * math.sin(r) - 10 * s)
        d.line([top, mid, end], fill=col, width=int(14 * s), joint="curve")


def tree(d, x, gy, s, col):
    d.polygon([(x - 14 * s, gy), (x + 14 * s, gy), (x + 8 * s, gy - 180 * s), (x - 8 * s, gy - 180 * s)], fill=col)
    for ox, oy, r in [(0, -250, 95), (-80, -200, 70), (80, -200, 70), (-40, -310, 70), (45, -300, 65)]:
        d.ellipse([x + ox * s - r * s, gy + oy * s - r * s, x + ox * s + r * s, gy + oy * s + r * s], fill=col)


def boat(d, x, gy, s, col):
    d.polygon([(x - 180 * s, gy - 70 * s), (x + 180 * s, gy - 70 * s), (x + 130 * s, gy), (x - 130 * s, gy)], fill=col)
    d.line([(x, gy - 70 * s), (x, gy - 330 * s)], fill=col, width=int(8 * s))
    d.polygon([(x + 6 * s, gy - 320 * s), (x + 150 * s, gy - 110 * s), (x + 6 * s, gy - 110 * s)], fill=col)


def ark(d, x, gy, s, col):
    d.polygon([(x - 330 * s, gy - 150 * s), (x + 330 * s, gy - 150 * s), (x + 270 * s, gy), (x - 270 * s, gy)], fill=col)
    d.rectangle([x - 200 * s, gy - 250 * s, x + 200 * s, gy - 150 * s], fill=col)
    d.polygon([(x - 230 * s, gy - 250 * s), (x + 230 * s, gy - 250 * s), (x, gy - 330 * s)], fill=col)


def cross(d, x, gy, s, col):
    d.rectangle([x - 14 * s, gy - 520 * s, x + 14 * s, gy], fill=col)
    d.rectangle([x - 130 * s, gy - 430 * s, x + 130 * s, gy - 402 * s], fill=col)


def tomb(d, x, gy, s, col, open_=True):
    d.pieslice([x - 220 * s, gy - 300 * s, x + 220 * s, gy + 140 * s], 180, 360, fill=col)
    d.rectangle([x - 220 * s, gy - 80 * s, x + 220 * s, gy], fill=col)
    d.ellipse([x - 80 * s, gy - 170 * s, x + 80 * s, gy + 20 * s], fill=(0, 0, 0, 255) if not open_ else (255, 236, 190, 255))
    if open_:
        d.ellipse([x + 110 * s, gy - 170 * s, x + 270 * s, gy], fill=col)


def city(d, x, gy, s, col):
    rng = random.Random(int(x))
    d.rectangle([x - 360 * s, gy - 160 * s, x + 360 * s, gy], fill=col)
    for i in range(-3, 4):
        tx = x + i * 110 * s
        th = rng.uniform(220, 330) * s
        d.rectangle([tx - 38 * s, gy - th, tx + 38 * s, gy], fill=col)
        for k in range(3):
            bx = tx - 38 * s + k * 30 * s
            d.rectangle([bx, gy - th - 18 * s, bx + 16 * s, gy - th], fill=col)
    d.pieslice([x - 60 * s, gy - 130 * s, x + 60 * s, gy + 20 * s], 180, 360, fill=(0, 0, 0, 255))


def tower(d, x, gy, s, col):
    for i in range(6):
        w = (260 - i * 36) * s
        d.rectangle([x - w / 2, gy - (i + 1) * 110 * s, x + w / 2, gy - i * 110 * s + 2], fill=col)


def fire(d, x, gy, s, col=None):
    layer_cols = [(255, 140, 40, 255), (255, 200, 80, 255), (255, 245, 200, 255)]
    for k, c in enumerate(layer_cols):
        f = 1 - k * 0.3
        d.polygon([(x - 60 * s * f, gy), (x - 35 * s * f, gy - 120 * s * f), (x - 10 * s * f, gy - 80 * s * f), (x, gy - 190 * s * f), (x + 20 * s * f, gy - 90 * s * f), (x + 40 * s * f, gy - 130 * s * f), (x + 60 * s * f, gy)], fill=c)


def bush(d, x, gy, s, col):
    for ox, r in [(-50, 50), (0, 70), (50, 50)]:
        d.ellipse([x + ox * s - r * s, gy - r * 2 * s, x + ox * s + r * s, gy], fill=col)


def lion(d, x, gy, s, col, facing=1):
    d.ellipse([x - 110 * s, gy - 110 * s, x + 90 * s, gy - 40 * s], fill=col)
    hx = x + facing * 110 * s
    d.ellipse([hx - 55 * s, gy - 170 * s, hx + 55 * s, gy - 60 * s], fill=col)
    for k in (-80, -30, 40, 70):
        d.rectangle([x + k * s - 9 * s, gy - 60 * s, x + k * s + 9 * s, gy], fill=col)
    d.line([(x - facing * 100 * s, gy - 90 * s), (x - facing * 170 * s, gy - 140 * s)], fill=col, width=int(8 * s))


def fish(d, x, y, s, col):
    d.ellipse([x - 60 * s, y - 25 * s, x + 40 * s, y + 25 * s], fill=col)
    d.polygon([(x + 30 * s, y), (x + 80 * s, y - 30 * s), (x + 80 * s, y + 30 * s)], fill=col)


def dove(d, x, y, s, col):
    col = col or (255, 255, 255, 255)
    d.ellipse([x - 40 * s, y - 14 * s, x + 30 * s, y + 14 * s], fill=col)
    d.polygon([(x - 10 * s, y), (x - 70 * s, y - 70 * s), (x + 20 * s, y - 10 * s)], fill=col)
    d.polygon([(x - 10 * s, y), (x + 50 * s, y - 75 * s), (x + 20 * s, y - 5 * s)], fill=col)
    d.ellipse([x + 20 * s, y - 20 * s, x + 46 * s, y + 4 * s], fill=col)


def well(d, x, gy, s, col):
    d.rectangle([x - 90 * s, gy - 90 * s, x + 90 * s, gy], fill=col)
    for k in (-1, 1):
        d.rectangle([x + k * 80 * s - 7 * s, gy - 230 * s, x + k * 80 * s + 7 * s, gy - 90 * s], fill=col)
    d.polygon([(x - 120 * s, gy - 230 * s), (x + 120 * s, gy - 230 * s), (x, gy - 300 * s)], fill=col)


def star(d, x, y, s, col=None):
    c = (255, 250, 225, 255)
    pts = []
    for i in range(8):
        r = (70 if i % 2 == 0 else 14) * s
        a = i * math.pi / 4 - math.pi / 2
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    d.polygon(pts, fill=c)


def manger(d, x, gy, s, col):
    d.polygon([(x - 110 * s, gy - 110 * s), (x + 110 * s, gy - 110 * s), (x + 70 * s, gy - 40 * s), (x - 70 * s, gy - 40 * s)], fill=col)
    for k in (-1, 1):
        d.line([(x + k * 80 * s, gy - 60 * s), (x + k * 110 * s, gy)], fill=col, width=int(10 * s))
    d.ellipse([x - 40 * s, gy - 140 * s, x + 40 * s, gy - 100 * s], fill=(255, 236, 190, 255))


def stone(d, x, y, s, col):
    d.ellipse([x - 24 * s, y - 18 * s, x + 24 * s, y + 18 * s], fill=(235, 228, 215, 255))


ELEMENTS = dict(sheep=sheep, tent=tent, palm=palm, tree=tree, boat=boat, ark=ark, cross=cross, tomb=tomb,
                city=city, tower=tower, fire=fire, bush=bush, well=well, manger=manger)
AIR = dict(fish=fish, dove=dove, star=star, stone=stone)


def render_background(scene, seed=0, scale=1.12):
    """Return an RGBA image (W*scale x H*scale) of the scene without text."""
    pal = PALETTES.get(scene.get("bg", "dusk"), PALETTES["dusk"])
    w, h = int(W * scale), int(H * scale)
    rng = random.Random(seed)
    img = gradient(w, h, pal["sky"] + [pal["terrain"][3]])
    ox, oy = (w - W) / 2, (h - H) / 2  # offset so element coords stay in 1080x1920 space
    sun = scene.get("sun", scene.get("bg") not in ("storm",))
    if scene.get("stars") or scene.get("bg") == "night":
        draw_stars(img, rng)
    if scene.get("rays"):
        draw_rays(img, w / 2, oy + GROUND_Y - 330, pal["sun"])
    if sun:
        sx = ox + W * scene.get("sun_x", 0.5)
        sy = oy + GROUND_Y - 330
        glow(img, sx, sy, 900 if scene.get("rays") else 650, pal["sun"], 1.3 if scene.get("rays") else 1.0)
        if scene.get("bg") == "night":
            d = ImageDraw.Draw(img)
            d.ellipse([sx - 50, oy + 380 - 50, sx + 50, oy + 380 + 50], fill=hexrgb(pal["sun"]))
    if scene.get("rainbow"):
        rb = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        rd = ImageDraw.Draw(rb)
        cx, cy, R = w / 2, oy + GROUND_Y, 760
        for k, c in enumerate(["#e8574a", "#f39a3d", "#f6d55c", "#6cc16a", "#4aa3df", "#6a5fc9", "#9b59b6"]):
            r = R - k * 26
            rd.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=hexrgb(c, 150), width=26)
        img.alpha_composite(rb.filter(ImageFilter.GaussianBlur(4)))
    if scene.get("clouds") or scene.get("bg") == "storm":
        draw_clouds(img, rng, "#0d0f14" if scene.get("bg") == "storm" else "#ffffff", 6, dark=scene.get("bg") == "storm")

    terrain = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_terrain(terrain, scene.get("terrain", "mountains"), pal, rng)
    img.alpha_composite(terrain)

    fig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    col = hexrgb(pal["fig"])
    for el in scene.get("elements", []):
        t = el.get("type", "person")
        x = ox + W * el.get("x", 0.5)
        gy = oy + GROUND_Y + el.get("dy", 0)
        s = el.get("size", 1.0)
        if t in ("person", "giant"):
            person(d, x, gy, s * (2.3 if t == "giant" else 1), col, el.get("pose", "stand"), el.get("props", []),
                   el.get("facing", 1), giant=(t == "giant"))
        elif t == "fallen_giant":
            sub = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            person(ImageDraw.Draw(sub), w / 2, h / 2 + 300 * s, s * 2.0, col, giant=True)
            sub = sub.rotate(-88 * el.get("facing", 1), center=(w / 2, h / 2), expand=False)
            bb = sub.getbbox()
            if bb:
                piece = sub.crop(bb)
                # lie on the ground, slightly raised so it reads against the far terrain
                fig.alpha_composite(piece, (int(x - piece.width / 2), int(gy - piece.height - 12)))
        elif t == "lion":
            lion(d, x, gy, s, col, el.get("facing", 1))
        elif t in ELEMENTS:
            ELEMENTS[t](d, x, gy, s, col)
        elif t in AIR:
            AIR[t](d, x, oy + H * el.get("y", 0.4), s, col)
    img.alpha_composite(fig)
    return img
