# flatq · 扁平 Q 版工具包

1920×1080 矢量画面（skia），描边 + 扁平色 + 纸张颗粒 + 网点。适合日常、城市、轻快的歌。
Flat vector chibi style at 1920×1080 with skia: outlines, flat fills, paper grain, halftone.

Built for a Henan road-trip song (an electric bike, a pink helmet, a map of 18 cities); the
props and scene parts from that film are kept in `fq_scenes.py` / `props.py` as examples.

## Files / 文件

| file | what's in it |
|---|---|
| `fq.py` | `Frame` (rect, circle, oval, line, poly, curve, blob, vgrad, radial, text, push/pop camera, `array()` with grain + vignette), colours `C`, `mixc`, easing, `halftone`, bundled Noto Sans SC |
| `people.py` | characters `draw(f, who, x, feet, s, pose, expr, t)`, `head(...)`, `symbol(...)`; `who`: `he` `he_work` `she` `npc` |
| `props.py` | phone status bar, helmet, noodle bowl, e-bike, skyline, road, street lamps, room, table, stool, big hand, road sign, sunburst |
| `fq_scenes.py` | phone frame, photo, clouds, sheep, rain, speed lines, speech bubble, confetti, traffic light, zebra crossing, night market, office, coffee, a province map with city icons, highway scenes |
| `render.py` | `render(timeline, t0, t1, out, song=None, fade_in, fade_out, scale)` — shot functions are `fn(t, dur) -> Frame` |
| `sample.py` | a 4-shot emotional test clip (night, a bowl of noodles, riding alone) |
| `fonts/` | Noto Sans SC Bold / Black, subset to GB2312 + Latin + symbols (SIL OFL) |

- poses: `stand wave cheer reach chest eat sit ride hug_back arms_open peace shrug cover_ears walk`
- expressions: `normal smile happy grin shy peek surprise scared smug stunned cold sad lonely teary cry tired insomnia money determined blow love`
- `s=1` → head 160 px (medium shot); full body ≈ 380 px.

```python
import sys; sys.path.insert(0, 'styles/flatq')
from fq import *
import people as P
from render import render

def s01(t, dur):
    f = Frame('#2a2f55')
    f.vgrad(['#2a2f55', '#4a4f8a'], 0, 700)
    f.rect(0, 760, W, 320, '#3a3b52', line=None)
    P.draw(f, 'she', 900 + t * 60, 900, 1.0, 'walk', 'smile', t=t)
    return f

render([(0, 4, s01)], 0, 4, 'out.mp4')
```

Speed: skia is slower than pixel8bit (≈ 3–6 s of compute per second of 1080p on 2 cores); render
720p previews with `scale=0.667`.

Rules: [`STYLE.md`](STYLE.md).

A starting project that already renders: [`templates/starter-flatq/`](../../templates/starter-flatq/).
