---
name: pull-film
description: 一键视频拉片分析工具。自动分析视频的镜头语言、构图、色彩和音频，生成专业的HTML可视化报告。当用户需要：(1) 分析视频镜头语言 (2) 拉片 (3) 生成视频分析报告 (4) 使用 /pull-film 命令时使用此技能。
---

# 一键视频拉片分析

自动分析视频的镜头语言、构图、色彩和音频，生成专业的 HTML 可视化报告。

## 触发条件

当用户请求以下内容时触发：
- "帮我分析/拉片这个视频"
- "分析视频的镜头语言"
- "/pull-film <视频路径或URL>"

## 输入要求

- 视频来源：本地文件路径（.mp4/.mkv/.avi/.mov）或在线 URL（YouTube/Bilibili 等）
- 可选参数：`--language <zh/en/ja>` 音频语言、`--output <目录>` 输出目录、`--no-audio` 跳过音频、`--max-scenes <数量>` 限制镜头数

## 依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| ffmpeg/ffprobe | 视频处理、抽帧 | `brew install ffmpeg` |
| Python3 + PIL | 色彩分析 | `pip3 install Pillow` |
| scenedetect | 镜头切分 | `pip3 install "scenedetect[opencv]"` |
| yt-dlp | 在线视频下载（可选） | `pip3 install yt-dlp` |
| whisper | 音频转录（可选） | `pip3 install openai-whisper` |

## 执行流程

### 第 1 步：环境检查

检查 ffmpeg、python3、scenedetect 是否已安装，缺少则提示用户安装。

### 第 2 步：处理视频输入

**本地视频** — 用 `ffprobe` 获取元信息（时长、分辨率、帧率、编码）

**在线视频** — 用 `yt-dlp` 下载后再处理：
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  --merge-output-format mp4 -o "<输出目录>/source_video.mp4" "<URL>"
```

### 第 3 步：创建输出目录结构

```bash
mkdir -p "<输出目录>"/{frames,data,audio}
```

### 第 4 步：镜头切分

使用 ffmpeg 的场景检测或 PySceneDetect：

**方法 A - 使用 ffmpeg 场景检测：**
```bash
ffmpeg -i "<视频>" -filter:v "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep showinfo
```

**方法 B - 使用 PySceneDetect（更准确）：**
```bash
python3 << 'EOF'
from scenedetect import detect, AdaptiveDetector
import json

scenes = detect("<视频路径>", AdaptiveDetector())
result = []
for i, (start, end) in enumerate(scenes, 1):
    result.append({
        "id": i,
        "start_time": start.get_seconds(),
        "end_time": end.get_seconds(),
        "start_frame": start.get_frames(),
        "end_frame": end.get_frames()
    })
print(json.dumps(result, indent=2))
EOF
```

将结果保存到 `<输出目录>/data/scenes.json`

### 第 5 步：提取关键帧

对每个镜头提取 3 帧（开头、中间、结尾）：

```bash
# 对于每个镜头
ffmpeg -ss <start_time> -i "<视频>" -vframes 1 -q:v 2 "<输出目录>/frames/scene_<ID>_start.jpg"
ffmpeg -ss <mid_time> -i "<视频>" -vframes 1 -q:v 2 "<输出目录>/frames/scene_<ID>_mid.jpg"
ffmpeg -ss <end_time-0.1> -i "<视频>" -vframes 1 -q:v 2 "<输出目录>/frames/scene_<ID>_end.jpg"
```

### 第 6 步：镜头分析（使用 Claude Vision）

对每个镜头的关键帧，使用 Read 工具读取图片，然后分析：

**分析内容：**

1. **景别 (Shot Scale)**
   - 特写：面部或物体细节填满画面
   - 近景：人物胸部以上
   - 中景：人物膝盖或腰部以上
   - 全景：完整人物或场景主体
   - 远景：广阔环境，人物占比小

2. **运动 (Camera Movement)**
   - 固定：机位不动
   - 推：向主体靠近
   - 拉：远离主体
   - 摇：水平转动
   - 移：横向或纵向移动
   - 跟：跟随运动物体
   - 升降：垂直升降
   - 手持：有明显晃动

3. **角度 (Camera Angle)**
   - 平视：与被摄对象平行
   - 仰视：从下往上拍
   - 俯视：从上往下拍
   - 荷兰角：画面倾斜

4. **构图 (Composition)**
   - 三分法、对称、引导线、框中框、对角线、中心构图

5. **色彩情绪**
   - 色温：冷色调/暖色调/中性
   - 整体氛围

### 第 7 步：色彩分析

使用 Python 提取主色调：

```bash
python3 << 'EOF'
import json
from PIL import Image
from collections import Counter
import colorsys

