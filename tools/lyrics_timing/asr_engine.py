# -*- coding: utf-8 -*-
"""Speech-recognition engine used by align_asr.py (Whisper + SenseVoice + optional Demucs).
语音识别引擎：Whisper 听写 + SenseVoice 补漏 + 可选 Demucs 人声分离，再把歌词逐行对齐到时间上。
Models are cached in LF_MODEL_DIR (default: ~/.cache/lyricframe).
"""
import os, re, sys, shutil

MODEL_DIR = os.environ.get('LF_MODEL_DIR', os.path.join(os.path.expanduser('~'), '.cache', 'lyricframe'))

PUNCT = '，。！？、；：,.!?;:"“”‘’（）()…—-~～ '


def add_cuda_dlls():
    """Windows：让 ctranslate2 找到 pip 装的 cuBLAS / cuDNN"""
    import site
    roots = []
    try: roots += site.getsitepackages()
    except Exception: pass
    try: roots.append(site.getusersitepackages())
    except Exception: pass
    roots.append(os.path.join(sys.prefix, 'Lib', 'site-packages'))
    for sp in roots:
        for sub in ('cublas', 'cudnn', 'cuda_nvrtc', 'cuda_runtime'):
            p = os.path.join(sp, 'nvidia', sub, 'bin')
            if os.path.isdir(p):
                try: os.add_dll_directory(p)
                except Exception: pass
                os.environ['PATH'] = p + os.pathsep + os.environ.get('PATH', '')


def to_simplified(s):
    try:
        import zhconv
        return zhconv.convert(s, 'zh-cn')
    except Exception:
        return s


def clean(s):
    return ''.join(ch for ch in s if ch not in PUNCT).strip()


def ts(x):
    x = max(0.0, x)
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    ms = int(round((s - int(s)) * 1000))
    if ms == 1000: ms = 999
    return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"


def parse_ts(s):
    h, m, rest = s.strip().split(':')
    sec, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def read_srt(path):
    txt = open(path, encoding='utf-8-sig').read().replace('\r\n', '\n')
    out = []
    for block in re.split(r'\n\s*\n', txt.strip()):
        lines = block.strip().split('\n')
        if len(lines) < 2 or '-->' not in lines[1]: continue
        a, b = lines[1].split('-->')
        out.append([parse_ts(a), parse_ts(b), '\n'.join(lines[2:])])
    return out


