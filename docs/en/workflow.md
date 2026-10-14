# LyricFrame workflow (v4.0)

> An animated music video for a song that already exists: **the AI does not call a video model; it
> writes code that draws every frame**, then ffmpeg adds the original song. Characters are drawn by
> code, so they never change face; every frame depends only on time `t`, so any part can be redrawn
> on its own.
>
> This document is for AI assistants (Claude, Codex …) and for people who want to understand the
> process. The assistant's operating manual is [`AGENTS.md`](../../AGENTS.md); both say the same thing.
> 中文版：[`docs/zh/workflow.md`](../zh/workflow.md).

## Principles

1. **Accurate first, deep second.** Every lyric line gets a concrete picture a viewer reads at once.
   The deeper idea hides inside the story — no private symbol system the audience has to decode.
2. **Then beautiful.** Let the palette tell time, dare to leave space at the climax, polish the
   key objects separately.
3. **Light before objects; fewer cuts, wider views, always moving; one metaphor per song.**
4. **The main character must always be clearly visible.** Atmosphere never wins over legibility.
5. **(v4) People and places are *drawn*, not *assembled* from geometric shapes.** Every pose and every
   close-up is drawn on its own; buildings have parts and materials; framing varies and the camera keeps
   drifting; richness is measured with a script. See "Drawing rules".

Where these rules come from (frame-by-frame comparisons with well-received AI MVs) is in the appendix.

---

## Overview

```
0 Gather → 1 Timing ✋ → 2 Story ✋ → 3 One picture per line ✋ → 4 Storyboard ✋
→ 5 Style & emotion test ✋ → 6 Build by chapter → 7 Assemble & check ✋ → 8 Deliver
```

✋ = stop, show the user, continue only after they confirm.

| step | what | output |
|---|---|---|
| 0 Gather | audio + lyrics file; length, aspect, style | `project.json` |
| 1 Timing ✋ | when each line starts; beats, sections, energy | `timing.json`, `MUSIC_MAP.md` |
| 2 Story ✋ | understanding → one concrete story → one metaphor → palette | `STORY.md` |
| 3 One picture per line ✋ | **a picture hook for every line** (the key step) | `LYRIC_SHOTS.md` |
| 4 Storyboard ✋ | times, framing, camera, beat hits, what must be visible | `STORYBOARD.md` |
| 5 Style & emotion test ✋ | style rules, **character sheet ✋**, scene-parts sheet, one 5–8 s emotional shot | `STYLE_GUIDE.md`, sheets, stills, test clip |
| 6 Build | code per chapter, 720p previews, shot-by-shot, drawing and richness checks | `src/`, previews |
| 7 Assemble & check ✋ | 1080p render with the song, checklist, metrics | first cut, check sheets |
| 8 Deliver | clean + subtitled versions, covers, optional comparison and post text | video, covers, subtitles |

**Two paces**
- Default: stop at every ✋.
- The user says "don't stop, just make it": write every document anyway, finish in one go, show
  everything at the end; the user asks for changes afterwards.

**Default length**: a 30–60 s clip (one verse + one chorus) first; the full song once they like it.
A full 4-minute song takes a few hours.

---

## Drawing rules (v4, every style)

v3 fixed light, camera and restraint, but pictures still looked thin, because characters were
*assembled* by code: a circle for a head, an ellipse for a body, a line for an arm, then pixelated or
outlined. Up close it shows — egg-shaped bodies, arms growing out from behind the head, two heads
overlapping, a back view that is just the front in another colour, a building made of a few lines, and
close-ups that look empty.

Well-received code-drawn MVs work differently: **everything is drawn fresh for each film, but every
picture is fully drawn** — each pose of each character is a finished image (shoulder line, sleeve folds,
hem, highlights), buildings have window frames, AC units and laundry, and the camera keeps drifting.

> **The two styles shipped here (`pixel8bit`, `flatq`) still use parametric, assembled characters**, and
> the two examples are v3.1 work. Reuse their render pipeline, lighting, grading, particles and
> subtitles; **draw the characters and places for each film according to this section.**

**People and objects**

