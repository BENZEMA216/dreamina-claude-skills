---
name: dreamina-video-first-end-frame
description: 将两张图片作为首尾帧生成视频
---

# 首尾帧生视频工具

## API 端点
```
POST https://jimeng.jianying.com/mweb/v1/aigc_draft/generate
```

## Python 示例

```python
import requests
import hashlib
import time
import uuid
import json

def generate_sign(uri_path):
    device_time = int(time.time())
    sign_str = f"9e2c|{uri_path[-7:]}|7|5.8.0|{device_time}||11ac"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign, device_time

def first_end_frame_to_video(sessionid, first_image_uri, last_image_uri, prompt="", ratio="16:9", duration=5):
    uri = "/mweb/v1/aigc_draft/generate"
    sign, device_time = generate_sign(uri)
    
    RATIO_VALUES = {"16:9": 1, "9:16": 6, "1:1": 8, "4:3": 3, "3:4": 4}
    
    component_id = str(uuid.uuid4())
    image_ratio = RATIO_VALUES.get(ratio, 1)
    
    draft_content = {
        "type": "draft",
        "id": str(uuid.uuid4()),
        "min_version": "3.3.8",
        "is_from_tsn": True,
        "version": "3.3.8",
        "main_component_id": component_id,
        "component_list": [{
            "type": "video_base_component",
            "id": component_id,
            "min_version": "3.3.8",
            "metadata": {
                "type": "",
                "id": str(uuid.uuid4()),
                "created_platform": 3,
                "created_time_in_ms": int(time.time() * 1000)
            },
            "generate_type": "start_end_to_video",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "start_end_to_video": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "prompt": prompt,
                        "video_ratio": image_ratio,
                        "duration": duration * 1000,
                        "resolution": "1080p"
                    },
                    "first_frame_image": {
                        "type": "image",
                        "id": str(uuid.uuid4()),
                        "source_from": "upload",
                        "platform_type": 1,
                        "image_uri": first_image_uri,
                        "uri": first_image_uri
                    },
                    "last_frame_image": {
                        "type": "image",
                        "id": str(uuid.uuid4()),
                        "source_from": "upload",
                        "platform_type": 1,
                        "image_uri": last_image_uri,
                        "uri": last_image_uri
                    },
                    "history_option": {"type": "", "id": str(uuid.uuid4())}
                }
            }
        }]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Appid": "513695",
        "Appvr": "5.8.0",
        "Pf": "7",
        "Origin": "https://jimeng.jianying.com",
        "Referer": "https://jimeng.jianying.com",
        "Cookie": f"sessionid={sessionid}",
        "Device-Time": str(device_time),
        "Sign": sign,
        "Sign-Ver": "1"
    }
    
    data = {
        "extend": {},
        "submit_id": str(uuid.uuid4()),
        "draft_content": json.dumps(draft_content),
        "http_common_info": {"aid": 513695}
    }
    
    resp = requests.post(
        f"https://jimeng.jianying.com{uri}",
        params={"aid": 513695, "device_platform": "web", "region": "CN", "da_version": "3.3.8"},
        headers=headers,
        json=data
    )
    return resp.json()
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| first_image_uri | string | 是 | 首帧图片 URI |
| last_image_uri | string | 是 | 尾帧图片 URI |
| prompt | string | 否 | 变化描述 |
| ratio | string | 否 | 视频比例，默认 16:9 |
| duration | int | 否 | 时长秒数 3-10，默认 5 |

## 变化类型描述
- **空间变换**：第一人称视角、俯冲镜头、360°环绕、稳定器跟拍
- **身份变化**：镜头推进、烟雾缭绕、形态渐变
- **角色动态**：跟随主体运动、动作连贯

## 注意
- 着重描述**画面变化**，无需描述原始图片内容
- 首尾帧需要有视觉上的连贯性

## 使用流程
1. 上传首帧和尾帧图片获取 `image_uri`
2. 调用首尾帧生视频 API
3. 轮询查询结果
4. 下载视频文件
