# notebooklm-sync

## 功能说明

该 Skill 用于将本地生成的 Markdown 内容同步到 NotebookLM。

在知识库系统中，当用户执行 `/zk.add` 并成功写入飞书后，
该 Skill 会自动被调用，将同一内容同步到 NotebookLM，
用于后续的 AI 问答、总结、对比等能力。

---

## 使用场景

- 知识库内容二次结构化存储
- 飞书 → NotebookLM 自动同步
- AI 长文本分析与知识沉淀
- 构建可问答知识库

---

## 输入参数

| 参数名        | 类型   | 必填 | 说明 |
|--------------|--------|------|------|
| notebook_id  | string | 是   | NotebookLM 笔记本 ID |
| file_path    | string | 是   | 本地 Markdown 文件路径 |

---

## 执行逻辑

调用 NotebookLM CLI：

/Users/block/notebooklm-env/bin/notebooklm source add \
  --notebook {{notebook_id}} \
  --type file {{file_path}}

---

## 输出结果

- 成功：返回 source ID
- 失败：返回错误信息

---

## 示例

输入：

notebook_id = e363ecbe-70bc-490e-acbe-329f7e6fb85c  
file_path = /tmp/zk_123.md  

执行：

/Users/block/notebooklm-env/bin/notebooklm source add \
  --notebook e363ecbe-70bc-490e-acbe-329f7e6fb85c \
  --type file /tmp/zk_123.md

---

## 注意事项

- 必须确保 notebooklm CLI 可用
- 必须在正确 Python 虚拟环境路径下执行
- 文件必须存在，否则同步失败
- 不影响飞书主存储，仅作为增强同步

---

## 触发方式

该 Skill 不由用户手动触发  
由 `/zk.add` 自动调用