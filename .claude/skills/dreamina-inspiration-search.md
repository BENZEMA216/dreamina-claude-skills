---
name: dreamina-inspiration-search
description: 检索优质 Prompt 和图片作为创作参考
---

# 灵感搜索工具

## API 端点
```
POST https://jimeng.jianying.com/mweb/v1/search_image
```

## Python 示例

```python
import requests
import hashlib
import time

def generate_sign(uri_path):
    device_time = int(time.time())
    sign_str = f"9e2c|{uri_path[-7:]}|7|5.8.0|{device_time}||11ac"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign, device_time

def inspiration_search(sessionid, query, offset=0, limit=20):
    uri = "/mweb/v1/search_image"
    sign, device_time = generate_sign(uri)
    
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
    
    resp = requests.post(
        f"https://jimeng.jianying.com{uri}",
        params={"aid": 513695, "device_platform": "web", "region": "CN"},
        headers=headers,
        json={
            "query": query,
            "offset": offset,
            "limit": limit,
            "http_common_info": {"aid": 513695}
        }
    )
    return resp.json()
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索关键词 |
| offset | int | 否 | 结果偏移量，用于翻页 |
| limit | int | 否 | 返回数量，默认 20 |

## Query 构造规则

### 有图片时
提取：**[主体] + [风格] + [核心元素]**
- 错误：`类似的图片`
- 正确：`摩登上海 陆家嘴 蓝色调 海报`

### 纯文本时
直接提取关键词

## Offset 计算规则

### 条件 A → offset = 上轮offset + limit
- Query 与上轮语义相同
- 用户说"再找找"、"换一批"、"更多"
- 新图与上一张图属于同一主题

### 条件 B → offset = 0
- Query 语义完全改变
- 用户说"重新开始"、"重置"

## 响应结构
```json
{
  "ret": "0",
  "data": {
    "items": [
      {
        "id": "xxx",
        "prompt": "图片生成时使用的提示词",
        "image_url": "https://...",
        "width": 1024,
        "height": 1024
      }
    ],
    "has_more": true
  }
}
```

## 注意
- 连续搜索时**严禁重置 offset 为 0**（除非条件B）
- 关键词重叠度 >80% 时必须递增 offset
