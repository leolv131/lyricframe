# Step 7 checklist

Go through every item before delivering. The method is after each item.

## Lyrics and pictures
- [ ] Every line has a picture — `LYRIC_SHOTS.md`
- [ ] Repeated lines got new pictures — the repeated rows in the same file
- [ ] With the gist hidden, the hooks alone carry the feeling — look at the `contact_sheet.py` grid
- [ ] One metaphor language for the whole song; very little text on screen (title, prop words, credits)

## Characters
- [ ] **The main character reads in every shot, even at phone size** — `shot_check.py` `_phone.jpg`
- [ ] Faces, hair and clothes stay consistent
- [ ] Emotional shots have expressions (cry, laugh, blush, surprise), not a flat face

## Camera and rhythm
- [ ] Cuts land on beats (singing starts, downbeats) — `line_beats` in `music.json`
- [ ] Cut on phrases, 5–9 s per shot on average; at least one ≥ 3 s long take per chorus
- [ ] Something keeps moving in every shot — `metrics.py` in-shot motion / static seconds
- [ ] Framing varies; never 3 shots in a row with the same composition
- [ ] 3–4 core places come back instead of a new place per line

## Light and colour
- [ ] Every night / dark scene has a visible light with a glow (moody songs); sweet songs stay bright by day
- [ ] Palette switches land on emotional peaks; the token keeps its colour and is the only saturated one
- [ ] No large flat backgrounds; texture and small details

## Subtitle-safe zone
- [ ] While someone sings, the bottom (170 px landscape / 300 px portrait) holds no UI text, faces,
      hand actions or the token — `subtitle_safe.py`, 3 frames per line
- [ ] Move covered elements up, or lift the whole scene by 100–150 px

## Technical
- [ ] No black or skipped frames at transitions
- [ ] Audio and video are the same length; fade in and out
- [ ] 1080p (or 1080×1920 portrait), yuv420p, plays on a phone
- [ ] No lyric text written by the AI anywhere

## Metrics (reference values, not pass marks)
`python tools/review/metrics.py out/final.mp4 --mood moody|bright`; for each `look`, decide whether it is intentional.
