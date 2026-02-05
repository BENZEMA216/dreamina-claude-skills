# Stable Diffusion Prompt 生成规则

为千川素材中需要 AI 图片的镜头生成 Stable Diffusion prompt。

## Prompt 结构

```
Positive: [主体], [场景], [光影], [风格], [质量词]
Negative: [排除内容]
```

## Positive Prompt 构成

### 质量词（固定前缀）
```
best quality, masterpiece, ultra detailed, professional photography, 8k uhd
```

### 主体描述
- 产品：材质、颜色、细节、放置方式
- 人物：1girl/1boy, [年龄描述], [表情], [动作], [服装]
- 必须用英文，越具体越好

### 场景与光影
- 场景：in modern kitchen, at office desk, in bathroom, outdoor park
- 光影：soft natural lighting, studio lighting, golden hour light, rim light

### 风格控制
- 写实：photorealistic, commercial photography, RAW photo
- 日系：japanese style, soft colors, film grain
- 质感：high contrast, vivid colors, muted tones

## Negative Prompt 模板

### 通用排除
```
worst quality, low quality, blurry, watermark, text, logo, deformed, ugly, duplicate, morbid, mutilated, extra fingers, poorly drawn hands, poorly drawn face, mutation, extra limbs, bad anatomy, bad proportions, disfigured, gross proportions
```

### 产品类补充
```
cropped, out of frame, low resolution, oversaturated
```

### 人物类补充
```
bad hands, missing fingers, extra digit, fewer digits, cross-eyed, bad eyes
```

## 推荐参数配置

| 参数 | 产品特写 | 生活场景 | 人物口播 |
|------|----------|----------|----------|
| 模型 | Realistic Vision v5.1 | DreamShaper v8 | ChilloutMix |
| 采样器 | DPM++ 2M Karras | Euler a | DPM++ SDE Karras |
| Steps | 30-40 | 25-35 | 30-40 |
| CFG | 7-8 | 6-7 | 7-8 |
| 尺寸 | 576x1024 (9:16) | 576x1024 (9:16) | 576x1024 (9:16) |

## 输出模板

```
--- 镜号 X：[画面描述摘要] ---

【Stable Diffusion Prompt】
Positive: [完整正面 prompt]
Negative: [完整负面 prompt]

推荐模型：[模型名]
采样器：[采样器]
Steps：[数值]
CFG：[数值]
尺寸：576x1024
Seed：-1（随机）

【ControlNet 建议】：[如需要姿势/构图控制，建议使用的 ControlNet 类型]
```

## 千川素材常用 Prompt 模式

### 产品特写
```
Positive: best quality, masterpiece, commercial product photography, [product] on [surface], [material details], soft studio lighting, clean white background, close-up, 8k uhd, sharp focus
Negative: [通用排除]
```

### 使用场景
```
Positive: best quality, photorealistic, [person description] using [product] in [location], natural daylight, lifestyle photography, warm tones, medium shot, RAW photo
Negative: [通用排除] + [人物排除]
```

### 产品平铺
```
Positive: best quality, flat lay photography, [products] arranged on [surface], overhead shot, soft even lighting, minimalist style, commercial photography
Negative: [通用排除] + perspective distortion, tilted angle
```
