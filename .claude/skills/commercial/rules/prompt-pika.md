# Pika Prompt 生成规则

为千川素材生成 Pika 的视频 Prompt。Pika 使用英文 prompt，擅长短时长、高质量的视频片段生成。

## Pika 特点

- 擅长：短视频片段、产品展示、简单运动
- 时长：3s（默认）
- 支持图生视频（Image to Video）
- 特色功能：Lip Sync（口型同步）、Modify Region（局部修改）

## Prompt 结构

```
[主体描述], [动作/运动], [场景/光影], [风格]
```

## 参数说明

| 参数 | 说明 | 千川素材推荐 |
|------|------|--------------|
| Motion Strength | 运动强度 1-4 | 2（产品展示）/ 3（场景动态） |
| Camera | 镜头运动 | 按需选择 |
| Aspect Ratio | 画面比例 | 9:16（竖屏） |
| Negative Prompt | 排除内容 | blurry, distorted, low quality |

## Camera 运动选项

| 选项 | 效果 | 适用场景 |
|------|------|----------|
| None | 无镜头运动 | 主体运动为主 |
| Pan Left/Right | 左右平移 | 横向展示 |
| Tilt Up/Down | 上下摇移 | 纵向展示 |
| Zoom In/Out | 推进/拉远 | 聚焦/展示全貌 |
| Rotate CW/CCW | 顺/逆时针旋转 | 特殊效果 |

## 输出模板

```
--- 镜号 X：[画面描述摘要] ---

【Pika Prompt】
[完整英文 prompt]

Motion Strength: [1-4]
Camera: [None/Pan Left/Pan Right/Tilt Up/Tilt Down/Zoom In/Zoom Out]
Aspect Ratio: 9:16
Negative Prompt: blurry, distorted, low quality, watermark

【Image to Video 建议】：[是否建议使用 I2V 模式]
```

## 千川素材常用 Prompt 模式

### 产品微动展示
```
A [product] on [surface], subtle light reflections moving across the surface, soft studio lighting, commercial photography style

Motion Strength: 1
Camera: None
```
适用：产品特写，只需轻微光影变化

### 产品旋转
```
A [product] slowly rotating on a clean background, professional product photography, soft even lighting

Motion Strength: 2
Camera: None
```
适用：需要展示产品多角度

### 场景动态
```
[Person/hands] [action with product] in [setting], natural lighting, lifestyle photography style

Motion Strength: 3
Camera: Zoom In
```
适用：使用场景演示

### 质地流动
```
[Cream/liquid/texture] slowly flowing, macro shot, dramatic lighting, beauty commercial style

Motion Strength: 2
Camera: None
```
适用：护肤品、食品等质地展示

### 氛围动态
```
[Product] in [atmospheric setting], [environmental movement like curtain blowing, light rays moving], cinematic mood

Motion Strength: 2
Camera: Pan Right
```
适用：氛围感产品图

## Pika Lip Sync 功能

Pika 支持口型同步，适用于：
- 数字人口播素材
- 需要人物说话的场景

使用方式：
1. 上传静态人物图片
2. 上传音频文件
3. Pika 自动生成对应口型的视频

## Pika vs 其他工具选择

| 需求 | 推荐工具 | 原因 |
|------|----------|------|
| 快速迭代测试 | Pika | 生成速度快，3秒片段 |
| 产品微动效果 | Pika | Motion Strength 1-2 效果自然 |
| 口型同步 | Pika | Lip Sync 功能成熟 |
| 长时长视频 | Runway/可灵 | Pika 默认只有3秒 |
| 复杂镜头运动 | Runway | Pika 镜头运动相对简单 |
| 精确首尾帧控制 | 可灵 | Pika 不支持尾帧指定 |
