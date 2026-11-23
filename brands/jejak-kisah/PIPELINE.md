# Jejak Kisah: how to make and schedule one video

Jejak Kisah posts **two videos a day, at 12:00 and 19:00 WIB**, to Facebook, Instagram, TikTok and YouTube Shorts.
Topics are true stories that are rarely told: unsolved historical mysteries, real disasters and survivals, forgotten people,
Indonesian history, and the origins of everyday things. Videos publish automatically through Metricool.

One run makes **one** video for the next free slot. To fill both slots, run it twice.
It uses the same engine as the Bible reels (`engine/`), with the `--brand` flag for Jejak Kisah's look:
gold accents, a "JEJAK KISAH" watermark, and its own original music (`ambient.m4a`, made by `tools/make_music.py`).

Tools needed: the ElevenLabs connector, the Metricool connector (with the **Jejak Kisah** brand visible), Bash with ffmpeg,
Python with Pillow and numpy, and git push access.

```bash
cd /home/user/bible-story-reels && git pull --ff-only origin main
JK=brands/jejak-kisah
SLOT=$(python3 $JK/tools/slot.py next)     # e.g. "2026-11-22 12:00"
```

## 0. Check the brand

Call `getBrandSettings`. Find the brand whose label is **Jejak Kisah** and note its `id` (the blogId). If no such brand is
visible, stop and report that. **Never post Jejak Kisah videos to `bible_storyy`** (blogId 8002634): that brand is the Bible
accounts.

Read `$JK/posted.json`. Do not repeat a slug that is already in it. Look ahead: if `$SLOT` is more than 2 days away, stop,
because we are already far enough ahead.

## 1. Pick the topic and write the script

**Read `VIRAL.md` first.** Every script must pass the checklist at its end: a hook of 6 words or fewer, a re-hook at
scene 7–8, `*key words*` in the subtitles, and a closing either/or question.
Scripts that are already written wait in `stories/`. If the next queue title already has a story file, use it as it is.

- Take the **first title in `$JK/queue.json`** and remove it in the same commit. The new first title is the next video;
  tease it in the closing scene. When fewer than 10 titles are left, add new ones (not already in `posted.json`) and mix
  the five topic types listed above.
- **Facts come first.** Every claim must be well documented. Use only facts you are confident about, write numbers and
  dates exactly, and put 1–3 real sources in the story's `"sources"` field. When something is disputed or unknown, say so
  ("teori terkuat…", "sampai hari ini tidak diketahui"). For legends, say plainly that they are legends. Never invent
  dialogue, names or details.
- **Respect the victims.** For disasters and tragedies with victims who are still remembered, tell the story with respect:
  no graphic detail, and no jokes. Avoid recent tragedies whose families are still grieving.
- Language: Indonesian, speaking to the viewer as "kamu". Every sentence should be short enough to say in one breath.
- Length: **12–13 scenes and 140–170 words**, which gives 61–80 seconds. A shorter video is more likely to be watched to the end.
- **Structure:**
  1. **HOOK, scene 1 (no title yet).** 1–2 short sentences, with a `hook` + `hook_accent` headline at `headline_y` 420.
     Use these patterns, and vary them: a contrast ("Kapalnya utuh. Awaknya lenyap."), a question to the viewer, a
     shocking number, or "what would you do".
  1b. Use the either/or question in the closing scene, not an open question: "setia atau keras kepala?"
  2. **TITLE, scene 2.** A title card with `big`, `accent`, `small` and `ref`; the `ref` is the place and year.
  3. **The story**, building tension, with **the climax** at the end.
  4. **UNDERSTANDING, 2–3 scenes**, each with a `label` + `point` headline (`headline_y` 300). Choose from:
     - `FAKTANYA` (a surprising true fact)
     - `MITOSNYA` (a popular myth, corrected)
     - `TEORI TERKUAT` (the best explanation)
     - `KONTEKSNYA` (why it mattered then)
     - `PELAJARANNYA` (the one takeaway for life today)
  5. **The closing scene:** a `statement` question to the viewer, then "Tulis di komentar." Then a teaser for the next
     video and a follow call: "Berikutnya: <next title>. Follow, supaya tidak ketinggalan."
- Save the script as `$JK/stories/<slug>.json`. Use `$JK/stories/mary-celeste.json` as the model. The format and the
  element list are the same as in the root `PIPELINE.md`, plus these:
  - Backgrounds: `fog`, `sepia`, `ember`, `arctic` and `jungle` (plus all the Bible ones). `"mist": true` adds low fog.
  - Ground elements: `ship` (a sailing ship), `steamship`, `pyramid`, `lighthouse`, `ruins`, `house`, `castle`, `candi`
    and `volcano`.
  - Floating elements (give them `y`): `plane`, `smoke` and `moon`.
  - `bg: night` already draws a moon at `sun_x`, so do not add a `moon` element on top of the headline.
- **Key words:** wrap 1–2 important words per scene in asterisks, e.g. `"Suara ini terdengar sampai *4.800 kilometer* jauhnya."`.
  They are drawn in gold in the subtitle, and `tts_text.py` removes the asterisks for the narration. Numbers can stay as
  digits: `tts_text.py` writes them out in Indonesian words for the voice.