| # | rule | details |
|---|---|---|
| 1 | **Draw, don't assemble** | No ellipse bodies, no circle-and-line heads and arms. Each pose of each character is one complete image: pixel styles as palette-indexed character grids written cell by cell; vector / chalk / watercolour styles as paths following a real body outline (shoulders, collar, cuffs, hem, hands) |
| 2 | **Body checklist** (every pose) | Fixed head-to-body ratio for the whole film (chibi 1:2–1:2.5); shoulders wider than the neck, a trapezoid torso; arms start at the shoulder and have elbows and hands; clothes have collar, sleeves, hem, with trousers/skirt and shoes in separate colours; front, side and back **each drawn separately** (back: back of the hair, back collar, shoulder line); a shadow under the feet; with two people, decide who is in front — no overlapping heads or crossing limbs |
| 3 | **Fixed sizes, no arbitrary scaling** | 2–3 sizes per film: full body, half body, close-up, **each drawn on its own**. A close-up is a purpose-drawn bust (folds, hands, hair), never a small full-body figure scaled up |
| 4 | **Motion by frame swaps + moves; the camera brings energy** | Walk 4 frames; wave / cry / laugh 2–3 frames; no rotating line segments for arms; push-ins, pans, parallax and depth of field carry the motion |
| 5 | **Detail trio** (people, buildings, props) | Outline + 3 tones (light / mid / dark) + material texture (brick joints, tiles, wood grain, cloth folds). Buildings need real parts: window frames, AC units, laundry, signs, house numbers, awnings, window grilles |
| 6 | **Real everyday objects** | At least 2 objects per place that viewers recognise at once (building signs, a breakfast cart, a for-rent notice, a countdown board, a school gate, a corner shop, shared bikes). **Text inside the scene (signs, dates, numbers, stamps) is detail and allowed**; lyrics still never appear on screen |
| 7 | **Pixel technique** | Low-res canvas (e.g. 320×180 or 384×216) scaled up by an integer with nearest-neighbour; a fixed 16–32 colour palette; dithering only as texture, never as large fills |
| 8 | **One shared post layer** (all styles) | Per-layer depth of field, bloom, film grain, vignette, grading, optional letterbox; grading never touches UI. Use one fixed grain texture, not new random grain per frame (it bloats the file) |

**Backgrounds, camera, richness**

| # | rule | details |
|---|---|---|
| 9 | **Draw real places** | **Buildings**: wall material (brick, tile, paint, with stains and colour variation) + at least 5 kinds of parts (window frames, grilles, AC units, laundry, balcony plants, wires, signs, house numbers, meters, mailboxes, shutters) + light (low-sun shadows, lit windows, doorway light). **Ground**: tiles, kerbs, manholes, puddles, leaves, parked vehicles. **Night sky**: dark gradient + 3 layers of stars (hundreds of faint dots, dozens of medium, a few bright ones with cross glints) + a milky way or clouds — never a few "×". **Sports ground**: lane lines, grass texture, fences, goals, distant lit windows |
| 10 | **Fixed sizes ≠ fixed camera** | ① Framing mix: wide 25–35 %, medium 35–45 %, close/close-up 15–25 %, **insert shots** (letter, calendar, phone, breakfast…) ≥ 10 %; never more than 2 in a row at the same framing. ② ≥ 50 % of shots have a slow push/pull, pan or crane, 3–10 % per shot. ③ Size changes come from cutting framings + pushing in; draw assets at the shot's **closest** size, so the camera only ever shrinks them |
| 11 | **Richness check** (steps 6–7: `tools/review/richness.py`) | Defaults: detail ≥ 5, colours ≥ 30, textured blocks ≥ 50 %, light range across the film ≥ 25, camera zoom + pan ≥ 50 %; rework chapters that fall short. With a reference film, run `--ref reference.mp4`: **the higher of default and reference wins** |
| 12 | **Layers** | Every shot has foreground / midground / background content (the foreground can be a blurred sign, branch or window frame); something moves in the background; people are not all lined up on one horizon |
| 13 | **Character scale** | Character height as share of frame: **wide 10–15 %**, **medium ≤ 30 %**; close/close-up only where the storyboard says so (≤ 25 % of shots). Drawing medium shots as "full body fills the frame" turns the place into wallpaper |
| 14 | **Learn principles from references, don't copy** | Take the principles: scale, detail density, real objects, light, camera rhythm. **Don't copy** canvas size, viewpoint, signature objects and where they sit, face design, text overlays. Things that come from the lyrics may appear, but presented your own way. After the step-5 stills, compare item by item with each reference and change anything too close |