def write_srt(path, entries):
    with open(path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        for i, (a, b, t) in enumerate(entries, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")


def load_model(model_name):
    add_cuda_dlls()
    from faster_whisper import WhisperModel
    for dev, ct in (('cuda', 'float16'), ('cpu', 'int8')):
        try:
            print(f'加载模型 {model_name}（{dev}）……第一次会自动下载，请耐心等。')
            m = WhisperModel(model_name, device=dev, compute_type=ct)
            if dev == 'cuda':   # 真跑一小段确认显卡可用
                import numpy as np
                list(m.transcribe(np.zeros(16000, np.float32), language='zh')[0])
            return m, dev
        except Exception as e:
            print(f'  {dev} 不可用：{str(e)[:160]}')
    raise SystemExit('模型加载失败 / model failed to load — see the error above')


def load_audio(path, sr=16000):
    """自己解码成 16kHz 单声道（避开 faster-whisper 和新版 PyAV 的接口不兼容）"""
    import av, numpy as np
    chunks = []
    with av.open(str(path)) as c:
        st = next(s for s in c.streams if s.type == 'audio')
        rs = av.AudioResampler(format='s16', layout='mono', rate=sr)
        for frame in c.decode(st):
            for f in rs.resample(frame):
                chunks.append(f.to_ndarray().reshape(-1))
        for f in rs.resample(None):
            chunks.append(f.to_ndarray().reshape(-1))
    a = np.concatenate(chunks).astype(np.float32) / 32768.0
    return a


BANNED = ('amara', '字幕', '订阅', '点赞', '转发', '打赏', '谢谢观看', '感谢观看', '明镜', '栏目',
          '请不吝', '由社群', '社区提供', 'org', '优优独播', '本节目')


def is_hallucination(text):
    t = text.lower().replace(' ', '')
    return any(b in t for b in BANNED)


def separate_vocals(path):
    """用 Demucs 把人声从伴奏里分离出来（CPU 也能跑，一首歌一两分钟）。失败就返回 None，直接用原音频。"""
    import hashlib
    import numpy as np
    cache_dir = os.path.join(MODEL_DIR, 'vocals_cache')
    os.makedirs(cache_dir, exist_ok=True)
    h = hashlib.md5((os.path.abspath(path) + str(os.path.getsize(path))).encode('utf-8')).hexdigest()[:16]
    cache = os.path.join(cache_dir, h + '.npy')
    if os.path.exists(cache):
        print('  人声分离：用上次的缓存')
        return np.load(cache)
    try:
        import torch
        from demucs.pretrained import get_model
        from demucs.apply import apply_model
        import julius
    except Exception as e:
        import traceback
        print(f'  （人声分离组件加载失败，跳过：{e!r}）')
        traceback.print_exc(file=sys.stdout)
        return None
    try:
        print('  人声分离（Demucs）……第一次会下载约 80MB 的分离模型')
        os.environ.setdefault('TORCH_HOME', os.path.join(MODEL_DIR, 'torch'))
        model = get_model('htdemucs'); model.eval()
        sr = model.samplerate
        import av
        chunks = []
        with av.open(str(path)) as c:
            st = next(s for s in c.streams if s.type == 'audio')
            rs = av.AudioResampler(format='fltp', layout='stereo', rate=sr)
            for fr in c.decode(st):
                for f in rs.resample(fr): chunks.append(f.to_ndarray())
            for f in rs.resample(None): chunks.append(f.to_ndarray())
        wav = torch.from_numpy(np.concatenate(chunks, axis=1).astype(np.float32))
        ref = wav.mean(0)
        mu, sd = ref.mean(), ref.std() + 1e-8
        dev = 'cuda' if torch.cuda.is_available() else 'cpu'
        with torch.no_grad():
            out = apply_model(model, ((wav - mu) / sd)[None], device=dev, split=True, overlap=0.25, progress=True)[0]
        voc = out[model.sources.index('vocals')] * sd + mu
        voc16 = julius.resample_frac(voc.mean(0), sr, 16000).numpy().astype(np.float32)
        np.save(cache, voc16)
        return voc16
    except Exception as e:
        import traceback
        print(f'  人声分离失败，改用原音频：{e!r}')
        traceback.print_exc(file=sys.stdout)
        return None


def transcribe(model, audio, offset=0.0, use_sep=True):
    pcm = separate_vocals(audio) if use_sep else None
    if pcm is None:
        print('  解码音频……')
        pcm = load_audio(audio)
    print(f'  音频时长 {len(pcm) / 16000:.1f} 秒，开始识别')
    # 现场版 / 伴奏很响的歌：不用 VAD（它常把唱歌当成噪音剪掉），也不跳过「疑似无人声」的段落；
    # 按 20 秒一段切开逐段识别，避免 Whisper 在一段长音后提前收工
    sr = 16000
    win, hop = 20.0, 18.0
    total = len(pcm) / sr
    words = []
    dropped = [0]
    t0 = 0.0
    while t0 < total - 0.5:
        seg_pcm = pcm[int(t0 * sr):int(min(total, t0 + win) * sr)]
        segs, info = model.transcribe(
            seg_pcm, language='zh', task='transcribe', beam_size=5,
            vad_filter=False, no_speech_threshold=None, log_prob_threshold=None,
            word_timestamps=True, condition_on_previous_text=False,
            initial_prompt='以下是一首中文流行歌曲的歌词，请用简体中文。')
        keep_from = 0.0 if t0 == 0 else (win - hop) / 2      # 重叠部分各取一半
        keep_to = win if t0 + win >= total else win - (win - hop) / 2
        for seg in segs:
            if is_hallucination(seg.text):
                dropped[0] += 1; continue
            for w in (seg.words or []):
                if not (keep_from <= w.start < keep_to): continue
                t = clean(to_simplified(w.word))
                t = re.sub(r'[A-Za-z0-9]', '', t)
                if t: words.append((w.start + t0 + offset, w.end + t0 + offset, t))
        print(f'  识别到 {min(total, t0 + win):6.1f} / {total:.1f} 秒，累计 {len(words)} 个字', end='\r')
        t0 += hop
    words.sort()
    print(f'\n  Whisper 识别完成：{len(words)} 个字词（过滤掉 {dropped[0]} 段疑似幻觉，如「字幕由 Amara 提供」）')
    return words, pcm


# ---------------------------------------------------------------- 第二个识别引擎：SenseVoice（不会编「字幕由 Amara 提供」，补 Whisper 漏掉的句子）
SV_REPO = 'csukuangfj/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17'


SV_URL = 'https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2'


def sv_files():
    """先找本地，再走 hf-mirror，最后从 GitHub 下载压缩包。返回 (model, tokens) 或 None"""
    here = MODEL_DIR
    local = os.path.join(here, 'sensevoice')
    m, t = os.path.join(local, 'model.int8.onnx'), os.path.join(local, 'tokens.txt')
    if os.path.exists(m) and os.path.exists(t): return m, t
    try:
        from huggingface_hub import hf_hub_download
        print('  下载 SenseVoice 模型（约 230MB，只下一次）……')
        return hf_hub_download(SV_REPO, 'model.int8.onnx'), hf_hub_download(SV_REPO, 'tokens.txt')
    except Exception as e:
        print(f'  镜像下载失败（{str(e)[:60]}），改从 GitHub 下载……')
    try:
        import urllib.request, tarfile
        os.makedirs(local, exist_ok=True)
        arc = os.path.join(here, 'sensevoice.tar.bz2')
        def hook(n, bs, total):
            if total > 0 and n % 50 == 0: print(f'    {n * bs / 1e6:.0f} / {total / 1e6:.0f} MB', end='\r')
        urllib.request.urlretrieve(SV_URL, arc, hook)
        with tarfile.open(arc, 'r:bz2') as tf:
            for mem in tf.getmembers():
                name = os.path.basename(mem.name)
                if name in ('model.int8.onnx', 'tokens.txt'):
                    with tf.extractfile(mem) as src, open(os.path.join(local, name), 'wb') as dst:
                        shutil.copyfileobj(src, dst)
        os.remove(arc)
        if os.path.exists(m) and os.path.exists(t): return m, t
    except Exception as e:
        print(f'  GitHub 下载也失败：{e!r}')
    return None


def load_sensevoice():
    try:
        import sherpa_onnx
    except Exception as e:
        print(f'  （没装 SenseVoice，跳过：{e!r}）'); return None
    f = sv_files()
    if not f:
        print('  SenseVoice 不可用，只用 Whisper'); return None
    try:
        print('  加载 SenseVoice……')
        return sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f[0], tokens=f[1], language='zh', use_itn=False, num_threads=4)
    except Exception as e:
        import traceback
        print(f'  SenseVoice 加载失败，跳过：{e!r}'); traceback.print_exc(file=sys.stdout)
        return None


def sensevoice_words(rec, pcm, offset=0.0, sr=16000):
    """8 秒一窗、4 秒一跳，每窗只取中间 4 秒的字，避开窗口边缘丢字"""
    words = []
    total = len(pcm) / sr
    t0 = 0.0
    while t0 < total:
        st = rec.create_stream()
        st.accept_waveform(sr, pcm[int(t0 * sr):int(min(total, t0 + 8) * sr)])
        rec.decode_stream(st)
        lo = 0.0 if t0 == 0 else 2.0
        hi = 8.0 if t0 + 8 >= total else 6.0
        for tk, ts in zip(st.result.tokens, st.result.timestamps):
            c = re.sub(r'[A-Za-z0-9]', '', clean(to_simplified(tk)))
            if c and lo <= ts < hi:
                words.append((t0 + ts + offset, t0 + ts + 0.3 + offset, c))
        t0 += 4.0
    words.sort()
    print(f'  SenseVoice 识别：{len(words)} 个字')
    return words


def merge_fill(entries, w_words, s_words):
    """每一格分别用两个引擎填，Whisper 字数够（≥ SenseVoice 的 70%）就用 Whisper，否则用 SenseVoice。"""
    a, _ = fill_template(entries, w_words)
    if not s_words:
        return a, [i + 1 for i, e in enumerate(a) if '✎' in e[2]], [0, 0]
    b, _ = fill_template(entries, s_words)
    out, used = [], [0, 0]
    for ea, eb in zip(a, b):
        na = 0 if '✎' in ea[2] else len(ea[2].replace('\n', ''))
        nb = 0 if '✎' in eb[2] else len(eb[2].replace('\n', ''))
        if na >= 0.7 * nb and na > 0:
            out.append(ea); used[0] += 1
        elif nb > 0:
            out.append(eb); used[1] += 1
        else:
            out.append(ea)
    empty = [i + 1 for i, e in enumerate(out) if '✎' in e[2]]
    return out, empty, used


# ---------------------------------------------------------------- 有歌词文件（.lrc / .txt）时：用识别结果给每一行歌词对时间
def read_lyrics_file(path):
    """读 .lrc 或纯文本歌词，返回 [(lrc_time 或 None, 文本)]，去掉作词作曲等信息行"""
    raw = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'gb18030', 'utf-16'):
        try: txt = raw.decode(enc); break
        except Exception: continue
    out = []
    meta = ('作词', '作曲', '编曲', '制作', '演唱', '词：', '曲：', '词:', '曲:', '混音', '母带', '监制', '出品', '和声', '吉他', '贝斯', '鼓', '录音', 'OP', 'SP', '：', ':')
    for line in txt.replace('\r', '').split('\n'):
        tags = re.findall(r'\[(\d+):(\d+(?:\.\d+)?)\]', line)
        text = re.sub(r'\[[^\]]*\]', '', line).strip()
        if not text: continue
        if re.match(r'^\[?(ti|ar|al|by|offset|length)[:：]', line.strip(), re.I): continue
        if any(m in text for m in meta[:16]) and len(text) < 30 and ('：' in text or ':' in text): continue
        if tags:
            for mm, ss in tags: out.append((int(mm) * 60 + float(ss), text))
        else:
            out.append((None, text))
    out.sort(key=lambda x: (x[0] is None, x[0] or 0))
    return out


