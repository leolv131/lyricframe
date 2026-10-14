"""Richness check (workflow v4, rule 11): is there enough detail, colour, texture, light and camera
movement? 丰富度自查（工作流 v4 规则 11）：细节、颜色、纹理、明暗起伏、镜头运动够不够。

    python richness.py out/final.mp4
    python richness.py out/final.mp4 --ref reference.mp4      # thresholds = max(default, reference)
    python richness.py out/ch3.mp4 --no-camera                # picture metrics only (faster)

  detail        median edge density of frames (Canny, %)                      default >= 5
  colors        median number of colours covering > 0.2 % of a frame          default >= 30
  textured      median share of 16x16 blocks with real texture (std > 8, %)   default >= 50
  light_range   std of mean brightness across the film (light rising/falling) default >= 25
  camera_move   share of sampled moments where the camera zooms or pans (%)   default >= 50
                (reported separately as zooming % and panning %)

Frames are sampled every 3 s at 640x360 (letterbox bars and near-flat frames such as black cards are
skipped). Camera movement is estimated every 4 s by matching ORB features between two frames 0.5 s
apart. A clip of a few minutes takes well under a minute.

Measured once on well-received code-drawn MVs (for orientation, not as targets):
  detailed pixel MV        detail 8.0  colors 35  textured 70 %  light_range 34  zoom 10 %  pan 14 %
  cinematic, much blur     detail 4.0  colors 35  textured 49 %  light_range 47  zoom 64 %  pan 81 %
  a flat early attempt     detail 3.5  colors 25  textured 35 %  light_range 12  zoom  9 %  pan 23 %

Needs numpy, opencv-python-headless and ffmpeg.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from lf_common import ffmpeg, duration  # noqa: E402

try:
    import cv2
except ImportError:
    sys.exit('needs OpenCV: pip install opencv-python-headless')

W, H = 640, 360
DEFAULT = dict(detail=5.0, colors=30, textured=50.0, light_range=25.0, camera_move=50.0)


def _frames(path, step):
    p = subprocess.Popen([ffmpeg(), '-v', 'error', '-i', path, '-vf', f'fps=1/{step},scale={W}:{H}',
                          '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def picture(path, step=3.0):
    E, C, T, L = [], [], [], []
    for im in _frames(path, step):
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        rows = np.where(g.mean(1) > 12)[0]          # crop letterbox bars
        if len(rows) < 50:
            continue
        im, g = im[rows[0]:rows[-1] + 1], g[rows[0]:rows[-1] + 1]
        if g.std() < 6:                              # title / black cards
            continue
        e = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 60, 140)
        E.append(e.mean() / 255 * 100)
        q = (im // 32).reshape(-1, 3)
        _, cnt = np.unique(q, axis=0, return_counts=True)
        C.append(int((cnt > q.shape[0] * 0.002).sum()))
        h, w = g.shape
        blk = g[:h // 16 * 16, :w // 16 * 16].reshape(h // 16, 16, w // 16, 16).std(axis=(1, 3))
        T.append((blk > 8).mean() * 100)
        L.append(g.mean())
    if not E:
        return None
    return dict(frames=len(E), detail=round(float(np.median(E)), 2), colors=int(np.median(C)),
                textured=round(float(np.median(T)), 1), light_range=round(float(np.std(L)), 1),
                detail_p10=round(float(np.percentile(E, 10)), 2))


def _gray_at(path, t):
    b = subprocess.run([ffmpeg(), '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1',
                        '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                       capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(H, W) if len(b) == W * H else None


def camera(path, every=4.0, gap=0.5):
    dur = duration(path) or 0
    orb = cv2.ORB_create(1500)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    zs, pans = [], []
    for t in np.arange(min(2.0, dur / 4), max(dur - gap - 0.1, 0), every):
        a, b = _gray_at(path, t), _gray_at(path, t + gap)
        if a is None or b is None:
            continue
        ka, da = orb.detectAndCompute(a, None)
        kb, db = orb.detectAndCompute(b, None)
        if da is None or db is None or len(ka) < 30 or len(kb) < 30:
            continue
        m = bf.match(da, db)
        if len(m) < 25:
            continue
        pa = np.float32([ka[x.queryIdx].pt for x in m])
        pb = np.float32([kb[x.trainIdx].pt for x in m])
        M, inl = cv2.estimateAffinePartial2D(pa, pb, ransacReprojThreshold=2)
        if M is None or inl.sum() < 20:
            continue
        zs.append(abs(np.hypot(M[0, 0], M[1, 0]) - 1))
        pans.append(np.hypot(M[0, 2], M[1, 2]))
    if not zs:
        return dict(samples=0, zooming=0, panning=0, camera_move=0)
    zs, pans = np.array(zs), np.array(pans)
    zoom, pan = zs > 0.004, pans > 1
    return dict(samples=len(zs), zooming=round(float(zoom.mean() * 100)),
                panning=round(float(pan.mean() * 100)), camera_move=round(float((zoom | pan).mean() * 100)))


def analyse(path, with_camera=True):
    r = picture(path) or {}
    if with_camera:
        r.update(camera(path))
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video')
    ap.add_argument('--ref', action='append', default=[], help='reference video(s); raises thresholds to their values')
    ap.add_argument('--no-camera', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    ours = analyse(a.video, not a.no_camera)
    refs = {os.path.basename(p): analyse(p, not a.no_camera) for p in a.ref}
    need = dict(DEFAULT)
    for r in refs.values():
        for k in need:
            if k in r:
                need[k] = max(need[k], r[k])
    if a.json:
        print(json.dumps(dict(video=ours, refs=refs, thresholds=need), ensure_ascii=False, indent=1))
        return
    if not ours:
        sys.exit('no usable frames')
    print(f'{os.path.basename(a.video)}  ({ours.get("frames", 0)} frames sampled)')
    for k, label in [('detail', 'detail 细节量'), ('colors', 'colors 颜色数'), ('textured', 'textured 纹理区块 %'),
                     ('light_range', 'light_range 明暗起伏'), ('camera_move', 'camera_move 镜头推拉+横移 %')]:
        if k not in ours:
            continue
        ok = ours[k] >= need[k]
        print(f'  {label:<28} {ours[k]:>7}   need >= {need[k]:<6} {"ok" if ok else "LOW → rework"}')
    if 'zooming' in ours:
        print(f'  (zooming {ours["zooming"]} %, panning {ours["panning"]} %, {ours["samples"]} samples)')
    for n, r in refs.items():
        print(f'  ref {n}: ' + ', '.join(f'{k} {r[k]}' for k in ('detail', 'colors', 'textured', 'light_range', 'camera_move') if k in r))


if __name__ == '__main__':
    main()
