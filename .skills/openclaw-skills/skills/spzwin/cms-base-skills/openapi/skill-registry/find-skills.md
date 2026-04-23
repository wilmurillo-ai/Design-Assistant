# Skill 发现接口

## 接口信息

| 项 | 值 |
|---|---|
| 请求方式 | GET |
| URL | `https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list` |
| 需要 token | 否（nologin 接口） |

## 说明

获取平台所有已发布的 Skill 列表。无需鉴权。

## 响应示例

```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "123",
      "name": "work-collaboration",
      "code": "work-collaboration",
      "version": "1.0",
      "status": "",
      "description": "工作协同系统助手",
      "downloadUrl": "https://filegpt-hn.file.mediportal.com.cn/xxx.zip",
      "isInternal": false,
      "label": "",
      "createTime": "2025-01-01 00:00:00"
    }
  ]
}
```

## 对应脚本

`scripts/skill_registry/find_skills.py`

## CLI 参数

| 参数 | 说明 |
|------|------|
| `--search <keyword>` | 按关键词搜索（名称/描述/code 模糊匹配） |
| `--detail <query>` | 查看单个 Skill 详情（按 code 或 name 匹配） |
| `--url <query>` | 仅输出 downloadUrl（供机器调用） |
| `--json` | 输出原始 JSON 格式 |
