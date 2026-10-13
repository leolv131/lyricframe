# pixel8bit · 8bit 像素工具包

320×180 的像素画布，最近邻放大 6 倍输出 1920×1080，30fps。Python + numpy + Pillow，不需要显卡。
A 320×180 pixel canvas upscaled ×6 to 1920×1080. Python + numpy + Pillow, no GPU.

Used for: 《告白气球》, 《蝴蝶》 (see `examples/`). Rendering ≈ 1 s of 1080p per second of video on 2 cores.

## Files / 文件

| file | what's in it |
|---|---|
| `px.py` | `Canvas` (rect, ellipse, rrect, poly, line, sprite, pixel text, darken, tint, blit), palette `PAL`, `hexc`, `mix`, `ease`, bundled fonts `FONT12` / `FONT16` / `font(size)` |
| `chars.py` | chibi characters: `char(cv, who, cx, feet, Hh, pose, expr, t)`, `head(...)` for close-ups, `symbol(cv, kind, x, y, t)` (heart, q, excl, note, sparkle, sweat) |
| `stage.py` | **light first, then people**: `Stage().person(...)`, `.face(...)`, `.light(cv, lights, ambient, t)`, `.flat(cv)` |
| `light.py` | `Light(x, y, col, r, i, flick)`, `lightmap`, `lit`, `glow`, `reflect` (wet ground), `rim` (rim light), `sky`, `skyline`, `rain`, `fireflies`, `mist`, `umbrella` |
| `scenes.py` | skies with dithered bands, sun, clouds, hills, roofs, stars, rice fields, wires, level crossing, shop, station, platform, rails, train, light cone |
| `ui.py` | game-style UI and effects: typed dialog box, item pop-up, loading bar, rays, glitch, confetti, rain cloud; props: big hand, mitt, tin box, bicycle, big eye |
| `hd.py` | colour grading to a ramp (`grade`, `to_ramp`, `radial_keep`), "ghost" half-visible person, rain, umbrella, buildings, puddles, bricks, broken wall, `title_text`, `staff` credits, butterfly + trail |
| `lib.py` | more places and props from 《蝴蝶》: street, ruins, room, alley, rooftop, flower shop, seedling, cardboard box, phone, snow, scarf, labels, stamps, speech bubbles |
| `render.py` | `render(timeline, t0, t1, out, song=..., scale=6, srt=None)`, `frame_at(timeline, T)` |
| `example.py` | minimal two-shot example |
| `fonts/` | WenQuanYi Zen Hei + GNU Unifont, subset to GB2312 + Latin + symbols (licences inside) |

A complete starting project that already renders is in [`templates/starter-pixel8bit/`](../../templates/starter-pixel8bit/).

## Characters / 角色

- `who`: `boy` `girl` `man` `woman` `kid` `he` `she` `npc` `npc_g` `post` (+ the two leads of 《蝴蝶》: `wu`, `die`). Add your own by copying an entry in `chars.LOOK` (hair style, top, bottom, dress/coat).
- poses: `stand walk run jump sit wave clap hold_l hold_r give take reach cheer hand_chest arms_down`
- expressions: `normal smile happy joy shy peek wonder surprise stunned forced sad hesitate swallow cry look_up wave_smile`, or a dict (`eyes`, `mouth`, `brow`, `blush`, `tear`, `wet`, `look`).
- sizes (head height `Hh`): wide 14 · medium 24–34 · close 44 · extreme close ≥ 36 (fine eyes, highlights, tears switch on automatically).

## Minimal shot / 最小镜头

```python
import lf_path                      # puts this folder on sys.path
from px import *
from scenes import sky, roofs
from light import Light, glow
from stage import Stage
from render import render

def s01(t, D):   # 0.00–5.00 夜里的街，她走过来
    cv = Canvas()
    st = Stage()
    sky(cv, [hexc('0b0d1c'), hexc('1f2748')], 0, 120)
    roofs(cv, 120, hexc('4a5078'), off=t * 3)
    cv.rect(0, 138, W, 42, hexc('8a86a0'))
    st.person('girl', 60 + t * 14, 150, 26, 'walk', 'smile', t=t)
    st.light(cv, [Light(207, 70, 'ffd9a0', 130, 1.2)], ambient=(0.3, 0.32, 0.5), t=t)
    glow(cv, 207, 62, 20, 'ffd9a0')
    return cv

TL = [(0, 5, lambda t: s01(t, 5))]
render(TL, 0, 5, 'out.mp4')        # add song='song.mp3' to mux the same range of the song
```

## Rules of the style / 画风规则

See [`STYLE.md`](STYLE.md).
