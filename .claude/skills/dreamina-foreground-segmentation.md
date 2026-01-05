---
name: dreamina-foreground-segmentation
description: 使用 foreground_segmentation 工具提取图片前景，去除背景（抠图）
---

# foreground_segmentation 前景分割工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "imageCutout",
    "agent_scene": "creation_agent_v40",
    "resource_uri": "<tos_uri>",
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `imageCutout` |
| agent_scene | string | 是 | `creation_agent_v40` |
| resource_uri | string | 是 | 输入图片 TOS URI |
| submit_id | string | 否 | UUID，幂等 |

## 功能
从图片中提取前景主体，去除背景，输出透明背景图片
