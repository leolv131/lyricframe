import lf_path  # noqa: F401
import numpy as np, seg
from w3 import *
cv = seg.s1(5.8, 6.96)
title_text(cv, '蝴  蝶', 236, 24, hexc('fff6e0'), size=28, outline=hexc('0a0c1e'))
cv.text(316, 160, '原唱 · 陶喆', hexc('fff6e0'), outline=hexc('0a0c1e'), anchor='rt')
bfly(cv, 176, 22, 2, 0, flap=1.0); glow(cv, 176, 22, 16, '3a7aff', 0.5)
import os
os.makedirs('out', exist_ok=True)
cv.save('out/cover.png', scale=6)
print('-> out/cover.png')
