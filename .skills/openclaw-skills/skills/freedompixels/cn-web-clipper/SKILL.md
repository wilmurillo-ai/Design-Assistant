---
name: cn-web-clipper
description: "网页剪藏工具。发送网页链接，自动提取正文内容，保存为本地Markdown文件。基于readability算法提取干净正文，支持批量处理。"
metadata:
  openclaw:
    emoji: "📎"
    category: productivity
    tags:
      - web
      - clipper
      - bookmark
---

## 功能
- 网页正文智能提取（readability算法）
- 本地Markdown文件保存
- 标题/作者/发布日期识别
- 文章摘要自动生成（前200字）
- 批量URL处理

## 使用方法
```
python3 scripts/clip_webpage.py <URL>
python3 scripts/clip_webpage.py <URL> --dir <保存目录>
```

## 依赖
- Python 3.7+
- requests, beautifulsoup4, readability-lxml

## 权限声明
- 访问网页URL
- 生成本地Markdown文件

## 使用场景
- 收藏优质文章到本地知识库
- 竞品调研资料归档
- 论文/报告内容提取
- 网页内容离线备份
