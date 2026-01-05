---
name: dreamina-inspiration-search
description: 使用 dreamina_inspiration_search 工具检索优质 Prompt 和图片作为创作参考
---

# dreamina_inspiration_search 灵感搜索工具

## API 调用
```bash
curl -X POST 'https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1/search' \
  -H 'Content-Type: application/json' \
  -H 'cookie: <认证cookie>' \
  -d '{
    "query": "上海 海报 未来感",
    "offset": 0
  }'
```

## 参数说明
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| query | string | 是 | 搜索关键词 |
| offset | int | 否 | 结果偏移量，用于翻页/去重 |

## Query 构造规则

### 有图片时
提取：**[主体] + [风格] + [核心元素]**
- 错误：`类似的图片`
- 正确：`摩登上海 陆家嘴 蓝色调 海报`

### 纯文本时
直接提取关键词

## Offset 计算规则

### 条件 A → offset = 上轮offset + 8
- Query 与上轮语义相同
- 用户说"再找找"、"换一批"、"更多"
- 新图与上一张图属于同一主题

### 条件 B → offset = 0
- Query 语义完全改变
- 用户说"重新开始"、"重置"

## 重要
- 连续搜索时**严禁重置 offset 为 0**（除非条件B）
- 关键词重叠度 >80% 时必须递增 offset
