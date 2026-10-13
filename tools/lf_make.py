"""The render command behind every project's `src/make.py`. 每个工程 make.py 背后的渲染命令。

A project's make.py only lists its shots and calls run():

    import lf_path                     # finds the repo, puts styles/<style> and tools on sys.path
    from lf_make import run

    def shot_list():
        import ch1, ch2
        return ch1.SHOTS + ch2.SHOTS   # [(start, end, fn), ...] in SONG time; fn(t, D)

    if __name__ == '__main__':
        run(shot_list, __file__)

Run it from anywhere:
    python src/make.py                         # clip from project.json (or everything) -> out/final.mp4
    python src/make.py --preview               # 720p -> out/preview.mp4
    python src/make.py --preview --subs        # + out/preview_subs.mp4 with lyrics burned in, FOR THE USER
    python src/make.py --start 60 --end 75     # any range (song time)
    python src/make.py --still 12.5 30         # PNG stills -> out/stills/
    python src/make.py --shots-json            # shot list -> out/shots.json (for tools/review/shot_check.py)
    python src/make.py --jobs 4                # render in 4 parallel processes
    python src/make.py --no-song               # silent

Defaults come from <project>/project.json: "audio", "clip" {start, end}, "style".
Fades: --fade-in (default 0.3 s) and --fade-out (default 1.0 s) on picture and sound.
Check tools look at the clean video; the *_subs copy is only for showing the user.
"""
import argparse
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lf_common import ffmpeg, ROOT  # noqa: E402

STYLE_RENDER = {
    'pixel8bit': dict(full=6, preview=4, fps=30),
    'flatq': dict(full=1.0, preview=2 / 3, fps=30),
}


def load_project(project_dir):
    p = os.path.join(project_dir, 'project.json')
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    return {}


def shot_notes(shots):
    """[(start, end, fn)] -> [{no, start, end, must}] using the comment on each shot's `def` line."""
    out = []
    for a, b, fn in shots:
        f = getattr(fn, '__wrapped__', fn)
        note = ''
        try:
            line = inspect.getsourcelines(f)[0][0]
            if '#' in line:
                note = line.split('#', 1)[1].strip()
        except (OSError, TypeError):
            pass
        out.append(dict(no=getattr(f, '__name__', '?'), start=round(a, 3), end=round(b, 3), must=note))
    return out


def timeline_for(style, shots):
    """Adapt [(start, end, fn(t, D))] to what the style's render() expects."""
    if style == 'flatq':
        return [(a, b, fn) for a, b, fn in shots]                       # flatq calls fn(t, dur)
    return [(a, b, (lambda fn, D: (lambda t: fn(t, D)))(fn, b - a)) for a, b, fn in shots]


def frame_image(style, shots, T):
    """PIL image of the frame at song time T."""
    from PIL import Image
    import numpy as np
    for a, b, fn in shots:
        if a <= T < b:
            fr = fn(T - a, b - a)
            break
    else:
        fr = None
    if fr is None:
        return Image.new('RGB', (1920, 1080))
    if style == 'flatq':
        return Image.fromarray(fr.array())
    arr = fr.a
    return Image.fromarray(np.repeat(np.repeat(arr, 6, 0), 6, 1))


def render_segment(style, shots, t0, t1, out, scale):
    """Silent render of [t0, t1) with the style's own renderer."""
    from render import render
    tl = timeline_for(style, shots)
    if style == 'flatq':
        render(tl, t0, t1, out, song=None, scale=scale, crf=16)
    else:
        render(tl, t0, t1, out, audio=False, scale=int(round(scale)), crf=16)


def finish(video, song, t0, t1, out, fade_in, fade_out):
    """Mux the song range in and apply picture + sound fades (one encode)."""
    d = t1 - t0
    cmd = [ffmpeg(), '-v', 'error', '-y', '-i', video]
    if song:
        cmd += ['-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', song]
    vf, af = [], []
    if fade_in > 0:
        vf.append(f'fade=t=in:st=0:d={fade_in}'); af.append(f'afade=t=in:st=0:d={fade_in}')
    if fade_out > 0:
        vf.append(f'fade=t=out:st={max(0, d - fade_out):.3f}:d={fade_out}')
        af.append(f'afade=t=out:st={max(0, d - fade_out):.3f}:d={fade_out}')
    if vf:
        vcodec = os.environ.get('LF_VCODEC', 'libx264')
        cmd += ['-vf', ','.join(vf)]
        cmd += (['-c:v', 'libx264', '-crf', '18', '-preset', 'medium'] if vcodec == 'libx264'
                else ['-c:v', vcodec, '-b:v', '12M'])
        cmd += ['-pix_fmt', 'yuv420p']
    else:
        cmd += ['-c:v', 'copy']
    if song:
        if af:
            cmd += ['-af', ','.join(af)]
        cmd += ['-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-movflags', '+faststart', out]
    if subprocess.run(cmd).returncode:
        sys.exit('ffmpeg failed while finishing ' + out)


