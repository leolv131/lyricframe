"""Generate a free demo song to try LyricFrame without bringing your own music.
生成一首免版权的演示歌（代码合成的 8bit 旋律 + 原创歌词 .lrc），不用找歌也能先试一遍流程。

    python demo/make_demo_song.py            # -> demo/paper_plane.wav + demo/paper_plane.lrc

"Paper Plane / 纸飞机" — 46 s, 100 BPM, an 8bit tune (square + triangle + noise) written by code.
The lyrics are original and released with this project (MIT). There are no vocals: the melody
"sings" the lines, so the timing tools still find each phrase.
Then:  python tools/lyrics_timing/lrc_timing.py demo/paper_plane.lrc --audio demo/paper_plane.wav --out work/
"""
import os
import wave

import numpy as np

SR = 44100
BPM = 100
BEAT = 60 / BPM            # 0.6 s
BAR = 4 * BEAT             # 2.4 s
HERE = os.path.dirname(os.path.abspath(__file__))

# original lyrics (CC0-style, part of this repo) — one line per 2 bars
LYRICS = [
    '雨停在窗台上',
    '我折了一架纸飞机',
    '写上没说出口的话',
    '让风替我带给你',
    '飞过红色的屋顶',
    '飞过整座城市的灯',
    '如果你抬起头',
    '就能看见我',
]


def note(n):               # MIDI number -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def square(f, d, duty=0.5, vol=0.18):
    t = np.arange(int(d * SR)) / SR
    w = np.where((t * f) % 1 < duty, 1.0, -1.0) * vol
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2)
    return w * env


def tri(f, d, vol=0.22):
    t = np.arange(int(d * SR)) / SR
    w = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
    return w * vol * np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.02 + 1e-9)


def noise(d, vol=0.12, decay=30):
    t = np.arange(int(d * SR)) / SR
    rng = np.random.default_rng(int(d * 1000))
    return rng.uniform(-1, 1, len(t)) * vol * np.exp(-t * decay)


def put(buf, start, sig):
    a = int(start * SR)
    b = min(len(buf), a + len(sig))
    if a < len(buf):
        buf[a:b] += sig[:b - a]


def main():
    chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]        # C G Am F
    # melody per 2-bar line: (beat offset, length in beats, midi)
    phrases = [
        [(0, 1, 72), (1, 1, 74), (2, 2, 76), (4, 1, 74), (5, 1, 72), (6, 2, 69)],
        [(0, .5, 67), (.5, .5, 69), (1, 1, 72), (2, 1, 72), (3, 1, 74), (4, 2, 76), (6, 2, 74)],
        [(0, 1, 76), (1, 1, 77), (2, 1, 79), (3, 1, 76), (4, 2, 74), (6, 2, 72)],
        [(0, 1, 74), (1, 1, 72), (2, 2, 69), (4, 1, 71), (5, 1, 72), (6, 2, 72)],
        [(0, 1, 79), (1, 1, 79), (2, 2, 81), (4, 1, 79), (5, 1, 77), (6, 2, 76)],
        [(0, .5, 76), (.5, .5, 77), (1, 1, 79), (2, 1, 81), (3, 1, 79), (4, 2, 77), (6, 2, 76)],
        [(0, 1, 74), (1, 1, 76), (2, 2, 77), (4, 2, 76), (6, 2, 74)],
        [(0, 2, 72), (2, 2, 74), (4, 4, 72)],
    ]
    intro = 2 * BAR
    total = intro + len(phrases) * 2 * BAR + BAR
    buf = np.zeros(int(total * SR) + SR)
    nbars = int(total / BAR) + 1
    for b in range(nbars):                              # bass, arpeggio, drums
        c = chords[b % 4]
        t0 = b * BAR
        for k in range(4):
            put(buf, t0 + k * BEAT, tri(note(c[0] - 12), BEAT * 0.9))
            put(buf, t0 + k * BEAT, noise(0.08, 0.10 if k % 2 == 0 else 0.06, 40 if k % 2 == 0 else 18))
        for k in range(8):
            put(buf, t0 + k * BEAT / 2, square(note(c[k % 3] + 12), BEAT / 2 * 0.9, 0.25, 0.05))
    lrc = []
    for i, ph in enumerate(phrases):                    # lead melody = the "voice"
        t0 = intro + i * 2 * BAR
        lrc.append((t0, LYRICS[i]))
        for off, ln, n in ph:
            put(buf, t0 + off * BEAT, square(note(n), ln * BEAT * 0.95, 0.5, 0.16))
    end = intro + len(phrases) * 2 * BAR
    buf = buf[:int(total * SR)]
    fade = int(BAR * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    buf = np.clip(buf / max(1e-6, np.abs(buf).max()) * 0.85, -1, 1)
    pcm = (buf * 32767).astype(np.int16)
    wav_path = os.path.join(HERE, 'paper_plane.wav')
    with wave.open(wav_path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    with open(os.path.join(HERE, 'paper_plane.lrc'), 'w', encoding='utf-8') as f:
        f.write('[ti:纸飞机 Paper Plane]\n[ar:LyricFrame demo]\n')
        for t, s in lrc:
            f.write(f'[{int(t // 60):02d}:{t % 60:05.2f}]{s}\n')
        f.write(f'[{int(end // 60):02d}:{end % 60:05.2f}]\n')
    print(f'-> {wav_path} ({total:.1f} s)')
    print(f'-> {os.path.join(HERE, "paper_plane.lrc")}')


if __name__ == '__main__':
    main()
