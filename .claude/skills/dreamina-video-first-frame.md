---
name: dreamina-video-first-frame
description: 使用 text_first_frame_to_video 工具将图片作为首帧生成视频
---

# text_first_frame_to_video 首帧生视频工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/video_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "image2videoV2",
    "agent_scene": "creation_agent_v40",
    "prompt": "镜头缓缓推进，城市灯光闪烁",
    "ratio": "16:9",
    "first_frame_resource_uri": "<tos_uri>",
    "duration": 5,
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `image2videoV2` |
| agent_scene | string | 是 | `creation_agent_v40` |
| prompt | string | 是 | 视频描述 |
| ratio | string | 是 | 视频比例 |
| first_frame_resource_uri | string | 是 | 首帧图 TOS URI |
| duration | int | 否 | 时长秒数，3-10，默认5 |
| video_resolution | string | 否 | `720p` / `1080p` |
| submit_id | string | 否 | UUID，幂等 |

## 描述要点
- 镜头运动：推拉、摇移、跟随、升降、变焦
- 主体动作：自然连续，幅度适中
- 背景动态：风吹、光影变化、人群流动
- 镜头需遵循首帧角度
