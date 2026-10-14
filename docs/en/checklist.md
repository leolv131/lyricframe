# Step 7 checklist

Go through every item before delivering. The method is after each item.

## Lyrics and pictures
- [ ] Every line has a picture — `LYRIC_SHOTS.md`
- [ ] Repeated lines got new pictures — the repeated rows in the same file
- [ ] With the gist hidden, the hooks alone carry the feeling — look at the `contact_sheet.py` grid
- [ ] One metaphor language for the whole song; no floating labels or speech bubbles (signs, dates, numbers inside the scene are fine)

## Characters
- [ ] **The main character reads in every shot, even at phone size** — `shot_check.py` `_phone.jpg`
- [ ] Faces, hair and clothes stay consistent
- [ ] Emotional shots have expressions (cry, laugh, blush, surprise), not a flat face
- [ ] (v4) **Drawing**: no ellipse bodies, line arms or overlapping heads; back views drawn on their own;
      close-ups are purpose-drawn busts, not scaled-up figures — look at middle frames at 100 %
- [ ] (v4) Character height: wide 10–15 % of the frame, medium ≤ 30 % — measure on the `shot_check.py` sheet

## Camera and rhythm
- [ ] Cuts land on beats (singing starts, downbeats) — `line_beats` in `music.json`
- [ ] Cut on phrases, 5–9 s per shot on average; at least one ≥ 3 s long take per chorus
- [ ] Something keeps moving in every shot — `metrics.py` in-shot motion / static seconds
- [ ] (v4) Framing mix: wide 25–35 %, medium 35–45 %, close 15–25 %, insert ≥ 10 %; never more than 2 in a row
      at the same framing — count `STORYBOARD.md`
- [ ] (v4) ≥ 50 % of shots have a slow push/pull, pan or crane
- [ ] 3–4 core places come back instead of a new place per line

## Light and colour
- [ ] Every night / dark scene has a visible light with a glow (moody songs); sweet songs stay bright by day
- [ ] Palette switches land on emotional peaks; the token keeps its colour and is the only saturated one
- [ ] No large flat backgrounds; texture and small details
- [ ] (v4) Buildings have material and at least 5 kinds of parts; at least 2 recognisable everyday objects per
      place; foreground / midground / background all have content

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

## Richness (v4, rule 11)
`python tools/review/richness.py out/final.mp4` (add `--ref reference.mp4` with a reference film). Defaults:
detail ≥ 5, colours ≥ 30, textured blocks ≥ 50 %, light range ≥ 25, camera zoom + pan ≥ 50 %; with a
reference, the higher value wins. Rework anything marked `LOW`.
