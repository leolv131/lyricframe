"""本片共用：色板、核心场景。Shared by all chapters: palette and the 3–4 core places.

Write each place once, with a time-of-day / weather parameter, and revisit it.
"""
from px import Canvas, W, H, hexc, mix, clamp, ease, lerp, rng
from scenes import sky, roofs, stars, clouds, sun
from light import Light, glow, reflect

# --- palette (lock 4–8 colours per time / mood) -------------------------------------
NIGHT = [hexc('0b0d1c'), hexc('141a33'), hexc('1f2748'), hexc('2c3560')]
DUSK = [hexc('3a2a5a'), hexc('7a3e6a'), hexc('d0616a'), hexc('f3a35e'), hexc('ffd27a')]
DAY = [hexc('8fc8f0'), hexc('a8d8f4'), hexc('c4e6f8'), hexc('e2f3fb')]
TOKEN = hexc('ff3b5c')          # the one saturated colour, reserved for the token


def street(cv, t, tod='night'):
    """Core place #1: a small street with a lamp. tod = night | dusk | day.
    Returns the lights for this time of day."""
    cols = dict(night=NIGHT, dusk=DUSK, day=DAY)[tod]
    sky(cv, cols, 0, 120)
    if tod == 'night':
        stars(cv, t, n=60, y1=90)
    elif tod == 'day':
        clouds(cv, t, 20, [hexc('ffffff'), hexc('eef6fb')], speed=3.0)
    else:
        sun(cv, 240, 104, 14, hexc('ffe6a8'))
    far = hexc('4a5078') if tod != 'day' else hexc('9aa7c4')
    near = hexc('6a6488') if tod != 'day' else hexc('c8b8a8')
    win = hexc('ffd98a') if tod != 'day' else None
    roofs(cv, 104, far, seed=5, off=t * 2, win=win, t=t)   # far layer drifts slowly (parallax)
    roofs(cv, 124, near, seed=9, off=t * 5, win=win, t=t)
    cv.rect(0, 138, W, H - 138, hexc('8a86a0') if tod != 'day' else hexc('b8a890'))   # ground
    cv.rect(0, 138, W, 2, hexc('b0acc4') if tod != 'day' else hexc('d8c8b0'))
    for x in range(-40, W + 40, 34):                                                   # paving lines
        cv.line(x + 160 * 0.2, 140, x * 1.6 - 96, H, hexc('6a6680') if tod != 'day' else hexc('a09078'))
    # lamp post
    cv.rect(206, 58, 2, 82, hexc('1a1824'))
    cv.rect(201, 56, 12, 4, hexc('1a1824'))
    if tod == 'day':
        return []
    return [Light(207, 70, 'ffd9a0', 130, 1.3, flick=0.15)]


def emissive_windows(cv, col=hexc('ffd98a')):
    """Lit windows glow on their own: pass this mask to Stage.light(..., emissive=...)."""
    import numpy as np
    return np.all(cv.a == np.array(col, np.uint8), axis=2)
