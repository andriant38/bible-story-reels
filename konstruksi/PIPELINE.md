# Daily construction & mining 3D reel: how to run it

One daily run makes **one new** Indonesian reel about construction or mining, as **3D animation** rendered in code (three.js in headless Chromium). It gets an ElevenLabs voice over and is scheduled in Metricool.

Tools needed: the ElevenLabs connector (`creative_*`), the Metricool connector, Bash with Node 22, ffmpeg, Python (Pillow) and the pre-installed Playwright Chromium, plus git push access to this repo.

Everything for this channel lives in `konstruksi/`. Do not touch the Bible-reel files (`engine/`, `stories/`, `videos/`, `posted.json`).

---

## 0. Prepare

```bash
cd /home/user/bible-story-reels && git pull --ff-only origin main
(cd konstruksi/engine && npm install --silent)        # three.js, once per container
TODAY=$(TZ=Asia/Jakarta date +%F)
```

- Read `konstruksi/posted.json`. Do not repeat a topic (slug) that is already in it.
- If `$TODAY` already has an entry, stop: today is done.

## 1. Choose a topic and write the script

- **Pick a topic** that is not in `posted.json`, alternating construction and mining.
- **Ideas:**
  - TBM / how the MRT is dug
  - how a skyscraper is built
  - a climbing tower crane
  - inside reinforced concrete
  - a sea bridge (piers and segments)
  - a cable-stayed bridge
  - pile foundations
  - earthquake-resistant buildings (base isolators)
  - how a dam is built
  - an open-pit mine and why it has steps
  - blasting in slow motion
  - nickel from the ground to an EV battery (pit → smelter)
  - coal to electricity
  - a giant excavator vs a car
  - a mine conveyor belt
  - toll road layers
  - mine reclamation
- **Facts:** only use facts you are sure of. Round them and say "sekitar" / "hampir". Do not use brand names in the narration, and do not invent statistics. If unsure, leave the fact out.
- **Language and length:** Indonesian, speaking to the viewer as "kamu". **11–13 scenes**, **150–190 words** in total (about 60–75 s). Keep each sentence short.
- **Structure:**
  1. **HOOK (scene 1, 2–4 s).** A shocking fact or question, shown as big text: `headline` with `hook` + `hook_accent`, `headline_y` about 260. Vary the pattern: comparison ("Bannya lebih tinggi dari kamu"), question ("Kenapa jembatan ini tidak tenggelam?"), or danger ("Satu kesalahan di sini, gedung bisa miring").
  2. **TITLE (scene 2).** `big` / `accent` / `big`.
  3. **The process or the facts,** step by step. Big numbers use `stat` + `unit`.
  4. **UNDERSTANDING (2 scenes).** `label` (a yellow tag, e.g. "KENAPA?", "FAKTA", "CARA KERJANYA") + `point`.
  5. **CLOSING.** `statement` + `ref` ("TULIS DI KOMENTAR"), with a specific question for the viewer.
- Save it as `konstruksi/stories/<slug>.json`. **Copy `konstruksi/stories/truk-tambang-raksasa.json` as the model.**


### Growth rules (the owner's goal is FOLLOWERS, not only views)

Every video must give the viewer a reason to follow:
- **Series.** Most videos belong to a numbered series, set as `"series": "HITUNGAN PROYEK #3"` in the story JSON (drawn as a badge on every scene). Series:
  - `HITUNGAN PROYEK #n`: field calculations (rit, truk molen, semen, besi, solar).
  - `PROSES PROYEK #n`: start-to-finish process (pengaspalan, gedung, jembatan, MRT).
  - `FAKTA TAMBANG #n`: mining (truk raksasa, peledakan, nikel).
  - About 1 in 4 videos can be a stand-alone general-interest topic (e.g. gempa) to reach new people.
  Number each series in order. `posted.json` and earlier stories show the last number used.
