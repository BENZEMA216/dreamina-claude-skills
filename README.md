# Dreamina Claude Skills

即梦 AI 创作工具的 Claude Code 技能集合，提供图片/视频生成、编辑功能和最佳实践指南。

## 🚀 快速开始

### 1. 安装 Claude Code

确保已安装最新版本的 Claude Code：
```bash
npm install -g @anthropic/claude-code
```

### 2. 配置 Skills

将本项目的 skills 目录链接到 Claude Code：

```bash
# 克隆本仓库
git clone https://github.com/BENZEMA216/dreamina-claude-skills.git
cd dreamina-claude-skills

# 创建软链接（推荐）
ln -s $(pwd)/.claude/skills ~/.claude/skills/dreamina

# 或者直接复制
cp -r .claude/skills/* ~/.claude/skills/
```

### 3. 安装推荐工具

#### Chrome DevTools MCP (推荐)
用于网页自动化和截图功能：

```bash
# 使用 npm 安装
npm install -g @britt/mcp-server-chrome-devtools

# 配置 Claude Code
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

配置示例：
```json
{
  "name": "chrome-devtools",
  "command": "npx",
  "args": ["@britt/mcp-server-chrome-devtools"],
  "env": {}
}
```

### 4. 获取 Dreamina SessionID（可以安装 Chrome devtool 之后，让 Claude Code 帮你完成上述步骤）

1. 访问 [即梦创作平台](https://jimeng.jianying.com)
2. 登录账号
3. 打开浏览器开发者工具 (F12)
4. 在 Application > Cookies 中找到 `sessionid`
5. 复制 sessionid 值备用

## 📋 技能列表

### 工具类技能
- `dreamina-gen-image` - 文生图
- `dreamina-edit-image` - 图片编辑
- `dreamina-super-resolution` - 智能超清
- `dreamina-foreground-segmentation` - 智能抠图
- `dreamina-upload-image` - 图片上传
- `dreamina-video-first-frame` - 首帧生视频
- `dreamina-video-first-end-frame` - 首尾帧生视频
- `dreamina-video-multi-frame` - 多帧生视频
- `dreamina-inspiration-search` - 灵感搜索
- `dreamina-query-result` - 结果查询

### 规范类技能
- `dreamina-prompt-writing` - Prompt 编写规范
- `dreamina-video-description` - 视频描述规范
- `dreamina-poster-design` - 海报设计规范
- `dreamina-character-consistency` - 角色一致性指南
- `dreamina-text-in-image` - 图片文字生成规范

### 配置类技能
- `dreamina-api-config` - API 配置说明
- `dreamina-auth` - 认证配置
- `dreamina-batch-management` - 批量管理规范

### 特殊功能
- `dreamina-poster` - 海报生成
- `storyboard-generator` - 分镜生成器

### 视频配音配乐
- `/tts` - TTS 配音（Fish Audio / Azure Speech / OpenAI / MiniMax）
- `/bgm` - AI 配乐（Suno / MusicGen / Mubert）
- `/compose` - 视频合成（FFmpeg / MoviePy）
- `/video-pipeline` - 全流程：文案 → 配音 → 配乐 → 合成

## 💡 使用示例

### 生成图片
```bash
# 在 Claude Code 中使用
claude code

# 输入指令
> 使用 dreamina 生成一张"夕阳下的富士山"图片，16:9比例
```

### 批量生成
```bash
> 批量生成5张不同风格的猫咪图片，创建新文件夹管理
```

### 视频生成
```bash
> 使用首帧图片生成3秒的动态视频
```

### 视频配音配乐
```bash
# TTS 配音
> /tts 用 OpenAI 的 nova 音色朗读这段文案："欢迎来到即梦创作平台"

# AI 配乐
> /bgm 生成30秒轻快的企业宣传背景音乐

# 视频合成
> /compose 把 video.mp4、voice.mp3、bgm.mp3 合成为 final.mp4

# 一条龙
> /video-pipeline 给 promo.mp4 配上这段文案的配音，再加个轻快的BGM
```

## 🎬 Video Tools

`video-tools/` 目录包含视频自动化配音配乐 Python 工具链：

### TTS 配音（4 服务）
```bash
python3 video-tools/tts/fish_audio.py --text "文案" --voice "音色ID" --output voice.mp3
python3 video-tools/tts/azure_speech.py --text "文案" --voice "zh-CN-XiaoxiaoNeural" --output voice.mp3
python3 video-tools/tts/openai_tts.py --text "文案" --voice "alloy" --output voice.mp3
python3 video-tools/tts/minimax_tts.py --text "文案" --voice "female-shaonv" --output voice.mp3
```

### AI 配乐（3 服务）
```bash
python3 video-tools/music/suno.py --prompt "轻快的背景音乐" --duration 30 --output bgm.mp3
python3 video-tools/music/musicgen.py --prompt "calm background music" --duration 30 --output bgm.mp3  # 需GPU
python3 video-tools/music/mubert.py --prompt "upbeat corporate" --duration 30 --output bgm.mp3
```

### 视频合成
```bash
python3 video-tools/compose/compose.py --video input.mp4 --voice voice.mp3 --bgm bgm.mp3 --bgm-volume 0.2 --output final.mp4
```

### 环境变量
```bash
# TTS
export FISH_AUDIO_KEY="..."
export AZURE_SPEECH_KEY="..."
export AZURE_SPEECH_REGION="eastasia"  # 可选
export OPENAI_API_KEY="..."
export MINIMAX_KEY="..."

# Music
export SUNO_KEY="..."
export MUBERT_KEY="..."
```

## 🔧 高级配置

### 环境变量
可以通过环境变量配置默认参数：

```bash
export DREAMINA_SESSIONID="your_sessionid"
export DREAMINA_DEFAULT_MODEL="jimeng-image-4.5"
```

### 自定义配置文件
在项目根目录创建 `.dreamina.config.json`：

```json
{
  "sessionid": "your_sessionid",
  "defaultModel": "jimeng-image-4.5",
  "defaultRatio": "16:9",
  "outputDir": "./outputs"
}
```

## 📊 技能完备性

当前技能集合完备性：**95%**

详细测试报告：
- [完整测试报告](./Dreamina_Skills_Test_Report.md)
- [完备性总结](./skills-completeness-summary.md)

## 🛠️ 故障排除

### SessionID 过期
- 重新登录即梦平台获取新的 sessionid
- 更新配置中的 sessionid 值

### API 调用失败
- 检查网络连接
- 确认 sessionid 有效
- 查看 API 响应错误信息

### Chrome DevTools 连接失败
- 确保 Chrome 浏览器已启动
- 检查 MCP 服务是否正常运行
- 重启 Claude Code

## 📚 相关文档

- [CLAUDE.md](./CLAUDE.md) - 项目指导文件
- [API 配置说明](./.claude/skills/dreamina-api-config.md)
- [认证配置](./.claude/skills/dreamina-auth.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License
