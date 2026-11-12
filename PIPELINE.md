# Daily Bible-story reel: how to run it

This is the full procedure for one daily run. Every day the run creates **one new** Indonesian Bible-story reel in the silhouette style, then schedules it in Metricool for Facebook, Instagram, TikTok and YouTube Shorts. It publishes **automatically, with no human review**, as the owner asked.

Tools needed: the ElevenLabs connector (`creative_*`), the Metricool connector, Bash with ffmpeg and Python (Pillow and numpy), and git push access to this repo.

---

## 0. Prepare

```bash
cd /home/user/bible-story-reels && git pull --ff-only origin main
TODAY=$(TZ=Asia/Jakarta date +%F)
```

- Read `posted.json`. **Do not repeat** a story (slug) that is already in it.
- If `posted.json` already has an entry for `$TODAY`, stop: today is done.

## 1. Choose a story and write the script

- Pick a well-known Bible story that is not in `posted.json`. Vary it: alternate Old and New Testament, and mix stories, parables and miracles. Ideas: Nuh & bahtera, Abraham & Ishak, Yusuf dijual saudaranya, Musa & semak menyala, Laut Teberau terbelah, Tembok Yerikho, Gideon & 300 orang, Simson, Rut & Naomi, Samuel dipanggil Tuhan, Elia & nabi Baal, Daniel di gua singa, Sadrakh Mesakh Abednego, Yunus & ikan besar, Ester, Kelahiran Yesus, Yesus meredakan badai, Yesus memberi makan 5000 orang, Petrus berjalan di atas air, Zakheus, Anak yang hilang, Orang Samaria yang baik hati, Lazarus dibangkitkan, Perjamuan terakhir, Penyaliban, Kebangkitan, Saulus bertobat, and so on.
- Language: **Indonesian**. Stay faithful to the Bible text; use wording close to the Terjemahan Baru (TB) for any quoted verse. Do not add details that are not in the Bible.
- Length: **10–13 scenes**, total narration **150–190 words** (about 60–80 seconds).
- Structure (same arc as the Daud vs Goliat video):
  1. A strong hook plus the title card (`headline`).
  2. The story, scene by scene, as short narrative sentences.
  3. The climax.
  4. One short truth line, e.g. "Pertempuran adalah milik TUHAN."
  5. The closing scene: a short reflection headline with its verse reference, then a question to the viewer plus "Tulis di kolom komentar."
- Write it to `stories/<slug>.json` using the format below. **Copy `stories/daud-melawan-goliat.json` as the model.**

### Story JSON format

```jsonc
{
  "slug": "nuh-dan-bahtera",            // lowercase-with-dashes, unique
  "title": "Nuh dan Bahtera",
  "reference": "Kejadian 6–9",
  "scenes": [
    {
      "text": "Narration spoken for this scene (1–2 sentences).",
      "subtitle": "(optional) on-screen text if it should differ from text",
      "bg": "dusk|night|dawn|desert|sea|storm|golden",
      "terrain": "mountains|valley|plain|desert|sea|hill",
      "camera": "push|pull|pan_left|pan_right|static",   // optional
      "sun_x": 0.5, "stars": false, "rays": false, "clouds": false, "rainbow": false,  // optional
      "headline": [ {"text": "NUH", "style": "big"}, {"text": "dan", "style": "small"},
                    {"text": "BAHTERA", "style": "accent"}, {"text": "KEJADIAN 6–9", "style": "ref"} ],
      "elements": [ {"type": "person", "x": 0.3, "size": 1.0, "pose": "stand", "props": ["staff"], "facing": 1} ]
    }
  ],
  "caption": "Post caption, ends with a question + 6–9 hashtags",
  "youtube_title": "Max 90 chars, ends with #shorts",
  "youtube_tags": ["...", "..."]
}
```

- **`headline` styles:** `big`, `accent` (orange), `small`, `ref`, `statement` (for the closing reflection). Use a headline on the **first** and the **last** scene only.
- **Element types:**
  - `person` and `giant` take `pose`, `props` and `facing`.
  - `fallen_giant`, `lying` (a sleeping or lying person), `sheep`, `tent`, `palm`, `tree`, `boat`, `ark`, `cross`, `tomb` (`"open": false` for sealed), `city`, `tower`, `fire` (coloured), `bush`, `well`, `manger` and `lion` stand on the ground.
  - `fish`, `dove`, `star` and `stone` float; give them `"y"` from 0 to 1.
- **Poses:** `stand`, `arms_up`, `praise`, `pray`, `point`, `sling`, `kneel`.
- **Props:** `staff`, `spear`, `sword`, `shield`, `crown`, `sling`, `tablets`, `basket`, `child`, `beard`.
- **Layout:**
  - `x` runs from 0 to 1 across the frame, and `size` 1.0 is about 300 px tall. Keep figures within x 0.12–0.88.
  - Use `dy` (pixels) to raise an element, e.g. `-250` to put a figure on top of a `hill`.
  - Keep the first scene's figures low or small, so the title card at the top stays readable.
