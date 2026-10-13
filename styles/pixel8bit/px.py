"""8bit 像素画布 / pixel canvas — 320x180 internal, x6 nearest upscale to 1920x1080.

Every frame is a pure function of time t (seek(t) deterministic rendering).
Fonts are bundled in ./fonts (subsets: GB2312 + Latin + symbols of WenQuanYi Zen Hei and GNU Unifont).
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 320, 180
SCALE = 6

def hexc(h):
    if not isinstance(h, str): return tuple(int(v) for v in h)
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# ---------------------------------------------------------------- palette
PAL = {k: hexc(v) for k, v in {
    'ink': '1a1426', 'ink2': '2b2238', 'white': 'f6f2e6', 'cream': 'efe2c4',
    'red': 'e8344a', 'red_d': 'a8213a', 'pink': 'ff8a9a', 'blush': 'ff6f86',
    'skin': 'f4c6a0', 'skin_d': 'd9987a', 'hair': '2a2233', 'hair_h': '4a3c58',
    'shirt': 'f4f1e8', 'shirt_d': 'c6c3d8', 'pants': '35407a', 'pants_d': '252d5a',
    'dress': '86c0e6', 'dress_d': '5e94c8', 'shoe': 'f0ece0',
    'coat': '3d4560', 'coat_d': '2a3046', 'bag': '8a5a3a', 'gold': 'ffd35a', 'gold_d': 'e0a030',
    'tear': '8fd8ff',
}.items()}

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
ZH_FONT = os.path.join(FONT_DIR, 'wqy-zenhei.ttf')          # proportional, any size
ZH_MONO = os.path.join(FONT_DIR, 'wqy-zenhei-mono.ttf')     # 12px bitmap strike
UNIFONT = os.path.join(FONT_DIR, 'unifont.otf')             # 16px pixel font


def font(size=12, path=None):
    """Load a bundled font. 加载自带字体（GB2312 常用字 + 拉丁字母 + 符号；生僻字请换成完整字体文件）。"""
    return ImageFont.truetype(path or ZH_FONT, size)


FONT12 = ImageFont.truetype(ZH_MONO, 12)
FONT16 = ImageFont.truetype(UNIFONT, 16)


class Canvas:
    def __init__(self, bg=(0, 0, 0)):
        self.a = np.zeros((H, W, 3), np.uint8)
        self.a[:] = bg

    # ---- basic
    def px(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H: self.a[y, x] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(W, int(x + w)), min(H, int(y + h))
        if x1 > x0 and y1 > y0: self.a[y0:y1, x0:x1] = c

    def hline(self, x0, x1, y, c): self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, c)
    def vline(self, x, y0, y1, c): self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, c)

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy

    def mask_fill(self, m, c, ox=0, oy=0):
        """m: bool array; paste at ox,oy"""
        h, w = m.shape
        x0, y0 = int(ox), int(oy)
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = min(w, W - x0), min(h, H - y0)
        if sx1 <= sx0 or sy1 <= sy0: return
        sub = self.a[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
        sub[m[sy0:sy1, sx0:sx1]] = c

    def ellipse(self, cx, cy, rx, ry, c, outline=None):
        m = ell_mask(rx, ry)
        ox, oy = int(round(cx - m.shape[1] / 2)), int(round(cy - m.shape[0] / 2))
        if outline is not None:
            self.mask_fill(dilate(m), outline, ox - 1, oy - 1)
        self.mask_fill(m, c, ox, oy)

    def rrect(self, x, y, w, h, r, c, outline=None):
        m = rrect_mask(w, h, r)
        if outline is not None:
            self.mask_fill(dilate(m), outline, x - 1, y - 1)
        self.mask_fill(m, c, x, y)

    def poly(self, pts, c):
        im = Image.new('1', (W, H), 0)
        ImageDraw.Draw(im).polygon([(int(a), int(b)) for a, b in pts], fill=1)
        self.a[np.array(im)] = c

    def sprite(self, rows, pal, x, y, flip=False):
        for j, row in enumerate(rows):
            if flip: row = row[::-1]
            for i, ch in enumerate(row):
                if ch != '.' and ch in pal: self.px(x + i, y + j, pal[ch])

    def text(self, x, y, s, c, font=FONT12, outline=None, anchor=None):
        im = Image.new('1', (W, H), 0)
        d = ImageDraw.Draw(im); d.fontmode = '1'
        d.text((int(x), int(y)), s, font=font, fill=1, anchor=anchor)
        m = np.array(im)
        if outline is not None:
            self.a[dilate(m, 1)] = outline
        self.a[m] = c

    def text_w(self, s, font=FONT12):
        return int(font.getlength(s))

    # ---- effects
    def darken(self, k):
        self.a[:] = (self.a.astype(np.float32) * k).clip(0, 255).astype(np.uint8)

    def tint(self, c, k):
        self.a[:] = (self.a * (1 - k) + np.array(c) * k).clip(0, 255).astype(np.uint8)

    def shift(self, dx, dy):
        self.a = np.roll(np.roll(self.a, int(dy), 0), int(dx), 1)

    def blit(self, other, x=0, y=0, key=None):
        src = other.a if isinstance(other, Canvas) else other
        h, w = src.shape[:2]
        x0, y0 = int(x), int(y)
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = min(w, W - x0), min(h, H - y0)
        if sx1 <= sx0 or sy1 <= sy0: return
        s = src[sy0:sy1, sx0:sx1]
        dst = self.a[y0 + sy0:y0 + sy1, x0 + sx0:x0 + sx1]
        if key is None: dst[:] = s
        else:
            m = np.any(s != key, axis=2); dst[m] = s[m]

    def quantize(self, levels=None):
        pass

    def out(self):
        return np.repeat(np.repeat(self.a, SCALE, 0), SCALE, 1)

    def save(self, path, scale=SCALE):
        Image.fromarray(np.repeat(np.repeat(self.a, scale, 0), scale, 1)).save(path)


# ---------------------------------------------------------------- masks
_cache = {}
def ell_mask(rx, ry):
    key = ('e', rx, ry)
    if key in _cache: return _cache[key]
    w, h = int(round(rx * 2)), int(round(ry * 2))
    w, h = max(w, 1), max(h, 1)
    yy, xx = np.mgrid[0:h, 0:w]
    m = ((xx + 0.5 - w / 2) / (w / 2)) ** 2 + ((yy + 0.5 - h / 2) / (h / 2)) ** 2 <= 1.0
    _cache[key] = m; return m

def rrect_mask(w, h, r):
    key = ('r', w, h, r)
    if key in _cache: return _cache[key]
    w, h = int(w), int(h); r = int(min(r, w // 2, h // 2))
    m = np.ones((h, w), bool)
    if r > 0:
        c = ell_mask(r, r)  # 2r x 2r
        tl = c[:r, :r]
        m[:r, :r] = tl; m[:r, w - r:] = tl[:, ::-1]
        m[h - r:, :r] = tl[::-1, :]; m[h - r:, w - r:] = tl[::-1, ::-1]
    _cache[key] = m; return m

def dilate(m, n=1):
    h, w = m.shape
    o = np.zeros((h + 2 * n, w + 2 * n), bool) if m.shape != (H, W) else None
    if o is None:  # full-frame dilate in place size
        r = m.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                r |= np.roll(np.roll(m, dy, 0), dx, 1)
        return r
    for dy in range(-n, n + 1):
        for dx in range(-n, n + 1):
            o[n + dy:n + dy + h, n + dx:n + dx + w] |= m
    return o


# ---------------------------------------------------------------- helpers
def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def mix(c1, c2, t): return tuple(int(round(lerp(int(a), int(b), clamp(t)))) for a, b in zip(c1, c2))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def step12(t): return int(t * 12) / 12.0   # 12fps animation clock

def bayer_mask(level):
    """4x4 ordered dither mask for full frame, level 0..16"""
    b = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
    tile = b < level
    return np.tile(tile, (H // 4 + 1, W // 4 + 1))[:H, :W]

def rng(seed): return np.random.default_rng(seed)
