"""Render the 《蝴蝶》 example. 渲染《蝴蝶》案例（选项见 tools/lf_make.py）。

    python src/make.py --still 130                     # one frame -> out/stills/
    python src/make.py --start 117.5 --end 143.3 --preview   # chorus 2, 720p
    python src/make.py --song /path/to/your/copy.mp3 --jobs 4 # full film with your own audio

The song is NOT in this repository (copyright) — bring your own copy, or render silent.
原曲不在仓库里（版权），用你自己的音源，或者不配音渲染。
"""
import lf_path  # noqa: F401
from lf_make import run


def shot_list():
    import c1, seg, c3, c4, c5, c6
    return c1.SHOTS + seg.SHOTS + c3.SHOTS + c4.SHOTS + c5.SHOTS + c6.SHOTS


if __name__ == '__main__':
    run(shot_list, __file__)
