"""Light first, then people: the v3.1 lighting pipeline as a small reusable class.
先布光、再合成人物：v3.1 的打光流程。

    from stage import Stage
    from light import Light, glow

    def shot(t, D):
        cv = Canvas()
        st = Stage()
        street(cv, t)                                   # 1. draw the place in its own colours
        st.person('girl', 160, 150, 26, 'walk', 'smile', t=t)    # 2. queue people (drawn later)
        st.light(cv, [Light(206, 60, 'ffd9a0', 120)],   # 3. light the scene, then composite people
                 ambient=(0.25, 0.27, 0.40), t=t)       #    with a brightness floor
        glow(cv, 206, 60, 18, 'ffd9a0')                 # 4. glows, particles, text on top
        return cv

Why: people drawn into a dark scene become unreadable. Characters are composited after lighting
with `floor` (minimum brightness, 0.5–0.9) so the main character always reads, and can get a rim
light facing the main light source. `alpha < 1` draws a dithered, half-there person with a
crawling dashed outline ("being ignored"); `tint` pushes them toward a colour (memory, cold).
For daylight scenes call `st.flat(cv)` — no darkening, people composited as they are.
"""
import numpy as np

from px import H, W, hexc, dilate
from chars import char, head
from hd import Layer
from light import lightmap, rim, DITH, XX, YY


class Stage:
    def __init__(self):
        self.pending = []

    def person(self, who, x, feet, Hh, pose='stand', expr='normal', t=0.0, facing=0,
               floor=0.85, alpha=1.0, tint=None, rim_light=None, **kw):
        """Queue a full-body character (see chars.LOOK for `who`). Returns (mask, info)."""
        L = Layer()
        f = char(L, who, int(x), int(feet), max(8, int(Hh)), pose, expr, t=t, facing=facing, **kw)
        m = L.mask()
        self.pending.append((L, m, floor, alpha, tint, rim_light))
        return m, f

    def face(self, who, cx, top, Hh, expr='normal', t=0.0, body=None, floor=0.9, tint=None, rim_light=None):
        """Queue a head-and-shoulders close-up."""
        L = Layer()
        L.ellipse(cx, top + Hh * 1.6, Hh * 0.95, Hh * 0.62, body or hexc('c6c3d8'), hexc('1a1426'))
        f = head(L, who, int(cx), int(top), int(Hh), expr, t=t)
        m = L.mask()
        self.pending.append((L, m, floor, 1.0, tint, rim_light))
        return m, f

    def layer(self, L, floor=0.9):
        """Queue any hd.Layer you drew yourself (a prop that must stay readable)."""
        m = L.mask()
        self.pending.append((L, m, floor, 1.0, None, None))
        return m

    def light(self, cv, lights, ambient, t=0.0, emissive=None):
        """Multiply the scene by the light map, then composite queued people on top."""
        Lm = lightmap(lights, ambient, t)
        a = cv.a.astype(np.float32) / 255.0
        out = np.clip(a * Lm, 0, 1)
        if emissive is not None:
            out = np.where(emissive[..., None], a, out)
        rims = []
        for (L, m, floor, alpha, tint, rl) in self.pending:
            sh = np.clip(Lm, floor, 1.25)
            ca = np.clip(L.a.astype(np.float32) / 255.0 * sh, 0, 1)
            if tint is not None:
                c = np.array(hexc(tint[0]), np.float32) / 255.0
                g = ca.mean(2, keepdims=True)
                ca = ca * (1 - tint[1]) + (g * 0.6 + c * 0.4) * tint[1]
            mm = m & (DITH < alpha) if alpha < 1 else m
            out[mm] = ca[mm]
            if alpha < 1:
                e = dilate(m) & ~m & (((XX + YY + int(t * 8)) // 2) % 2 == 0)
                out[e] = np.array([0.55, 0.6, 0.7])
            if rl:
                rims.append((m, rl))
        self.pending.clear()
        cv.a = (out * 255).astype(np.uint8)
        for m, (lx, ly, col) in rims:
            rim(cv, m, lx, ly, col)

    def flat(self, cv):
        """Daylight: no darkening, just composite the people."""
        self.light(cv, [], (1.0, 1.0, 1.0))
