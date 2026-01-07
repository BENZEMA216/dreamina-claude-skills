---
name: dreamina-edit-image
description: 使用 edit_image 工具编辑图片或基于参考图生成新图，适用于有参考图的编辑和生成场景
---

# edit_image 图片编辑工具

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

def generate_sign(uri_path):
    device_time = int(time.time())
    sign_str = f"9e2c|{uri_path[-7:]}|7|5.8.0|{device_time}||11ac"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign, device_time

def edit_image_with_reference(sessionid, prompt, image_uri, ratio="16:9"):
    uri = "/mweb/v1/aigc_draft/generate"
    sign, device_time = generate_sign(uri)
    
    RATIO_VALUES = {"21:9": 0, "16:9": 1, "3:2": 2, "4:3": 3, "1:1": 8, "3:4": 4, "2:3": 5, "9:16": 6}
    DIMENSIONS_2K = {
        "21:9": (3024, 1296), "16:9": (2560, 1440), "3:2": (2496, 1664),
        "4:3": (2304, 1728), "1:1": (2048, 2048), "3:4": (1728, 2304),
        "2:3": (1664, 2496), "9:16": (1440, 2560)
    }
    
    image_ratio = RATIO_VALUES.get(ratio, 1)
    width, height = DIMENSIONS_2K.get(ratio, (2560, 1440))
    
    component_id = str(uuid.uuid4())
    model = "high_aes_general_v30l:general_v3.0_18b"
    
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
            "generate_type": "blend",
            "aigc_mode": "workbench",
            "abilities": {
                "type": "",
                "id": str(uuid.uuid4()),
                "blend": {
                    "type": "",
                    "id": str(uuid.uuid4()),
                    "min_features": [],
                    "core_param": {
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "model": model,
                        "prompt": prompt + "##",
                        "sample_strength": 0.5,
                        "image_ratio": image_ratio,
                        "large_image_info": {
                            "type": "",
                            "id": str(uuid.uuid4()),
                            "height": height,
                            "width": width,
                            "resolution_type": "2k"
                        }
                    },
                    "ability_list": [{
                        "type": "",
                        "id": str(uuid.uuid4()),
                        "name": "byte_edit",
                        "image_uri_list": [image_uri],
                        "image_list": [{
                            "type": "image",
                            "id": str(uuid.uuid4()),
                            "source_from": "upload",
                            "platform_type": 1,
                            "name": "",
                            "image_uri": image_uri,
                            "width": 0,
                            "height": 0,
                            "format": "",
                            "uri": image_uri
                        }],
                        "strength": 0.5
                    }],
                    "history_option": {"type": "", "id": str(uuid.uuid4())},
                    "prompt_placeholder_info_list": [{"type": "", "id": str(uuid.uuid4()), "ability_index": 0}],
                    "postedit_param": {"type": "", "id": str(uuid.uuid4()), "generate_type": 0}
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
        "extend": {"root_model": model, "template_id": ""},
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
    return resp.json()
```

## 内网 MCP API

### 端点
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/image_generate' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "generate_type": "seedEdit40",
    "agent_scene": "creation_agent_v40",
    "prompt": "将背景改为夜景",
    "ratio": "2:3",
    "resource_uri_list": ["<tos_uri>"],
    "submit_id": "<uuid>"
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| prompt | string | 是 | 编辑指令 |
| image_uri | string | 是 | 参考图 URI (通过 upload_image 获取) |
| ratio | string | 是 | 图片比例 (16:9, 1:1, 9:16 等) |

## 功能
1. **图像编辑**：添加/去除物品、修改背景、添加滤镜、改变姿势
2. **参考生图**：基于参考图生成新场景
3. **画面微调**：prompt 填 "画面微调"

## 比例选项
21:9, 16:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16

## 注意
- 需要先上传图片获取 `image_uri` (见 dreamina-upload-image)
- 未指定数量时生成 **1张**
- 公网 API 使用 `blend` + `byte_edit` 模式
