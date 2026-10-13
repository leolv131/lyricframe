# flatq · STYLE

- Outlines 5 px in deep purple-brown `#2b1d2e`; flat fills with one shadow tone; no gradients on
  characters. Backgrounds may use soft vertical gradients and halftone dots.
- Paper grain and a light vignette are applied in `Frame.array()` — keep them on for every frame
  so shots match.
- Big heads (≈ 1:1.3) so faces carry the emotion; close-ups at `s ≥ 1.6`.
- Same light rules as pixel8bit: a visible light source per night scene (`radial` glows), people
  readable at phone size, something always moving (rain, speed lines, traffic, steam, confetti).
- One saturated token colour (in the original film: the pink helmet `#ff8fb0`).
- Text: Noto Sans SC Bold with a dark outline (`text(..., outline=INK)`), only for signs, phone UI,
  titles and credits. Keep the bottom 170 px clear of key elements while someone sings.
- Subtitles for this style: Noto Sans SC Bold + dark outline
  (`tools/lyrics_timing/burn_subtitles.py --style flatq`).
