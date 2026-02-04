---
name: dreamina-auth
description: Dreamina API 认证配置
---

# Dreamina API 认证配置

## SessionID

从浏览器 Cookie 中获取 `sessionid` 字段即可，无需完整 cookie。

```
sessionid=7ee405dc81fbb63630aab56fcf91812b
```

### 获取方式
1. 登录 https://jimeng.jianying.com
2. 打开浏览器开发者工具 (F12)
3. 在 Application > Cookies 中找到 `sessionid`

## Sign 签名生成

```python
import hashlib
import time

def generate_sign(uri_path):
    device_time = int(time.time())
    sign_str = f"9e2c|{uri_path[-7:]}|7|5.8.0|{device_time}||11ac"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign, device_time
```

## 通用 Headers

```python
def get_headers(sessionid, uri_path):
    sign, device_time = generate_sign(uri_path)
    return {
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
```

## Base URL

```
https://jimeng.jianying.com/mweb/v1
```

## 常用端点
| 功能 | 端点 |
|------|------|
| 图片/视频生成 | `/aigc_draft/generate` |
| 结果查询 | `/get_history_by_ids` |
| 上传令牌 | `/get_upload_token` |
