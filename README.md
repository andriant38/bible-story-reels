# bible-story-reels

Video renungan kisah Alkitab harian (gaya siluet, voice over ElevenLabs) yang otomatis dijadwalkan lewat Metricool ke Facebook, Instagram, TikTok, dan YouTube Shorts.

- `engine/` — pembuat video (`render.py`, gambar siluet di `draw.py`)
- `stories/` — naskah + adegan tiap kisah (JSON)
- `videos/` — video jadi (disimpan 7 hari, Metricool menyimpan salinannya sendiri)
- `posted.json` — daftar kisah yang sudah diposting (agar tidak berulang)
- `PIPELINE.md` — langkah lengkap satu kali jalan harian
- Musik latar: `assets/music.m4a` (dari video Daud vs Goliat milik pemilik). Font: Inter (lisensi OFL, `assets/fonts/LICENSE-Inter.txt`).
