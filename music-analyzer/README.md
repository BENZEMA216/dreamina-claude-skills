# music-analyzer

Claude Code 插件 — 分析本地音频文件，提取结构化音乐特征，生成 Dreamina 生图 prompt 与分镜表。

```
音频文件 (MP3/WAV/FLAC)
    │
    ▼
python3 -m music_analyzer analyze song.mp3
    │
    ├─ analysis.json ──→ /music-to-dreamina  ──→ Dreamina prompts
    │                ──→ /music-to-storyboard ──→ 分镜表 JSON
    │                ──→ /music-color-palette  ──→ 配色方案
    │
    └─ 独立分析: /music-rhythm · /music-emotion · /music-timbre · /music-tonality · /music-lyrics
```

## 安装

```bash
# 基础安装 (librosa, ~50MB)
pip install -e ~/.claude/plugins/music-analyzer/src/

# 完整安装 (含 demucs/whisper/CLAP, ~2GB)
pip install -e "~/.claude/plugins/music-analyzer/src/[full]"
```

## 使用

在 Claude Code 中直接调用 skill 命令：

```
/music-analyze ~/Music/song.mp3
/music-to-dreamina ~/Music/song.mp3
/music-to-storyboard /tmp/song_analysis.json
```

或通过命令行：

```bash
python3 -m music_analyzer analyze song.mp3 -o analysis.json
python3 -m music_analyzer dreamina analysis.json -o dreamina.json
python3 -m music_analyzer storyboard analysis.json -o storyboard.json
python3 -m music_analyzer color-palette analysis.json

# 生成 HTML 可视化报告（自动打开浏览器）
python3 -m music_analyzer visualize song.mp3 --open
```

子命令：`analyze` · `rhythm` · `emotion` · `timbre` · `tonality` · `lyrics` · `dreamina` · `storyboard` · `color-palette` · `visualize`

## HTML 可视化报告

`visualize` 命令生成一个自包含的单文件 HTML 报告，包含：

- 概览仪表盘（BPM / 调性 / 情绪 / 能量）
- Beat Grid 节拍可视化 + 段落色带
- 情绪仪表（能量 / 效价 / 唤醒度）+ 能量曲线柱状图
- 音色雷达（亮度 / 温暖度 / 频谱参数）
- 和弦进行流
- 配色方案大色块
- Dreamina Prompt 卡片（点击复制，中英双语）
- 分镜表（镜头类型 / 运动 / 转场 / 视觉描述）

```bash
python3 -m music_analyzer visualize song.mp3 --open
```

## 分析输出示例

以窦靖童《烟花》为例：

| 维度 | 结果 |
|------|------|
| 节奏 | 129.2 BPM, 4/4 拍, 20 个结构段 |
| 情绪 | uplifting, 能量 45%, 效价 +0.20 |
| 调性 | C# major (置信度 75%) |
| 音色 | 温暖度 0.85, 亮度 0.12, 动态范围 25.8dB |
| 起始点 | 1140 个, 密度 3.64/s |

### Dreamina Prompt (副歌段)

```json
{
  "section": "chorus_1",
  "time_range": {"start": 152.88, "end": 160.29},
  "prompt_zh": "阳光金色，向上运动感，温暖明亮，动态构图，强对比...",
  "prompt_en": "golden sunlight, upward motion, warm and bright, dynamic composition...",
  "color_palette": ["#FFD700", "#FFA500", "#FF8C00", "#FFFACD"],
  "energy_level": 0.59
}
```

### 分镜表 (Storyboard)

| # | 段落 | 时间 | 镜头 | 运动 | 转场 |
|---|------|------|------|------|------|
| 1 | intro | 0:00-0:00 | wide | slow dolly in | fade |
| 2 | verse | 0:00-0:15 | medium | static | cut |
| ... | ... | ... | ... | ... | ... |
| 20 | outro | 4:59-5:13 | wide | slow dolly out | fade |

## 依赖分层

| 层级 | 依赖 | 功能 |
|------|------|------|
| **lite** | librosa, numpy, scipy, pydantic, soundfile, matplotlib | 节奏 / 调性 / 频谱 / 起始点 |
| **standard** | + essentia, pyloudnorm | 更精准的和弦 / 结构检测 |
| **full** | + demucs, faster-whisper, laion-clap | 音源分离 / 歌词转录 / AI 情绪分类 |

每个分析器在高级依赖缺失时自动降级到 librosa-only 方案。

## Dreamina 映射逻辑

| 音乐特征 | 视觉参数 | 映射 |
|----------|---------|------|
| 情绪 | 风格关键词 | happy → 明亮暖色调; sad → 冷色调阴影 |
| 能量 | 构图强度 | 高 → 动态对比; 低 → 宁静开阔 |
| BPM | 节奏描述 | >140 → 激烈闪烁; <100 → 舒缓流动 |
| 调式 | 明暗基调 | 大调 → 明亮开放; 小调 → 戏剧暗调 |
| 流派 | 视觉风格 | 电子 → 赛博霓虹; 爵士 → 烟雾温暖 |
| 段落 | 场景序列 | 副歌 → 更强烈视觉 |

## 项目结构

```
music-analyzer/
├── CLAUDE.md                              # 插件说明
├── .claude-plugin/plugin.json             # 插件清单
├── .claude/skills/                        # 9 个 Skill
│   ├── music-analyze/SKILL.md             # 主入口：完整分析
│   ├── music-rhythm/SKILL.md              # 节奏与结构
│   ├── music-emotion/SKILL.md             # 情绪与风格
│   ├── music-timbre/SKILL.md              # 音色与频谱
│   ├── music-tonality/SKILL.md            # 调性与和弦
│   ├── music-lyrics/SKILL.md              # 歌词转录
│   ├── music-to-dreamina/SKILL.md         # → Dreamina prompt
│   ├── music-to-storyboard/SKILL.md       # → 分镜表
│   └── music-color-palette/SKILL.md       # → 配色方案
└── src/music_analyzer/
    ├── cli.py                             # CLI 入口
    ├── models.py                          # Pydantic 数据模型
    ├── config.py                          # 依赖检测与配置
    ├── analyzers/
    │   ├── rhythm.py                      # BPM / 节拍 / 结构分段
    │   ├── emotion.py                     # CLAP 情绪分类 + 启发式降级
    │   ├── timbre.py                      # MFCC / 频谱 / Demucs 分离
    │   ├── tonality.py                    # 调性 / 和弦 (Essentia 降级)
    │   ├── lyrics.py                      # faster-whisper 歌词转录
    │   └── onset.py                       # 起始点检测
    ├── formatters/
    │   ├── dreamina_formatter.py          # 音乐特征 → Dreamina prompt
    │   ├── storyboard_formatter.py        # 段落 → 镜头分镜表
    │   ├── color_palette.py               # 情绪 + 调式 → 配色
    │   ├── json_formatter.py              # 通用 JSON 输出
    │   └── html_report.py                 # HTML 可视化报告生成
    └── utils/
        ├── audio_io.py                    # 音频加载 / 格式检测
        ├── cache.py                       # 分析结果缓存
        └── visualization.py              # 频谱图 / 波形图导出
```

## License

MIT
