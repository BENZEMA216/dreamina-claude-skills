#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SOURCE="$SCRIPT_DIR/.claude/skills"

echo "Dreamina Skills 安装脚本"
echo "========================"
echo ""
echo "选择安装位置："
echo "1) 全局安装 (~/.claude/skills) - 所有项目可用"
echo "2) 当前项目安装 (./.claude/skills) - 仅当前项目可用"
echo ""
read -p "请选择 [1/2]: " choice

case $choice in
  1)
    TARGET_DIR="$HOME/.claude/skills"
    ;;
  2)
    TARGET_DIR="./.claude/skills"
    ;;
  *)
    echo "无效选择"
    exit 1
    ;;
esac

mkdir -p "$TARGET_DIR"

for file in "$SKILLS_SOURCE"/*.md; do
  filename=$(basename "$file")
  cp "$file" "$TARGET_DIR/"
  echo "已安装: $filename"
done

echo ""
echo "安装完成！Skills 已安装到: $TARGET_DIR"
echo ""
echo "包含 16 个 Skills，可直接使用。"