- Use varied backgrounds and cameras across scenes, and make the visuals match the text.

## 2. Narration (ElevenLabs)

- Create one flow: `creative_create_flow` with the name `Reel <slug>`.
- For **each scene**, call `creative_generate_speech`:
  - `voice_id` = `3rL9ZxRgBgIkh4tcbrEH` (Deden Cahya)
  - `model_id` = `eleven_v4`
  - `generations_count` = 1
  - the shared `flow_id`
  - `prompt` = that scene's line from `python3 engine/tts_text.py stories/<slug>.json`, **not** the raw `text`. This applies the owner's pronunciation rules: "Allah" is sent as "Alah" so the voice uses the Indonesian pronunciation, not the Arabic one. Subtitles and captions keep "Allah". To add a rule, edit `PRONUNCIATION` in that file.
- **Run the scenes one at a time.** The free ElevenLabs plan allows only one generation at a time, and parallel calls fail with "Free generations are busy". Start a scene, poll `creative_get_flow_run_status` until it completes, download its file, and only then start the next scene.
- Keep a list of `scene number → session_id → content_url`, so no scene is generated twice.
- **If "busy" keeps coming back**, wait about 90 seconds. Then send **all the remaining scenes in one call**: their TTS lines joined with a blank line between them. Split the result with `python3 engine/split_audio.py combo.mp3 work/<slug> <scene numbers…> --story stories/<slug>.json`, and check that the printed cut times look sensible.
- Never re-run a scene that actually started: that charges again. If a scene **did not start** (for example "busy"), start that one scene again once.
- Download each `content_url` in scene order:

```bash
mkdir -p work/<slug>
curl -sS -o work/<slug>/01.mp3 "<content_url of scene 1>"   # 02.mp3, 03.mp3, ...
```

`work/` is git-ignored.

## 3. Render and check

```bash
python3 engine/render.py stories/<slug>.json --audio-dir work/<slug> --out videos/$TODAY-<slug>.mp4
ffmpeg -v error -y -i videos/$TODAY-<slug>.mp4 -vf "fps=1/3,scale=270:-1,tile=6x5" -frames:v 1 work/<slug>/sheet.jpg
```

Look at `work/<slug>/sheet.jpg` and check that:

- the figures are visible and not hidden behind the title or the subtitles,
- the text is readable,
- every scene matches its narration.

Fix the JSON and render again if needed. Re-rendering costs no credits.

## 4. Publish the file

```bash
python3 engine/log_post.py <slug> "$TODAY"     # adds the story to posted.json
# Keep the repo small: delete rendered videos older than 7 days. Metricool keeps its own copy.
find videos -name '*.mp4' -mtime +7 -delete
git add -A && git commit -m "Reel $TODAY: <title>" && git push -u origin main
```

The public URL is `https://raw.githubusercontent.com/andriant38/bible-story-reels/main/videos/$TODAY-<slug>.mp4`.

## 5. Schedule in Metricool

- `blogId` = `8002634`. The networks connected are facebook, instagram, tiktok and youtube.
- **Time:** call `getBestTimeToPostByNetwork` with `socialNetwork=instagram`, `timezone=Asia/Jakarta`, from now to now + 24h. Pick the highest-value slot that is **at least 30 minutes from now**. If every value is 0 (the account has no data yet), use **19:00 WIB**: today if that is still at least 30 minutes away, otherwise tomorrow. Never schedule two reels on the same calendar day: check `posted.json` and `getScheduledPosts`.
- Call `createScheduledPost` with the `date` in `+07:00`, `publicationDate.timezone` = `Asia/Jakarta`, and `info` set as follows:
  - `autoPublish` = true, `draft` = false
  - `media` = [the raw URL]
  - `providers` = facebook, instagram, tiktok, youtube
  - `text` = caption
  - `facebookData` = `{"type":"REEL","title":<title>}`
  - `instagramData` = `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`
  - `tiktokData` = `{"privacyOption":"PUBLIC_TO_EVERYONE","title":<title>,"isAigc":true}`
  - `youtubeData` = `{"title":<youtube_title>,"type":"short","privacy":"public","tags":<youtube_tags>,"category":"NONPROFITS_ACTIVISM","madeForKids":false,"isAiGeneratedContent":true}`
- If Metricool rejects the media, wait 1 minute (raw.githubusercontent caches) and try once more. If it fails again, report it. Do not keep retrying.

## 6. Report

End with a short message in Indonesian: the story title, the scheduled time (WIB), the Metricool `plannerUrl`, and the credits used. If any step failed, say exactly which one.
