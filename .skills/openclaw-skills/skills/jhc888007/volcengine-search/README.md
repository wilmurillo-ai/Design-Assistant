# Search Web Skill

使用火山引擎联网问答智能体 API 进行网络搜索和问答。

**注意：建议在 TOOLS.md 中指明搜索时调用 volcengine-search 技能，防止大模型尝试调用自带搜索工具，浪费时间和token**

## 功能特性

- ✅ 联网搜索并获取智能体回答
- ✅ 支持参考来源展示（URL、标题、发布时间）
- ✅ 支持追问建议
- ✅ 支持流式和非流式响应
- ✅ Token 使用统计
- ✅ 高级功能：引用角标、图文混排、百科划线词等

## 环境变量配置

在调用脚本前，您需要在火山引擎控制台开通“联网搜索/联网搜索总结版”服务：
https://console.volcengine.com/search-infinity/web-search
然后生成您的 **API Key**：
https://console.volcengine.com/search-infinity/api-key

## 官方说明文档
https://www.volcengine.com/docs/87772/2272953?lang=zh

**调用示例：**
```bash
# 执行一次普通的网页搜索
python scripts/search_web.py -q "北京市这周末的天气"

# 执行带有大模型智能总结的搜索
python scripts/search_web.py -q "2026年量子计算的最新商业化进展" -t web_summary
```

## 功能说明

search_type有两种类型，web（不带总结）和web_summary（带总结），分别每月有一定免费额度。
