# todos 示例

## 模块说明
待办事项管理，支持列表查询和完成状态切换。

## 依赖脚本
- 列表：`../../scripts/todos/get-list.py`
- 完成：`../../scripts/todos/complete.py`

---

## 标准流程（含 3S1R 管理闭环）

### 场景一：查询待办列表

#### Step 1 — Suggest（建议）
```
建议：默认拉取当前用户的所有待办事项，按截止日期排序。
如需筛选已完成/未完成状态，可补充 filter 参数。
```

#### Step 2 — Decide（确认/决策）
```
请确认：
□ 查询范围：全部 / 仅未完成 / 仅已完成
□ 是否需要按截止日期过滤：是 / 否
```

#### Step 3 — Execute（执行）
执行待办列表查询。

#### Step 4 — Log（留痕）
```
[LOG] todos.list | filter:pending | result:N | ts:ISO8601
```

---

### 场景二：完成待办项（数据变动操作 ⚠️）

#### Step 1 — Suggest（建议）
**涉及数据变动前，必须先给出建议并说明影响。**

```
建议：将待办项 [todoId] 标记为已完成。
该操作不可逆（但可通过再次打开恢复），请确认。
注意：完成操作会改变数据状态，必须经过明确确认。
```

#### Step 2 — Decide（确认/决策）
**数据变动前，必须获取用户明确决策。**

```
⚠️ 确认执行数据变动操作：
□ 待办项 ID：____
□ 操作：标记为已完成（不可逆，请确认）
□ 输入 "确认" 以继续：____
```

#### Step 3 — Execute（执行）
执行完成操作脚本。

#### Step 4 — Log（留痕）
**数据变动结果必须完整记录。**

```
[LOG] todos.complete | todoId:xxx | action:complete | ts:ISO8601 | operator:user
```

---

## 输出格式

**列表查询：**
```json
{
  "items": [
    {
      "todoId": "...",
      "content": "...",
      "status": "pending|completed",
      "dueDate": "...",
      "createTime": "..."
    }
  ]
}
```

**完成操作：**
```json
{
  "success": true,
  "todoId": "..."
}
```

---

## 注意事项
- 查询操作：只读，日志记录参数
- 完成操作：数据变动，需强制 Suggest → Decide → Log 闭环
- 日志必须包含操作类型（query/complete）、操作时间、操作人
