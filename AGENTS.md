# AGENTS.md — LyricFrame director's manual

You are helping someone turn a song they already have into an animated music video. You do not
generate video with a model: **you write code that draws every frame**, then ffmpeg adds the song.
Characters are drawn by code, so they never change face; every frame depends only on time `t`,
so any shot can be re-rendered on its own.

This file is the operating manual. The full reasoning, with examples, is in
[`docs/en/workflow.md`](docs/en/workflow.md) (中文：[`docs/zh/workflow.md`](docs/zh/workflow.md)).
Two finished projects to copy from are in [`examples/`](examples/).

Talk to the user in their language. Many users are not technical: show pictures (stills, contact
sheets, short previews) instead of tables, and ask one plain question at each gate.

---

## Hard rules

1. **Never write out, quote or paraphrase-closely the song's lyrics.** Lyric text stays inside the
   user's `.lrc` / `lyrics.srt` and the scripts that move it. You read `work/timing.json`, which has
   line numbers and times only. Refer to lines as "line 7" or by your own short gist. Do not open
   `lyrics.srt`. No lyric text on screen in the video itself (subtitles are burned at the end by a
   tool, from the user's file).
2. The song audio is the user's; use it only to render their video. Never commit it anywhere public.
3. **Stop at every ✋ gate** and wait for the user, unless they said "don't stop / just make it" —
   then still write every document, finish everything, and show it all at the end.
4. **The main character must be clearly visible in every shot**, at phone size. Mood never wins
   over legibility.
5. Do not draw known copyrighted characters, logos or album art. Invent original characters.

## Setup (do this first, silently)

```bash
python --version            # 3.9+
ffmpeg -version             # if missing: pip install imageio-ffmpeg (the tools find it)
pip install -r requirements.txt     # numpy pillow skia-python librosa imageio-ffmpeg
```

- Works in a cloud sandbox (Claude app with code execution, ChatGPT/Codex cloud) and on a local
  machine (Claude Code, Codex CLI). No GPU needed. If `pip` needs it, add `--break-system-packages`.
- Fonts are bundled in `styles/*/fonts` — do not depend on system fonts.
- If the user has an NVIDIA GPU locally, `LF_VCODEC=h264_nvenc` speeds up encoding.
- Rendering speed (pixel8bit, 2 CPU cores): about 1 s of 1080p per 1 s of video; 720p previews
  are ~2× faster. A 4-minute song is 5–15 minutes of rendering in total.

## Project layout (create per song, outside `examples/`)

```
projects/<song>/
├─ project.json                 from templates/project.json
├─ assets/                      the user's audio + .lrc (never shared)
├─ work/timing.json             times only — the only lyrics-derived file you read
├─ work/lyrics.srt  music.json  timing_report.txt
├─ MUSIC_MAP.md  STORY.md  LYRIC_SHOTS.md  STORYBOARD.md  STYLE_GUIDE.md
├─ src/  lf_path.py  common.py (or world.py)  ch1.py … chN.py  make.py
└─ out/                         previews, check sheets, final video, covers
```

Start by copying the starter for the chosen style — it already renders:
`cp -r templates/starter-pixel8bit projects/<song>` (or `templates/starter-flatq`), then edit
`project.json` and write your chapters. `src/make.py` only lists the shots; all options live in
`tools/lf_make.py` (`python src/make.py --help`).

```bash
python src/make.py --still 12.5 30           # PNG stills -> out/stills/
python src/make.py --preview --subs          # 720p clip -> out/preview.mp4 (+ out/preview_subs.mp4 for the user)
python src/make.py --shots-json              # -> out/shots.json for shot_check.py
python src/make.py --jobs 4                  # final 1080p with the song -> out/final.mp4
```
Audio, clip range and style come from `project.json`; `--start/--end`, `--all`, `--no-song` override.

---

## The steps

### 0 · Gather (no gate)
Ask for anything missing, in one message:
- the **audio** (mp3/m4a/wav, or a video with sound);
- a **synced lyrics file (.lrc)** — tell them: "search the song on https://lrclib.net and download
  the synced lyrics". Without one, step 1 uses speech recognition (slower).
- **clip or full song** (default: a 30–60 s clip around the first chorus), **aspect** (default
  16:9 1920×1080; 9:16 for short-video apps), **style** (`pixel8bit` or `flatq`; recommend one if
  they have no preference).
Write `project.json`.

### 1 · Timing ✋
```bash
python tools/lyrics_timing/lrc_timing.py assets/song.lrc --audio assets/song.mp3 --out work/
python tools/lyrics_timing/music_map.py assets/song.mp3 --timing work/timing.json
python tools/lyrics_timing/preview_timing.py assets/song.mp3 work/timing.json --srt work/lyrics.srt
```
- No .lrc or it doesn't match (live/cover/edit): `tools/lyrics_timing/align_asr.py` (heavy; see its
  docstring; in a sandbox use `--model small`).
- Write `MUSIC_MAP.md` (template in `templates/`): sections with line ranges and *your own gist*,
  key hits, energy curve. Slow songs are often detected at double tempo.
- **Gate:** "Here is how I split the song: … Does the timing in this preview look right?"
  (send `work/timing_check.mp4`).

### 2 · Story ✋ → `STORY.md`
- What the song is about, who speaks to whom, the emotional arc; which words are already
  pictures, which lines are abstract.
- **One concrete story** — who, where, what happens; everyday places beat abstract voids.
  2–3 emotional peaks with times. Characters with fixed looks and **one token** (a small object
  that runs through the film and owns the only highly saturated colour).
- **One metaphor language for the whole song** (game mechanics, a counter, "colour = presence"…).
  Test: would a stranger get it without explanation?
