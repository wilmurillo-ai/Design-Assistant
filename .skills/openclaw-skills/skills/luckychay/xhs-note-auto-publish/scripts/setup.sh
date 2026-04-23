#!/bin/bash

# xhs-auto-publish 技能安装脚本

echo "========================================"
echo "  xhs-auto-publish 技能安装"
echo "========================================"
echo

# 检查是否在正确的目录
if [ ! -f "../SKILL.md" ]; then
    echo "错误：请在技能目录的 scripts/ 子目录中运行此脚本"
    exit 1
fi

echo "1. 检查依赖..."
echo

# 检查小红书技能是否存在
if [ ! -d "../../xhs" ]; then
    echo "⚠️  警告：小红书技能 (xhs) 未找到"
    echo "   请确保已安装小红书技能"
else
    echo "✅ 小红书技能已安装"
fi

# 检查主脚本是否存在
if [ ! -f "../references/xhs-auto-publish-v2.sh" ]; then
    echo "❌ 错误：主脚本未找到"
    exit 1
else
    echo "✅ 主脚本已就绪"
fi

echo
echo "2. 设置脚本权限..."
chmod +x ../references/xhs-auto-publish-v2.sh
echo "✅ 脚本权限已设置"

echo
echo "3. 创建工作空间脚本链接..."
# 检查工作空间 scripts 目录是否存在
if [ ! -d "../../../scripts" ]; then
    mkdir -p ../../../scripts
    echo "✅ 创建 scripts 目录"
fi

# 复制脚本到工作空间
cp ../references/xhs-auto-publish-v2.sh ../../../scripts/
chmod +x ../../../scripts/xhs-auto-publish-v2.sh
echo "✅ 脚本已复制到工作空间 scripts/ 目录"

echo
echo "4. 验证安装..."
echo "脚本位置: $(realpath ../../../scripts/xhs-auto-publish-v2.sh)"
echo "脚本权限: $(ls -la ../../../scripts/xhs-auto-publish-v2.sh | awk '{print $1}')"

echo
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo
echo "使用方法："
echo "  # 外部主题模式"
echo "  ./scripts/xhs-auto-publish-v2.sh \"新加坡Kaplan学院\""
echo "  ./scripts/xhs-auto-publish-v2.sh \"新加坡留学申请攻略\""
echo
echo "  # 自动选题模式"
echo "  ./scripts/xhs-auto-publish-v2.sh --auto"
echo "  ./scripts/xhs-auto-publish-v2.sh -a"
echo
echo "提示："
echo "  1. 确保小红书账号已登录"
echo "  2. 脚本会自动检查避免重复执行"
echo "  3. 可以配置cron定时任务自动运行"