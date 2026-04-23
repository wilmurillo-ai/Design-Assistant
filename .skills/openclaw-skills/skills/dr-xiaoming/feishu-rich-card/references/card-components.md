# 飞书卡片组件速查手册 (Schema 2.0)

> ⚠️ **实测日期：2026-03-25** — 所有标注 ✅ 的组件已在飞书 Open API 验证通过。

---

## ⚠️ Schema 2.0 废弃标签（重要！）

以下标签在 Schema 2.0 中**已废弃**，发送会报 `200861 unsupported tag` 错误：

| 废弃标签 | 说明 | 替代方案 |
|---------|------|---------|
| `action` | 按钮容器 | 用 markdown `[文字](url)` 链接替代 |
| `note` | 底部备注 | 用 markdown + `<font color='grey'>...</font>` 替代 |

### 按钮替代方案

```json
// ❌ 废弃写法
{"tag": "action", "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": "查看"}, "url": "https://..."}]}

// ✅ 替代写法
{"tag": "markdown", "content": "[查看详情](https://...)"}
```

### 备注替代方案

```json
// ❌ 废弃写法
{"tag": "note", "elements": [{"tag": "plain_text", "content": "备注文字"}]}

// ✅ 替代写法
{"tag": "markdown", "content": "<font color='grey'>备注文字</font>"}
```

---

## Card 基本结构 ✅

```json
{
  "schema": "2.0",
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "标题文字"},
    "template": "blue"
  },
  "body": {"elements": [ ... ]}
}
```

**颜色模板：** `blue` `wathet` `turquoise` `green` `yellow` `orange` `red` `carmine` `violet` `purple` `indigo` `grey` `default`

---

## Markdown ✅

```json
{"tag": "markdown", "content": "**粗体** *斜体* ~~删除线~~ `代码`\n- 列表\n[链接](url)\n<at id=all></at>\n<font color='red'>彩色文字</font>"}
```

支持：粗体、斜体、删除线、行内代码、链接、列表、引用、@人、`<font color>` 标签

---

## HR 分割线 ✅

```json
{"tag": "hr"}
```

---

## Column Set 多列布局 ✅

```json
{
  "tag": "column_set",
  "flex_mode": "none",
  "background_style": "default",
  "columns": [
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "vertical_align": "top",
      "elements": [{"tag": "markdown", "content": "左列"}]
    },
    {
      "tag": "column",
      "width": "weighted",
      "weight": 1,
      "vertical_align": "top",
      "elements": [{"tag": "markdown", "content": "右列"}]
    }
  ]
}
```

- **flex_mode:** `none` | `stretch` | `flow` | `bisect`
- **width:** `"weighted"` (配合 weight) | `"auto"` | 固定像素如 `"120px"`

---

## Collapsible Panel 折叠面板 ✅

```json
{
  "tag": "collapsible_panel",
  "expanded": false,
  "header": {
    "title": {"tag": "plain_text", "content": "展开查看详情"}
  },
  "elements": [
    {"tag": "markdown", "content": "折叠内容..."}
  ]
}
```

> ⚠️ **陷阱：** `vertical_spacing` 属性不接受 `"default"` 等字符串值。建议**省略此属性**，或用像素值如 `"8px"`。

---

## Image 图片 ✅

```json
{
  "tag": "img",
  "img_key": "img_v2_xxx",
  "alt": {"tag": "plain_text", "content": "alt text"},
  "mode": "fit_horizontal",
  "preview": true
}
```

需先通过飞书上传图片接口获取 `img_key`。

---

## Chart 图表 ✅

基于 VChart 的图表组件，支持折线图、柱状图、饼图。

### 折线图 (line)

```json
{
  "tag": "chart",
  "chart_spec": {
    "type": "line",
    "title": {"text": "趋势图"},
    "data": {
      "values": [
        {"date": "1月", "value": 100, "type": "系列A"},
        {"date": "2月", "value": 150, "type": "系列A"},
        {"date": "1月", "value": 80, "type": "系列B"},
        {"date": "2月", "value": 120, "type": "系列B"}
      ]
    },
    "xField": "date",
    "yField": "value",
    "seriesField": "type",
    "point": {"visible": true}
  }
}
```

### 柱状图 (bar)

```json
{
  "tag": "chart",
  "chart_spec": {
    "type": "bar",
    "title": {"text": "对比图"},
    "data": {
      "values": [
        {"category": "产品A", "value": 200, "type": "Q1"},
        {"category": "产品A", "value": 300, "type": "Q2"},
        {"category": "产品B", "value": 150, "type": "Q1"},
        {"category": "产品B", "value": 250, "type": "Q2"}
      ]
    },
    "xField": "category",
    "yField": "value",
    "seriesField": "type",
    "stack": true
  }
}
```

`stack: true` 堆叠模式；省略或 `false` 为分组模式。

### 饼图 (pie)

```json
{
  "tag": "chart",
  "chart_spec": {
    "type": "pie",
    "title": {"text": "占比分布"},
    "data": {
      "values": [
        {"category": "分类A", "value": 40},
        {"category": "分类B", "value": 30},
        {"category": "分类C", "value": 30}
      ]
    },
    "categoryField": "category",
    "valueField": "value"
  }
}
```

---

## 完整示例：数据看板卡片

```json
{
  "schema": "2.0",
  "config": {"wide_screen_mode": true},
  "header": {
    "title": {"tag": "plain_text", "content": "📊 周度数据看板"},
    "template": "turquoise"
  },
  "body": {
    "elements": [
      {
        "tag": "column_set",
        "flex_mode": "none",
        "columns": [
          {"tag": "column", "width": "weighted", "weight": 1,
           "elements": [{"tag": "markdown", "content": "**总阅读量**\n<font color='blue'>12,345</font>"}]},
          {"tag": "column", "width": "weighted", "weight": 1,
           "elements": [{"tag": "markdown", "content": "**互动率**\n<font color='green'>8.5%</font>"}]},
          {"tag": "column", "width": "weighted", "weight": 1,
           "elements": [{"tag": "markdown", "content": "**新增粉丝**\n<font color='red'>+523</font>"}]}
        ]
      },
      {"tag": "hr"},
      {
        "tag": "chart",
        "chart_spec": {
          "type": "line",
          "title": {"text": "每日阅读趋势"},
          "data": {"values": [
            {"date": "周一", "value": 1500},
            {"date": "周二", "value": 1800},
            {"date": "周三", "value": 2200}
          ]},
          "xField": "date",
          "yField": "value",
          "point": {"visible": true}
        }
      },
      {"tag": "hr"},
      {
        "tag": "collapsible_panel",
        "expanded": false,
        "header": {"title": {"tag": "plain_text", "content": "📋 查看明细"}},
        "elements": [
          {"tag": "markdown", "content": "| 日期 | 阅读 | 点赞 |\n|---|---|---|\n| 周一 | 1500 | 120 |\n| 周二 | 1800 | 150 |"}
        ]
      },
      {"tag": "hr"},
      {"tag": "markdown", "content": "<font color='grey'>自动生成 | 数据看板</font>"}
    ]
  }
}
```
