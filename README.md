# bible-story-reels

Video renungan kisah Alkitab harian (gaya siluet, voice over ElevenLabs) yang otomatis dijadwalkan lewat Metricool ke Facebook, Instagram, TikTok, dan YouTube Shorts.

- `engine/` — pembuat video (`render.py`, gambar siluet di `draw.py`)
- `stories/` — naskah + adegan tiap kisah (JSON)
- `videos/` — video jadi (disimpan 7 hari, Metricool menyimpan salinannya sendiri)
- `posted.json` — daftar kisah yang sudah diposting (agar tidak berulang)
- `PIPELINE.md` — langkah lengkap satu kali jalan harian
- Musik latar: `assets/music.m4a` (dari video Daud vs Goliat milik pemilik). Font: Inter (lisensi OFL, `assets/fonts/LICENSE-Inter.txt`).

## Jejak Kisah (brand kedua)

Kisah nyata, sejarah dan misteri, 2 video sehari (12.00 & 19.00 WIB). Semua ada di `brands/jejak-kisah/`: brand kit, `brand.json` (warna emas, watermark, musik orisinal `ambient.m4a`), `queue.json`, `posted.json`, naskah di `stories/`, dan langkah lengkapnya di `brands/jejak-kisah/PIPELINE.md`. Engine yang sama dipakai dengan flag `--brand brands/jejak-kisah/brand.json`.