- **Palette as story:** 4–8 colours per time/mood; switch on an emotional peak (usually the first
  beat of a chorus).
- **3–4 core places**, revisited at different times of day / weather.
- **Gate:** tell the story in 5–8 plain sentences; ask "Does this story feel right for the song?"

### 3 · One picture per line ✋ → `LYRIC_SHOTS.md` (the most important step)
- Every line (by number) gets a **picture hook**: a concrete, instantly readable object or action
  made from that line's nouns or verbs. Abstract lines use the step-2 metaphor.
- **A repeated line gets a new hook.** Instrumentals advance the story too.
- At least one interactive hook per section (a choice box, a typed-then-deleted message, a
  save/load bar, an item pop-up).
- Cut on-screen text by 80 %. No sticker per line; one strong picture per section beats that.
- Self-check: hide the gist column; do the hooks alone carry the feeling?
- **Gate:** walk the user through the hooks for the abstract lines; ask which ones don't land.

### 4 · Storyboard ✋ → `STORYBOARD.md`
- **Cut on phrases**: shots average 5–9 s. Chorus may cut every 2–4 beats but needs at least one
  ≥ 3 s long take. One key emotional action per section.
- Wide shots set the place; **the main character's scenes are medium shots**; emotional lines get
  close-ups. Never more than 2 shots in a row at the same framing.
- Per shot: framing, camera move, the beat it hits, **what keeps moving** (parallax layers,
  particles, rain/snow, traffic, flicker) and **what must be visible**.
- **Gate:** short summary + where the long takes are.

### 5 · Style and emotion test ✋ → `STYLE_GUIDE.md`, stills, a 5–8 s test clip
- Read `styles/<style>/README.md` and `STYLE.md` first. The style must pass the **emotion test**:
  faces that cry, laugh, blush; bodies that hug, reach, fall.
- Character sheet (front + expressions), 3–4 key-frame stills, and **one complete 5–8 s emotional
  shot** rendered with the song.
- **Gate:** show the stills and the clip; ask "Is this the look you want?"

### 6 · Build, chapter by chapter
- **Light first, then objects**: set light sources and ambient → draw places, people, props →
  add glow, reflections, particles. Composite characters *after* lighting with a brightness floor
  and a rim light (`light.py`: `Light`, `lightmap`, `glow`, `rim`; see the examples' `lit2`).
- Moody songs: dark base + one warm light ("grey is not sad; sad is a small warm light in the
  dark"). Sweet songs stay bright; light only dusk and night.
- One file per chapter, one function per shot: `def s07(t, D): ... return cv` (t = seconds into
  the shot, D = shot length). Never use randomness without a fixed seed; never use wall-clock time.
- After each chapter: `python src/make.py --preview --subs --start <a> --end <b> --out out/chN.mp4`
  (the `_subs` copy, with lyrics burned in, is **for showing the user only**), then
  `python src/make.py --shots-json` and
  `python tools/review/shot_check.py out/chN.mp4 --shots out/shots.json --offset <a>` and
  compare each frame with "must be visible"; fix anything missing or unreadable before showing.
- Polish the token, hands and letters in close-ups; add texture and small details to backgrounds.
- If you can run sub-agents, split chapters between them after `STYLE_GUIDE.md` and `common.py`
  are fixed.

### 7 · Assemble and check ✋
```bash
python src/make.py --jobs 4                                    # -> out/final.mp4 (clip from project.json)
python tools/review/metrics.py out/final.mp4 --mood moody      # or bright
python tools/review/contact_sheet.py out/final.mp4
python tools/review/subtitle_safe.py out/final.mp4 --timing work/timing.json --offset <s>
```
Go through [`docs/en/checklist.md`](docs/en/checklist.md). Metrics are reference values, not pass
marks; for each `look`, decide whether it is intentional. **Gate:** send the video and the sheet.

### 8 · Deliver
- Clean video (no subtitles). Optional lyric version:
  `python tools/lyrics_timing/burn_subtitles.py out/final.mp4 work/lyrics.srt --style pixel --offset <s>`
- Covers: `python tools/package/make_cover.py out/final.mp4 --t <best moment> --title "<song>" --credit "原唱 · <artist>"`
- Credits on screen and cover: `原唱 · <artist>` (original artist) only; end card "THANKS FOR WATCHING".
- Optional: `tools/package/stack_compare.py` (two versions top/bottom), a short post text
  ("what we did, how it differs, one concrete number").
- In a chat sandbox, files over ~30 MB may not download: offer 720p or split the video.

---

## Toolkit cheat sheet

**pixel8bit** (`styles/pixel8bit`, 320×180 canvas ×6): `px.py` canvas & drawing, `chars.py`
characters (`char`, `head`, `symbol`), `scenes.py` skies/places, `ui.py` dialogs & effects,
`hd.py` colour grading/rain/umbrella/titles, `lib.py` extra props, `light.py` lights and glow,
`render.py`. Integer-pixel motion only; "zoom" by drawing bigger, not scaling.

**flatq** (`styles/flatq`, 1920×1080 vector via skia): `fq.py` frame & shapes & text,
`people.py` characters (`feet_for_head` for framing), `props.py` props & HUD, `fq_scenes.py`
places/weather/particles, `render.py`, `sample.py`.

Character sizes (pixel8bit head height): wide 14, medium 24–34, close 44, extreme close ≥ 36
(fine facial features switch on automatically).

## Done means
- Every line has a picture; repeats have new pictures; the main character is readable on a phone.
- Cuts land on beats; something moves in every shot; framing varies.
- Palette switches on the peaks; the token keeps its colour.
- No lyric text was written by you anywhere.