def run(shot_list, make_file, style=None):
    src_dir = os.path.dirname(os.path.abspath(make_file))
    project_dir = os.path.dirname(src_dir)
    proj = load_project(project_dir)
    style = style or proj.get('style') or os.environ.get('LF_STYLE') or 'pixel8bit'
    cfg = STYLE_RENDER[style]

    ap = argparse.ArgumentParser(description='Render this project. 渲染这个工程。')
    ap.add_argument('--song', default=None, help='audio file (default: project.json "audio")')
    ap.add_argument('--no-song', action='store_true')
    ap.add_argument('--start', type=float, default=None, help='song time (default: project.json clip.start)')
    ap.add_argument('--end', type=float, default=None)
    ap.add_argument('--all', action='store_true', help='ignore the clip in project.json, render every shot')
    ap.add_argument('--out', default=None)
    ap.add_argument('--preview', action='store_true', help='720p')
    ap.add_argument('--subs', action='store_true', help='also write *_subs.mp4 with work/lyrics.srt burned in (for the user)')
    ap.add_argument('--fade-in', type=float, default=0.3)
    ap.add_argument('--fade-out', type=float, default=1.0)
    ap.add_argument('--jobs', type=int, default=1, help='parallel render processes')
    ap.add_argument('--still', type=float, nargs='*', default=None, help='save PNG stills at these song times')
    ap.add_argument('--shots-json', nargs='?', const='', default=None, help='write the shot list (default out/shots.json)')
    ap.add_argument('--_segment', nargs=3, default=None, help=argparse.SUPPRESS)
    ap.add_argument('--_scale', type=float, default=None, help=argparse.SUPPRESS)
    a = ap.parse_args()

    shots = shot_list()
    out_dir = os.path.join(project_dir, 'out')
    os.makedirs(out_dir, exist_ok=True)

    if a._segment:                                           # worker process
        t0, t1, path = float(a._segment[0]), float(a._segment[1]), a._segment[2]
        render_segment(style, shots, t0, t1, path, a._scale)
        return

    if a.shots_json is not None:
        path = a.shots_json or os.path.join(out_dir, 'shots.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(shot_notes(shots), f, ensure_ascii=False, indent=1)
        print('->', path)
        return

    if a.still is not None:
        sd = os.path.join(out_dir, 'stills')
        os.makedirs(sd, exist_ok=True)
        for T in a.still:
            p = os.path.join(sd, f'still_{T:07.2f}.png')
            frame_image(style, shots, T).save(p)
            print('->', p)
        return

    clip = proj.get('clip') or {}
    t0 = a.start if a.start is not None else (None if a.all else clip.get('start'))
    t1 = a.end if a.end is not None else (None if a.all else clip.get('end'))
    t0 = shots[0][0] if t0 is None else t0
    t1 = shots[-1][1] if t1 is None else t1
    song = None if a.no_song else (a.song or proj.get('audio'))
    if song and not os.path.isabs(song) and not os.path.exists(song):
        song = os.path.join(project_dir, song)
    if song and not os.path.exists(song):
        print(f'(audio not found: {song} — rendering silent)')
        song = None
    out = a.out or os.path.join(out_dir, 'preview.mp4' if a.preview else 'final.mp4')
    scale = cfg['preview'] if a.preview else cfg['full']
    fps = cfg['fps']

    tmp = tempfile.mkdtemp(prefix='lf_')
    try:
        n = int(round((t1 - t0) * fps))
        jobs = max(1, min(a.jobs, n // fps or 1))
        cuts = [t0 + round(n * k / jobs) / fps for k in range(jobs + 1)]
        parts = [os.path.join(tmp, f'part{k:02d}.mp4') for k in range(jobs)]
        if jobs == 1:
            render_segment(style, shots, t0, t1, parts[0], scale)
        else:
            procs = [subprocess.Popen([sys.executable, os.path.abspath(make_file), '--_segment',
                                       f'{cuts[k]:.6f}', f'{cuts[k + 1]:.6f}', parts[k], '--_scale', str(scale)])
                     for k in range(jobs)]
            if any(p.wait() for p in procs):
                sys.exit('a render process failed')
        if jobs > 1:
            lst = os.path.join(tmp, 'list.txt')
            with open(lst, 'w') as f:
                f.write(''.join(f"file '{p}'\n" for p in parts))
            joined = os.path.join(tmp, 'joined.mp4')
            subprocess.run([ffmpeg(), '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', joined], check=True)
        else:
            joined = parts[0]
        finish(joined, song, t0, t1, out, a.fade_in, a.fade_out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'-> {out}   (song time {t0:.2f}–{t1:.2f} s)')

    if a.subs:
        srt = os.path.join(project_dir, 'work', 'lyrics.srt')
        if os.path.exists(srt):
            subs_out = os.path.splitext(out)[0] + '_subs.mp4'
            subprocess.run([sys.executable, os.path.join(HERE, 'lyrics_timing', 'burn_subtitles.py'), out, srt,
                            '--style', 'pixel' if style == 'pixel8bit' else 'flatq', '--offset', str(t0),
                            '--out', subs_out], check=True)
            print('   (the _subs copy is for the user to check timing; run review tools on the clean file)')
        else:
            print('(no work/lyrics.srt — skipped --subs)')
