"""8bit backgrounds. Every scene: back / mid / fore layers, at least one moving thing."""
import math
import numpy as np
from px import *

INK = PAL['ink']

# ---------------------------------------------------------------- palettes (<=16 colours per mood)
SUNSET = [hexc(c) for c in ['3b2a5c', '6a3a6e', 'a64a6a', 'e0715a', 'f5a65a', 'ffd27a']]
DUSK_COLD = [hexc(c) for c in ['1e2438', '2c3550', '414d6b', '5f6c88', '8592a8']]
NIGHT = [hexc(c) for c in ['0e0f26', '161a3a', '1f2550', '2a3366']]
DAY = [hexc(c) for c in ['7cc4f0', '9ad4f4', 'bfe4f8']]
STATION_EVE = [hexc(c) for c in ['2b2050', '4a2e6a', '7a3e78', 'c0567a', 'f08a6a', 'ffc07a']]


def sky(cv, cols, y0=0, y1=H, dither=True):
    """Banded vertical gradient with ordered dithering between bands."""
    n = len(cols)
    band = (y1 - y0) / n
    b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
    for y in range(y0, y1):
        f = (y - y0) / band
        i = min(int(f), n - 1); fr = f - i
        c1 = cols[i]; c2 = cols[min(i + 1, n - 1)]
        row = np.empty((W, 3), np.uint8)
        if dither and fr > 0.6 and i < n - 1:
            th = (fr - 0.6) / 0.4
            mask = b[y % 4][np.arange(W) % 4] < th
            row[:] = c1; row[mask] = c2
        else:
            row[:] = c1
        cv.a[y] = row


