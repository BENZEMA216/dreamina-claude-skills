---
name: dreamina-query-result
description: 查询 Dreamina 生成任务结果，获取图片/视频下载链接
---

# 结果查询工具

## API 调用
```bash
curl 'https://jimeng.jianying.com/mweb/v1/get_history_by_ids?aid=513695&device_platform=web&region=cn' \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'appid: 513695' \
  -H 'appvr: 8.4.0' \
  -H 'pf: 3' \
  -H 'lan: zh-Hans' \
  -H 'loc: cn' \
  -H 'origin: https://jimeng.jianying.com' \
  -H 'referer: https://jimeng.jianying.com/ai-tool/generate?type=image' \
  -H 'Cookie: <认证cookie>' \
  -d '{"submit_ids":["<submit_id>"]}'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| submit_ids | array | 是 | 提交ID数组，支持批量查询 |

## 响应结构 - 图片
```json
{
  "ret": "0",
  "data": {
    "<submit_id>": {
      "status": 50,
      "item_list": [{
        "image": {
          "large_images": [{
            "image_uri": "tos-cn-i-tb4s082cfz/<hash>",
            "image_url": "https://p26-dreamina-sign.byteimg.com/...",
            "width": 2048,
            "height": 2048,
            "format": "png"
          }]
        }
      }]
    }
  }
}
```

## 响应结构 - 视频
```json
{
  "ret": "0",
  "data": {
    "<submit_id>": {
      "status": 50,
      "item_list": [{
        "video": {
          "video_resource": {
            "video_url": "https://...",
            "video_uri": "tos-cn-v-xxx/...",
            "duration": 5000,
            "width": 1280,
            "height": 720
          }
        }
      }]
    }
  }
}
```

## 任务状态
| status | 说明 |
|---|---|
| 10 | 排队中 |
| 20 | 生成中 |
| 50 | 已完成 |
| -1 | 失败 |

## 下载资源
```bash
# 图片：从 item_list[].image.large_images[].image_url 获取
curl -o output.png '<image_url>'

# 视频：从 item_list[].video.video_resource.video_url 获取
curl -o output.mp4 '<video_url>'
```

## 完整流程示例
```bash
# 1. 提交生成任务
SUBMIT_ID=$(uuidgen)
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <cookie>' \
  -d "{\"generate_type\":\"text2imageV2\",\"prompt\":\"...\",\"submit_id\":\"$SUBMIT_ID\"}"

# 2. 轮询查询结果（间隔3-5秒）
curl 'https://jimeng.jianying.com/mweb/v1/get_history_by_ids?aid=513695&device_platform=web&region=cn' \
  -H 'Content-Type: application/json' \
  -H 'appid: 513695' \
  -H 'pf: 3' \
  -H 'Cookie: <cookie>' \
  -d "{\"submit_ids\":[\"$SUBMIT_ID\"]}"

# 3. status=50 后下载
curl -o result.png '<image_url>'
```

## 注意事项
- 图片/视频 URL 带签名，有过期时间（约1-2小时）
- 建议生成后立即下载
- 支持批量查询多个 submit_id
- 轮询间隔建议 3-5 秒
- 视频生成时间较长，建议 10-30 秒轮询
