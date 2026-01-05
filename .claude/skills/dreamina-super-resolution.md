---
name: dreamina-super-resolution
description: 使用 super_resolution 工具对图片进行超分辨率放大
---

# super_resolution 图片超分工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "imageSuperResolution",
    "agent_scene": "creation_agent_v40",
    "resource_uri": "<tos_uri>",
    "resolution_type": "2k",
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `imageSuperResolution` |
| agent_scene | string | 是 | `creation_agent_v40` |
| resource_uri | string | 是 | 输入图片 TOS URI |
| resolution_type | string | 否 | `2k` / `4k` |
| submit_id | string | 否 | UUID，幂等 |
