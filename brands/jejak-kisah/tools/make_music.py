"""Make the Jejak Kisah background track: a dark, loopable ambient pad (original, no samples).

Run: python3 brands/jejak-kisah/tools/make_music.py  → brands/jejak-kisah/ambient.m4a
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100
BLOCK = 8.0                     # seconds per chord
CHORDS = [  # A minor → F → D minor → E (Phrygian-ish tension that resolves back)
    [57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59],
    [57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 56, 59],
]
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ambient.m4a")


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pad(freq, n, rng):
    t = np.arange(n) / SR
    v = np.zeros(n)
    for det in (-0.12, 0.0, 0.13):        # detuned partials make a soft chorus
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        v += np.sin(2 * np.pi * f * t + ph) + 0.25 * np.sin(4 * np.pi * f * t + ph)
    return v / 3


def main():
    rng = np.random.default_rng(7)
    total = int(SR * BLOCK * len(CHORDS))
    t = np.arange(total) / SR
    L = total / SR
    # drone on A1 + A2, LFO with a whole number of cycles so the loop is seamless
    drone = 0.55 * np.sin(2 * np.pi * 55 * t) + 0.3 * np.sin(2 * np.pi * 110 * t + 1.0)
    drone *= 0.75 + 0.25 * np.sin(2 * np.pi * (4 / L) * t)
    music = 0.5 * drone
    nb = int(SR * BLOCK)
    xf = int(SR * 2.5)
    for k, ch in enumerate(CHORDS):
        n = nb + xf
        seg = sum(pad(hz(m), n, rng) for m in ch) / len(ch)
        env = np.ones(n)
        env[:xf] = np.linspace(0, 1, xf) ** 1.5
        env[-xf:] = np.linspace(1, 0, xf) ** 1.5
        seg *= env * 0.45
        start = k * nb - xf // 2
        idx = (np.arange(n) + start) % total   # wrap so the end flows into the start
        np.add.at(music, idx, seg)
    # a few soft high "bell" notes from the chord, for a sense of mystery
    for k, ch in enumerate(CHORDS):
        if k % 2:
            continue
        s0 = int((k * BLOCK + 3.0) * SR)
        n = int(SR * 4)
        f = hz(ch[2] + 12)
        bt = np.arange(n) / SR
        bell = (np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(2 * np.pi * 2.76 * f * bt)) * np.exp(-bt * 1.4) * 0.12
        music[s0:s0 + n] += bell
    # cheap reverb: feedback comb filters, applied circularly for a seamless loop
    wet = np.zeros_like(music)
    for d_ms, g in ((53, 0.6), (79, 0.55), (113, 0.5)):
        d = int(SR * d_ms / 1000)
        y = music.copy()
        for _ in range(12):
            y = music + g * np.roll(y, d)
        wet += y
    mix = 0.6 * music + 0.4 * wet / 3
    mix = np.convolve(mix, np.ones(6) / 6, mode="same")   # gentle low-pass
    mix /= np.max(np.abs(mix)) * 1.12
    stereo = np.stack([mix, np.roll(mix, int(SR * 0.012))], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "aac", "-b:a", "128k", OUT], check=True)
    print(f"wrote {OUT} ({L:.0f}s loop)")


if __name__ == "__main__":
    main()
