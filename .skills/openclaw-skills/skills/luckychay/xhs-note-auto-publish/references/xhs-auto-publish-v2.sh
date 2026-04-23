#!/bin/bash

# 小红书笔记自动生成与发布脚本（版本2）
# 支持两种模式：外部主题模式和自动选题模式

# 显示帮助信息
show_help() {
    cat << EOF
小红书笔记自动生成与发布脚本

使用方法:
  $0 [选项] [主题]

选项:
  -a, --auto         自动选题模式（搜索小红书热点内容确定主题）
  -h, --help         显示此帮助信息

参数:
  主题：任意外部输入的主题，将直接传递给agent处理（默认模式）

示例:
  # 外部主题模式
  $0 "新加坡Kaplan学院"
  $0 "新加坡留学申请攻略"
  $0 "新加坡学生签证最新政策"

  # 自动选题模式
  $0 --auto
  $0 -a

模式说明:
  1. 外部主题模式：使用用户指定的主题生成内容
  2. 自动选题模式：自动搜索小红书社区关于新加坡私立大学留学的热点内容确定主题

通用要求:
  - 封面使用ImageMagick生成浅色背景深色字体封面，标题作为封面文字
  - 标题默认选择第一个
  - 内容真诚务实、不引导讨论
  - 话题标签不超过5个
  - 必须包含#留学新加坡 #新加坡私立大学
  - 生成完成后使用小红书技能的幂等校验发布脚本发布无需确认
  - 仅发布一次，无论成功与否均退出
EOF
}

# 构建prompt
build_prompt() {
    local mode="$1"  # auto 或 manual
    local topic="$2"  # 主题（仅manual模式使用）
    
    local prompt=""
    
    if [ "$mode" = "auto" ]; then
        # 自动选题模式
        prompt="请生成一篇关于新加坡私立大学留学的笔记，主题请根据新加坡私立大学留学的热点内容自行确定，要求：封面使用ImageMagick生成浅色背景深色字体封面，标题作为封面文字，标题默认选择第一个，封面文字内容与标题保持一致，内容真诚务实、不引导讨论，话题标签不超过5个，必须包含#留学新加坡 #新加坡私立大学，生成完成后使用小红书技能发布无需确认，且仅发布一次,无论成功与否均停止"
    else
        # 外部主题模式
        prompt="请生成一篇关于${topic}的小红书笔记，要求：封面使用ImageMagick生成浅色背景深色字体封面，标题作为封面文字，标题默认选择第一个，封面文字内容与标题保持一致，内容真诚务实、不引导讨论，话题标签不超过5个，必须包含#留学新加坡 #新加坡私立大学，生成完成后使用小红书技能发布脚本发布无需确认，且仅发布一次，无论成功与否均停止"
    fi
    
    echo "$prompt"
}

# 主函数
main() {
    local auto_mode=false
    local topic=""
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--auto)
                auto_mode=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                echo "错误: 未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                # 第一个非选项参数作为主题
                if [ -z "$topic" ]; then
                    topic="$1"
                else
                    topic="$topic $1"
                fi
                shift
                ;;
        esac
    done
    
    # 检查参数
    if [ "$auto_mode" = false ] && [ -z "$topic" ]; then
        show_help
        exit 1
    fi
    
    echo "========================================"
    echo "  小红书笔记自动生成与发布脚本"
    echo "========================================"
    echo
    
    # 显示模式信息
    if [ "$auto_mode" = true ]; then
        echo "模式: 自动选题模式"
        echo "说明: 将自动搜索小红书社区热点内容确定主题"
        echo
    else
        echo "模式: 外部主题模式"
        echo "主题: $topic"
        echo
    fi
    
    # 构建标准prompt
    local prompt
    if [ "$auto_mode" = true ]; then
        prompt=$(build_prompt "auto" "")
    else
        prompt=$(build_prompt "manual" "$topic")
    fi
    
    echo "生成的prompt:"
    echo "$prompt"
    echo
    
    # 幂等性检查：避免重复执行
    echo "检查是否有正在运行的xhs-auto-publish任务..."
    local running_count
    running_count=$(ps aux | grep -E "openclaw.*agent.*xhs-auto-publish" | grep -v grep | wc -l)
    
    if [ "$running_count" -gt 0 ]; then
        echo "警告：发现 $running_count 个正在运行的xhs-auto-publish任务，跳过本次执行以避免重复"
        echo "如果要强制执行，请先停止现有任务"
        exit 1
    fi
    
    echo "正在执行agent任务..."
    
    # 执行agent任务
    openclaw agent --message "$prompt" --agent main
    
    echo
    echo "任务已提交给agent处理，无论成功与否脚本都将退出。"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
