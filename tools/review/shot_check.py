"""Shot-by-shot check sheet: the middle frame of every shot, labelled, next to what the storyboard
says must be visible. 逐镜对照图：每镜取中间一帧，对照分镜里"必须看得见"的元素。

    python shot_check.py preview.mp4 --shots shots.json      # shots from your project
    python shot_check.py preview.mp4                          # shots found by cut detection

shots.json: [{"no": "01", "start": 0.0, "end": 3.3, "must": "纸箱、雨、路灯"}, ...]
(make.py in the examples can export it; or write it from STORYBOARD.md.)
Also saves a 'phone' version at 1/4 size — if the hook is not readable there, it is not readable.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import duration, grab, cjk_font, fmt_t  # noqa: E402
from metrics import analyse  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--shots', default=None)
    ap.add_argument('--cols', type=int, default=4)
    ap.add_argument('--out', default=None)
    ap.add_argument('--offset', type=float, default=0.0, help='if the video starts at song time X, pass X')
    a = ap.parse_args()
    if a.shots:
        shots = json.load(open(a.shots, encoding='utf-8'))
    else:
        cuts = [0.0] + analyse(a.video)['cut_times'] + [duration(a.video)]
        shots = [dict(no=f'{i + 1:02d}', start=cuts[i], end=cuts[i + 1], must='') for i in range(len(cuts) - 1)]
    tw, th, cap = 480, 270, 54
    rows = (len(shots) + a.cols - 1) // a.cols
    S = Image.new('RGB', (a.cols * tw, rows * (th + cap)), (16, 16, 20))
    d = ImageDraw.Draw(S)
    f1, f2 = cjk_font(18), cjk_font(15)
    for i, s in enumerate(shots):
        t = (s['start'] + s['end']) / 2 - a.offset
        im = grab(a.video, max(0.0, t), w=tw)
        x, y = (i % a.cols) * tw, (i // a.cols) * (th + cap)
        if im:
            S.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + th + 4), f"镜 {s['no']}  {fmt_t(s['start'])}–{fmt_t(s['end'])}", font=f1, fill=(255, 220, 140))
        if s.get('must'):
            d.text((x + 6, y + th + 28), '必须看得见：' + s['must'][:26], font=f2, fill=(220, 220, 230))
    out = a.out or os.path.splitext(a.video)[0] + '_shots.jpg'
    S.save(out, quality=88)
    S.resize((S.width // 4, S.height // 4)).save(out.replace('.jpg', '_phone.jpg'), quality=85)
    print('->', out)
    print('->', out.replace('.jpg', '_phone.jpg'))


if __name__ == '__main__':
    main()
