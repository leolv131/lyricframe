"""Find lyric line times by speech recognition — for when the .lrc does not match the recording
(live versions, covers, edits) or there is no .lrc at all.
用语音识别找每句歌词的时间：.lrc 和这版录音对不上（现场版、翻唱、剪辑版）或者没有 .lrc 时用。

    python align_asr.py song.mp3 --lyrics song.lrc --out work/     # align your lyrics file (best)
    python align_asr.py song.mp3 --out work/                       # no lyrics: recognise lines

Writes the same files as lrc_timing.py: work/timing.json (times only) + work/lyrics.srt (+ a report
with a match ratio per line; check lines below 50 %).

Setup (once, ~1.5 GB; a GPU is used automatically when available):
    pip install faster-whisper sherpa-onnx av zhconv
    pip install torch demucs        # optional: separating the vocals makes live recordings much better
First run downloads the models (~3 GB) into ~/.cache/lyricframe (change with LF_MODEL_DIR).
In a cloud sandbox without GPU use --model small or medium.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from lrc_timing import srt_ts  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('--lyrics', help='.lrc or plain .txt lyrics (one line per row)')
    ap.add_argument('--out', default='work')
    ap.add_argument('--model', default='large-v3', help='large-v3 (best) / medium / small (fast, CPU)')
    ap.add_argument('--offset', type=float, default=0.0)
    ap.add_argument('--nosep', action='store_true', help='skip vocal separation')
    a = ap.parse_args()
    import asr_engine as E

    model, dev = E.load_model(a.model)
    sv = E.load_sensevoice()
    words, pcm = E.transcribe(model, a.audio, a.offset, use_sep=not a.nosep)
    s_words = E.sensevoice_words(sv, pcm, a.offset) if sv is not None else []
    total = len(pcm) / 16000
    os.makedirs(a.out, exist_ok=True)
    report = []
    if a.lyrics:
        lines = E.read_lyrics_file(a.lyrics)
        out, ratios, off, rng = E.build_from_lyrics(lines, [words, s_words], total)
        report.append(f'lyrics file lines {rng[0]}–{rng[1]} used, {len(out)} lines; .lrc constant offset ≈ {off:+.2f} s')
        low = [i + 1 for i, r in enumerate(ratios) if r < 0.5]
        report.append(f'lines with match < 50 % (check these): {low}')
    else:
        out = E.lines_from_words(words or s_words)
        ratios = [None] * len(out)
        report.append(f'no lyrics file: {len(out)} lines recognised (text may contain wrong characters)')
    timing = dict(source='asr:' + os.path.basename(a.audio), audio=os.path.basename(a.audio),
                  audio_duration=round(total, 3), offset_applied=a.offset,
                  note='Line numbers and times only. Lyric text lives in lyrics.srt; the AI assistant must not read or quote it.',
                  lines=[dict(n=i + 1, start=round(s, 3), end=round(e, 3), chars=len(re.sub(r'\s', '', t)),
                              match=ratios[i]) for i, (s, e, t) in enumerate(out)])
    with open(os.path.join(a.out, 'timing.json'), 'w', encoding='utf-8') as f:
        json.dump(timing, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.out, 'lyrics.srt'), 'w', encoding='utf-8') as f:
        for i, (s, e, t) in enumerate(out, 1):
            f.write(f'{i}\n{srt_ts(s)} --> {srt_ts(e)}\n{t}\n\n')
    with open(os.path.join(a.out, 'timing_report.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(report) + '\n')
        for i, (s, e, _), r in zip(range(1, len(out) + 1), out, ratios):
            f.write(f'{i}\t{s:.2f}-{e:.2f}' + (f'\tmatch {int(r * 100)}%' if r is not None else '') + '\n')
    print('\n'.join(report))
    print('->', os.path.join(a.out, 'timing.json'))


if __name__ == '__main__':
    main()
