"""Beat grid, energy curve and section hints for MUSIC_MAP.md. 节拍、能量曲线、段落建议。

    python music_map.py song.mp3 --timing work/timing.json --out work/music.json

Prints a short report and writes music.json:
  bpm (plus a half-tempo hint for slow songs), beats[], energy per 4 s (0–1),
  vocal blocks (from timing.json) and suggested section boundaries, and for each lyric
  line the nearest beat (so cuts can land on the beat).
Requires librosa (pip install librosa).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import load_audio, read_timing, fmt_t  # noqa: E402

BARS = '▁▂▃▄▅▆▇█'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('--timing', help='timing.json from lrc_timing.py')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    import librosa

    sr = 22050
    y = load_audio(a.audio, sr)
    total = len(y) / sr
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
    bpm = float(np.atleast_1d(tempo)[0])
    rms = librosa.feature.rms(y=y, hop_length=512)[0]
    t_rms = np.arange(len(rms)) * 512 / sr
    win = 4.0
    energy = []
    for t0 in np.arange(0, total, win):
        m = (t_rms >= t0) & (t_rms < t0 + win)
        energy.append(float(rms[m].mean()) if m.any() else 0.0)
    e = np.array(energy)
    e = (e - e.min()) / (e.max() - e.min() + 1e-9)

    lines = read_timing(a.timing)['lines'] if a.timing else []
    blocks = []                      # vocal blocks separated by gaps > 4 s
    for ln in lines:
        if blocks and ln['start'] - blocks[-1]['end'] <= 4.0:
            blocks[-1]['end'] = ln['end']; blocks[-1]['lines'].append(ln['n'])
        else:
            blocks.append(dict(start=ln['start'], end=ln['end'], lines=[ln['n']]))
    for b in blocks:
        m = (t_rms >= b['start']) & (t_rms < b['end'])
        b['energy'] = round(float(rms[m].mean() / (rms.max() + 1e-9)), 3) if m.any() else 0.0

    beats = np.asarray(beats, float)
    snap = []
    for ln in lines:
        if len(beats):
            j = int(np.abs(beats - ln['start']).argmin())
            snap.append(dict(n=ln['n'], start=ln['start'], beat=round(float(beats[j]), 3),
                             diff=round(float(beats[j] - ln['start']), 3)))

    res = dict(duration=round(total, 2), bpm=round(bpm, 1),
               bpm_note='Slow ballads are often detected at double speed; if this feels too fast, use half.' if bpm > 120 else '',
               beat_period=round(60 / bpm, 3), beats=[round(float(b), 3) for b in beats],
               energy_window=win, energy=[round(float(x), 3) for x in e],
               vocal_blocks=blocks, line_beats=snap)
    out = a.out or os.path.join(os.path.dirname(a.timing) if a.timing else '.', 'music.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=1)

    print(f'duration {fmt_t(total)}   bpm ≈ {bpm:.1f}' + (f'  (maybe {bpm / 2:.1f})' if bpm > 120 else ''))
    print('energy per 4 s:')
    print('  ' + ''.join(BARS[min(7, int(x * 8))] for x in e))
    if blocks:
        print('vocal blocks (gaps > 4 s split them; use these to draw section boundaries):')
        for b in blocks:
            print(f"  {fmt_t(b['start'])}–{fmt_t(b['end'])}  lines {b['lines'][0]}–{b['lines'][-1]}  energy {b['energy']:.2f}")
    print('->', out)


if __name__ == '__main__':
    main()
