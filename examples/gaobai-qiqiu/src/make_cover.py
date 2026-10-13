import lf_path  # noqa: F401  shared toolkit on sys.path
import gb2
from gbl import *
cv = gb2.frame(68.0)
title_text(cv, '告 白 气 球', 92, 24, hexc('fff6e0'), size=24, outline=BAL_D)
cv.text(316, 168, '原唱 · 周杰伦', hexc('fff6e0'), outline=INK, anchor='rt')
cv.save('cover.png', scale=6)
