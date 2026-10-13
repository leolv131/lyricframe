"""本片共用：色板和核心场景（flatq）。Shared by all chapters: palette and the core places.

Name it world.py (not common.py): styles/flatq already has toolkit modules on the path.
"""
import math

from fq import *                     # Frame, W, H, INK, C, mixc, lerp, clamp, ease, ...
import people as P
import fq_scenes as S                # clouds, rain, confetti, bubble, coffee, ...

PAL = dict(
    day_sky=('#9fd3f2', '#d8f0fb'), dusk_sky=('#5a4a8a', '#e88a7a', '#ffcf8a'), night_sky=('#141a3a', '#2a2f5a'),
    wall='#f2e6d0', wall_d='#d9c6a8', roof='#d9705a', window='#ffd98a', ground='#c9b79a',
    token='#ff5f7e',                 # the one saturated colour — reserved for the token
)


def street(f, t, tod='day'):
    """Core place #1: a row of small houses. tod = day | dusk | night. Parallax: far row drifts."""
    sky = dict(day=PAL['day_sky'], dusk=PAL['dusk_sky'], night=PAL['night_sky'])[tod]
    f.vgrad(list(sky), 0, 760)
    if tod != 'night':
        for i in range(3):
            S.cloud(f, (300 + i * 650 + t * 18) % 2300 - 200, 150 + 60 * (i % 2), 0.8, '#ffffff', a=0.95)
    else:
        for i in range(40):
            x, y = (i * 397) % W, (i * 211) % 520
            f.circle(x, y, 2.5 + (i % 3), '#fff4d0', a=0.4 + 0.4 * math.sin(t * 2 + i))
    lit = tod != 'day'
    for row, (y0, k, col) in enumerate([(640, 0.35, '#b9a4c8' if lit else '#cfe0ea'), (760, 1.0, PAL['wall'])]):
        off = (t * 40 * k) % 360
        for i in range(-1, 8):
            x = i * 360 - off
            h = 220 + 60 * ((i * 7 + row) % 3)
            f.rect(x, y0 - h, 300, h, col, INK, 5 if row else 0)
            f.poly([(x - 20, y0 - h), (x + 150, y0 - h - 90), (x + 320, y0 - h)], PAL['roof'] if row else '#a98fb8', INK, 5 if row else 0)
            if row:
                for wy in (y0 - h + 50, y0 - h + 140):
                    for wx in (x + 50, x + 180):
                        f.rect(wx, wy, 70, 60, PAL['window'] if lit else '#a8d4ec', INK, 4, r=4)
                        if lit:
                            f.radial(wx + 35, wy + 30, 90, PAL['window'], 0.0, a=0.25)
    f.rect(0, 760, W, H - 760, PAL['ground'], INK, 5)
    lamp_on = tod != 'day'
    f.rect(1500, 420, 14, 340, '#3a3550', INK, 4)
    f.circle(1507, 410, 26, '#ffe6a8' if lamp_on else '#e8e4dc', INK, 5)
    if lamp_on:
        f.radial(1507, 410, 260, '#ffe6a8', 0.0, a=0.45)
