"""Print the text to send to text-to-speech (ElevenLabs or Voicebox) for each scene.

The on-screen subtitles keep the normal spelling. Only the narration text gets fixes:
- pronunciation rules (e.g. "Allah" is sent as "Alah" so the voice uses the Indonesian pronunciation)
- *highlight* marks are removed
- numbers are written out in Indonesian words ("1883" → "seribu delapan ratus delapan puluh tiga"),
  so every voice engine reads years and amounts the same way
Usage: python engine/tts_text.py stories/<slug>.json
"""
import json
import re
import sys

# word -> spelling that makes the voice pronounce it the Indonesian way
PRONUNCIATION = {
    r"\bAllah": "Alah",  # also Allahku, Allahmu, Allahnya  # owner's choice: Indonesian pronunciation, not Arabic
}

_ONES = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]


def terbilang(n):
    """Indonesian number words: 1883 → 'seribu delapan ratus delapan puluh tiga'."""
    if n < 12:
        return _ONES[n] if n else "nol"
    if n < 20:
        return f"{_ONES[n - 10]} belas"
    if n < 100:
        return (f"{_ONES[n // 10]} puluh " + (_ONES[n % 10] if n % 10 else "")).strip()
    if n < 1000:
        head = "seratus" if n // 100 == 1 else f"{_ONES[n // 100]} ratus"
        return (head + " " + (terbilang(n % 100) if n % 100 else "")).strip()
    for size, name in ((10 ** 9, "miliar"), (10 ** 6, "juta"), (1000, "ribu")):
        if n >= size:
            q, r = divmod(n, size)
            head = "seribu" if (size == 1000 and q == 1) else f"{terbilang(q)} {name}"
            return (head + " " + (terbilang(r) if r else "")).strip()
    return str(n)


def tts_text(text):
    text = text.replace("*", "")
    for pat, rep in PRONUNCIATION.items():
        text = re.sub(pat, rep, text)
    # 36.000 / 4.800 (Indonesian thousands separator) and plain numbers like 1883
    text = re.sub(r"\b\d{1,3}(?:\.\d{3})+\b|\b\d+\b", lambda m: terbilang(int(m.group().replace(".", ""))), text)
    return text


if __name__ == "__main__":
    story = json.load(open(sys.argv[1], encoding="utf-8"))
    for i, sc in enumerate(story["scenes"], 1):
        print(f"{i:02d} | {tts_text(sc['text'])}")
