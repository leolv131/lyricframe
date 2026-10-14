# pixel8bit · STYLE

规则来自《小镇姑娘》《蝴蝶》《告白气球》几轮重做。Rules learned over several rebuilds.

> v4：下面是 v3.1 时期的画风规则，仍然有效；人物和场景的画法以工作流「造型规范」为准（逐格 / 逐笔画，不拼装）。
> v4: these v3.1 style rules still hold; for how to draw people and places, the workflow's drawing rules win.

## Pixels / 像素
- Move by whole pixels only. "Push in" by drawing a bigger version, never by smooth scaling.
  只按整像素移动；推近靠换更大的画，不做平滑缩放。
- Skies are colour bands with 4×4 ordered dithering. Light is quantised the same way (`light.py`).
- Characters and props get a 1-pixel dark outline.
- 12 fps animation clock for limbs and blinking (`step12`) feels more "8bit" than 30 fps motion;
  camera pans and particles can stay at 30 fps.

## Light / 光（v3）
- Light first, then objects: places in their own colours → `Stage.light()` → glows / particles / text.
- Moody songs: dark base + at least one visible light source with a glow; skies ≥ 3 bands; wet
  ground or glass gets a reflection (`reflect`). Grey is not sad — a small warm light in the dark is.
- Sweet songs: keep daylight bright (`Stage.flat`), light only dusk and night scenes.
- People are composited after lighting with a brightness floor (0.55 day … 0.9 night close-ups)
  and a rim light toward the main source. **The main character must read at phone size.**

## Camera / 镜头
- Cut on phrases: 5–9 s per shot on average. Every shot keeps something moving: ≥ 3 parallax
  layers, rain/snow/petals/fireflies, traffic, flickering windows.
- Wide shots only set the place; the main character's scenes are medium shots (head 24–34 px).
- 3–4 core places, built once with depth and lights, revisited at different times and weather.

## Colour / 颜色
- Lock 4–8 colours per time or mood; switch palettes on emotional peaks.
- One highly saturated colour belongs to the token only (the red balloon, the blue butterfly).
- Grade the scene before drawing UI, so UI keeps its colours.

## Text / 字
- Almost none on screen: title, a few prop words (signs, cards), credits. No lyric subtitles in
  the clean version.
- Keep the bottom 28 canvas pixels (170 px at 1080p) free of faces, hands and the token whenever
  someone is singing — subtitles may be added later.

## Known weak spots / 已知短板
| weak spot | what helps |
|---|---|
| backgrounds look geometric | texture, small hand-made details (signs, laundry, clutter), perspective shots with a vanishing point |
| hands and fists in close-ups | round mitten hands (`ui.mitt`); polish key props separately |
| only chibi proportions | for a more literary song, draw a 1:5 figure set (`light.person` is a start) |
