"""8bit 工具包 · 通用 UI、特效、道具（从《小镇姑娘》练手中提炼）"""
import math
import numpy as np
from PIL import Image, ImageDraw
from px import *
from px import ell_mask, rrect_mask, dilate
from chars import char, head, symbol, outline_poly, thick_line

INK = PAL['ink']

def tie(cv, x, y, s=1):
    """red hair tie (scrunchie): ring of bumps when big"""
    if s < 3:
        cv.ellipse(x, y, 4 * s, 3 * s, PAL['red'], INK)
        cv.ellipse(x, y, 2 * s, 1 * s, PAL['red_d'])
        cv.px(x - 2 * s, y - 2 * s, PAL['pink']); cv.px(x - 2 * s + 1, y - 2 * s, PAL['pink'])
        return
    R = 4.2 * s; rb = 1.6 * s
    n = 12
    for i in range(n):  # outline pass
        a = i / n * 6.283
        cv.ellipse(x + math.cos(a) * R, y + math.sin(a) * R * 0.75, rb + 1, rb + 1, INK)
    for i in range(n):
        a = i / n * 6.283
        bx, by = x + math.cos(a) * R, y + math.sin(a) * R * 0.75
        cv.ellipse(bx, by, rb, rb, PAL['red'] if i % 2 else hexc('d82a42'))
        cv.px(bx - rb * 0.4, by - rb * 0.5, PAL['pink'])
    cv.ellipse(x, y, R - rb - 1, (R - rb - 1) * 0.75, hexc('3a3048'))


