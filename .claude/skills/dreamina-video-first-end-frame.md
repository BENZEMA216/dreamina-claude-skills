---
name: dreamina-video-first-end-frame
description: 使用 text_first_end_frame_to_video 工具将两张图片作为首尾帧生成视频
---

# text_first_end_frame_to_video 首尾帧生视频工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/video_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "startEnd2Video",
    "agent_scene": "creation_agent_v40",
    "prompt": "镜头跟随主体快速运动，场景渐变过渡",
    "ratio": "16:9",
    "first_frame_resource_uri": "<首帧tos_uri>",
    "last_frame_resource_uri": "<尾帧tos_uri>",
    "duration": 5,
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| generate_type | string | 是 | `startEnd2Video` |
| agent_scene | string | 是 | `creation_agent_v40` |
| prompt | string | 否 | 变化描述 |
| ratio | string | 是 | 视频比例 |
| first_frame_resource_uri | string | 是 | 首帧图 TOS URI |
| last_frame_resource_uri | string | 是 | 尾帧图 TOS URI |
| duration | int | 否 | 时长秒数，3-10 |
| submit_id | string | 否 | UUID，幂等 |

## 变化类型
- **空间变换**：第一人称视角、俯冲镜头、360°环绕、稳定器跟拍
- **身份变化**：镜头推进、烟雾缭绕、形态渐变
- **角色动态**：跟随主体运动、动作连贯

## 注意
- 着重描述**画面变化**，无需描述原始图片内容
