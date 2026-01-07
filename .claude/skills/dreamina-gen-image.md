---
name: dreamina-gen-image
description: 使用 gen_image_verbatim 工具从文字描述生成图片，适用于无参考图的文生图场景
---

# gen_image_verbatim 文生图工具

## 公网 API (推荐)

### 端点
```
POST https://jimeng.jianying.com/mweb/v1/aigc_draft/generate
```

### 完整请求示例
```python
import requests
import hashlib
import time
import uuid
import json
import random

def generate_sign(uri_path):
    device_time = int(time.time())
    sign_str = f"9e2c|{uri_path[-7:]}|7|5.8.0|{device_time}||11ac"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign, device_time

def generate_image(sessionid, prompt, ratio="16:9", model="jimeng-image-3.0"):
    uri = "/mweb/v1/aigc_draft/generate"
    sign, device_time = generate_sign(uri)
    
    MODEL_MAP = {
        "jimeng-image-4.5": "high_aes_general_v40l",
        "jimeng-image-4.1": "high_aes_general_v41",
        "jimeng-image-4.0": "high_aes_general_v40",
        "jimeng-image-3.1": "high_aes_general_v30l_art_fangzhou:general_v3.0_18b",
        "jimeng-image-3.0": "high_aes_general_v30l:general_v3.0_18b"
    }
    RATIO_VALUES = {"21:9": 0, "16:9": 1, "3:2": 2, "4:3": 3, "1:1": 8, "3:4": 4, "2:3": 5, "9:16": 6}
    DIMENSIONS_2K = {
        "21:9": (3024, 1296), "16:9": (2560, 1440), "3:2": (2496, 1664),
        "4:3": (2304, 1728), "1:1": (2048, 2048), "3:4": (1728, 2304),
        "2:3": (1664, 2496), "9:16": (1440, 2560)
    }
    
    model_key = MODEL_MAP.get(model, MODEL_MAP["jimeng-image-3.0"])
    image_ratio = RATIO_VALUES.get(ratio, 1)
    width, height = DIMENSIONS_2K.get(ratio, (2560, 1440))
    resolution_type = "2k" if "4." in model else "1k"
    
    component_id = str(uuid.uuid4())
    
    draft_content = {
        "type": "draft",
        "id": str(uuid.uuid4()),
        "min_version": "3.2.2",
        "is_from_tsn": True,
        "version": "3.2.2",
        "main_component_id": component_id,
        "component_list": [{
            "type": "image_base_component",
            "id": component_id,
            "min_version": "3.2.2",
            "metadata": {
                "type": "",
                "id": str(uuid.uuid4()),
                "created_platform": 3,
                "created_platform_version": "",
                "created_time_in_ms": int(time.time() * 1000),
                "created_did": ""
            },
            "generate_type": "generate",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "generate": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "model": model_key,
                        "prompt": prompt,
                        "negative_prompt": "",
                        "seed": random.randint(2500000000, 2600000000),
                        "sample_strength": 0.5,
                        "image_ratio": image_ratio,
                        "large_image_info": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "height": height,
                            "width": width,
                            "resolution_type": resolution_type
                        }
                    },
                    "history_option": {"type": "", "id": str(uuid.uuid4())}
                }
            }
        }]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
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
        "extend": {"root_model": model_key, "template_id": ""},
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

# 使用示例
# result = generate_image('your_sessionid', '一只柴犬在太空飞翔，赛博朋克风格')
# history_id = result['data']['aigc_data']['history_record_id']
```

### 查询结果
```python
def query_result(sessionid, history_id):
    uri = "/mweb/v1/get_history_by_ids"
    sign, device_time = generate_sign(uri)
    
    headers = {
        "Content-Type": "application/json",
        "Appid": "513695",
        "Pf": "7",
        "Cookie": f"sessionid={sessionid}",
        "Device-Time": str(device_time),
        "Sign": sign,
        "Sign-Ver": "1"
    }
    
    resp = requests.post(
        f"https://jimeng.jianying.com{uri}",
        params={"aid": 513695, "device_platform": "web", "region": "CN"},
        headers=headers,
        json={"history_ids": [history_id], "http_common_info": {"aid": 513695}}
    )
    data = resp.json()['data']
    if history_id in data and data[history_id]['status'] == 50:
        return data[history_id]['item_list'][0]['image']['large_images'][0]['image_url']
    return None
```

## 内网 MCP API

### 端点
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "text2imageV2",
    "agent_scene": "creation_agent_v40",
    "prompt": "<生成提示词>",
    "ratio": "1:1",
    "model_key": "high_aes_general_v40",
    "subject_id": "default",
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| prompt | string | 是 | 生成提示词 |
| ratio | string | 是 | 图片比例 |
| model | string | 否 | 模型选择 |

## model 选项
- `jimeng-image-4.5` - 最新模型 (高质量)
- `jimeng-image-4.1` - 4.1 模型
- `jimeng-image-4.0` - 4.0 模型
- `jimeng-image-3.1` - 3.1 模型 (艺术风格)
- `jimeng-image-3.0` - 3.0 模型 (默认)

## 比例选项
21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16

## 默认行为
- 未指定数量时生成 **1张**
- 4.x 模型使用 2K 分辨率
- 3.x 模型使用 1K 分辨率
