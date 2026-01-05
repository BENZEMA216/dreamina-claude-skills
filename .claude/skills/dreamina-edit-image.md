---
name: dreamina-edit-image
description: 使用 edit_image 工具编辑图片或基于参考图生成新图，适用于有参考图的编辑和生成场景
---

# edit_image 图片编辑工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "seedEdit40",
    "agent_scene": "creation_agent_v40",
    "prompt": "将背景改为夜景",
    "ratio": "2:3",
    "resource_uri_list": ["<tos_uri>"],
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `seedEdit40` / `seedEditV2` |
| agent_scene | string | 是 | `creation_agent_v40` |
| prompt | string | 是 | 编辑指令 |
| ratio | string | 是 | 图片比例 |
| resource_uri_list | array | 是 | 输入图片 TOS URI 列表 |
| submit_id | string | 否 | UUID，幂等 |

## generate_type 选项
- `seedEdit` - 编辑 v2.1
- `seedEditV2` - 编辑 v3.0
- `seedEdit40` - 编辑 4.0（推荐）

## 功能
1. **图像编辑**：添加/去除物品、修改背景、添加滤镜、改变姿势
2. **参考生图**：基于多张图做风格参考
3. **画面微调**：prompt 填 "画面微调"

## 比例选项
21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16

## 注意
- 多张输入图用"图1、图2"指代（按传入顺序）
- 未指定数量时生成 **4张**