- **The closing scene promises the next episode and asks for a follow**, e.g. the narration ends with "Follow, besok kita hitung berapa besi untuk rumah dua lantai.". The `ref` line reads "TULIS DI KOMENTAR · FOLLOW UNTUK #4". Keep that promise: the next video in that series must be that topic.
- **Hook in the first 2 seconds** on a question the viewer has asked themselves (cost, quantity, danger, "kenapa"). Prefer topics that home builders and site workers (tukang, mandor, operator, checker) search for, such as semen, besi, rit, solar, retak, and topics that make them argue in the comments.
- **The caption** ends with "Follow untuk episode berikutnya" and the question for the comments.
- **Hashtags: at most 5** in the caption (Instagram allows only 5). Pick the 5 most relevant: usually the topic, the machine/material, the series (#hitunganproyek / #solusilapangan), #konstruksi or #tambang, and one audience tag.

### Scene format

```jsonc
{
  "text": "Narration (1–2 sentences).",
  "subtitle": "(optional) on-screen text if it differs from text",
  "headline": [{"text": "360", "style": "stat"}, {"text": "TON", "style": "unit"}], "headline_y": 200,
  "world": "site|pit|cutaway|sea|city|plain",
  "time": "day|golden|dusk|night",
  "strata": "laterite|coal|rock|soil",             // soil layer colours (pit / cutaway)
  "pit": {"benches": 5, "bench_h": 12, "berm": 26, "face": 7, "floor_r": 60, "water": false},
  "tunnel_y": -18, "tunnel_r": 3.3, "depth": 40,  // cutaway world only
  "camera": {"move": "orbit|push|pull|rise|drop|flyby|static", "target": [x,y,z], "dist": 40, "height": 15,
             "angle": 35, "sweep": 25, "follow": "<object id>", "fov": 50, "shake": 0.6, "shake_at": 0.3},
  "shadow_size": 60,                                 // about the size of the subject (m); larger for wide shots
  "objects": [ {"type": "...", "pos": [x,y,z] | "pit:<bench>:<angle>", "rot": 0, "scale": 1, "id": "t1",
                "anim": "...", "progress": [0, 1], "start": 0, "end": 1, ...} ]
}
```

**Units.** Units are metres and y points up. `rot` is in degrees around y; an object's front points along +x. `camera.angle` is the camera's direction around the target: 0 = from +z, 90 = from +x. `height` is the camera height above the target.

**Framing in portrait.** The top area (y about 200–700 px) is for the headline and the bottom (about 1500–1780 px) is for the subtitles. When a scene has a headline, raise `target.y` slightly so the subject sits lower in the frame.

**Road layers.** The top of each layer (with `ey` = 1) is: sub 0, lpb 0.35, lpa 0.65, prime 0.67, acbc 0.83, acwc 0.95. Put machines at that y on top of the layer they work on. The layer front is at `x = -40 + 80 * progress`. For a cross-section shot, raise the road (`pos` y = 1.8 with `ey` 3) and point the camera at the −x end face: `target` [-40, 3.2, -0.8], `angle` about -70, `dist` about 23.

**Pit positions.** `"pit:<k>:<angle>"` puts an object on bench k (1 = top bench, k = benches−1 is the lowest). Use `"pit:floor:<angle>"` for the pit floor and `"pit:0:<angle>"` for the rim. The height of bench k is `-k*bench_h`.

**`progress`.** It controls the animation across the scene: `[0.3, 0.6]` means going from 30% to 60% complete. Use it for continuity between scenes (e.g. a building at 0→0.4 in one scene, then 0.4→1 in the next). `start`/`end` limit the animation to part of the scene.

### Object types

| type | key params | anim |
|---|---|---|
| `worker` | `hat` (colour), `color` | `walk`, `wave` |
| `excavator` | `scale` (2–2.5 = mining excavator), `swing`, `period` | `dig`, `load` |
| `haul_truck` (mine truck, 7.7 m tall) / `dump_truck` | `to` (target position: it drives there), `loaded`, `load_color`, `ease`, `tarp`, `steam` (hot asphalt) | `dump`, `assemble` (wheels → cabin → bed fitted together), `fill` (load grows in the bed) |
| `car`, `house` | `color`; house `h` | – |
| `tower_crane` | `height`, `height_to`, `jib`, `load` (`beam`/`bucket`/`panel`), `slew`, `swing`, `trolley_from/to`, `drop_from/to` | `swing`, `climb`, `idle` |
| `building` | `floors`, `floor_h`, `w`, `d`, `facade` | `build` (columns → slab → glass) |
| `bridge` | `spans`, `span_len`, `deck_h`, `deck_w`, `style: "cable"`, `pylon_h` | `build` (piers → segments) |
| `tbm` (tunnel boring machine, axis +x) | `radius`, `advance` | `bore` (needs world `cutaway` with matching `tunnel_y`) |
| `blast` | `at` (moment 0–1), `size`, `slowmo`, `push` | automatic |
| `ore_pile` | `radius`, `h`, `color` | `grow` |
| `conveyor` | `length`, `incline`, `h`, `color`, `speed` | moves automatically |
| `factory` (smelter / power plant) | `w`, `d`, `h`, `chimneys` | smoke automatically |
| `pile` (pile foundation + rig) | `count`, `spacing`, `length` | `drive` |
| `column` (reinforced-concrete cutaway) | `w`, `h`, `filled` | `pour` |
| `dam` | `length`, `h` | `build` |
| `base_isolator` (quake-resistant building) | `floors` | `quake` |
| `dimension` (yellow measuring line) | `h`, `label`, `label_size`, `label_side` | `grow` |
| `label` (3D text) | `text`, `size`, `color`, `show_at` | – |
| `zone` (red danger area) | `w`, `d`, `color` | `pulse` |
| `flag` (safety whip on mine vehicles) | `h` | – |
| `road_layers` (road section along x, 80 m) | `layers` (finished: `sub`,`lpb`,`lpa`,`prime`,`acbc`,`acwc`,`marking`), `build` (layer being laid, its front advances with progress), `tags` (layer labels on the −x end face), `ey` (vertical exaggeration for cross-section shots, e.g. 3) | – |
| `grader` (motor grader) | `to` | `shuttle` (back and forth with `period`) or drives to `to` |
| `roller` | `kind`: `tandem` (steel drums, asphalt), `pneumatic` (rubber tyres), `vibro` (soil/aggregate); `to`, `period`, `phase`, `vibrate` | `shuttle`, `drive` |
| `paver` (asphalt finisher) | `to`, `screed_w`; moves linearly, so give it the same `progress` as the `build` layer | – |
| `sprayer` (prime-coat distributor / water tanker) | `to`, `color`, `spray_color`, `cab` | sprays while moving |
| `amp` (asphalt mixing plant) | – | drum turns, smoke |
| `cones` (traffic cones in a row along x) | `count`, `spacing` | – |
| `trees`, `city` (background fill) | `count`, `area`, `clear` (empty radius), `max_h` | – |
| `road` | `length`, `w` | – |

Colours are integers (e.g. `9127979` = 0x8b4a2b, laterite nickel ore).

## 2. Check the visuals BEFORE voicing (no credits spent)

```bash
python3 konstruksi/engine/render.py konstruksi/stories/<slug>.json --sheet work/k-<slug>/sheet.jpg
```

Open the sheet and check that:
- the subject is clearly visible and not covered by the headline or subtitles,
- the camera is not inside an object,
- objects stand on the ground or a bench and are not floating,
- every scene matches its narration.

To look at a single scene at several moments, run `node konstruksi/engine/render3d.cjs <story> --stills /tmp/x --scenes 7 --at 0.1,0.5,0.9`. Fix the JSON and repeat until it is right.

## 3. Narration (ElevenLabs)

- `creative_create_flow` with the name `Reel konstruksi <slug>`.
- For each scene, call `creative_generate_speech` with:
  - `voice_id` = `LMO8Em46czmXgX8nuxIU` (WING, energetic Indonesian male)
  - `model_id` = `eleven_v4`
  - `generations_count` = 1
  - `prompt` = the scene's `text`
- Write numbers out as words in `text` ("tiga ratus enam puluh ton"); the headline can use digits.
- **The free plan allows only one generation at a time.** Send **all scenes in one call**, separated by blank lines, then split them:

```bash
mkdir -p work/k-<slug>
curl -sS -o work/k-<slug>/combo.mp3 "<content_url>"
python3 konstruksi/engine/split_audio.py work/k-<slug>/combo.mp3 work/k-<slug> --story konstruksi/stories/<slug>.json
```

The splitter prints each scene's duration next to its character count; the two should be roughly proportional (about 13–15 characters per second). If one scene is clearly too long and the next too short, list the pauses (`ffmpeg -i combo.mp3 -af silencedetect=n=-40dB:d=0.25 -f null -`), find the pause that really separates the two sentences, and cut those two clips again by hand with `ffmpeg -ss … -to …`. Check that the printed cut times make sense. Never re-run a generation that already started.

## 4. Render

```bash
python3 konstruksi/engine/render.py konstruksi/stories/<slug>.json --audio-dir work/k-<slug> --out konstruksi/videos/$TODAY-<slug>.mp4
ffmpeg -v error -y -i konstruksi/videos/$TODAY-<slug>.mp4 -vf "fps=1/3,scale=270:-1,tile=6x5" -frames:v 1 work/k-<slug>/final.jpg
```

Rendering takes about 6–10 minutes (≈0.25 s per frame). If `konstruksi/assets/music.mp3` exists, it is used as background music.

## 5. Commit, schedule, report

```bash
python3 konstruksi/engine/log_post.py <slug> "$TODAY"
find konstruksi/videos -name '*.mp4' -mtime +7 -delete
git add -A konstruksi && git commit -m "Konstruksi reel $TODAY: <title>" && git push -u origin main
```

- **Public URL:** `https://raw.githubusercontent.com/andriant38/bible-story-reels/main/konstruksi/videos/$TODAY-<slug>.mp4`
- **Schedule in Metricool:** same as steps 5–6 of the root `PIPELINE.md`, but with this channel's own `blogId` (see `konstruksi/README.md`). Use the caption, `youtube_title` and `youtube_tags` from the story. For `youtubeData.category` use `EDUCATION`.
- **Report:** end with a short message in Indonesian: the title, the time (WIB), the Metricool link, and the credits used.
