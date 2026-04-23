---
name: file-crypto
description: 使用来布公司内置的 file-crypto SDK 对服务器本地文件进行加密或解密处理。当用户提到"加密文件"、"解密文件"、"文件加密"、"文件解密"、"encrypt file"、"decrypt file"，或者提供了服务器文件路径并希望对其进行加解密操作时，必须使用此 skill。适用于单文件加密、单文件解密、批量加解密（多次调用）等场景。只要涉及到 file-crypto 或来布文件加解密，都应优先触发此 skill。
---

# file-crypto — 文件加解密 Skill

本 skill 指导如何通过 `file_crypto` SDK 命令行工具对服务器本地文件执行加密或解密操作，并将结果清晰地反馈给用户。

---

## 前置知识

`file_crypto` SDK 已预装在服务器上，**必须在指定目录下调用**：

```
/data/endecode-win-linux
```

命令格式：

```bash
cd /data/endecode-win-linux
python3 -m file_crypto --action <encrypt|decrypt> --filePath <文件物理地址> --authId <鉴权ID>
```

- `--action encrypt`：加密
- `--action decrypt`：解密
- `--filePath`：目标文件的**完整物理路径**（如 `/data/upload/report.pdf`）
- `--authId`：调用方的**鉴权 ID**（用户身份标识，必填，最长 64 字符）

---

## 执行流程

### 第一步：确认参数

在执行前，确保从用户输入中获取到以下三项：

1. **操作类型**：加密还是解密？
2. **文件路径**：完整的服务器物理路径是什么？
3. **鉴权 ID（authId）**：调用方的用户身份 ID 是什么？

缺少任意一项都应主动追问，例如：
> "请提供您的鉴权 ID（authId），用于身份验证（如：10001）"
> "请提供需要加密的文件完整路径（如 `/data/upload/合同.pdf`）"

如果用户同时提供多个文件，对每个文件分别执行一次命令（authId 保持不变）。

---

### 第二步：构造并执行命令

根据操作类型，构造对应的 Bash 命令：

**加密：**
```bash
cd /data/endecode-win-linux && python3 -m file_crypto --action encrypt --filePath <文件路径> --authId <鉴权ID>
```

**解密：**
```bash
cd /data/endecode-win-linux && python3 -m file_crypto --action decrypt --filePath <文件路径> --authId <鉴权ID>
```

使用 Bash 工具执行上述命令，捕获完整的 JSON 输出。

---

### 第三步：解析 JSON 输出并告知用户

命令执行后会返回一个 JSON 对象，按以下逻辑处理：

#### ✅ 成功（`"success": true` 且 `"code": 0`）

```json
{
  "code": 0,
  "message": "处理成功",
  "success": true,
  "data": {
    "sourceFilePath": "/data/upload/test.pdf",
    "targetFilePath": "/data/output/test_encrypt.pdf",
    "action": "encrypt"
  }
}
```

向用户报告：
- 操作类型（加密 / 解密）
- 原始文件路径（`sourceFilePath`）
- 处理后文件路径（`targetFilePath`）

示例回复：
> ✅ 加密成功！
> - 原始文件：`/data/upload/test.pdf`
> - 加密后文件：`/data/output/test_encrypt.pdf`

---

#### ❌ 失败，根据 `code` 区分原因：

| code | message | 说明 | 建议给用户的提示 |
|------|---------|------|----------------|
| 400  | 请求参数非法 | 参数格式有误 | 请检查文件路径格式是否正确，`--action` 是否为 `encrypt` 或 `decrypt`，`--authId` 是否已传入且不超过 64 字符 |
| 401  | 鉴权失败 | authId 无效或无权限 | 请确认您的鉴权 ID 是否正确，或联系管理员确认账号权限 |
| 404  | 源文件不存在 | 文件路径不存在 | 请确认文件路径是否正确，文件是否已上传到服务器 |
| 500  | 文件处理失败 | SDK 内部处理异常 | 请检查文件格式是否受支持，或联系管理员查看服务器日志 |

示例回复（401）：
> ❌ 操作失败：鉴权失败。
> 请确认您的 authId `10001` 是否正确，或联系管理员确认账号权限。

示例回复（404）：
> ❌ 操作失败：源文件不存在。
> 请确认路径 `/data/upload/test.pdf` 是否正确，文件是否已上传至服务器。

---

## 批量处理

如果用户需要对多个文件进行加解密，逐一执行命令，并汇总结果：

```
文件加解密完成（3/3）：
✅ /data/upload/a.pdf → /data/output/a_encrypt.pdf
✅ /data/upload/b.pdf → /data/output/b_encrypt.pdf
❌ /data/upload/c.pdf → 失败（源文件不存在）
```

---

## 注意事项

- 本工具仅处理**服务器本地文件**，不支持本地桌面文件
- 命令**必须在 `/data/endecode-win-linux` 目录下执行**，否则会找不到模块
- 文件路径区分大小写，请原样传入
- `--authId` 为每次调用的必填项，代表调用方身份，长度不超过 64 字符
- 加密后的文件通常保存在 `/data/output/` 下，文件名会附带 `_encrypt` 后缀；解密同理附带 `_decrypt` 后缀（以实际 `targetFilePath` 返回值为准）
