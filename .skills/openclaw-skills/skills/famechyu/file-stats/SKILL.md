---
name: file-stats
description: 统计给定目录的文件总数和总大小（字节和MB）。原生支持 Windows 文件路径。
# 增加明确的参数定义，告诉 LangChain/大模型必须传入 path 变量
input_schema:
  type: object
  properties:
    path:
      type: string
      description: "目标目录的绝对路径，例如 C:\\Users\\Public\\Documents"
  required:
    - path
---

# File Stats Skill

本技能用于递归扫描目标文件夹，计算其中包含的文件总数以及总占用空间。

## 处理 Windows 路径的注意事项
当用户提供 Windows 路径（例如 `C:\Users\Public\Documents`）时，请在传递给此工具前，**确保路径中的反斜杠被正确转义**（例如写成 `C:\\Users\\Public\\Documents`），或者将其替换为正斜杠（`C:/Users/Public/Documents`），以防止 JSON 解析转义错误。

## 执行方法
请运行此技能目录下的 `scripts/stats.py` 脚本，将目标目录的绝对路径作为第一个命令行参数传入。
例如命令格式为：`python stats.py <path>`
脚本将返回包含统计信息的 JSON 字符串。
