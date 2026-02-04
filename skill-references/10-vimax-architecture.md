# ViMax: Agentic Video Generation - Architecture Reference

> 来源: https://github.com/HKUDS/ViMax
> 注意: 这不是一个 SKILL.md，而是一个多 Agent 视频生成系统的架构参考

## 概述

ViMax 是一个 "Director, Screenwriter, Producer, and Video Generator All-in-One" 系统。
它将原始想法转化为完整的视频故事，通过智能多 Agent 工作流自动化故事讲述、角色设计和视频制作。

## 核心功能模式

| 模式 | 说明 |
|------|------|
| Idea2Video | 从一个想法出发，自动生成完整视频故事 |
| Novel2Video | 将完整小说转化为分集视频内容（智能叙事压缩、角色追踪、逐场景视觉化） |
| Script2Video | 从剧本出发，无限制地创建视频 |
| AutoCameo | 从照片生成视频，将自己/宠物变成视频中的角色 |

## Agent 架构

以下是 ViMax 的多 Agent 系统中的各个专业 Agent：

### 创意/叙事 Agent
- `screenwriter.py` - 编剧：负责剧本创作
- `script_planner.py` - 剧本规划：结构化剧本框架
- `script_enhancer.py` - 剧本增强：优化和丰富剧本内容
- `novel_compressor.py` - 小说压缩：将长篇小说压缩为可视化叙事

### 视觉设计 Agent
- `storyboard_artist.py` - 分镜师：将剧本转化为视觉叙事
- `character_extractor.py` - 角色提取：从文本中提取角色信息
- `character_portraits_generator.py` - 角色肖像生成：为角色创建一致的视觉形象

### 场景/事件 Agent
- `scene_extractor.py` - 场景提取：从剧本中识别和分离场景
- `event_extractor.py` - 事件提取：提取关键剧情事件
- `global_information_planner.py` - 全局信息规划：维护整体一致性

### 技术执行 Agent
- `camera_image_generator.py` - 摄影机画面生成：根据分镜生成画面
- `reference_image_selector.py` - 参考图选择：为画面生成选择合适的参考
- `best_image_selector.py` - 最佳图片选择：从多个生成结果中选择最佳画面

## 生产流程

```
创意输入 (想法/小说/剧本)
    ↓
剧本创作 & 增强 (screenwriter + script_enhancer)
    ↓
角色提取 & 肖像生成 (character_extractor + portraits_generator)
    ↓
场景/事件提取 (scene_extractor + event_extractor)
    ↓
分镜设计 (storyboard_artist)
    ↓
画面生成 & 选择 (camera_image_generator + best_image_selector)
    ↓
视频合成
```

## 解决的核心挑战

1. **角色一致性** - 跨场景保持角色外观一致
2. **叙事连贯性** - 多场景之间的故事逻辑衔接
3. **长视频生成** - 从秒级扩展到分钟级甚至更长
4. **端到端自动化** - 从文字输入到视频输出全自动

## 对做 Skill 的参考价值

ViMax 的架构展示了如何将"短片创作"拆分为多个专业 Agent 协作的模式。
如果你要做一个短片创作的 Skill，可以参考这种分工方式：

1. **编剧 Agent** - 负责故事/剧本
2. **分镜 Agent** - 负责将剧本可视化为分镜头
3. **角色设计 Agent** - 负责角色外观一致性
4. **画面生成 Agent** - 负责实际的图片/视频生成
5. **质量控制 Agent** - 负责检查一致性和质量