**Relation to v3**: lighting, cutting on phrases, revisiting core places and one metaphor per song all
still hold. "Cut on-screen text by 80 %" now means floating labels and speech bubbles only; text inside
the scene stays (rule 6). A permanent HUD is still off by default, but counters (day N, letter N) can
become objects in the scene (a stamp, a calendar, a numbered envelope).

---

## Step 0 · Gather

Ask for (all missing items in one message):
1. **Audio**: mp3 / m4a / wav / flac, or a video with sound.
2. **A synced lyrics file (.lrc)**: search the song on [lrclib.net](https://lrclib.net) and download
   the synced lyrics — free, no account. Without one, step 1 finds the times by speech recognition.
3. Three choices (defaults if they don't care): **clip or full** (clip around the first chorus),
   **aspect** (16:9 1920×1080; 9:16 1080×1920 for short-video apps), **style** (`pixel8bit` or `flatq`;
   recommend one from the song's mood).
4. Optional: what the song means to them, reference MVs, a story direction.

Write `project.json` (title, artist, audio, clip range, aspect, style, output folder).

### Copyright rules (for the whole process)
- **The AI never writes out, quotes or closely paraphrases the lyrics.** Lyric text only moves
  between the user's files and scripts (`.lrc` → subtitle file). The AI reads **times** and **line
  numbers**.
- Talk about lines as "line 7", "the second chorus line", or with a short gist in your own words.
- The audio is used only for the user's own video and never published in the repo or templates.
- **No lyric subtitles in the picture.** If the user wants subtitles, step 8 burns their .lrc in with
  a tool; the AI never touches the text.

---

## Step 1 · Timing ✋ → `timing.json` + `MUSIC_MAP.md`

**1.1 Line times**
- With an .lrc: `python tools/lyrics_timing/lrc_timing.py song.lrc --audio song.mp3 --out work/`
  - `timing.json` — line numbers and start/end times, no text (the only file the AI reads);
    `lyrics.srt` — for burning subtitles in step 8 (the AI does not read it).
  - The script checks the .lrc against note onsets in this recording and corrects a constant offset
    of more than 0.3 s when it is clearly off; the report says what it did.
- No .lrc, or the .lrc doesn't match this recording (live, cover, edit): `tools/lyrics_timing/align_asr.py`
  (speech recognition; downloads models on first run).
- List repeated choruses line by line; never merge them.

**1.2 Beats and sections** → `python tools/lyrics_timing/music_map.py song.mp3 --timing work/timing.json`
- BPM, beat grid, energy per 4 s, vocal blocks to place section boundaries.
- Slow songs are often detected at double tempo (72 → 144); use common sense.
- Write `MUSIC_MAP.md`: sections (range, line numbers, **your own gist**, cutting rhythm), key hits,
  energy curve. Template in `templates/`.

✋ **Confirm**: are the sections right, is the timing tight? Send the check video from
`tools/lyrics_timing/preview_timing.py`.

---

## Step 2 · Story ✋ → `STORY.md`

**2.1 Understanding** — what the song is about, who speaks to whom, how the emotion moves (look up
interpretations and background). Mark the **words that are already pictures** (nouns, actions,
places) and the **abstract lines** (they need a metaphor).

**2.2 One concrete story** — a one-line idea is fine, but hide it in the story; **the audience must
not have to decode it**. Answer **who, where, what happens**; prefer everyday places (a café, a bus
stop, a rented room, a flower shop) over abstract voids (starfields, emptiness, a stage curtain).
2–3 emotional peaks with times. Characters with fixed looks; **one token** — a small object that runs
through the film (a red balloon, a blue butterfly hair clip).

**2.3 One metaphor language** — one system the audience reads at once, for the abstract lines:
game mechanics (HP, GAME OVER, save slots, CONTINUE?), a counter (calendar pages, DAY n, a progress
bar), a physical metaphor ("colour = presence": the ignored person turns grey and transparent; colour
flows back when she comes near). Test: **would a stranger get it without explanation?** If not,
change it. Persistent HUDs are off by default; show them only around key moments, and use chapter
cards for structure.

**2.4 Palette as story** — 4–8 colours per time or mood (memory, present, climax). **Switch on an
emotional peak** (usually the first beat of a chorus). Reserve one highly saturated colour for the token.

**2.5 3–4 core places** — build them with depth, light and detail, and revisit them at different
times and weather (the same alley: rainy night / clearing / dusk). Far better than a new place per line.

✋ **Confirm**: story, characters and token, metaphor, palette, core places, peaks.

---

## Step 3 · One picture per line ✋ → `LYRIC_SHOTS.md` (the key step)

One row per line (by number — never the lyric):

| line | time | gist | picture hook | place | action / face | section |
|---|---|---|---|---|---|---|
| 07 | 0:44.2–0:47.6 | (your own words) | huge scissors snip a luggage strap; little things scatter | delivery room, surgical lamp | the baby reaches out, a "!" pops up | verse 1 |

- **Picture hook**: turn the line's nouns or verbs into **one concrete, fun, instantly readable**
  object or action. Lines that are already pictures: draw them precisely. Abstract lines: use the
  step-2 metaphor.
- **A repeated line gets a new hook.**
- Read top to bottom, the table is one continuous story, not a pile of illustrations.
- Intros, interludes and outros advance the story or recap it.
- At least one **interactive hook** per section (a choice box, a message typed and deleted, a save bar,
  an item pop-up).
- Abstract lines use the one metaphor; concrete lines are told through changes in the place. **No floating
  labels or speech bubbles** (signs, dates and stamps inside the scene are fine — drawing rule 6).

**Self-check**: cover the gist column; do the hooks alone carry the feeling? Guessing every line is
not required — one strong picture per section beats a sticker per line.

✋ **Confirm**: go through it, especially the abstract lines.

---

## Step 4 · Storyboard ✋ → `STORYBOARD.md`

| shot | time | length | line | hook | framing | camera | beat hit | what keeps moving | must be visible |
|---|---|---|---|---|---|---|---|---|---|

- **Two required columns (v4)**: **framing** (wide / medium / close / close-up / insert) and **camera
  move** (push / pull / pan / crane / still). Count the mix when done (rule 10): wide 25–35 %, medium
  35–45 %, close 15–25 %, insert ≥ 10 %; ≥ 50 % of shots move.
- **Cut on phrases**: 5–9 s per shot on average; one or two lines per shot. The chorus may cut every
  2–4 beats but needs at least one long take.
- **Framing**: wide shots only set the place; **the main character's scenes are medium shots**;
  emotional lines get close-ups. Never more than 2 shots in a row at the same framing.
- **Beat hits**: cuts (on the beat where singing starts) and in-shot hits (a light snaps on, an
  object pops on the downbeat).
- **Rhythm**: verses can be dense; choruses need space — at least one ≥ 3 s long take or wide scene.
  One key emotional action per section.
- **Must be visible** and **what keeps moving** for every shot (checked in step 6). A shot with
  nothing moving is not finished.

✋ **Confirm**: rhythm, framing mix, camera moves, where the long takes are.

---

## Step 5 · Style and emotion test ✋ → `STYLE_GUIDE.md` + stills + test clip

**5.1 Pick a style that passes the emotion test**: faces that cry, laugh, blush, look surprised;
bodies that hug, reach, fall. Two render pipelines ship with this repo:

| style | folder | suits | tech |
|---|---|---|---|
| 8bit pixel | `styles/pixel8bit` | nostalgic, game-like, sweet, story songs | numpy + Pillow, 320×180 ×6 |
| flat chibi | `styles/flatq` | everyday, city, upbeat songs | skia vector, 1920×1080 |

Their **characters are parametric starter versions**; per the drawing rules, draw characters and places
for each film and reuse the pipeline, lighting, grading and particles.

Shadow puppets, paper cut and ink wash cannot act emotions; use them only for a film-within-the-film,
memories or transitions. Photorealism cannot be drawn by code and is out of scope.

**5.2 Rules** (in `STYLE_GUIDE.md`): palettes per mood/time, light rules, textures; ≥ 6 expressions
per lead + symbols above heads; three layers per place, ≥ 3 props, something moving; character scale per
rule 13 (wide 10–15 % of frame height, medium ≤ 30 %), with full / half / close-up drawn separately (rule 3).

**5.3 Sheets, stills and test clip**
- ✋ **Character sheet** (v4): every pose of every character (front / side / back / sitting / walking /
  waving / holding hands / hugging) + close-up bust + expressions on one sheet, next to the reference
  film's characters if there is one; go through the body checklist (rule 2). **No building until it passes.**
- **Scene-parts sheet** (v4): each core place's buildings and props on their own — outline + 3 tones +
  material, real parts, everyday objects (rules 5, 6, 9).
- With a reference film: compare the stills item by item (rule 14) and run `richness.py` on the reference
  to set this film's thresholds (rule 11).
- 3–4 key frames, **one complete 5–8 s emotional shot**
with the song. Only start building when the emotion really plays.

✋ **Confirm**: character sheet, scene-parts sheet, the look, the test clip.

---

## Step 6 · Build by chapter

**Light first, then objects**
1. Set the light sources (position, colour, strength) and the ambient light for each place.
2. Draw buildings, people, props.
3. Add glows, reflections, particles.
4. **Composite people after lighting** with a brightness floor (pixel8bit `floor=0.55–0.9`) and a rim
   light so they read in dark scenes (`styles/pixel8bit/stage.py`).

**Light rules**: moody songs are dark by default; every place has at least one visible light with a
glow; skies have ≥ 3 bands; water and glass reflect. **Grey is not sad. Sad is a small warm light in
the dark.** Sweet songs stay bright: light only dusk and night.

**Project layout**
```
projects/<song>/
├─ project.json
├─ work/timing.json        times only, no lyrics
├─ MUSIC_MAP.md  STORY.md  LYRIC_SHOTS.md  STORYBOARD.md  STYLE_GUIDE.md
├─ src/
│  ├─ lf_path.py           puts styles/<style> on the path
│  ├─ common.py            palette, character looks, the core places
│  ├─ ch1.py … chN.py      one file per chapter, one function per shot: s07(t, D)
│  └─ make.py              lists the shots; options in tools/lf_make.py (range, still, 720p, shot list)
└─ out/                    previews, check sheets, final video
```
Copy `templates/starter-pixel8bit/` or `templates/starter-flatq/` (they already render: lighting, character
compositing, sample shots); two finished projects are in `examples/`.

```bash
python src/make.py --still 12.5               # one frame -> out/stills/
python src/make.py --preview --subs           # 720p preview + a lyrics-burned copy for the user
python src/make.py --jobs 4                   # 1080p final -> out/final.mp4
```

**Per chapter**
1. Render a **720p preview** and send it; rework only that chapter if needed.
2. **Burn subtitles into the preview** (`make.py --preview --subs`; previews only, never the final) so the
   user can judge "is this the right picture for this line".
3. **Shot-by-shot check** (before showing any preview): `tools/review/shot_check.py` — the middle frame
   of each shot next to "must be visible"; look at the phone-size version too. Anything written but
   not drawn, or drawn but unreadable, is fixed now.
4. **Drawing check** (v4): look at each middle frame at 100 % — ellipse bodies, line arms, overlapping
   heads, wrong back views, "a building made of lines", a small figure scaled up as a close-up: all get
   reworked. Measure character height against rule 13 while you are there.
5. **Richness check** (v4): `python tools/review/richness.py out/chN.mp4` (add `--ref` with a reference
   film); rework anything marked `LOW` (rule 11).
6. **Polish**: the token, hands, letters get their own pass in close-ups; backgrounds get texture and
   small hand-made details (signs, clutter, laundry), no large flat areas; check the palettes.

**Parallel work**: where sub-agents are available (e.g. Claude Code), split chapters between them once
`STYLE_GUIDE.md` and `common.py` are fixed, then render everything together.

---

## Step 7 · Assemble and check ✋

Render 1080p with the song, then:
```bash
python tools/review/metrics.py out/final.mp4                 # five picture metrics
python tools/review/richness.py out/final.mp4                # v4: detail, colours, texture, light range, camera
python tools/review/contact_sheet.py out/final.mp4           # 20 evenly spaced frames
python tools/review/subtitle_safe.py out/final.mp4 --timing work/timing.json
```
Checklist: [`checklist.md`](checklist.md).

**Metrics are reference values, not pass marks** — measured on a few well-received AI MVs; sweet,
pastel songs naturally sit brighter and less saturated. `look` means "worth a look".

| metric | meaning | reference |
|---|---|---|
| dark frames | mean brightness < 50/255 | moody songs ≥ 30 % (references 36–53 %); ignore for sweet songs |
| saturation | mean | ≥ 0.40 (references ≈ 0.53; pastel styles lower) |
| in-shot motion (median) | change between neighbouring frames inside a shot | ≥ 1.0 (references 1.1–1.9) |
| static seconds | share of seconds that barely move | ≤ 20 % (references 20–23 %) |
| average shot length | cuts detected automatically | 5–9 s, cut on phrases |

✋ **Confirm**: send the first cut, the contact sheet, the metrics and the richness report.

---

## Step 8 · Deliver

- **Video**: the clean version (no subtitles).
- **Lyric version** (optional): `python tools/lyrics_timing/burn_subtitles.py final.mp4 work/lyrics.srt --style pixel`.
  The text comes from the user's .lrc; the AI never touches it. Subtitle style follows the art style
  (pixel: pixel font on a half-transparent box; flatq: Noto Sans SC Bold with a dark outline).
- **Covers**: the best frame + title + credit: 16:9, plus 9:16 / 3:4 for short-video apps
  (`tools/package/make_cover.py`).
- **Credits**: `原唱 · <artist>` ("original artist") in the opening/closing and on the cover; a closing
  line (THANKS FOR WATCHING) in the film's own type.
- **Comparison** (optional, e.g. two AIs made the same song): `tools/package/stack_compare.py top.mp4 bottom.mp4 out.mp4`
  — 1920×2160, one audio track.
- **Post text** (optional): "review with substance" — the method, how it differs from other versions,
  one concrete number (shot count, hours).

---

## Appendix · Where the rules come from

The author compared their own MVs with well-received AI MVs of the same songs (20 evenly spaced frames
each, plus picture metrics):

| metric | theirs: 小镇姑娘 | ours v2 | theirs: 蝴蝶 | ours v2 |
|---|---|---|---|---|
| dark frames | 53 % | 16 % | 36 % | 6 % |
| saturation | 0.54 | 0.43 | 0.53 | 0.29 |
| in-shot motion (median) | 1.9 | 0.5 | 1.1 | 0.8 |
| static seconds | 20 % | 32 % | 23 % | 32 % |
| shots | ≈ 32 | ≈ 70 | ≈ 57 | 72 |

Conclusion: **translating the lyrics into pictures was already fine; light, camera and restraint were
not.** Hence v3: light first, fewer cuts on phrases, constant motion, one metaphor per song, 3–4 core
places revisited.

v3.1: the first v3 test pushed "wide shots, tiny figures, silhouettes" too far — characters 14–40 px
tall, dark people on dark ground, unreadable, worse than before. Fixed by keeping v3's light and long
takes for the places while bringing characters back to medium-shot chibi size, composited after
lighting with a brightness floor. **The main character must always read.**

Earlier (v1 → v2): a shadow-puppet MV with an invented private metaphor had a good idea but the
audience couldn't read it, puppets couldn't act, and storyboard details vanished in the render. That is
why the per-line picture table, the emotion test and the shot-by-shot check exist.

v4: two well-received MVs of the same song were compared shot by shot with our v3 film (a dorm street,
a school building at night, a starry sports ground) and measured with a script (that script is now
`richness.py`):

| metric (one frame every 3 s) | reference A (detailed pixel) | reference B (cinematic, heavy blur) | ours v3 |
|---|---|---|---|
| detail | 8.0 | 4.0 | **3.5** |
| colours | 35 | 35 | **25** |
| textured blocks | 70 % | 49 % | **35 %** |
| light range across the film | 34 | 47 | **12** |
| time zooming | 10 % | 64 % | **9 %** |
| time panning | 14 % | 81 % | **23 %** |

Conclusion: **the gap is not a missing asset kit but the way people and buildings are drawn** — plus a
static camera and flat light. Hence the 14 drawing rules. Two were added while making v4 films:
characters drawn too big (medium shots filling half the frame, the place reduced to wallpaper) → rule
13; copying a reference's canvas size, viewpoint and signature objects until it looked too similar →
rule 14.
