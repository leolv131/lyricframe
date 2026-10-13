"""Grid of evenly spaced frames — the fastest way to judge a whole video at a glance.
均匀抽帧拼图：一眼看全片的光、色、构图。

    python contact_sheet.py final.mp4                  # 20 frames, 5 columns -> final_sheet.jpg
    python contact_sheet.py ours.mp4 theirs.mp4        # one sheet per video, same layout, for comparing
    python contact_sheet.py final.mp4 -n 30 --cols 6
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import duration, grab, cjk_font, fmt_t  # noqa: E402


def sheet(path, n=20, cols=5, tw=384, out=None):
    dur = duration(path)
    times = [(i + 0.5) * dur / n for i in range(n)]
    ims = [grab(path, t, w=tw) for t in times]
    th = next((im.size[1] for im in ims if im), tw * 9 // 16)
    rows = (n + cols - 1) // cols
    S = Image.new('RGB', (cols * tw, rows * th + 40), (12, 12, 16))
    d = ImageDraw.Draw(S)
    f = cjk_font(22)
    d.text((10, 8), f'{os.path.basename(path)}   {fmt_t(dur)}', font=f, fill=(230, 230, 230))
    for i, (t, im) in enumerate(zip(times, ims)):
        x, y = (i % cols) * tw, 40 + (i // cols) * th
        if im:
            S.paste(im.resize((tw, th)), (x, y))
        d.text((x + 6, y + 4), fmt_t(t), font=cjk_font(16), fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    out = out or os.path.splitext(path)[0] + '_sheet.jpg'
    S.save(out, quality=88)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('videos', nargs='+')
    ap.add_argument('-n', type=int, default=20)
    ap.add_argument('--cols', type=int, default=5)
    ap.add_argument('--width', type=int, default=384, help='thumbnail width')
    a = ap.parse_args()
    for v in a.videos:
        print('->', sheet(v, a.n, a.cols, a.width))


if __name__ == '__main__':
    main()