def chars_with_times(words):
    """把识别结果拆成单个字，每个字一个时间"""
    cs = []
    for a, b, t in words:
        n = len(t)
        for k, ch in enumerate(t):
            cs.append((a + (b - a) * k / max(1, n), ch))
    cs.sort()
    return cs


def dp_align(lyr, rec):
    """半全局序列对齐（两头空缺不扣分）：歌词字 vs 识别字，严格按顺序，返回 {歌词下标: 识别下标}"""
    import numpy as np
    n, m = len(lyr), len(rec)
    if n == 0 or m == 0: return {}
    MATCH, MIS, GAP_REC, GAP_LYR = 2.0, -1.0, -0.4, -0.9
    S = np.zeros((n + 1, m + 1), np.float32)
    T = np.zeros((n + 1, m + 1), np.int8)   # 0 斜，1 上（跳过歌词字），2 左（跳过识别字）
    T[1:, 0] = 1; T[0, 1:] = 2
    rec_arr = np.array([ord(c) for c in rec])
    for i in range(1, n + 1):
        eq = (rec_arr == ord(lyr[i - 1]))
        diag = S[i - 1, :-1] + np.where(eq, MATCH, MIS)
        up = S[i - 1, 1:] + GAP_LYR
        best = np.maximum(diag, up)
        tb = np.where(diag >= up, 0, 1).astype(np.int8)
        row = S[i]; trow = T[i]
        row[0] = 0.0
        prev = 0.0
        for j in range(1, m + 1):
            v = best[j - 1]; t = tb[j - 1]
            l = prev + GAP_REC
            if l > v: v, t = l, 2
            row[j] = v; trow[j] = t; prev = v
    i_end = int(np.argmax(S[:, m])); j_end = m
    if S[n].max() > S[i_end, m]:
        i_end, j_end = n, int(np.argmax(S[n]))
    match = {}
    i, j = i_end, j_end
    while i > 0 and j > 0:
        t = T[i, j]
        if t == 0:
            if lyr[i - 1] == rec[j - 1]: match[i - 1] = j - 1
            i -= 1; j -= 1
        elif t == 1: i -= 1
        else: j -= 1
    return match


