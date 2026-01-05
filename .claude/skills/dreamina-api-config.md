---
name: dreamina-api-config
description: Dreamina MCP API 基础配置，包含 endpoint、headers 和通用参数
---

# Dreamina MCP API 配置

## Base URL
```
https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1
```

## 通用 Headers
```bash
Content-Type: application/json
x-tt-env: ppe_resource_query
x-use-ppe: 1
x-schedule-vdc: sinfonline
get-svc: 1
pf: 3
cookie: <用户认证cookie>
```

## 通用参数
- `agent_scene`: `creation_agent_v40`
- `creation_agent_version`: `3.0.0`
- `submit_id`: UUID 格式，用于幂等

## generate_type 枚举

### 图片生成
| 值 | 说明 |
|---|---|
| text2image | 文生图 v2.1 |
| text2imageV2 | 文生图 v3.0 |
| seedEdit | 编辑 v2.1 |
| seedEditV2 | 编辑 v3.0 |
| seedEdit40 | 编辑 4.0 |
| ipKeep | IP保持 |
| imageSuperResolution | 图片超分 |
| imageCutout | 图片抠图 |
| imageFinetune | 图片微调 |
| imageExtend | 图片扩展 |

### 视频生成
| 值 | 说明 |
|---|---|
| text2video | 文生视频 v2.1 |
| text2videoV2 | 文生视频 v3.0 |
| image2video | 图生视频 v2.1 |
| image2videoV2 | 图生视频 v3.0 |
| startEnd2Video | 首尾帧生成视频 |
| multiFrame2video | 多帧生成视频 |

## model_key 枚举
```
Model30Key = "high_aes_general_v30l:general_v3.0_18b"
Model31Key = "high_aes_general_v30l_art_fangzhou:general_v3.0_18b"
Model40Key = "high_aes_general_v40"
```
