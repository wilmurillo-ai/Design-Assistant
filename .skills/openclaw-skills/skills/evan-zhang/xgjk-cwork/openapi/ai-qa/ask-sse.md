# GET https://cwork-web.mediportal.com.cn/cwork/report/aiSseQa

## 作用
针对 CWork 内部知识库（笔记本）进行 AI 问答。

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `content` | string | 是 | 问答内容 |
| `notebookId` | string | 否 | 笔记本 ID (不传则搜索全局) |

## 脚本映射
- `../../scripts/ai-qa/ask-sse.py`
