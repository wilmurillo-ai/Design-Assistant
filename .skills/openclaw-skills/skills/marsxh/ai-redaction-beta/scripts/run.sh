#!/bin/bash

# A-File-Process Skill 执行脚本
# 用于运行编译后的 TypeScript 代码

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 切换到技能目录
cd "$SKILL_DIR"

# 检查是否已编译
if [ ! -d "dist" ]; then
  echo "未找到编译输出目录，正在编译..."
  npm run build
fi

# 执行编译后的 JavaScript
node dist/index.js "$@"
