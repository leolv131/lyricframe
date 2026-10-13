"""第 1 章 · Chapter 1 — three shots showing the patterns you will use most.

Every shot is `def name(t, D):  # start–end what happens` and returns a Canvas.
t = seconds since the shot started, D = shot length. Only t decides the picture.
The comment on the `def` line becomes the storyboard (make.py --shots-json).
"""
import math

from common import *
from chars import symbol
from stage import Stage


def s01(t, D):   # 0.00–5.00 夜里的街，路灯下她一个人走过来（中景，先布光再合成人物）
    cv = Canvas()
    st = Stage()
    lights = street(cv, t, 'night')
    emis = emissive_windows(cv)                         # windows keep their own light
    x = 60 + t * 14                                     # walks in
    st.person('girl', x, 150, 26, 'walk', 'normal', t=t, facing=1, floor=0.6,
              rim_light=(207, 62, hexc('ffe0b0')))
    st.light(cv, lights, ambient=(0.30, 0.32, 0.52), t=t, emissive=emis)
    glow(cv, 207, 62, 22, 'ffd9a0', 0.6)                  # glow goes on after lighting
    return cv


def s02(t, D):   # 5.00–9.00 特写：她抬头，看见什么，头顶冒出"!"
    cv = Canvas()
    st = Stage()
    lights = street(cv, t + 5, 'night')
    emis = emissive_windows(cv)
    st.face('girl', 150, 30, 64, 'normal' if t < 1.5 else 'surprise', t=t, body=hexc('86c0e6'))
    st.light(cv, lights + [Light(150, 40, 'ffd9a0', 160, 0.6)], ambient=(0.3, 0.32, 0.5), t=t, emissive=emis)
    if t > 1.5:
        symbol(cv, 'excl', 200, 34, t, s=2)
    return cv


def s03(t, D):   # 9.00–15.00 同一条街到了黄昏：一只红气球飘下来，她接住，笑了（长镜头）
    cv = Canvas()
    st = Stage()
    lights = street(cv, t, 'dusk')
    st.person('girl', 150, 150, 28, 'reach' if t < 3 else 'stand', 'wonder' if t < 3 else 'joy', t=t, floor=0.85)
    by = min(96, 10 + t * 30)                           # the token: a red balloon drifts down
    bx = 172 + 4 * math.sin(t * 2)
    st.light(cv, lights + [Light(240, 100, 'ffb070', 200, 0.7)], ambient=(0.55, 0.45, 0.55), t=t)
    cv.line(bx, by + 8, 168, 118 if t > 3 else by + 30, hexc('f6f2e6'))
    cv.ellipse(bx, by, 7, 8, TOKEN, outline=hexc('1a1426'))
    if t > 3.4:
        symbol(cv, 'heart', 150, 102, t, s=2)
    return cv


SHOTS = [(0.0, 5.0, s01), (5.0, 9.0, s02), (9.0, 15.0, s03)]
