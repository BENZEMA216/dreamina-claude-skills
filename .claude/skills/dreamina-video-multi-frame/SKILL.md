---
name: dreamina-video-multi-frame
description: 将多张图片生成连续视频，适用于绘本转视频、多场景串联
---

# 多帧生视频工具

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

def multi_frame_to_video(sessionid, image_uri_list, prompt_list=None, duration_list=None, ratio="16:9"):
    uri = "/mweb/v1/aigc_draft/generate"
    sign, device_time = generate_sign(uri)
    
    RATIO_VALUES = {"16:9": 1, "9:16": 6, "1:1": 8, "4:3": 3, "3:4": 4}
    
    component_id = str(uuid.uuid4())
    image_ratio = RATIO_VALUES.get(ratio, 1)
    
    n = len(image_uri_list)
    if prompt_list is None:
        prompt_list = [""] * (n - 1)
    if duration_list is None:
        duration_list = [3000] * n
    
    frame_list = []
    for i, uri in enumerate(image_uri_list):
        frame_list.append({
            "type": "image",
            "id": str(uuid.uuid4()),
            "source_from": "upload",
            "platform_type": 1,
            "image_uri": uri,
            "uri": uri,
            "duration": duration_list[i] if i < len(duration_list) else 3000,
            "prompt": prompt_list[i] if i < len(prompt_list) else ""
        })
    
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
            "generate_type": "multi_frame_to_video",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "multi_frame_to_video": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "video_ratio": image_ratio,
                        "resolution": "1080p"
                    },
                    "frame_list": frame_list,
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
| image_uri_list | array | 是 | 图片 URI 列表 |
| prompt_list | array | 否 | 每段过渡描述 (n-1 个) |
| duration_list | array | 否 | 每段时长毫秒列表 |
| ratio | string | 否 | 视频比例，默认 16:9 |

## 适用场景
- 绘本/分镜转视频
- 多场景连续串联
- 展现完整演变过程

## 对比 start_end_to_video
| 功能 | multi_frame_to_video | start_end_to_video |
|------|---------------------|-------------------|
| 图片数 | 多张 | 2张 |
| 适用 | 多帧连续 | 精确控制首尾 |
| 灵活性 | 更完整 | 更可控 |

## 使用流程
1. 上传所有图片获取 `image_uri` 列表
2. 调用多帧生视频 API
3. 轮询查询结果
4. 下载视频文件
