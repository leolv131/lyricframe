"""Render the 《告白气球》 example. 渲染《告白气球》案例（选项见 tools/lf_make.py）。

    python src/make.py --still 68                      # one frame -> out/stills/
    python src/make.py --start 23 --end 44 --preview   # 21 s, 720p
    python src/make.py --song /path/to/your/copy.mp3 --jobs 4 # full film with your own audio

The song is NOT in this repository (copyright) — bring your own copy, or render silent.
原曲不在仓库里（版权），用你自己的音源，或者不配音渲染。
"""
import functools

import lf_path  # noqa: F401
from lf_make import run


def shot_list():
    import gb2

    def with_hud(fn, a):                     # the "confession progress" HUD around its 5 moments
        @functools.wraps(fn)
        def shot(t, D):
            cv = fn(t, D)
            if fn.__name__ not in gb2.NO_HUD:
                gb2.hud_moment(cv, a + t)
            return cv
        return shot
    return [(a, b, with_hud(fn, a)) for a, b, fn in gb2.SHOTS]


if __name__ == '__main__':
    run(shot_list, __file__)
