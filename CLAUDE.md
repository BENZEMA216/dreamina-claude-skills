# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dreamina Agent Skills for Claude Code - 即梦 AI 创作工具的技能集合，用于图片/视频生成、编辑和最佳实践指南。

## API Architecture

**生成 API**: `https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1`
- `/image_generate` - 图片生成/编辑/超分/抠图
- `/video_generate` - 视频生成
- `/search` - 灵感搜索

**结果查询 API**: `https://jimeng.jianying.com/mweb/v1/get_history_by_ids?aid=513695&device_platform=web&region=cn`

## 生成流程

1. 提交任务到生成 API，获得 `submit_id`
2. 轮询结果查询 API（图片 3-5 秒，视频 10-30 秒）
3. `status=50` 表示完成，从响应中获取下载 URL
4. URL 带签名，1-2 小时过期，需立即下载

## Skills 结构

`.claude/skills/` 目录包含 17+ 个 skill 文件：
- 工具类：gen-image, edit-image, poster, super-resolution, foreground-segmentation, video-*, inspiration-search, query-result
- 规范类：prompt-writing, video-description, poster-design, character-consistency, text-in-image
- 配置类：api-config, auth
- 音乐分析：music-analyze, music-rhythm, music-emotion, music-timbre, music-tonality, music-lyrics, music-to-dreamina, music-to-storyboard, music-color-palette

## Music Analyzer

`music-analyzer/` 目录包含音频分析 Python 后端，分析本地音频文件并生成 Dreamina prompt / 分镜表 / 配色方案。

```bash
pip install -e music-analyzer/src/                    # 基础安装
python3 -m music_analyzer analyze song.mp3            # 完整分析
python3 -m music_analyzer dreamina analysis.json      # 生成 Dreamina prompt
python3 -m music_analyzer visualize song.mp3 --open   # HTML 可视化报告
```

详见 `music-analyzer/README.md`。

## 关键参数

- `generate_type`: text2imageV2, seedEdit40, image2videoV2, multiFrame2video 等
- `agent_scene`: creation_agent_v40
- `model_key`: high_aes_general_v40
- `submit_id`: UUID 格式，用于幂等和结果查询

## 环境要求

需要字节内网环境访问 API。

## 操作规范

### 图片生成和下载
- **直接执行**: 生成和下载图片的 curl 指令直接执行，无需用户确认
- **分批管理**: 生成图片下载要分批创建新的文件夹
- **文档记录**: 每个文件夹写一个 README.md 说明该批次内容

### 文件夹命名规范
```
batch-YYYYMMDD-HHmm-描述/
├── README.md
├── image1.png
├── image2.png
└── ...
```
