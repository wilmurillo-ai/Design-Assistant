---
name: ht-skills
description: 管理灏天文库文集和文档，支持新建文集、新建文档、查询文集/文档、更新文档、修改文档归属、管理文档层级。适用于 OpenClaw 自主写文章并上传、文集创建、文档入库、文档移动等场景。
allowed-tools: [bash]
---

# ht-skills 灏天文库管理（客户端）

通过服务端 API 调用，需配置 `config.json` 中的`token`（个人 API Token）。

---

## 客户端注意事项（必须遵守）

- **查询文集列表**：无 `--limit`、`--offset`，由服务端固定限制。
- **查询文档列表**：必须带 `--collection-id`（文集 ID）；若没有文集 ID，需先 `list_collections.py --name "文集名称"` 查询，或**向用户询问目标文集名称**。
- **查询文档列表**：无 `--limit`、`--offset`，由服务端固定限制。
- **更新文档**：`author` 字段不可更新，只能更新 name、content、sort、parent。
- **修改文档归属**：需有目标文集权限；文档属于多个文集时需指定 `--from-collection-id`。

---

## 智能体执行规范（必须遵守）

### 规范一：修改特定文档

1. **先查询**：使用 `list_documents.py --collection-id <文集ID> --name "关键词"` 或 `get_document.py --id <ID>` 定位要修改的文档，确认文档 ID。
2. **再修改**：使用 `update_document.py --id <ID>` 修改标题、正文。

### 规范二：添加特定文档

1. **文集必填**：用户必须提供目标文集。若用户未提供或只说「随便加」「你决定」等，**必须主动询问**：「请告知要将文档添加到的文集名称」。
2. **查询文集 ID**：用户给出文集名称后，用 `list_collections.py --name "文集名称"` 查询文集 ID；若不存在则询问是否新建。
3. **添加文档**：使用 `add_document.py --collection-id <ID> --name "标题" [--content 内容] [--content-file 文件路径]`。

### 规范三：添加文集

1. **用户确认**：新建文集前**必须**让用户确认要创建的文集名称，例如：「将创建文集「xxx」，请确认名称是否正确？」。
2. **确认后再执行**：用户确认后再执行 `create_collection.py --name "文集名称"`。若使用 `--get-if-exists` 则同名已存在时直接返回已有 ID，不重复创建。

### 规范四：修改文档归属

1. **先定位文档**：用 `list_documents.py --collection-id <文集ID> --name "关键词"` 或 `get_document.py --id <ID>` 确认文档 ID。
2. **确认目标文集**：用户需提供目标文集名称或 ID；若无则 `list_collections.py --name "关键词"` 查询。
3. **执行移动**：使用 `move_document.py --id <文档ID> --collection-id <目标文集ID>`；文档属于多个文集时需加 `--from-collection-id <原文集ID>`。

---

## 前置条件

1. **config.json**：在 client 目录配置 `config.json`，填写`token`。
2. **环境变量**（可选）：`HT_SKILL_SERVER_URL`、`HT_SKILL_TOKEN` 优先级高于 config.json。
3. **依赖**：`pip install requests`

## 脚本目录

所有脚本位于 `scripts/`，在 client 根目录执行。

## 功能一：新建文集（支持有则用、无则建）

```bash
python scripts/create_collection.py --name "文集名称" [--description "50字内简介"] [--brief "500字以上详细介绍"]
python scripts/create_collection.py --name "文集名称" --get-if-exists
```

## 功能二：新建文档到指定文集

```bash
python scripts/add_document.py --collection-id 123 --name "文档标题" [--content "正文"] [--content-file 路径] [--parent 0]
```

## 功能三：查询文集列表

```bash
python scripts/list_collections.py [--name "关键词"]
```

## 功能四：查询文集详情

```bash
python scripts/get_collection.py --id 123 [--include-docs]
```

## 功能五：查询文档列表

```bash
python scripts/list_documents.py --collection-id 123 [--name "关键词"]
# collection-id 必填。若无文集 ID，需先 list_collections 查询或向用户询问
```

## 功能六：查询文档详情

```bash
python scripts/get_document.py --id 456
```

## 功能七：更新文档（修订已发文章）

```bash
python scripts/update_document.py --id 456 --name "新标题"
python scripts/update_document.py --id 456 --content "新正文"
python scripts/update_document.py --id 456 --content-file 文件路径
python scripts/update_document.py --id 456 --sort 50
python scripts/update_document.py --id 456 --parent 0
```

## 功能八：修改文档归属（移动到目标文集）

```bash
# 将文档移动到目标文集
python scripts/move_document.py --id 456 --collection-id 789

# 文档属于多个文集时，需指定原文集 ID
python scripts/move_document.py --id 456 --collection-id 789 --from-collection-id 123
```

- `--id`：文档 ID（必填）
- `--collection-id`：目标文集 ID（必填）
- `--from-collection-id`：原文集 ID；文档只属于一个文集可不填，属于多个文集则必填

## 功能九：设置文档父级（文集内层级）

```bash
python scripts/set_document_parent.py --collection-id 123 --document-id 456 --parent 0 [--sort 1]
```

- `parent=0` 表示根文档；同级别 `sort` 越小越靠前
