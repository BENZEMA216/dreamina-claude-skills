# Midjourney Prompt 生成规则

为千川素材中需要 AI 图片的镜头生成 Midjourney prompt。

## Prompt 结构

```
[主体描述], [场景环境], [光影氛围], [色调风格], [镜头/构图] --ar 9:16 --s [风格化程度] --v 6.1
```

## 各部分要求

### 主体描述
- 产品为主体时：材质、颜色、尺寸感、关键细节
- 人物为主体时：性别、年龄段、表情、动作、穿着风格
- 始终用英文，具体且可视化

### 场景环境
- 必须匹配目标人群的生活场景
- 常用场景关键词：modern living room, minimalist bathroom, bright kitchen, cozy bedroom, outdoor garden, office desk, gym, café

### 光影氛围
- 产品类：soft studio lighting, product photography lighting, rim lighting
- 生活场景：natural daylight, golden hour, warm ambient light
- 高级感：dramatic lighting, cinematic lighting, backlit

### 色调风格
- 根据产品调性选择：warm tones, cool tones, pastel colors, vibrant colors, muted earth tones
- 可指定具体风格：commercial photography style, editorial style, lifestyle photography

### 镜头/构图
- 特写：close-up shot, macro shot, extreme close-up
- 中景：medium shot, waist shot
- 全景：wide shot, full body shot
- 构图：centered composition, rule of thirds, overhead flat lay, 45-degree angle

## 参数说明

| 参数 | 用途 | 千川素材推荐值 |
|------|------|----------------|
| --ar | 画面比例 | 9:16（竖屏首选）、16:9（横版）、1:1（方版） |
| --s | 风格化程度 | 150-250（商业摄影感）、50-100（写实感） |
| --v | 模型版本 | 6.1（最新） |
| --q | 质量 | 1（标准）、2（高质量） |
| --no | 排除元素 | 按需排除：--no text, watermark, logo |

## 输出模板

```
--- 镜号 X：[画面描述摘要] ---

【Midjourney Prompt】
[完整英文 prompt]
--ar 9:16 --s 250 --v 6.1 --no text, watermark

【用途说明】：该图片用于 [镜头用途]
【建议后处理】：[是否需要在剪映/PS中做进一步处理]
```

## 千川素材常用 Prompt 模式

### 产品特写
```
[product name] placed on [surface], [material/texture details], soft studio lighting, commercial product photography, clean background, close-up shot --ar 9:16 --s 200 --v 6.1
```

### 使用场景
```
[age] [gender] [action with product] in [location], [expression], natural daylight, lifestyle photography, warm tones, medium shot --ar 9:16 --s 180 --v 6.1
```

### 效果对比
```
split screen comparison, left side [before state], right side [after state], clean layout, professional photography, bright lighting --ar 9:16 --s 150 --v 6.1
```

### 氛围图
```
[product] in [aesthetic scene], [mood keywords], cinematic lighting, editorial photography style, shallow depth of field --ar 9:16 --s 250 --v 6.1
```