def analyze_colors(image_path, n_colors=5):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((100, 100))  # 缩小加速
    pixels = list(img.getdata())

    # 简化颜色（量化）
    def quantize(color):
        return tuple(c // 32 * 32 for c in color)

    quantized = [quantize(p) for p in pixels]
    counter = Counter(quantized)
    top_colors = counter.most_common(n_colors)

    # 转为 HEX
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(*c[0]) for c in top_colors]

    # 分析色温
    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)
    temperature = "暖色调" if avg_r > avg_b * 1.1 else ("冷色调" if avg_b > avg_r * 1.1 else "中性")

    return {"dominant": hex_colors, "temperature": temperature}

result = analyze_colors("<图片路径>")
print(json.dumps(result))
EOF
```

### 第 8 步：音频分析（可选）

如果没有 `--no-audio`：

```bash
# 提取音频
ffmpeg -i "<视频>" -vn -acodec pcm_s16le -ar 16000 -ac 1 "<输出目录>/audio/audio.wav"

# 使用 Whisper 转录（如果已安装）
python3 << 'EOF'
import whisper
import json

model = whisper.load_model("base")
result = model.transcribe("<输出目录>/audio/audio.wav", language="<语言>")

output = {
    "language": result.get("language", "unknown"),
    "segments": [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in result["segments"]],
    "full_text": result["text"]
}
print(json.dumps(output, ensure_ascii=False, indent=2))
EOF
```

将转录结果保存到 `<输出目录>/data/transcript.json`

### 第 9 步：生成 HTML 报告

创建一个包含以下内容的 HTML 报告：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>视频拉片报告 - [标题]</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* 现代化样式 */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 40px; border-radius: 12px; text-align: center; }
        .section { background: white; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .scene-card { border: 1px solid #eee; border-radius: 10px; margin: 15px 0; overflow: hidden; }
        .scene-header { background: #f8f9fa; padding: 15px; display: flex; justify-content: space-between; }
        .keyframes { display: flex; gap: 10px; }
        .keyframes img { width: 200px; height: 112px; object-fit: cover; border-radius: 6px; }
        .color-swatch { width: 30px; height: 30px; border-radius: 6px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎬 [视频标题]</h1>
            <p>时长: [时长] | 分辨率: [宽x高] | 镜头数: [数量]</p>
        </header>

        <div class="section">
            <h2>📊 统计概览</h2>
            <canvas id="scaleChart"></canvas>
            <canvas id="durationChart"></canvas>
        </div>

        <div class="section">
            <h2>🎞️ 拉片表</h2>
            <!-- 每个镜头的卡片 -->
            <div class="scene-card">
                <div class="scene-header">
                    <span>镜头 #1</span>
                    <span>0.00s - 3.50s</span>
                </div>
                <div class="scene-content">
                    <div class="keyframes">
                        <img src="frames/scene_001_start.jpg">
                        <img src="frames/scene_001_mid.jpg">
                        <img src="frames/scene_001_end.jpg">
                    </div>
                    <div class="analysis">
                        <p><strong>景别:</strong> 中景</p>
                        <p><strong>运动:</strong> 固定</p>
                        <p><strong>角度:</strong> 平视</p>
                        <p><strong>构图:</strong> 三分法</p>
                        <p><strong>色温:</strong> 暖色调</p>
                        <p><strong>主色调:</strong> <span class="color-swatch" style="background:#xxx"></span></p>
                        <p><strong>对白:</strong> "..."</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📝 完整对白</h2>
            <pre>[转录文本]</pre>
        </div>
    </div>

    <script>
        // Chart.js 图表代码
    </script>
</body>
</html>
```

将报告保存到 `<输出目录>/report.html`

### 第 10 步：输出结果

完成后告知用户：
- 报告路径：`<输出目录>/report.html`
- 镜头数量
- 总时长
- 是否包含音频转录

## 输出格式

```
<输出目录>/
├── report.html          # 主报告（浏览器打开）
├── frames/              # 关键帧截图
│   ├── scene_001_start.jpg
│   ├── scene_001_mid.jpg
│   └── ...
├── data/
│   ├── scenes.json      # 镜头数据
│   ├── analysis.json    # 分析结果
│   └── transcript.json  # 对白转录
└── audio/
    └── audio.wav        # 提取的音轨
```

## 示例

**用户输入：**
```
/pull-film ./movie.mp4
```

**用户输入：**
```
/pull-film https://www.youtube.com/watch?v=xxxxx --language zh
```

**用户输入：**
```
帮我分析一下这个视频的镜头语言 ./trailer.mp4
```

## 注意事项

1. 对于长视频（>10分钟），建议使用 `--max-scenes` 限制分析数量
2. Claude Vision 分析需要逐个读取关键帧图片
3. Whisper 转录在首次使用时会下载模型（约 150MB）
4. 在线视频下载依赖 yt-dlp，某些平台可能有限制