def align_lines(lines, words):
    cs = chars_with_times(words)
    rec = ''.join(ch for _, ch in cs)
    lyr, owner = [], []
    for i, (_, text) in enumerate(lines):
        for ch in clean(to_simplified(text)):
            lyr.append(ch); owner.append(i)
    match = dp_align(lyr, rec)
    hit = [[] for _ in lines]
    for x, y in match.items():
        hit[owner[x]].append(cs[y][0])
    res = []
    for i, (_, text) in enumerate(lines):
        n = max(1, len(clean(text)))
        h = sorted(hit[i])
        if len(h) >= max(2, n * 0.3):
            res.append([h[0], h[-1], len(h) / n])
        else:
            res.append([None, None, len(h) / n])
    return res


def select_window(lines, words):
    return 0, len(lines)


def build_from_lyrics(lines, words_list, total):
    """words_list: 各引擎的识别结果。返回 (srt 条目, 每行匹配率, .lrc 偏移, 用到的行号范围)"""
    lines = [l for l in lines if clean(l[1])]
    ref = max(words_list, key=lambda w: len(w or []))
    a0, b0 = select_window(lines, ref or [])
    lines = lines[a0:b0]
    best, best_score = None, -1
    for ws in words_list:            # 整首只用一个引擎（逐行混选会让时间前后乱跳）
        if not ws: continue
        al = align_lines(lines, ws)
        sc = sum(r for s_, e_, r in al if s_ is not None)
        if sc > best_score: best, best_score = al, sc
    if best is None: best = [[None, None, 0.0] for _ in lines]
    good = [i for i, b in enumerate(best) if b[0] is not None and b[2] >= 0.35]
    mono, last = [], -1.0
    for i in good:
        if best[i][0] >= last - 0.1:
            mono.append(i); last = best[i][0]
    good = mono
    if good:
        keep = set(good)
        # 两个对上的行之间没对上的行：时间够放才保留（避免副歌重复时挤成一团）
        for p, q in zip(good, good[1:]):
            gap = best[q][0] - best[p][1]
            mids = list(range(p + 1, q))
            if mids and gap >= 1.5 * len(mids):
                for k, i in enumerate(mids, 1):
                    best[i][0] = best[p][1] + gap * k / (len(mids) + 1) - 0.5
                    best[i][1] = None
                    keep.add(i)
        idx = sorted(keep)
    else:
        idx = []
    offs = [best[i][0] - lines[i][0] for i in good if lines[i][0] is not None and best[i][2] >= 0.5]
    off = sorted(offs)[len(offs) // 2] if offs else 0.0
    out, ratios = [], []
    for n, i in enumerate(idx):
        a = max(0.0, best[i][0] - 0.2)
        nxt = best[idx[n + 1]][0] - 0.2 if n + 1 < len(idx) else total
        end = best[i][1] + 0.9 if best[i][1] is not None else a + 3.0
        end = min(max(end, a + 1.0), nxt - 0.05, a + 9.0, total)
        if end <= a: end = a + 0.8
        out.append([a, end, lines[i][1].strip()])
        ratios.append(round(best[i][2], 2))
    rng_ = (idx[0] + 1, idx[-1] + 1) if idx else (0, 0)
    return out, ratios, off, rng_