def big_hand(cv, x, y, sleeve, holding=None, s=1.5):
    """A large hand reaching up; (x,y)= wrist."""
    sw = int(18 * s)
    cv.rect(x - sw // 2 - 1, y, sw + 2, H - y, INK); cv.rect(x - sw // 2, y + 1, sw, H - y, sleeve)
    cv.rect(x - sw // 2, y + 1, sw, 2, mix(sleeve, INK, 0.25))
    pw, ph = int(16 * s), int(12 * s)
    cv.rrect(x - pw // 2, y - ph, pw, ph + 1, int(5 * s), PAL['skin'], INK)
    fw = int(2 * s); fh = int(6 * s)
    for i in range(4):
        fx = x - pw // 2 + 1 + i * (pw - 2) // 4
        cv.rect(fx - 1, y - ph - fh - 1, fw + 2, fh + 3, INK)
        cv.rect(fx, y - ph - fh, fw, fh + 2, PAL['skin'])
    cv.rect(x - pw // 2 - int(5 * s), y - int(9 * s), int(6 * s), int(4 * s), INK)
    cv.rect(x - pw // 2 - int(4 * s), y - int(8 * s), int(5 * s), int(2 * s), PAL['skin'])
    if holding == 'tie':
        tie(cv, x, y - ph // 2 - 2, 2)


def dialog(cv, x, y, w, h, text, cursor=True, t=0.0, tail=None):
    cv.rect(x - 2, y - 2, w + 4, h + 4, INK)
    cv.rect(x - 1, y - 1, w + 2, h + 2, PAL['white'])
    cv.rect(x, y, w, h, hexc('1e2240'))
    if tail:
        tx, ty = tail
        for i in range(6):
            cv.rect(tx - i // 2, y + h + 1 + i, 3 - i // 3, 1, PAL['white'])
    cx = draw_text_dots(cv, x + 6, y + 4, text, PAL['white'])
    if cursor and int(t * 4) % 2 == 0:
        cv.rect(cx + 1, y + 6, 2, 13, PAL['gold'])


def draw_text_dots(cv, x, y, text, col, font=FONT16):
    """FONT16 text, but '…' drawn as three chunky 2x2 dots. Returns end x."""
    for ch in text:
        if ch == '…':
            for k in range(3): cv.rect(x + 1 + k * 5, y + 11, 3, 3, col)
            x += 15
        else:
            cv.text(x, y, ch, col, font=font); x += cv.text_w(ch, font)
    return x


def text_mask(s, font=FONT16, scale=2):
    w = int(font.getlength(s)) + 2; h = font.size + 4
    im = Image.new('1', (w, h), 0); d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, 0), s, font=font, fill=1)
    m = np.array(im)
    ys, xs = np.nonzero(m)
    m = m[:ys.max() + 1, :xs.max() + 1]
    return np.repeat(np.repeat(m, scale, 0), scale, 1)


def ui_box(cv, x, y, w, h):
    cv.rect(x - 2, y - 2, w + 4, h + 4, INK)
    cv.rect(x - 1, y - 1, w + 2, h + 2, PAL['white'])
    cv.rect(x, y, w, h, hexc('1e2240'))


def load_ui(cv, t, prog, x=88, y=12):
    ui_box(cv, x, y, 144, 30)
    cv.text(x + 6, y + 3, '读取存档：1999 · 夏', PAL['white'])
    cv.rect(x + 6, y + 18, 132, 7, INK); cv.rect(x + 7, y + 19, 130, 5, hexc('2a2e50'))
    n = int(130 * clamp(prog))
    for i in range(0, n, 6): cv.rect(x + 7 + i, y + 19, min(5, n - i), 5, PAL['gold'])


def mitt(cv, x, y, d, sleeve, frm, wrist_tie=False, over=False):
    """chibi mitten hand at (x,y) with sleeve coming from point frm; d=+1 points right."""
    thick_line(cv, frm[0], frm[1], x - d * 12, y + 4, 26, sleeve, INK)
    # cuff
    if wrist_tie:
        thick_line(cv, x - d * 14, y + 4, x - d * 9, y + 3, 22, PAL['red'], INK)
        cv.rect(x - d * 12 - 2, y - 6, 2, 2, PAL['pink'])
    cv.ellipse(x + d * 4, y, 17, 13, PAL['skin'], INK)
    # thumb on top
    cv.ellipse(x - d * 2, y - 12, 6, 5, PAL['skin'], INK)
    cv.ellipse(x + d * 4, y, 16, 12, PAL['skin'])
    cv.ellipse(x - d * 2, y - 11, 5, 4, PAL['skin'])
    # finger creases
    for k in range(3):
        cv.rect(x + d * 13, y - 5 + k * 5, d * 6 if d > 0 else 6, 1, PAL['skin_d']) if d > 0 else cv.rect(x - 18, y - 5 + k * 5, 6, 1, PAL['skin_d'])


def tin_box(cv, x, y, w, h, open_=True, big=False):
    lid_c, box_c = hexc('8a9aa8'), hexc('6a7a8a')
    cv.rect(x - 1, y - 1, w + 2, h + 2, INK); cv.rect(x, y, w, h, box_c)
    cv.rect(x, y, w, 2, mix(box_c, (255, 255, 255), 0.3))
    if big:  # inside
        cv.rect(x + 3, y + 3, w - 6, h - 6, hexc('3a3048'))
        # old photo + marble + letter
        cv.rect(x + 8, y + 8, 30, 22, PAL['cream']); cv.rect(x + 10, y + 10, 26, 16, hexc('e0a070'))
        cv.rect(x + 16, y + 16, 4, 8, PAL['white']); cv.rect(x + 24, y + 16, 4, 8, PAL['dress'])
        cv.ellipse(x + w - 14, y + h - 12, 4, 4, hexc('8fd8ff'), INK)
    if open_:
        cv.poly([(x, y), (x + w, y), (x + w + 4, y - h * 0.6), (x + 4, y - h * 0.6)], INK)
        cv.poly([(x + 1, y - 1), (x + w - 1, y - 1), (x + w + 3, y - h * 0.6 + 1), (x + 5, y - h * 0.6 + 1)], lid_c)


def big_eye(cv, cx, cy, w, h, t, left=True, closed=False, meteor=None):
    if closed:
        for i in range(w + 6):
            x = cx - w // 2 - 3 + i
            yy = cy + 6 + int(4 * math.sin(math.pi * i / (w + 6)))
            cv.rect(x, yy, 1, 4, INK)
        return
    m = ell_mask(w / 2, h / 2)
    cv.mask_fill(m, INK, cx - w // 2, cy - h // 2)
    iw, ih = w - 8, h - 10
    im = ell_mask(iw / 2, ih / 2)
    ix, iy = cx - iw // 2, cy - ih // 2 + 3
    # iris: night-sky gradient
    for j in range(ih):
        c = mix(hexc('1a1a48'), hexc('4a3a7a'), j / ih)
        row = im[j]
        cv.a[iy + j, ix:ix + iw][row] = c
    # stars inside iris
    r = rng(31 if left else 37)
    for i in range(18):
        sx = ix + int(r.integers(3, iw - 3)); sy = iy + int(r.integers(3, ih - 3))
        if not im[sy - iy, sx - ix]: continue
        v = math.sin(t * (2 + r.random() * 3) + i)
        if v > -0.2:
            cv.px(sx, sy, hexc('fff4c0'))
            if v > 0.85: cv.px(sx - 1, sy, hexc('fff4c0')); cv.px(sx + 1, sy, hexc('fff4c0')); cv.px(sx, sy - 1, hexc('fff4c0')); cv.px(sx, sy + 1, hexc('fff4c0'))
    # pupil
    cv.ellipse(cx, cy + 6, iw * 0.18, ih * 0.16, hexc('0e0c20'))
    # meteor streak across iris
    if meteor is not None and 0 <= meteor <= 1:
        mx = int(ix + iw * (1.1 - meteor * 1.3)); my = int(iy + ih * (0.2 + meteor * 0.5))
        for k in range(10):
            xx, yy = mx + k, my - k // 2
            if 0 <= yy - iy < ih and 0 <= xx - ix < iw and im[yy - iy, xx - ix]:
                cv.px(xx, yy, mix(hexc('ffffff'), hexc('4a3a7a'), k / 10))
    # highlights
    cv.rrect(cx + iw // 2 - 14, iy + 4, 9, 9, 3, PAL['white'])
    cv.rect(cx - iw // 2 + 5, iy + ih - 10, 4, 4, PAL['white'])
    # lashes: thick top line + outer flicks
    cv.rect(cx - w // 2 + 6, cy - h // 2 - 2, w - 12, 5, INK)
    sgn = -1 if left else 1
    ox = cx + sgn * (w // 2 + 2)
    for k in range(3):
        cv.rect(ox + sgn * k * 3 - (2 if sgn < 0 else 0), cy - h // 2 - 5 - k * 3, 3, 3, INK)
    # lower lash hint
    cv.rect(cx - w // 2 + 4, cy + h // 2, w - 8, 1, PAL['skin_d'])


def bicycle(cv, x, ground, t, moving):
    wr = 9
    rot = t * 12 if moving else 0
    for wx in (x - 14, x + 14):
        cv.ellipse(wx, ground - wr, wr, wr, INK)
        cv.ellipse(wx, ground - wr, wr - 2, wr - 2, hexc('c8d0d8'))
        cv.ellipse(wx, ground - wr, wr - 3, wr - 3, (0, 0, 0))
        cv.a[cv.a.sum(2) == 0] = PAL['cream']
        for k in range(3):
            a = rot + k * 2.09
            cv.line(wx, ground - wr, wx + math.cos(a) * (wr - 3), ground - wr + math.sin(a) * (wr - 3), hexc('8a8a9a'))
    fc = hexc('2f6a5a')
    cv.line(x - 14, ground - wr, x, ground - wr - 2, fc); cv.line(x, ground - wr - 2, x + 10, ground - 22, fc)
    cv.line(x - 14, ground - wr, x - 4, ground - 22, fc); cv.line(x - 4, ground - 22, x + 10, ground - 22, fc)
    cv.line(x + 14, ground - wr, x + 10, ground - 26, fc)
    cv.rect(x + 7, ground - 28, 8, 2, INK)  # handlebar
    cv.rect(x - 7, ground - 24, 6, 2, INK)  # seat
    # bell
    cv.ellipse(x + 14, ground - 30, 2, 2, PAL['gold'], INK)
    # mail bag
    cv.rect(x - 22, ground - 26, 9, 9, INK); cv.rect(x - 21, ground - 25, 7, 7, hexc('8a6a3a'))


def rays(cv, cx, cy, t, c1, c2, n=16):
    a0 = t * 0.6
    from PIL import Image, ImageDraw
    im = Image.new('1', (W, H), 0); d = ImageDraw.Draw(im)
    for i in range(n):
        a = a0 + i * 2 * math.pi / n
        a2 = a + math.pi / n
        d.polygon([(cx, cy), (cx + math.cos(a) * 400, cy + math.sin(a) * 400), (cx + math.cos(a2) * 400, cy + math.sin(a2) * 400)], fill=1)
    m = np.array(im)
    cv.a[:] = c2; cv.a[m] = c1


def popup(cv, t, x, y, w, h, title, item, icon_fn=None):
    k = clamp(t / 0.12)
    hh = max(2, int(h * k)); yy = y + (h - hh) // 2
    ui_box(cv, x, yy, w, hh)
    if k >= 1:
        cv.text(x + 6, y + 4, title, PAL['gold'])
        cv.text(x + 6, y + 19, item, PAL['white'])
        if icon_fn: icon_fn(cv, x + w - 22, y + 8)


def icon_notice(cv, x, y):
    cv.rect(x - 1, y - 1, 16, 20, INK); cv.rect(x, y, 14, 18, PAL['cream'])
    for k in range(4): cv.rect(x + 2, y + 3 + k * 3, 10, 1, hexc('8a8a9a'))
    cv.ellipse(x + 10, y + 14, 3, 3, PAL['red'], INK)


def glitch(cv, level, t, seed=0):
    if level <= 0: return
    r = rng(int(t * 24) + seed)
    a = cv.a
    # horizontal slice displacement
    for _ in range(level * 4):
        y0 = int(r.integers(0, H - 4)); h = int(r.integers(2, 4 + level * 3)); dx = int(r.integers(-level * 6, level * 6 + 1))
        a[y0:y0 + h] = np.roll(a[y0:y0 + h], dx, axis=1)
    # channel shift
    if level >= 2:
        a[:, :, 0] = np.roll(a[:, :, 0], level, axis=1)
        a[:, :, 2] = np.roll(a[:, :, 2], -level, axis=1)
    # colour blocks
    for _ in range(level * 2 - 1):
        bx, by = int(r.integers(0, W - 20)), int(r.integers(0, H - 8))
        cv.rect(bx, by, int(r.integers(8, 30)), int(r.integers(2, 8)), [hexc('ff3a6a'), hexc('3affd0'), hexc('ffffff'), hexc('1a1426')][int(r.integers(0, 4))])
    # scanlines
    if level >= 3:
        a[::2] = (a[::2] * 0.75).astype(np.uint8)


def confetti(cv, t, seed=3, n=40, cols=None):
    cols = cols or [PAL['red'], PAL['gold'], hexc('86c0e6'), hexc('8aba5a'), PAL['pink']]
    r = rng(seed)
    for i in range(n):
        x0 = r.integers(0, W); sp = 30 + r.random() * 40; ph = r.random() * 5
        y = int((t * sp + r.integers(-60, 0)) % (H + 20)) - 10
        x = int(x0 + math.sin(t * 4 + ph) * 4)
        c = cols[i % len(cols)]
        if int(t * 10 + i) % 2: cv.rect(x, y, 2, 1, c)
        else: cv.rect(x, y, 1, 2, c)


def rain_cloud(cv, x, y, t, rain=True):
    for dx, r_ in ((-10, 8), (0, 11), (11, 8)):
        cv.ellipse(x + dx, y, r_, r_ * 0.8, INK)
    for dx, r_ in ((-10, 7), (0, 10), (11, 7)):
        cv.ellipse(x + dx, y, r_, r_ * 0.8 - 1, hexc('7a8098'))
    cv.rect(x - 16, y + 3, 32, 2, hexc('5a6078'))
    if rain:
        for i in range(10):
            rx = x - 14 + (i * 7) % 30
            ry = y + 8 + int((t * 90 + i * 13) % 34)
            cv.rect(rx, ry, 1, 3, PAL['tear'])

