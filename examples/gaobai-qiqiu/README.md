# 案例 · 《告白气球》（原唱 · 周杰伦）

**像素风 · 巴黎粉彩 · 甜歌** — 38 镜 · 3:36 · v3.1

![contact sheet](../../media/gaobai_sheet.jpg)

![clip](../../media/gaobai.gif)

> 原曲和歌词不在仓库里。下面的命令渲染的是**无声画面**；你有自己的音源时加 `--song`。
> The song and lyrics are not in this repo. Rendering is silent unless you pass your own audio with `--song`.

## 一句话立意
他准备了一只告白气球，整首歌都在等它"告白成功"。

## 值得看的地方
- **信物**：红色爱心气球是全片唯一的正红，也是"告白进度"的图标（5 格，最后一格落在她答应的那一拍）
- **重复句全部换新画面**：主歌 2、导歌 2 的每一句都和第一遍不同（晴天 → 雨天，写错名字 → 写对，一只气球 → 一整串），见 [`docs/LYRIC_SHOTS.md`](docs/LYRIC_SHOTS.md) 末尾
- **甜歌不压暗**：白天保持亮粉彩，只给黄昏和夜景布光；每个镜头加了云、花瓣、小气球、水面闪光
- **常驻界面改成"关键时刻出现"**：v1 右上角一直挂着进度条，v3.1 只在 5 次 +1 前后出现 3 秒

## v1 → v3.1
| | v1 | v3.1 |
|---|---|---|
| 镜头数 | 56 | 38（按乐句合并） |
| 告白进度 | 常驻右上角 | 只在 +1 时出现 |
| 画面上的字 | 很多（清单、牌子、对话） | 砍掉大部分 |
| 环境动态 | 少 | 每镜都有 |

## 指标（`tools/review/metrics.py --mood bright`）
| 平均镜头 | 饱和度 | 镜头内动态 | 几乎不动的秒数 |
|---|---|---|---|
| 5.3 s | 0.31 | 0.58 | 37 % |

粉彩风饱和度天然偏低；镜头内动态和静止秒数离参考值（≥ 1.0 / ≤ 20 %）还有距离 —— 这是这支片子还能继续改的地方，欢迎提 PR。

## 文件
- `docs/` — STORY（故事）、MUSIC_MAP（段落）、LYRIC_SHOTS（v1 逐句画面表）、STYLE_GUIDE（风格）、STORYBOARD（v3.1 实际镜头，从代码生成）
- `src/gb2.py` — v3.1 的 38 个镜头；`gbl.py` 本片零件（铁塔、楼房、咖啡馆、气球、进度条）；`g1–g5.py` v1 的场景函数（被 v3.1 复用）
- `shots.json` — 镜头表（给 `tools/review/shot_check.py` 用）

## 运行
```bash
cd examples/gaobai-qiqiu/src
python make.py --still 68                      # 看一帧
python make.py --start 23 --end 44 --preview   # 21 秒、720p、无声
python make.py --song 你的音源.mp3              # 整片 1080p 配原曲
python make_cover.py                           # 封面
```
