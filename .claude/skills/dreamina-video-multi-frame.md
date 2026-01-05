---
name: dreamina-video-multi-frame
description: 使用 multi_frame_to_video 工具将多张图片生成连续视频，适用于绘本转视频、多场景串联
---

# multi_frame_to_video 多帧生视频工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/video_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "multiFrame2video",
    "agent_scene": "creation_agent_v40",
    "media_resource_uri_list": ["<tos_uri_1>", "<tos_uri_2>", "<tos_uri_3>"],
    "media_type_list": ["image", "image", "image"],
    "prompt_list": ["镜头推进", "场景切换"],
    "duration_list": [3, 3, 3],
    "ratio": "16:9",
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `multiFrame2video` |
| agent_scene | string | 是 | `creation_agent_v40` |
| media_resource_uri_list | array | 是 | 图片 TOS URI 列表 |
| media_type_list | array | 是 | 媒体类型列表，如 `["image", "image"]` |
| prompt_list | array | 否 | 每段过渡描述 |
| duration_list | array | 否 | 每段时长列表 |
| ratio | string | 是 | 视频比例 |
| submit_id | string | 否 | UUID，幂等 |

## 适用场景
- 绘本/分镜转视频
- 多场景连续串联
- 展现完整演变过程

## 对比 startEnd2Video
- `multiFrame2video`：更完整，适合多帧连续
- `startEnd2Video`：更可控，可展示中间状态
