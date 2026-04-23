#!/bin/bash
# StarryForest Agent SKILL 快速开始

# 设置 Python 路径
export PYTHONPATH=/home/wudi:$PYTHONPATH

# 示例 1：发送单个提醒事项
python3 << 'EOF'
import sys
sys.path.append('/home/wudi')

from skills import StarryForestAgent

agent = StarryForestAgent()
agent.create_reminder(
    title="测试提醒",
    due="2026-02-07 22:00",
    notes="来自快速开始",
    priority="中"
)
agent.send_all("starryforest_ymxk@hotmail.com")
EOF

echo ""
echo "✅ 提醒事项已发送！"
echo ""
echo "更多示例："
echo "  python3 /home/wudi/skills/examples.py --example 1  # 单个提醒事项"
echo "  python3 /home/wudi/skills/examples.py --example 2  # 批量操作"
echo "  python3 /home/wudi/skills/examples.py --example 3  # 日历日程"
echo "  python3 /home/wudi/skills/examples.py --example 4  # 备忘录"
echo "  python3 /home/wudi/skills/examples.py --example 5  # 专注模式"
echo "  python3 /home/wudi/skills/examples.py --example 6  # 音乐控制"
echo "  python3 /home/wudi/skills/examples.py --example 7  # 写日记"
echo "  python3 /home/wudi/skills/examples.py --example 8  # QQ 邮箱"
echo "  python3 /home/wudi/skills/examples.py --example 9  # 便捷函数"
echo "  python3 /home/wudi/skills/examples.py --example 10  # 复用 Agent"
echo ""
echo "详细文档：/home/wudi/skills/README.md"