def sun(cv, x, y, r, c=hexc('ffe39a'), stripes=None):
    cv.ellipse(x, y, r, r, c)
    if stripes:  # retro sunset stripes
        for i, sy in enumerate(range(int(y + r * 0.2), int(y + r), max(2, int(r // 4)))):
            cv.rect(x - r, sy, 2 * r + 1, 1 + i // 2, stripes)


def clouds(cv, t, y, cols, seed=1, speed=2.0, n=4):
    r = rng(seed)
    for i in range(n):
        x = (r.integers(0, W) + t * speed * (0.6 + r.random())) % (W + 60) - 40
        w = r.integers(18, 40)
        yy = y + r.integers(-6, 8)
        cv.rrect(int(x), int(yy), int(w), 5, 2, cols[0])
        cv.rrect(int(x + w * 0.2), int(yy - 3), int(w * 0.5), 5, 2, cols[0])
        cv.rect(int(x) + 2, int(yy) + 4, int(w) - 4, 1, cols[1])


def hills(cv, y, amp, col, seed=0, freq=0.03, off=0.0):
    for x in range(W):
        h = y - (math.sin((x + off) * freq + seed) * amp + math.sin((x + off) * freq * 2.3 + seed * 2) * amp * 0.4)
        cv.rect(x, int(h), 1, H - int(h), col)


def roofs(cv, y, col, seed=3, off=0, win=None, t=0.0):
    r = rng(seed)
    x = -int(off) % 40 - 40
    i = 0
    while x < W + 40:
        w = int(r.integers(16, 30)); h = int(r.integers(8, 20))
        cv.rect(x, y - h, w, h + 40, col)
        # roof line
        cv.rect(x - 1, y - h - 1, w + 2, 1, col)
        if win is not None:
            for wy in range(y - h + 3, y - 2, 5):
                for wx in range(x + 3, x + w - 3, 5):
                    if r.random() < 0.45:
                        flick = (math.sin(t * 2 + wx * 0.7 + wy) > -0.8)
                        cv.rect(wx, wy, 2, 2, win if flick else col)
        x += w + int(r.integers(0, 4)); i += 1


def stars(cv, t, seed=7, n=90, y1=110, cols=None):
    cols = cols or [hexc('fff4c0'), hexc('c8d0ff'), hexc('ffffff')]
    r = rng(seed)
    for i in range(n):
        x, y = int(r.integers(0, W)), int(r.integers(0, y1))
        ph = r.random() * 6.28; sp = 1.5 + r.random() * 3
        v = math.sin(t * sp + ph)
        c = cols[i % len(cols)]
        if v > 0.2:
            cv.px(x, y, c)
            if i % 9 == 0 and v > 0.8:
                cv.px(x - 1, y, c); cv.px(x + 1, y, c); cv.px(x, y - 1, c); cv.px(x, y + 1, c)
        elif v > -0.5:
            cv.px(x, y, mix(c, cv.a[y, x] if 0 <= y < H else c, 0.5))


def rice(cv, y0, t, cols=None, sway=True, seed=4):
    """calm rice field: soft rows with sparse swaying ear highlights"""
    cols = cols or [hexc('6a8a3a'), hexc('8aaa48'), hexc('b8c860'), hexc('e0d070')]
    cv.rect(0, y0, W, H - y0, cols[0])
    r = rng(seed)
    y = y0; row = 0
    while y < H:
        k = (y - y0) / max(1, H - y0)
        gap = 2 + int(k * 4)
        cv.rect(0, y, W, 1, cols[1])
        sp = 7 + int(k * 6)
        for x in range(-(row * 3) % sp, W, sp):
            s = int(round(math.sin(t * 2.0 + x * 0.04 + row * 0.5) * (0.5 + k * 1.5))) if sway else 0
            hgt = 1 + int(k * 3)
            c = cols[2] if (x + row) % 3 else cols[3]
            cv.line(x, y, x + s, y - hgt, c)
        y += gap; row += 1


def wires(cv, y, col, t, birds=0, fly_t=None):
    for x in range(0, W, 1):
        yy = y + int(4 * (1 - ((x % 120) / 60 - 1) ** 2))
        cv.px(x, yy, col)
    for k in range(birds):
        bx = 40 + k * 23
        if fly_t is not None and t > fly_t:
            dt = t - fly_t
            by = y - 2 - int(dt * 40) - k * 3; bx = bx + int(dt * 30)
            wing = math.floor(t * 10 + k) % 2
            cv.px(bx - 1, by - wing, col); cv.px(bx, by, col); cv.px(bx + 1, by - wing, col)
        else:
            cv.rect(bx, y + int(4 * (1 - ((bx % 120) / 60 - 1) ** 2)) - 2, 2, 2, col)


# ---------------------------------------------------------------- props
def pole(cv, x, ytop, ybot, col):
    cv.rect(x, ytop, 2, ybot - ytop, col)
    cv.rect(x - 3, ytop + 2, 8, 1, col)


def crossing(cv, x, ground, t, down, lamp_on, col=INK):
    # post
    cv.rect(x, ground - 34, 3, 34, hexc('3a3a48'))
    # crossbuck
    cv.line(x - 6, ground - 34, x + 8, ground - 26, hexc('f0f0f0')); cv.line(x - 6, ground - 26, x + 8, ground - 34, hexc('f0f0f0'))
    # lamps
    for i, lx in enumerate((x - 5, x + 6)):
        on = lamp_on and ((i + int(t * 4)) % 2 == 0)
        cv.ellipse(lx, ground - 22, 2.5, 2.5, hexc('ff3a3a') if on else hexc('4a1a22'), INK)
    # barrier arm
    L = 46
    a = math.radians(lerp(80, 0, ease(down)))
    x0, y0 = x + 2, ground - 12
    x1, y1 = x0 + math.cos(a) * L, y0 - math.sin(a) * L
    n = 12
    for i in range(n):
        xa = lerp(x0, x1, i / n); ya = lerp(y0, y1, i / n)
        xb = lerp(x0, x1, (i + 1) / n); yb = lerp(y0, y1, (i + 1) / n)
        c = hexc('f4f0e0') if i % 2 == 0 else hexc('e8344a')
        cv.line(xa, ya, xb, yb, c); cv.line(xa, ya + 1, xb, yb + 1, c)


def shop(cv, x, ground, col_wall=hexc('c8b89a'), awning=(hexc('e8344a'), hexc('f4f0e0')), t=0.0, night=False):
    w, h = 64, 46
    cv.rect(x, ground - h, w, h, col_wall)
    cv.rect(x, ground - h, w, 2, INK)
    # sign (pictogram only: bottle + candy)
    cv.rect(x + 8, ground - h + 4, w - 16, 9, hexc('2f5a8a'))
    cv.rect(x + 14, ground - h + 6, 3, 5, hexc('f4f0e0')); cv.rect(x + 15, ground - h + 5, 1, 1, hexc('f4f0e0'))
    cv.ellipse(x + 26, ground - h + 8.5, 2.5, 2.5, hexc('ffd35a')); cv.ellipse(x + 36, ground - h + 8.5, 2.5, 2.5, hexc('ff8a9a')); cv.ellipse(x + 46, ground - h + 8.5, 2.5, 2.5, hexc('8fd8ff'))
    # awning stripes
    for i in range(0, w + 4, 4):
        cv.rect(x - 2 + i, ground - h + 15, 4, 5, awning[(i // 4) % 2])
    for i in range(0, w + 4, 4):
        cv.rect(x - 2 + i, ground - h + 20, 4, 1, awning[0])
    # window/door
    cv.rect(x + 4, ground - 24, 26, 24, hexc('2a3044') if not night else hexc('ffd27a'))
    cv.rect(x + 36, ground - 24, 24, 24, hexc('3a4058'))
    # shelves inside
    for sy in (ground - 20, ground - 13, ground - 6):
        cv.rect(x + 5, sy, 24, 1, hexc('8a6a4a'))
        for k in range(x + 6, x + 28, 3):
            cv.rect(k, sy - 2, 2, 2, [hexc('e8344a'), hexc('ffd35a'), hexc('86c0e6'), hexc('8aaa48')][(k // 3) % 4])
    # fridge outside
    cv.rect(x + w + 2, ground - 16, 12, 16, hexc('d0e8f4')); cv.rect(x + w + 2, ground - 16, 12, 1, INK)
    cv.rect(x + w + 3, ground - 14, 10, 6, hexc('8fc8e8'))
    # crates
    cv.rect(x - 14, ground - 8, 10, 8, hexc('c86a3a')); cv.rect(x - 14, ground - 8, 10, 1, INK)
    for k in range(3): cv.rect(x - 13 + k * 3, ground - 11, 2, 3, hexc('3a7a3a'))


def station_house(cv, x, ground, cols):
    wall, roof, trim, win = cols
    cv.rect(x, ground - 40, 90, 40, wall)
    cv.poly([(x - 8, ground - 40), (x + 98, ground - 40), (x + 86, ground - 54), (x + 4, ground - 54)], roof)
    cv.rect(x - 8, ground - 41, 106, 2, trim)
    for k in range(4):
        cv.rect(x + 8 + k * 20, ground - 30, 12, 14, win)
        cv.rect(x + 8 + k * 20 + 5, ground - 30, 1, 14, trim)
    cv.rect(x + 40, ground - 22, 12, 22, trim)
    # clock
    cv.ellipse(x + 45, ground - 47, 4, 4, hexc('f4f0e0'), INK); cv.px(x + 45, ground - 48, INK); cv.px(x + 46, ground - 47, INK)


def station_sign(cv, x, y, text='小镇站', bg=hexc('f4f0e0'), fg=hexc('2a3366')):
    w = cv.text_w(text) + 10
    cv.rect(x - 1, y - 1, w + 2, 16, INK)
    cv.rect(x, y, w, 14, bg)
    cv.rect(x, y + 11, w, 3, fg)
    cv.text(x + 5, y, text, fg)
    cv.rect(x + 3, y + 15, 2, 14, hexc('5a5a6a')); cv.rect(x + w - 5, y + 15, 2, 14, hexc('5a5a6a'))


def platform(cv, y, cols):
    edge, top, side = cols
    cv.rect(0, y, W, H - y, top)
    cv.rect(0, y, W, 2, edge)
    for x in range(0, W, 8):
        cv.rect(x, y + 2, 4, 1, side)


def rails(cv, y, cols, off=0):
    bed, tie, rail = cols
    cv.rect(0, y, W, 14, bed)
    for x in range(-int(off) % 8 - 8, W, 8):
        cv.rect(x, y + 3, 4, 9, tie)
    cv.rect(0, y + 4, W, 1, rail); cv.rect(0, y + 10, W, 1, rail)


def train(cv, x, ytop, cols, n_cars=4, windows_lit=True, faces=None, t=0.0, head_dir=-1):
    """head_dir=-1: engine on the left. Car = 96 px."""
    body, stripe, roof, win = cols
    for k in range(n_cars):
        cx = x + k * 98
        cv.rect(cx - 1, ytop - 1, 98, 44, INK)
        cv.rect(cx, ytop, 96, 42, body)
        cv.rect(cx, ytop, 96, 4, roof)
        cv.rect(cx, ytop + 30, 96, 4, stripe)
        for wk in range(4):
            wx = cx + 8 + wk * 22
            cv.rect(wx - 1, ytop + 9, 16, 15, INK)
            cv.rect(wx, ytop + 10, 14, 13, win)
            cv.rect(wx, ytop + 10, 14, 2, mix(win, (255, 255, 255), 0.4))
        cv.rect(cx + 2, ytop + 42, 92, 3, INK)
        for wh in (cx + 14, cx + 30, cx + 66, cx + 82):
            cv.ellipse(wh, ytop + 45, 4, 4, hexc('2a2a34'), INK)
    # engine nose
    nx = x - 14 if head_dir < 0 else x + n_cars * 98 - 2
    cv.rect(nx, ytop + 8, 16, 34, body); cv.rect(nx, ytop + 30, 16, 4, stripe)
    lamp = nx + (3 if head_dir < 0 else 10)
    cv.ellipse(lamp, ytop + 20, 2.5, 2.5, hexc('fff4c0'), INK)


def light_cone(cv, x, y, w, col, k=0.35):
    """additive-ish dither cone from a lamp at (x,y) downward"""
    m = np.zeros((H, W), bool)
    b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
    for yy in range(int(y), H):
        hw = (yy - y) * w
        x0, x1 = int(x - hw), int(x + hw)
        lvl = int(16 * k * (1 - (yy - y) / (H - y + 1)))
        for xx in range(max(0, x0), min(W, x1)):
            if b[yy % 4][xx % 4] < lvl: m[yy, xx] = True
    cv.a[m] = (cv.a[m] * 0.5 + np.array(col) * 0.5).astype(np.uint8)
