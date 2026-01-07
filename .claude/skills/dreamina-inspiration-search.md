---
name: dreamina-inspiration-search
description: 检索优质 Prompt 和图片作为创作参考
---

# 灵感搜索工具

## API 端点
```
POST https://jimeng.jianying.com/mweb/v1/get_explore
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

def inspiration_search(sessionid, keyword="", category_id=11222, offset=0, count=20):
    uri = "/mweb/v1/get_explore"
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
    
    data = {
        "count": count,
        "offset": offset,
        "filter": {
            "work_type_list": ["video", "image", "canvas"]
        },
        "category_id": category_id,
        "feed_refer": "feed_enterauto",
        "image_info": {
            "width": 2048,
            "height": 2048,
            "format": "webp",
            "image_scene_list": [
                {"scene": "smart_crop", "width": 720, "height": 720, "format": "webp", "uniq_key": "smart_crop-w:720-h:720"},
                {"scene": "loss", "width": 720, "height": 720, "format": "webp", "uniq_key": "720"}
            ]
        }
    }
    
    if keyword:
        data["keyword"] = keyword
    
    resp = requests.post(
        f"https://jimeng.jianying.com{uri}",
        params={"aid": 513695, "device_platform": "web", "region": "CN", "da_version": "3.3.8"},
        headers=headers,
        json=data
    )
    return resp.json()

def search_guess(sessionid):
    uri = "/mweb/search/v1/guess"
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
        params={"aid": 513695},
        headers=headers,
        json={"search_channel": "inspiration"}
    )
    return resp.json()
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 (为空时返回推荐内容) |
| category_id | int | 否 | 分类ID，默认 11222 |
| offset | int | 否 | 结果偏移量，用于翻页 |
| count | int | 否 | 返回数量，默认 20 |
| filter.work_type_list | array | 否 | 作品类型过滤 ["video", "image", "canvas"] |

## 搜索建议 API
`/mweb/search/v1/guess` 返回热门搜索词：
```json
{
  "data": {
    "guess_list": [
      {"gid": "0", "word": "毛笔字"},
      {"gid": "0", "word": "ip"},
      {"gid": "0", "word": "海报制作"}
    ]
  }
}
```

## Query 构造规则

### 有图片时
提取：**[主体] + [风格] + [核心元素]**
- 错误：`类似的图片`
- 正确：`摩登上海 陆家嘴 蓝色调 海报`

### 纯文本时
直接提取关键词

## Offset 计算规则

### 条件 A → offset = 上轮offset + count
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
    "has_more": true,
    "next_offset": 20,
    "item_list": [
      {
        "common_attr": {
          "id": "xxx",
          "title": "作品标题",
          "cover_url": "https://...",
          "cover_url_map": {"720": "https://..."}
        },
        "author": {
          "name": "作者名",
          "avatar_url": "https://..."
        },
        "aigc_image_params": {
          "text2image_params": {
            "prompt": "生成时使用的提示词"
          }
        }
      }
    ]
  }
}
```

## 注意
- 连续搜索时**严禁重置 offset 为 0**（除非条件B）
- 关键词重叠度 >80% 时必须递增 offset
- 使用 `next_offset` 作为下一页的 offset 值