- **Do not put emoji in `subtitle` or `headline`**, because the font cannot draw them. Emoji are fine in the caption.
- **Originality:** use different backgrounds, terrain and cameras from the previous 3 videos, and do not use the same hook
  pattern twice in a row.

## 2. Narration

**Voicebox (the owner records it, free).** Run `python3 $JK/tools/naskah.py <slug>`. This writes
`$JK/narration/<slug>/NASKAH-VOICEBOX.txt`, with one line per scene. The owner records each line in Voicebox and commits
`01.mp3`, `02.mp3`, … to that folder. When all the clips are there, copy them to `work/<slug>/` and go to step 3. If they
are not there yet, stop and report which story is waiting for its recording.

**ElevenLabs (paid, only when there are credits).** The rules are the same as step 2 of the root `PIPELINE.md`, except for these settings:

- **voice_id** `uzkxbhFCx9Ni2LANf1zB` (Fikri, a calm documentary narrator). It is deliberately not the Bible channel's
  voice, so the two brands sound different.
- **model_id** `eleven_v4`, and **generations_count** 1.
- One flow per video, named `Jejak Kisah <slug>`.
- **Cost:** about 1,300 credits per video, or about 80,000 credits a month at 2 videos a day.
- The fastest way: generate scene 1 alone, then all remaining scenes in one call with a blank line between scenes. Split
  that file with:

  ```bash
  python3 engine/split_audio.py combo.mp3 work/<slug> 2 3 … 13 --story $JK/stories/<slug>.json
  ```

- Clips that were already paid for are kept in `$JK/narration/<slug>/NN.mp3`. Copy them into `work/<slug>/` and generate only the missing scenes. Never generate the same scene twice.
- If a generation fails for lack of credits, **stop** and report it. Do not retry, and do not post a video without
  narration.

## 3. Render and check

```bash
D=${SLOT% *}; T=${SLOT#* }; T=${T/:/}
OUT=$JK/videos/$D-$T-<slug>.mp4
python3 engine/render.py $JK/stories/<slug>.json --audio-dir work/<slug> --out $OUT --brand $JK/brand.json
ffmpeg -v error -y -i $OUT -vf "fps=1/3,scale=270:-1,tile=6x5" -frames:v 1 work/<slug>/sheet.jpg
```

`brand.json` plays the narration at 1.08× and shortens long pauses.

Look at the contact sheet. Check three things:

- No shape covers the headline.
- The text is readable.
- The visuals match the narration.

Also check the length with `ffprobe`: it must be **61–89 s**. If it is too long, shorten the script; changing the text
does not cost credits, but new narration does. If it is too short, it can still go out, but note that in the report.

## 4. Publish the file

```bash
python3 $JK/tools/slot.py log <slug> "$SLOT"
find $JK/videos -name '*.mp4' -mtime +7 -delete
git add -A && git commit -m "Jejak Kisah $SLOT: <title>" && git push -u origin main
```

The public URL is `https://raw.githubusercontent.com/andriant38/bible-story-reels/main/brands/jejak-kisah/videos/<file>.mp4`.

## 5. Schedule in Metricool

- `blogId`: the Jejak Kisah id from step 0.
- `date`: `<SLOT>:00+07:00`, with `publicationDate.timezone` set to `Asia/Jakarta`.
- Before you schedule, call `getScheduledPosts` for that day and make sure the slot is still empty.
- `info`:
  - `autoPublish`: true, and `draft`: false
  - `media`: [the raw URL]
  - `providers`: facebook, instagram, tiktok and youtube
  - `text`: the caption
  - `videoCoverMilliseconds`: 1200. This makes the hook frame the cover, which is also what shows on the profile grid.
  - `firstCommentText`: "🕯️ Kisah nyata baru setiap hari pukul 12.00 & 19.00 WIB. Follow supaya tidak ketinggalan! Berikutnya: <next title>"
  - `facebookData`: `{"type":"REEL","title":<title>}`
  - `instagramData`: `{"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}`
  - `tiktokData`: `{"privacyOption":"PUBLIC_TO_EVERYONE","title":<title>,"isAigc":true}`
  - `youtubeData`: `{"title":<youtube_title>,"type":"short","privacy":"public","tags":<youtube_tags>,"category":"EDUCATION","madeForKids":false,"isAiGeneratedContent":true}`
- If Metricool rejects the media, wait 1 minute and try once more. If it fails again, report it.

## 6. Report

End with a short report in Indonesian:

- the title and the slot (WIB)
- the `plannerUrl`
- the credits used
- any step that failed

## Caption format

- Line 1 is the hook.
- Then 1–2 lines of the story.
- Then the question, followed by "Tulis di kolom komentar 👇".
- Then the series line: "🕯️ Jejak Kisah: kisah nyata yang jarang diceritakan. Follow untuk kisah berikutnya."
- End with 6–9 hashtags, always including #JejakKisah #KisahNyata #MisteriSejarah.
