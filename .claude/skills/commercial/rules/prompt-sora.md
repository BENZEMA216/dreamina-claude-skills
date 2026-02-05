# Sora Prompt 生成规则

为千川素材生成 OpenAI Sora 的视频 Prompt。Sora 使用自然语言英文 prompt，擅长理解复杂场景描述。

## Sora 特点

- 擅长：复杂场景、长时长、物理运动模拟、多主体交互
- 时长：5s - 20s
- Prompt 风格：自然语言叙述，像讲故事一样描述
- 画面比例：16:9 / 9:16 / 1:1

## Prompt 结构

Sora 的 prompt 更像自然语言描述，而非关键词堆叠：

```
A [详细场景描述], [主体描述和动作], [光线和氛围], [镜头运动描述]. The style is [风格描述].
```

## Prompt 撰写技巧

### 1. 使用完整句子
✅ A woman in a white dress is walking through a sunlit garden, gently touching the flowers.
❌ woman, white dress, garden, walking, flowers

### 2. 描述时间流动
Sora 擅长理解时间序列，可以描述画面变化：
"The camera starts on a close-up of the product, then slowly pulls back to reveal the entire room."

### 3. 指定镜头运动
用自然语言描述：
- "The camera slowly pushes in..."
- "We follow the subject from behind..."
- "A sweeping drone shot reveals..."

### 4. 指定风格
在最后标注风格：
- "Shot in the style of a high-end commercial."
- "Cinematic lighting, shallow depth of field."
- "Documentary style, natural lighting."

## 输出模板

```
--- 镜号 X：[画面描述摘要] ---

【Sora Prompt】
[完整自然语言英文描述，2-4句话]

Duration: [5s/10s/15s/20s]
Aspect Ratio: 9:16
Style Reference: [如有风格参考]

【注意事项】：[该镜头使用 Sora 的特殊考虑]
```

## 千川素材常用 Prompt 模式

### 产品展示
```
A sleek [product] sits on a marble countertop in a modern bathroom. Soft morning light streams through a window, creating gentle highlights on the product's surface. The camera slowly pushes in, revealing the fine details and texture of the packaging. Shot in the style of a luxury beauty commercial.

Duration: 10s
```

### 使用场景
```
A young woman in a cozy sweater applies [product] to her face in front of a bathroom mirror. Natural daylight fills the space. She smiles contentedly as she finishes, then turns toward the camera. The style is warm and authentic, like a lifestyle documentary.

Duration: 10s
```

### 产品旅程
```
We follow a [product] as it moves through different scenes: first on a factory production line, then being packaged, then unboxed by excited hands in a bright living room. The transitions are smooth and continuous. Commercial photography style with clean, professional lighting.

Duration: 15s
```

### 效果展示
```
A split-screen comparison: on the left, [before state], on the right, [after state using product]. The dividing line slowly moves from left to right, dramatically revealing the transformation. Clean studio lighting, beauty commercial style.

Duration: 10s
```

### 场景氛围
```
A serene morning scene in a minimalist apartment. [Product] sits on a bedside table. Sunlight slowly moves across the room as time passes. The camera gently drifts through the space. Soft, dreamy aesthetic with warm color grading.

Duration: 15s
```

## Sora 使用建议

### 适合使用 Sora 的场景
- 需要复杂、连贯的场景叙事
- 需要多物体自然交互
- 需要长时长（10s+）单镜头
- 需要精确的物理运动（液体、布料等）

### 不适合使用 Sora 的场景
- 需要精确的首帧/尾帧控制 → 用可灵
- 需要快速迭代测试 → 用 Pika
- 预算有限 → Sora 成本较高

## Sora vs 其他工具选择

| 需求 | 推荐工具 | 原因 |
|------|----------|------|
| 复杂叙事场景 | Sora | 自然语言理解强 |
| 长时长单镜头 | Sora | 支持 20s |
| 多物体交互 | Sora | 物理模拟好 |
| 快速便宜迭代 | Pika/可灵 | Sora 成本高、慢 |
| 精确运动控制 | 可灵 | Sora 更像"导演"不像"操作员" |
| 抖音生态整合 | 可灵/即梦 | 国内工具审核更友好 |
