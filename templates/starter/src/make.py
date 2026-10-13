"""Render this project. 渲染入口。

  python make.py                          # whole video, silent, 1080p -> out.mp4
  python make.py --song song.mp3          # with your own copy of the song
  python make.py --start 60 --end 75 --preview   # 15 s at 720p for a quick look
  python make.py --still 68.0             # one PNG frame
  python make.py --shots-json shots.json  # shot list for tools/review/shot_check.py

Shot times are song times. To render a clip, pass --start/--end (the song is cut to match).
"""
import argparse

import lf_path  # noqa: F401  shared toolkit on sys.path
from render import render, frame_at


def SHOT_LIST():
    import ch1                      # add ch2, ch3 … here as you write them
    return ch1.SHOTS


def shots():
    """[(start, end, fn)] with the comment on each shot's `def` line as its description."""
    import inspect
    out = []
    for a, b, fn in SHOT_LIST():
        f = getattr(fn, '__wrapped__', fn)
        try:
            line = inspect.getsourcelines(f)[0][0]
            note = line.split('#', 1)[1].strip() if '#' in line else ''
        except (OSError, TypeError):
            note = ''
        out.append(dict(no=f.__name__, start=round(a, 3), end=round(b, 3), must=note))
    return out


def timeline():
    return [(a, b, (lambda fn, D: (lambda t: fn(t, D)))(fn, b - a)) for a, b, fn in SHOT_LIST()]


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--song', default=None)
    ap.add_argument('--start', type=float, default=0.0)
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--out', default='out.mp4')
    ap.add_argument('--preview', action='store_true', help='720p')
    ap.add_argument('--still', type=float, default=None, help='save one frame at this time (s) as PNG')
    ap.add_argument('--shots-json', default=None, help='write the shot list (for tools/review/shot_check.py)')
    a = ap.parse_args()
    if a.shots_json:
        import json
        with open(a.shots_json, 'w', encoding='utf-8') as f:
            json.dump(shots(), f, ensure_ascii=False, indent=1)
        print('saved', a.shots_json)
        raise SystemExit
    TL = timeline()
    if a.still is not None:
        name = f'still_{a.still:.2f}.png'
        frame_at(TL, a.still).save(name)
        print('saved', name)
    else:
        end = a.end if a.end is not None else TL[-1][1]
        render(TL, a.start, end, a.out, song=a.song, scale=4 if a.preview else 6)
        print('done ->', a.out)
