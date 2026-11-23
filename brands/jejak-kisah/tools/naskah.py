"""Write the Voicebox recording sheet for a story: brands/jejak-kisah/narration/<slug>/NASKAH-VOICEBOX.txt

  python3 brands/jejak-kisah/tools/naskah.py <slug>

Each line is the TTS text of one scene (numbers written out, *marks* removed), to record as 01.mp3, 02.mp3, …
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "..", "..", "engine"))
from tts_text import tts_text  # noqa: E402

slug = sys.argv[1]
story = json.load(open(os.path.join(HERE, "stories", f"{slug}.json"), encoding="utf-8"))
out_dir = os.path.join(HERE, "narration", slug)
os.makedirs(out_dir, exist_ok=True)
lines = [f"Narasi {story['title']} untuk Voicebox",
         "Satu adegan = satu file. Simpan dengan nama 01.mp3, 02.mp3, dst. (.wav juga boleh).",
         "Gaya: narator dokumenter pria, tenang, jelas, sedikit misterius. Adegan 1 dibaca lebih tegas dan cepat (hook).",
         ""]
for i, sc in enumerate(story["scenes"], 1):
    t = tts_text(sc["text"])
    lines.append(f"{i:02d}.mp3  →  {t[:1].upper() + t[1:]}")
open(os.path.join(out_dir, "NASKAH-VOICEBOX.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
words = sum(len(sc["text"].split()) for sc in story["scenes"])
print(f"{slug}: {len(story['scenes'])} scenes, {words} words -> narration/{slug}/NASKAH-VOICEBOX.txt")
