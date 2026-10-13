"""Five picture metrics for a finished video (step 7). 成片的五项画面指标。

    python metrics.py final.mp4
    python metrics.py final.mp4 --mood bright        # sweet / bright songs: no dark-frame target
    python metrics.py ours.mp4 theirs.mp4            # compare side by side

  dark_ratio        share of frames with mean brightness < 50/255
  saturation        mean saturation
  motion_median     median frame-to-frame change inside shots (how alive each shot is)
  static_ratio      share of seconds that barely move
  avg_shot          average shot length in seconds (cuts detected automatically)

Each value is printed next to a reference range from well-received AI MVs. 'look' means
"worth a look", not "wrong" — a pastel, sunny song can be right to stay bright.

Analysed at 160x90, 6 fps, so a 4-minute video takes a few seconds.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import read_frames  # noqa: E402

FPS = 6


def detect_cuts(d, fps=FPS, k=6.0, floor=12.0, min_gap=0.5):
    """Frame indices where a hard cut starts (big spike in the frame difference)."""
    med = np.median(d) + 1e-6
    cuts, last = [], -10 ** 9
    for i, v in enumerate(d):
        local = np.median(d[max(0, i - 6):i + 7])
        if v > max(floor, k * max(local, med)) and (i - last) / fps >= min_gap:
            cuts.append(i + 1)
            last = i
    return cuts


def analyse(path):
    a = read_frames(path, FPS, 160, 90).astype(np.float32)
    g = a.mean(3)
    d = np.abs(np.diff(g, axis=0)).mean((1, 2))
    cuts = detect_cuts(d)
    inside = np.ones(len(d), bool)
    for c in cuts:
        inside[max(0, c - 1)] = False
    mx, mn = a.max(3), a.min(3)
    sat = ((mx - mn) / (mx + 1e-3)).mean((1, 2))
    lum = g.mean((1, 2))
    n = len(d) // FPS
    per_sec = d[:n * FPS].reshape(n, FPS).mean(1) if n else np.zeros(1)
    dur = len(a) / FPS
    return dict(
        file=os.path.basename(path), seconds=round(dur, 1), shots=len(cuts) + 1,
        avg_shot=round(dur / (len(cuts) + 1), 2),
        dark_ratio=round(float((lum < 50).mean()), 3),
        saturation=round(float(sat.mean()), 3),
        motion_median=round(float(np.median(d[inside])) if inside.any() else 0.0, 3),
        static_ratio=round(float((per_sec < 0.6).mean()), 3),
        brightness=round(float(lum.mean() / 255), 3),
        cut_times=[round(c / FPS, 2) for c in cuts])


# Reference values measured on well-received AI MVs (see docs/zh/workflow.md, appendix).
# They are guides, not pass/fail rules: sweet, bright songs naturally sit lower on darkness and saturation.
REF = dict(dark_ratio=(0.30, None, 'moody songs >= 0.30 (references 0.36–0.53)'),
           saturation=(0.40, None, '>= 0.40 (references ~0.53; pastel styles run lower)'),
           motion_median=(1.0, None, '>= 1.0 (references 1.1–1.9)'),
           static_ratio=(None, 0.20, '<= 0.20 (references 0.20–0.23)'),
           avg_shot=(5.0, 9.0, '5–9 s, cut on phrases'))


def verdict(m, mood):
    rows = []
    for k, (lo, hi, note) in REF.items():
        if k == 'dark_ratio' and mood == 'bright':
            continue
        v = m[k]
        ok = (lo is None or v >= lo) and (hi is None or v <= hi)
        rows.append((k, v, ' ok ' if ok else 'look', note))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('videos', nargs='+')
    ap.add_argument('--mood', choices=['moody', 'bright'], default='moody')
    ap.add_argument('--json', default=None, help='also save results here')
    a = ap.parse_args()
    res = [analyse(v) for v in a.videos]
    for m in res:
        print(f"\n{m['file']}  {m['seconds']} s, {m['shots']} shots, brightness {m['brightness']}")
        for name, val, flag, target in verdict(m, a.mood):
            print(f'  [{flag}] {name:14s} {val:<8} {target}')
    if len(res) > 1:
        keys = ['shots', 'avg_shot', 'dark_ratio', 'saturation', 'motion_median', 'static_ratio']
        print('\n' + 'metric'.ljust(14) + ''.join(r['file'][:18].ljust(20) for r in res))
        for k in keys:
            print(k.ljust(14) + ''.join(str(r[k]).ljust(20) for r in res))
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
