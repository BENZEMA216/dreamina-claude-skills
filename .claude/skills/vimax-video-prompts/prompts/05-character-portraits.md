# Character Portraits Generator（角色肖像生成）

> 来源: `agents/character_portraits_generator.py` | 类: `CharacterPortraitsGenerator` | 方法: `generate_front_portrait()`, `generate_side_portrait()`, `generate_back_portrait()`

## 功能说明

为每个角色生成三视角（正面/侧面/背面）全身肖像的图片生成提示词。用于为下游的分镜画面生成提供角色参考图，确保角色一致性。位于角色提取之后。

---

## 正面肖像提示词（Front Portrait）

### Prompt Template

```
Generate a full-body, front-view portrait of character {identifier} based on the following description, with a pure white background. The character should be centered in the image, occupying most of the frame. Gazing straight ahead. Standing with arms relaxed at sides. Natural expression.
Features: {features}
Style: {style}
```

### 输入变量

| 变量 | 说明 | 来源 |
|------|------|------|
| `{identifier}` | 角色标识名称 | `CharacterInScene.identifier_in_scene` |
| `{features}` | 角色特征，格式为 `"(static) {static_features}; (dynamic) {dynamic_features}"` | 拼接自 `CharacterInScene` |
| `{style}` | 画面风格 | 外部传入（如 "realistic", "anime" 等） |

---

## 侧面肖像提示词（Side Portrait）

### Prompt Template

```
Generate a full-body, side-view portrait of character {identifier} based on the provided front-view portrait, with a pure white background. The character should be centered in the image, occupying most of the frame. Facing left. Standing with arms relaxed at sides.
```

### 输入变量

| 变量 | 说明 |
|------|------|
| `{identifier}` | 角色标识名称 |

> 注：侧面肖像需要前面生成的正面肖像图作为参考图（`reference_image_paths`）传入图片生成器。

---

## 背面肖像提示词（Back Portrait）

### Prompt Template

```
Generate a full-body, back-view portrait of character {identifier} based on the provided front-view portrait, with a pure white background. The character should be centered in the image, occupying most of the frame. No facial features should be visible.
```

### 输入变量

| 变量 | 说明 |
|------|------|
| `{identifier}` | 角色标识名称 |

> 注：背面肖像同样需要正面肖像图作为参考图传入。

---

## 使用要点

- **三视角生成顺序**：必须先生成正面 → 再用正面作为参考生成侧面和背面
- **白色背景**：所有肖像统一纯白背景，便于后续合成
- **全身画面**：角色居中，占据画面大部分空间
- **features 拼接格式**：`"(static) 角色静态特征; (dynamic) 角色动态特征"`
- **风格参数**：style 由外部传入，影响画面风格（写实、动漫等）
- **参考图机制**：侧面和背面生成依赖正面肖像作为 reference_image_paths
