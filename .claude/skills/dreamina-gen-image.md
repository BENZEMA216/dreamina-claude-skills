---
name: dreamina-gen-image
description: 使用 gen_image_verbatim 工具从文字描述生成图片，适用于无参考图的文生图场景
---

# gen_image_verbatim 文生图工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "text2imageV2",
    "agent_scene": "creation_agent_v40",
    "prompt": "<生成提示词>",
    "ratio": "1:1",
    "model_key": "high_aes_general_v40",
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `text2imageV2` |
| agent_scene | string | 是 | `creation_agent_v40` |
| prompt | string | 是 | 生成提示词 |
| ratio | string | 是 | 图片比例 |
| model_key | string | 否 | 模型标识 |
| submit_id | string | 否 | UUID，幂等 |

## model_key 选项
- `high_aes_general_v30l:general_v3.0_18b` (模型3.0)
- `high_aes_general_v30l_art_fangzhou:general_v3.0_18b` (模型3.1)
- `high_aes_general_v40` (模型4.0)

## 比例选项
21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16

## 默认行为
- 未指定数量时生成 **4张**
- 单次调用批量生成
