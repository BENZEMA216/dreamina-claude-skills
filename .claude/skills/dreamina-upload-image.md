---
name: dreamina-upload-image
description: 通过 ImageX 公网 API 上传图片获取 URI，用于垫图生成
---

# 图片上传工具

## 概述
通过 ByteDance ImageX 服务上传图片，获取 `image_uri` 用于后续垫图编辑。无需内网环境。

## 上传流程

### 1. 获取上传令牌
```bash
curl -X POST 'https://jimeng.jianying.com/mweb/v1/get_upload_token?aid=513695&da_version=3.2.2' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: sessionid=<your_sessionid>' \
  -d '{"scene": 2}'
```

响应:
```json
{
  "ret": "0",
  "data": {
    "access_key_id": "AKTP...",
    "secret_access_key": "...",
    "session_token": "..."
  }
}
```

### 2. 申请上传地址
使用 AWS V4 签名请求 ImageX:
```
GET https://imagex.bytedanceapi.com/?Action=ApplyImageUpload&FileSize=<size>&ServiceId=tb4s082cfz&Version=2018-08-01
```

### 3. 上传文件
```bash
POST https://<UploadHost>/upload/v1/<StoreUri>
Authorization: <Auth from step 2>
Content-Crc32: <crc32_hex>
Content-Type: application/octet-stream

<binary_data>
```

### 4. 提交上传
```
POST https://imagex.bytedanceapi.com/?Action=CommitImageUpload&ServiceId=tb4s082cfz&Version=2018-08-01
Body: {"SessionKey": "<from step 2>"}
```

返回 `image_uri` 如: `tos-cn-i-tb4s082cfz/xxxxx`

## Python 完整示例

```python
import requests
import hashlib
import hmac
import binascii
import zlib
from datetime import datetime

def get_upload_token(sessionid):
    resp = requests.post(
        'https://jimeng.jianying.com/mweb/v1/get_upload_token',
        params={'aid': 513695, 'da_version': '3.2.2'},
        headers={'Cookie': f'sessionid={sessionid}'},
        json={'scene': 2}
    )
    return resp.json()['data']

def aws_v4_sign(method, params, body, credentials, region='cn-north-1', service='imagex'):
    now = datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    amz_day = now.strftime('%Y%m%d')
    
    headers = {
        'X-Amz-Date': amz_date,
        'X-Amz-Security-Token': credentials['session_token']
    }
    
    if body:
        body_hash = hashlib.sha256(body.encode() if isinstance(body, str) else body).hexdigest()
        headers['X-Amz-Content-Sha256'] = body_hash
    else:
        body_hash = hashlib.sha256(b'').hexdigest()
    
    signed_headers = ';'.join(sorted(k.lower() for k in headers.keys()))
    canonical_headers = ''.join(f'{k.lower()}:{v}\n' for k, v in sorted(headers.items()))
    
    query_string = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
    canonical_request = f'{method}\n/\n{query_string}\n{canonical_headers}\n{signed_headers}\n{body_hash}'
    
    credential_scope = f'{amz_day}/{region}/{service}/aws4_request'
    string_to_sign = f'AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}'
    
    k_date = hmac.new(f"AWS4{credentials['secret_access_key']}".encode(), amz_day.encode(), hashlib.sha256).digest()
    k_region = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode(), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
    
    headers['Authorization'] = f"AWS4-HMAC-SHA256 Credential={credentials['access_key_id']}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    return headers

def upload_image(sessionid, image_path):
    with open(image_path, 'rb') as f:
        file_data = f.read()
    
    crc32_value = zlib.crc32(file_data) & 0xffffffff
    crc32_hex = format(crc32_value, 'x')
    
    creds = get_upload_token(sessionid)
    
    params = {
        'Action': 'ApplyImageUpload',
        'FileSize': len(file_data),
        'ServiceId': 'tb4s082cfz',
        'Version': '2018-08-01',
        's': ''.join(__import__('random').choices('abcdefghijklmnopqrstuvwxyz0123456789', k=11))
    }
    headers = aws_v4_sign('GET', params, '', creds)
    resp = requests.get('https://imagex.bytedanceapi.com/', params=params, headers=headers)
    upload_addr = resp.json()['Result']['UploadAddress']
    
    upload_url = f"https://{upload_addr['UploadHosts'][0]}/upload/v1/{upload_addr['StoreInfos'][0]['StoreUri']}"
    resp = requests.post(upload_url, data=file_data, headers={
        'Authorization': upload_addr['StoreInfos'][0]['Auth'],
        'Content-Crc32': crc32_hex,
        'Content-Type': 'application/octet-stream'
    })
    
    commit_params = {
        'Action': 'CommitImageUpload',
        'ServiceId': 'tb4s082cfz',
        'Version': '2018-08-01'
    }
    commit_body = {'SessionKey': upload_addr['SessionKey']}
    headers = aws_v4_sign('POST', commit_params, __import__('json').dumps(commit_body), creds)
    headers['Content-Type'] = 'application/json'
    resp = requests.post('https://imagex.bytedanceapi.com/', params=commit_params, json=commit_body, headers=headers)
    
    return resp.json()['Result']['Results'][0]['Uri']

# 使用示例
# image_uri = upload_image('your_sessionid', '/path/to/image.png')
# print(f'Image URI: {image_uri}')
```

## 支持的输入格式
- 本地文件路径
- HTTP/HTTPS URL
- Base64 数据 (data:image/png;base64,...)

## 返回值
`image_uri` 格式: `tos-cn-i-tb4s082cfz/<hash>`

用于 `edit_image` 的 `image_uri_list` 参数。
