"""Print the text to send to text-to-speech for each scene.

The on-screen subtitles keep the normal spelling. Only the narration text gets
pronunciation fixes, so the voice says words the Indonesian way rather than the Arabic way.
Usage: python engine/tts_text.py stories/<slug>.json
"""
import json
import re
import sys

# word -> spelling that makes the voice pronounce it the Indonesian way
PRONUNCIATION = {
    r"\bAllah": "Alah",  # also Allahku, Allahmu, Allahnya  # owner's choice: Indonesian pronunciation, not Arabic
}


def tts_text(text):
    for pat, rep in PRONUNCIATION.items():
        text = re.sub(pat, rep, text)
    return text


if __name__ == "__main__":
    story = json.load(open(sys.argv[1], encoding="utf-8"))
    for i, sc in enumerate(story["scenes"], 1):
        print(f"{i:02d} | {tts_text(sc['text'])}")
