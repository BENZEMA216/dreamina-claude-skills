# Dreamina Agent Skills for Claude Code

即梦 AI 创作工具的 Claude Code Skills 集合。

## 快速安装

```bash
chmod +x install-skills.sh
./install-skills.sh
```

## Skills 列表

### 工具类
| Skill | 说明 |
|-------|------|
| `dreamina-gen-image` | 文生图 |
| `dreamina-edit-image` | 图片编辑/参考生图 |
| `dreamina-poster` | 排版编辑 |
| `dreamina-super-resolution` | 图片超分 |
| `dreamina-foreground-segmentation` | 抠图 |
| `dreamina-video-first-frame` | 首帧生视频 |
| `dreamina-video-first-end-frame` | 首尾帧生视频 |
| `dreamina-video-multi-frame` | 多帧生视频 |
| `dreamina-inspiration-search` | 灵感搜索 |

### 规范类
| Skill | 说明 |
|-------|------|
| `dreamina-prompt-writing` | Prompt 撰写规范 |
| `dreamina-video-description` | 视频描述规范 |
| `dreamina-poster-design` | 海报设计规范 |
| `dreamina-character-consistency` | 角色一致性 |
| `dreamina-text-in-image` | 图片文字规范 |

### 配置类
| Skill | 说明 |
|-------|------|
| `dreamina-api-config` | API 基础配置 |
| `dreamina-auth` | 认证配置（已包含团队 cookie） |

## 使用要求

- 需要在字节内网环境
- API 地址：`https://dreamina-agent-operation.bytedance.net/dreamina/mcp/v1`

## 手动安装

将 `.claude/skills/` 目录复制到：
- 全局：`~/.claude/skills/`
- 项目：`<项目目录>/.claude/skills/`
