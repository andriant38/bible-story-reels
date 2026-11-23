# Konstruksi & Tambang 3D Reels

3D animated reels (in Indonesian) about construction and mining. Each video is made from a script in JSON, rendered as 3D animation in code (three.js), voiced with ElevenLabs, and scheduled through Metricool.

- `engine/kit.js` — 3D object kit (excavator, mine truck, tower crane, building, bridge, TBM, open pit, blasting, and more) and the camera
- `engine/render3d.cjs` — renders each scene's 3D background frame by frame (headless Chromium)
- `engine/render.py` — adds text and subtitles, voice over and music → 1080×1920 MP4; `--sheet` for a quick preview
- `stories/` — one script per video; `videos/` — finished videos (kept 7 days)
- `posted.json` — topics already posted
- `PIPELINE.md` — the full steps for one daily run

Metricool: **blogId not set yet** (fill this in once this channel's brand/account exists in Metricool).
Account watermark: `@ant_proyek`, drawn top-right on every video by `engine/render.py` (story field `handle` overrides; `--stamp <video> --out <video>` adds it to an already finished video).
Voice: WING (`LMO8Em46czmXgX8nuxIU`), model `eleven_v4`.
