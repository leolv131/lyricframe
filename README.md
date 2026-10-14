<div align="center">

# LyricFrame · 词帧

**Let an AI write the code that draws your song's music video, frame by frame.**

No video-generation model, no GPU, characters that never change face. Give it a song and its synced
lyrics file; the AI follows a director's workflow learned the hard way — story, one picture per lyric
line, storyboard — then draws every frame in code and puts the original song under it.

**English** · [简体中文](README.zh-CN.md)

![Confession Balloon](media/gaobai.gif) ![Butterfly](media/hudie.gif)

</div>

---

## What it makes

| 《告白气球》 · pixel · a sweet song | 《蝴蝶》 · pixel · light first |
|---|---|
| ![](media/gaobai_sheet.jpg) | ![](media/hudie_sheet.jpg) |
| 38 shots · 3:36 · [example](examples/gaobai-qiqiu) | 42 shots · 4:39 · [example](examples/hudie) |

Full code, story and storyboard for both are in `examples/`. The songs and lyrics are not included
(copyright).

> **Note (v4)**: these two were made with the v3.1 workflow, and their characters are still *assembled*
> by code (circle head, ellipse body, line arms). The workflow is now v4: characters and places are
> *drawn* cell by cell / stroke by stroke — see "Drawing rules" below. Films made the v4 way (a 16-bit
> pixel pipeline) will be added as new examples.

## Three ways to use it

### ① Claude app — no technical skills needed

1. Download `lyricframe-skill.zip` from [Releases](https://github.com/leolv131/lyricframe/releases).
2. In Claude: Settings → Capabilities → turn on code execution; under Skills click **Upload skill**
   and choose the zip.
3. Start a new chat, upload the **song** and its **lyrics file (.lrc)**, and say:

   > Make a music video for this song, pixel style.

Claude checks the story, pictures and style with you step by step, then sends you the video.

### ② Claude Code

```bash
git clone https://github.com/leolv131/lyricframe.git
cd lyricframe
claude
```
Then: "Use this project to make an MV for `~/Music/song.mp3`; the .lrc is next to it."
Claude Code reads `CLAUDE.md` → `AGENTS.md` automatically.

### ③ Codex

Clone and open Codex in the repo (it reads `AGENTS.md`), or unzip `lyricframe-skill.zip` into
`~/.agents/skills/`.
> The rules and taste were tuned on Claude; results on Codex are still being tested.

## What you need

| | |
|---|---|
| 🎵 the song | mp3 / m4a / wav, or a video with sound |
| 📝 a synced lyrics file `.lrc` | search the song on **[lrclib.net](https://lrclib.net)** and download the synced lyrics — free, no account. Without one the AI finds line times by speech recognition (slower). |
| 🎨 a style (optional) | `8bit pixel` or `flat chibi`; otherwise the AI recommends one |

**No song? Try the demo**: `python demo/make_demo_song.py` writes a free 8bit tune, "Paper Plane", with original synced lyrics — post the result anywhere.

By default it makes a **30–60 s clip** (one verse + one chorus) first; the full song once you like it.
A full 4-minute song takes a few hours.

## How it works

```
gather → lyric timing ✋ → story ✋ → one picture per line ✋ → storyboard ✋ → style & emotion test ✋ → build → check ✋ → deliver
```

At each ✋ the AI stops, shows you a picture and asks one question. Say "don't stop, just make it" to
run straight through.

The rules that matter most (from frame-by-frame comparisons with well-received AI MVs):

- **Accurate first, deep second** — every line gets a picture a viewer reads at once; a repeated line gets a new one.
- **Light before objects** — a small warm light in the dark carries more feeling than a grey screen.
- **Fewer cuts, always moving** — cut on phrases; something moves in every shot.
- **One metaphor per song**, 3–4 core places revisited in different light and weather.
- **The main character must always be clearly visible.**
- **(v4) Draw, don't assemble** — every pose, back view and close-up drawn on its own; buildings with
  window frames, AC units, laundry; varied framing and a camera that keeps drifting.
- **(v4) Measure richness** — detail, colour, texture, light range and camera movement, checked by
  `tools/review/richness.py`.

### Drawing rules (v4)

The two shipped styles (`pixel8bit`, `flatq`) provide the render pipeline, lighting, grading, particles
and subtitles; their **characters are parametric starter versions**, fine for quick tests. For a real
film the AI first shows you a **character sheet** (every pose, back view, close-up, expressions) and
only builds once you approve it. The 14 rules: [docs/en/workflow.md › Drawing rules](docs/en/workflow.md#drawing-rules-v4-every-style).

Full workflow: [docs/en/workflow.md](docs/en/workflow.md) · checklist: [docs/en/checklist.md](docs/en/checklist.md)

## What's inside

```
AGENTS.md / CLAUDE.md   the director's manual the AI follows
docs/                   full workflow and checklist (中文 / English)
templates/              story, per-line pictures, storyboard templates + runnable starter projects (one per style)
styles/pixel8bit/       8bit pixel toolkit (render, lighting, places, UI; starter characters) + fonts
styles/flatq/           flat chibi toolkit (skia vector; starter characters) + fonts
tools/lyrics_timing/    .lrc → timing, beats & sections, speech-recognition alignment, subtitle burning
tools/review/           five picture metrics, richness check (v4), contact sheets, shot-by-shot check, subtitle-safe check
tools/package/          covers (landscape / portrait), top-bottom comparison
examples/               two complete projects
demo/                   generates a free demo song with original lyrics
skill/                  packaging as a Claude / Codex skill
```

## Copyright

- **The AI never writes or quotes the lyrics.** Lyric text only moves between your `.lrc` and the
  scripts (for burning subtitles at the end); the AI reads line numbers and times.
- **The song is only for your own video** — don't commit it to a public repo.
- Characters are original; no existing characters, logos or album art.
- When you post the video, follow the platform's music rules.

## FAQ

**Do I need a GPU?** No. Frames are computed with numpy / skia on the CPU — about 1 s of compute per
second of 1080p for the pixel style. With an NVIDIA GPU, `LF_VCODEC=h264_nvenc` speeds up encoding.

**Vertical video?** Yes — ask for portrait / 9:16 at step 0 (1080×1920).

**Other styles?** The workflow is style-independent; a style is just a set of brushes. Watercolour,
chalkboard and letter-paper styles exist in the author's projects and will be added; new styles are
welcome.

**Cost?** Your own Claude / Codex plan. A full MV is a long conversation; on smaller plans start with a clip.

## Thanks

Inspired by [PDoomVideo](https://github.com/JohnHeibel/PDoomVideo) (a picture for every lyric line,
chapters built in parallel), [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) (style library
and director flow), [awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos)
(inspiration) and [opus-video-prompts](https://github.com/joeseesun/opus-video-prompts) (deterministic
`seek(t)` rendering and more).

Fonts: WenQuanYi Zen Hei, GNU Unifont, Noto Sans CJK — licences in `styles/*/fonts/`.

## Author

**吕行记 (Lü Xingji)** — former Huawei AI engineer, six years shipping AI in production. The MVs made
with this workflow are on Douyin.

- Douyin: **吕行记** (ID `994770495`)
- GitHub: [@leolv131](https://github.com/leolv131)

Issues and PRs welcome — and send me the MVs you make with it.

## License

Code: [MIT](LICENSE). Fonts keep their own licences. Songs, lyrics and album art are not part of this project.
