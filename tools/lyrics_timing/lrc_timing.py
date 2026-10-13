"""Turn a synced-lyrics .lrc file into a text-free timing file (+ an .srt for subtitles).
把 .lrc 歌词文件变成"只有时间、没有歌词"的时间轴，另出一份 .srt 给最后烧字幕用。

    python lrc_timing.py song.lrc --audio song.mp3 --out work/

Outputs
  work/timing.json   line numbers + start/end seconds + character count. NO lyric text.
                     This is the only file the AI assistant reads.
  work/lyrics.srt    the lyric text with times, for burning subtitles at the very end.
                     The AI assistant does not open it.
  work/timing_report.txt

Where to get .lrc files: https://lrclib.net (free, no sign-up) — search the song, download "synced lyrics".
.lrc 去 https://lrclib.net 搜歌名下载（免费、不用注册）。

With --audio, the script checks whether the .lrc lines up with this recording (by looking for
note onsets right after each line start) and corrects a constant offset when it is clearly off.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import load_audio, duration  # noqa: E402

TAG = re.compile(r'\[(\d+):(\d+(?:[.:]\d+)?)\]')
META_WORDS = ('作词', '作曲', '编曲', '制作', '演唱', '原唱', '混音', '母带', '监制', '出品', '和声', '吉他',
              '贝斯', '鼓', '录音', '弦乐', '词：', '曲：', '词:', '曲:', 'Lyrics', 'Composer', 'Producer', 'Arranger')


def read_text(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'gb18030', 'utf-16', 'big5'):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode('utf-8', errors='ignore')


def parse_lrc(path):
    """[(time, text)] sorted; empty text = an instrumental marker / end of previous line."""
    offset_ms = 0
    out = []
    for line in read_text(path).replace('\r', '').split('\n'):
        m = re.match(r'^\[offset:\s*([+-]?\d+)\]', line.strip(), re.I)
        if m:
            offset_ms = int(m.group(1))
            continue
        if re.match(r'^\[(ti|ar|al|by|re|ve|length|au|#)[:：]', line.strip(), re.I):
            continue
        tags = TAG.findall(line)
        if not tags:
            continue
        text = TAG.sub('', line)
        text = re.sub(r'<\d+:\d+(?:\.\d+)?>', '', text).strip()      # enhanced-LRC word tags
        for mm, ss in tags:
            out.append((int(mm) * 60 + float(ss.replace(':', '.')), text))
    out.sort(key=lambda x: x[0])
    # LRC [offset] is in ms; positive = lyrics shown earlier
    return [(t - offset_ms / 1000.0, s) for t, s in out]


def is_meta(text):
    return len(text) < 40 and any(w in text for w in META_WORDS) and (':' in text or '：' in text)


def onset_envelope(y, sr, hop=512):
    n = 2048
    if len(y) < n:
        return np.zeros(1), hop / sr
    frames = np.lib.stride_tricks.sliding_window_view(y, n)[::hop] * np.hanning(n)
    mag = np.log1p(np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(1)
    flux = np.concatenate([[0], flux])
    flux = (flux - np.median(flux)) / (flux.std() + 1e-6)
    return np.maximum(flux, 0), hop / sr


def estimate_offset(starts, env, dt, search=2.5, step=0.02):
    """Shift that best lines up line starts with onsets. Returns (best, score_best, score_zero)."""
    def score(off):
        s = 0.0
        for t in starts:
            a, b = int((t + off - 0.06) / dt), int((t + off + 0.20) / dt)
            if 0 <= a < b <= len(env):
                s += env[a:b].max()
        return s / max(1, len(starts))
    offs = np.arange(-search, search + 1e-9, step)
    sc = np.array([score(o) for o in offs])
    i = int(sc.argmax())
    return float(offs[i]), float(sc[i]), float(score(0.0))


def srt_ts(x):
    x = max(0.0, x)
    h, m = int(x // 3600), int(x % 3600 // 60)
    s = x % 60
    ms = min(999, int(round((s - int(s)) * 1000)))
    return f'{h:02d}:{m:02d}:{int(s):02d},{ms:03d}'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lrc')
    ap.add_argument('--audio', help='the recording you will use (to check / fix the offset)')
    ap.add_argument('--out', default='work')
    ap.add_argument('--offset', type=float, default=None, help='force a shift in seconds (+ = later)')
    ap.add_argument('--max-line', type=float, default=8.0, help='longest a subtitle may stay on screen')
    a = ap.parse_args()

    raw = parse_lrc(a.lrc)
    if not raw:
        sys.exit('no timed lines found — is this a synced .lrc file?')
    total = duration(a.audio) if a.audio else None
    note = []
    off = 0.0
    if a.offset is not None:
        off = a.offset
        note.append(f'offset forced: {off:+.2f} s')
    elif a.audio:
        y = load_audio(a.audio, sr=22050)
        env, dt = onset_envelope(y, 22050)
        starts = [t for t, s in raw if s]
        best, sb, s0 = estimate_offset(starts, env, dt)
        if abs(best) >= 0.3 and sb > 1.15 * s0:
            off = best
            note.append(f'offset detected and applied: {off:+.2f} s (onset score {s0:.2f} -> {sb:.2f})')
        else:
            note.append(f'offset check: .lrc matches this audio (best {best:+.2f} s, score {sb:.2f} vs {s0:.2f} at 0) — no change')

    raw = [(t + off, s) for t, s in raw]
    lines = []
    for i, (t, s) in enumerate(raw):
        if not s or is_meta(s):
            continue
        nxt = next((raw[j][0] for j in range(i + 1, len(raw))), None)
        end = min(nxt - 0.05 if nxt else t + 4.0, t + a.max_line)
        if total:
            end = min(end, total)
        if end <= t:
            end = t + 0.8
        lines.append(dict(start=round(t, 3), end=round(end, 3), text=s))

    if total:
        beyond = [l for l in lines if l['start'] >= total]
        if beyond:
            note.append(f'{len(beyond)} lines start after the audio ends ({total:.1f} s) — dropped. '
                        'If the audio is a short clip, use the full song or pass --offset.')
        lines = [l for l in lines if l['start'] < total]

    os.makedirs(a.out, exist_ok=True)
    timing = dict(
        source=os.path.basename(a.lrc), audio=os.path.basename(a.audio) if a.audio else None,
        audio_duration=round(total, 3) if total else None, offset_applied=round(off, 3),
        note='Line numbers and times only. Lyric text lives in lyrics.srt for subtitle burning; '
             'the AI assistant must not read or quote it.',
        lines=[dict(n=i + 1, start=l['start'], end=l['end'], chars=len(re.sub(r'\s', '', l['text'])))
               for i, l in enumerate(lines)])
    with open(os.path.join(a.out, 'timing.json'), 'w', encoding='utf-8') as f:
        json.dump(timing, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, 'lyrics.srt'), 'w', encoding='utf-8') as f:
        for i, l in enumerate(lines, 1):
            f.write(f"{i}\n{srt_ts(l['start'])} --> {srt_ts(l['end'])}\n{l['text']}\n\n")
    rep = [f'lines: {len(lines)}', *note]
    gaps = [(lines[i]['end'], lines[i + 1]['start']) for i in range(len(lines) - 1)
            if lines[i + 1]['start'] - lines[i]['end'] > 6]
    for g0, g1 in gaps:
        rep.append(f'instrumental gap {g0:.1f}–{g1:.1f} s ({g1 - g0:.1f} s)')
    with open(os.path.join(a.out, 'timing_report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep) + '\n')
    print('\n'.join(rep))
    print(f'-> {os.path.join(a.out, "timing.json")}  (AI reads this)')
    print(f'-> {os.path.join(a.out, "lyrics.srt")}   (only for burning subtitles)')


if __name__ == '__main__':
    main()
