---
name: dreamina-video-first-frame
description: 将图片作为首帧生成视频 (图生视频)
---

# 首帧生视频工具

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

def image_to_video(sessionid, image_uri, prompt, ratio="16:9", duration=5):
    uri = "/mweb/v1/aigc_draft/generate"
    sign, device_time = generate_sign(uri)
    
    RATIO_VALUES = {"16:9": 1, "9:16": 6, "1:1": 8, "4:3": 3, "3:4": 4}
    
    component_id = str(uuid.uuid4())
    image_ratio = RATIO_VALUES.get(ratio, 1)
    
    draft_content = {
        "type": "draft",
        "id": str(uuid.uuid4()),
        "min_version": "3.2.2",
        "is_from_tsn": True,
        "version": "3.2.2",
        "main_component_id": component_id,
        "component_list": [{
            "type": "video_base_component",
            "id": component_id,
            "min_version": "3.2.2",
            "metadata": {
                "type": "",
                "id": str(uuid.uuid4()),
                "created_platform": 3,
                "created_time_in_ms": int(time.time() * 1000)
            },
            "generate_type": "i2v",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "i2v": {
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
                        "image_uri": image_uri,
                        "uri": image_uri
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
        params={"aid": 513695, "device_platform": "web", "region": "CN", "da_version": "3.2.2"},
        headers=headers,
        json=data
    )
    return resp.json()
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_uri | string | 是 | 首帧图片 URI |
| prompt | string | 是 | 视频运动描述 |
| ratio | string | 否 | 视频比例，默认 16:9 |
| duration | int | 否 | 时长秒数 3-10，默认 5 |

## 比例选项
16:9, 9:16, 1:1, 4:3, 3:4

## 描述要点
- **镜头运动**：推拉、摇移、跟随、升降、变焦
- **主体动作**：自然连续，幅度适中
- **背景动态**：风吹、光影变化、人群流动
- 镜头需遵循首帧角度

## 使用流程
1. 上传首帧图片获取 `image_uri`
2. 调用图生视频 API
3. 轮询查询结果 (视频生成较慢，建议 10 秒间隔)
4. 下载视频文件
