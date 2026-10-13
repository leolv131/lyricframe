"""扁平 Q 版工具包 · 核心：skia 矢量画布、颜色、描边形状、文字、纸张颗粒、镜头。
所有坐标以 1920×1080 为准。每帧只由时间 t 决定。"""
import math
import os
import numpy as np
import skia

W, H = 1920, 1080
LINE = 5.0                      # 默认描边宽度
INK = '#2b1d2e'                 # 深紫棕描边色


def C(h, a=1.0):
    """'#rrggbb' -> skia Color4f"""
    h = h.lstrip('#')
    return skia.Color4f(int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def mixc(h1, h2, t):
    a = [int(h1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    t = max(0.0, min(1.0, t))
    return '#' + ''.join(f'{int(round(x + (y - x) * t)):02x}' for x, y in zip(a, b))


def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t, s=1.7):
    t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def bounce(t, f=8.0): return abs(math.sin(t * f))


# ------------------------------------------------------------------ fonts
# Bundled Noto Sans SC subsets (GB2312 + Latin + symbols). 自带思源黑体子集。
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
FONT_PATHS = {
    'bold': os.path.join(FONT_DIR, 'NotoSansSC-Bold.otf'),
    'black': os.path.join(FONT_DIR, 'NotoSansSC-Black.otf'),
}
FONT_PATHS['sans'] = FONT_PATHS['bold']
_tf = {}
def typeface(kind='bold'):
    if kind not in _tf:
        _tf[kind] = skia.Typeface.MakeFromFile(FONT_PATHS.get(kind, FONT_PATHS['bold']), 0)
    return _tf[kind]


# ------------------------------------------------------------------ paper grain / halftone (precomputed)
def _grain():
    r = np.random.default_rng(7)
    g = r.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)
    return g
_GRAIN = None


class Frame:
    """One frame. Use .c (skia.Canvas) or the helpers."""

    def __init__(self, bg='#000000'):
        self.surface = skia.Surface(W, H)
        self.c = self.surface.getCanvas()
        self.c.clear(C(bg))

    # ---------- paints
    @staticmethod
    def fill(col, a=1.0):
        p = skia.Paint(AntiAlias=True); p.setColor4f(C(col, a)); return p

    @staticmethod
    def stroke(col=INK, w=LINE, a=1.0, cap=skia.Paint.kRound_Cap):
        p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w)
        p.setColor4f(C(col, a)); p.setStrokeCap(cap); p.setStrokeJoin(skia.Paint.kRound_Join)
        return p

    # ---------- shapes (fill + outline)
    def path(self, path, col=None, line=INK, w=LINE, a=1.0):
        if col: self.c.drawPath(path, self.fill(col, a))
        if line and w > 0: self.c.drawPath(path, self.stroke(line, w, a))

    def rect(self, x, y, w, h, col, line=None, lw=LINE, r=0, a=1.0):
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
        if col: self.c.drawRRect(rr, self.fill(col, a))
        if line: self.c.drawRRect(rr, self.stroke(line, lw, a))

    def circle(self, x, y, r, col, line=None, lw=LINE, a=1.0):
        if col: self.c.drawCircle(x, y, r, self.fill(col, a))
        if line: self.c.drawCircle(x, y, r, self.stroke(line, lw, a))

    def oval(self, x, y, rx, ry, col, line=None, lw=LINE, a=1.0):
        rc = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
        if col: self.c.drawOval(rc, self.fill(col, a))
        if line: self.c.drawOval(rc, self.stroke(line, lw, a))

    def line(self, x0, y0, x1, y1, col=INK, w=LINE, a=1.0):
        self.c.drawLine(x0, y0, x1, y1, self.stroke(col, w, a))

    def poly(self, pts, col, line=INK, w=LINE, a=1.0, close=True):
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        if close: p.close()
        self.path(p, col, line, w, a)

    def curve(self, pts, col=INK, w=LINE, a=1.0):
        """smooth open curve through points (quadratic midpoints)"""
        p = skia.Path(); p.moveTo(*pts[0])
        for i in range(1, len(pts) - 1):
            mx = (pts[i][0] + pts[i + 1][0]) / 2; my = (pts[i][1] + pts[i + 1][1]) / 2
            p.quadTo(pts[i][0], pts[i][1], mx, my)
        p.lineTo(*pts[-1])
        self.c.drawPath(p, self.stroke(col, w, a))

    def blob(self, pts, col, line=INK, w=LINE, a=1.0):
        """smooth closed shape through points"""
        n = len(pts); p = skia.Path()
        m0 = ((pts[-1][0] + pts[0][0]) / 2, (pts[-1][1] + pts[0][1]) / 2)
        p.moveTo(*m0)
        for i in range(n):
            nx = pts[(i + 1) % n]; m = ((pts[i][0] + nx[0]) / 2, (pts[i][1] + nx[1]) / 2)
            p.quadTo(pts[i][0], pts[i][1], *m)
        p.close()
        self.path(p, col, line, w, a)

    # ---------- gradients
    def vgrad(self, cols, y0=0, y1=H, x0=0, x1=W):
        pts = [skia.Point(0, y0), skia.Point(0, y1)]
        shader = skia.GradientShader.MakeLinear(pts, [C(c).toColor() for c in cols])
        p = skia.Paint(AntiAlias=True); p.setShader(shader)
        self.c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)

    def radial(self, x, y, r, inner, outer_alpha=0.0, a=1.0):
        cols = [C(inner, a).toColor(), C(inner, outer_alpha).toColor()]
        shader = skia.GradientShader.MakeRadial(skia.Point(x, y), r, cols)
        p = skia.Paint(AntiAlias=True); p.setShader(shader)
        self.c.drawCircle(x, y, r, p)

    # ---------- text
    def text(self, x, y, s, size=48, col=INK, kind='bold', align='left', a=1.0, outline=None, ow=8):
        font = skia.Font(typeface(kind), size)
        w = font.measureText(s)
        if align == 'center': x -= w / 2
        elif align == 'right': x -= w
        if outline:
            self.c.drawString(s, x, y, font, self.stroke(outline, ow, a))
        self.c.drawString(s, x, y, font, self.fill(col, a))
        return w

    # ---------- camera
    def push(self, cx=W / 2, cy=H / 2, zoom=1.0, rot=0.0, dx=0.0, dy=0.0):
        """zoom/rotate around (cx,cy), then pan by (dx,dy). Call pop() after."""
        self.c.save()
        self.c.translate(cx + dx, cy + dy); self.c.rotate(rot); self.c.scale(zoom, zoom); self.c.translate(-cx, -cy)

    def pop(self): self.c.restore()

    # ---------- finish
    def array(self, grain=0.022, vignette=0.15):
        img = self.surface.makeImageSnapshot()
        a = img.toarray(colorType=skia.kRGBA_8888_ColorType)[:, :, :3].astype(np.float32)
        global _GRAIN
        if grain:
            if _GRAIN is None: _GRAIN = _grain()
            a += _GRAIN[:, :, None] * (255 * grain)
        if vignette:
            yy, xx = np.ogrid[0:H, 0:W]
            d = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
            a *= (1 - vignette * np.clip(d - 0.35, 0, 1))[:, :, None]
        return np.clip(a, 0, 255).astype(np.uint8)

    def save(self, path, **kw):
        from PIL import Image
        Image.fromarray(self.array(**kw)).save(path)


def halftone(f, x0, y0, w, h, col, step=14, rmax=4.0, a=0.35, angle=0.0, falloff='down'):
    """retro halftone dots in a rect; size grows toward falloff side"""
    p = f.fill(col, a)
    for j, y in enumerate(np.arange(y0, y0 + h, step)):
        for x in np.arange(x0 + (j % 2) * step / 2, x0 + w, step):
            k = (y - y0) / max(1, h) if falloff == 'down' else 1 - (y - y0) / max(1, h)
            r = rmax * k
            if r > 0.5: f.c.drawCircle(float(x), float(y), float(r), p)
