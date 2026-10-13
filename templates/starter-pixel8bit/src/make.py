"""Render this project — see tools/lf_make.py for every option. 渲染入口，选项见 tools/lf_make.py。

    python src/make.py --preview          # 720p preview of the clip in project.json
    python src/make.py                    # 1080p final -> out/final.mp4
    python src/make.py --still 3 7.5      # stills -> out/stills/
"""
import lf_path  # noqa: F401  finds the repo; puts styles/<style> and tools on sys.path
from lf_make import run


def shot_list():
    import ch1                      # add ch2, ch3 … as you write them
    return ch1.SHOTS


if __name__ == '__main__':
    run(shot_list, __file__)
