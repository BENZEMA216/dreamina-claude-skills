# Runway Gen-3 Prompt 生成规则

为千川素材生成 Runway Gen-3 Alpha 的视频 Prompt。Runway 使用英文 prompt。

## Prompt 结构

```
[场景/主体描述], [动作/运动], [camera movement], [风格/氛围]
```

## Runway Gen-3 特点

- 擅长：电影级质感、复杂镜头运动、写实风格
- 时长：5s / 10s
- 画面比例：16:9（横屏）/ 9:16（竖屏）/ 1:1
- 支持图生视频（Image to Video）

## Prompt 撰写规则

### 场景/主体描述
- 用英文，具体描述画面内容
- 从主体开始，然后是环境、光线
- 示例：A skincare bottle on a marble surface, soft morning light, minimalist bathroom setting

### 动作/运动描述
- 明确标注主体动作
- 示例：slowly rotating, liquid pouring, hands applying cream, person turning head

### Camera Movement 关键词
| 中文 | Runway 关键词 |
|------|---------------|
| 推进 | camera pushing in, dolly in, camera moves forward |
| 拉远 | camera pulling out, dolly out, camera moves backward |
| 左平移 | camera panning left, tracking left |
| 右平移 | camera panning right, tracking right |
| 上摇 | camera tilting up |
| 下摇 | camera tilting down |
| 环绕 | camera orbiting around, arc shot |
| 固定 | static camera, locked-off shot |
| 跟随 | camera following subject, tracking shot |
| 手持 | handheld camera, slight camera shake |

### 风格关键词
- 电影感：cinematic, film grain, anamorphic lens, shallow depth of field
- 商业感：commercial style, clean, professional, high-end
- 质感：high contrast, soft lighting, golden hour, dramatic lighting

## 参数设置

| 参数 | 说明 | 千川素材推荐 |
|------|------|--------------|
| Duration | 视频时长 | 5s（单镜头）/ 10s（复杂场景） |
| Aspect Ratio | 画面比例 | 9:16（竖屏投放首选） |
| Motion Amount | 运动幅度 | Medium（避免过度运动导致畸变） |

## 输出模板

```
--- 镜号 X：[画面描述摘要] ---

【Runway Gen-3 Prompt】
[完整英文 prompt]

Duration: 5s
Aspect Ratio: 9:16
Motion: [具体镜头运动描述]

【Image to Video 建议】：[是否建议先生成首帧图片再做 I2V，如是则说明首帧生成方式]
```

## 千川素材常用 Prompt 模式

### 产品旋转展示
```
A [product] on a [surface], slowly rotating 360 degrees, soft studio lighting, commercial product photography style, clean background, static camera
Duration: 5s
Motion: subject rotation only, camera static
```

### 产品使用演示
```
Hands gently applying [product] on skin, close-up shot, soft natural lighting, camera slowly pushing in, beauty commercial style, shallow depth of field
Duration: 5s
Motion: camera pushing in slowly
```

### 场景切换
```
[Scene A description], smooth transition to [Scene B description], cinematic lighting, camera tracking left, high-end commercial style
Duration: 10s
Motion: camera tracking with scene transition
```

### 人物展示
```
A [person description] holding [product], looking at camera with a smile, natural daylight in [location], camera slowly orbiting around subject, lifestyle photography style
Duration: 5s
Motion: slow orbit around subject
```

### 液体/质地展示
```
[Liquid/cream] slowly pouring onto [surface], macro shot, dramatic lighting highlighting texture, camera static, high-speed capture style
Duration: 5s
Motion: static camera, subject movement only
```

## Runway vs 可灵选择建议

| 需求 | 推荐工具 | 原因 |
|------|----------|------|
| 电影级质感 | Runway | 画面质感更电影化 |
| 精确运动控制 | 可灵 | 首帧尾帧控制更精确 |
| 复杂镜头运动 | Runway | camera movement 理解更好 |
| 中文 prompt | 可灵 | Runway 仅支持英文 |
| 快速迭代测试 | 可灵 | 生成速度更快 |
