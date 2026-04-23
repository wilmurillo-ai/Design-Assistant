# delete-recovery v0.6.0

> ⚠️ **Before deploying: backups written to `{workspace}/delete_backup/` (outside skill dir); `allowed_roots` unset by default — restores can target any path. Deploy only in trusted environments.**

### 中文

文件删除安全网——备份、恢复、SHA256完整性校验、路径交叉验证、**manifest 检索索引**、全自动清理、**v0.6.0 时间触发优化**。

### English

A safety net for file deletion — backup, recovery, SHA256 integrity verification, path cross-validation, **manifest retrieval index**, **v0.6.0 time-triggered cleanup optimization**, and fully automatic cleanup.

---

### 中文

一款轻量的 OpenClaw skill，在删除文件前自动将其备份到带时间戳的文件夹。**v0.6.0 性能优化**：7天/30天清理改为时间触发（默认24小时间隔），不再每次命令都全量扫描；manifest 操作改为增量模式，restore 后按需压缩。**v0.5.0 manifest 检索索引**：备份时自动将文件名、功能简介（≤6字）、路径写入 `manifest.jsonl`，支持 `search` 命令快速检索已删除文件。配合 v0.4.0 的 `--force` 安全修复（PATH 验证不可绕过）和 v0.3.0 的 SHA256 强制校验 + PATH 交叉验证，形成完整的安全防护体系。误删后一键恢复，无需人工干预。

### English

A lightweight OpenClaw skill that automatically backs up files to timestamped folders before deletion. **v0.6.0 performance optimization**: 7-day/30-day cleanup is now time-triggered (default 24-hour interval), eliminating per-call full scans; manifest operations use an incremental model with on-demand compaction after restores. **v0.5.0 manifest retrieval index**: on every backup, filename, brief description (≤6 chars), and path are written to `manifest.jsonl`, enabling fast `search` to locate deleted files. Combined with v0.4.0's `--force` security fix (PATH validation non-bypassable) and v0.3.0's mandatory SHA256 integrity checks and PATH cross-validation, this forms a complete security defense system. Recover accidentally deleted files with one click, with fully automatic cleanup requiring no manual intervention.

---

## 功能特性 / Features

### 中文

- **删除前自动备份** — 删除任何文件前，自动备份到带时间戳的文件夹
- **manifest 检索索引（v0.5.0 新增）** — backup 时自动将（文件名 + 功能简介≤6字 + 路径）写入 `manifest.jsonl`，`search` 命令支持文件名/功能/路径关键字模糊搜索；restore 成功后自动剔除对应索引，过期备份的残留索引在脚本启动或 cleanup 时自动清理
- **SHA256 强制校验（v0.3.0 修复）** — 备份时计算哈希，恢复时验证；SHA256 记录缺失或为空时 restore 默认阻止
- **PATH 交叉验证（v0.3.0 新增）** — `.sha256` 文件中绑定原始路径，恢复时双向交叉验证，彻底防止 `.path` 文件被篡改定向到任意位置
- **`--force` 路径安全强制验证（v0.4.0 修复 A4）** — `--force` 跳过 SHA256 存在性检查，但 PATH 交叉验证和路径遍历检测永远执行，即使 SHA256 记录不存在也不例外
- **日志注入防护（v0.3.0 已修复）** — detail 中过滤 `\n`、`\r`、`[`，防止伪造日志行
- **路径遍历防护** — 检测 `../` 逃逸序列，拒绝恢复目标超出合法范围
- **一键恢复** — 将误删文件恢复到原始位置
- **多文件安全处理** — 同一备份文件夹含多文件时，须全部恢复完毕才删除备份
- **时间触发清理（v0.6.0 新增）** — 备份7天后自动删除，日志30天后自动删除，改为时间触发（默认24小时间隔），不再在每次命令时全量扫描，显著提升响应速度
- **manifest 增量操作（v0.6.0 新增）** — restore/delete_backup 时按需压缩 manifest（候选集≤100条时全量rewrite，>100条时追加墓碑标记）；list/search/log 时自动检查并触发增量压缩；backup 操作完全不受影响
- **冲突保护恢复** — 恢复时若目标位置已有文件，自动移到 `temp_existing/` 暂存
- **完整操作日志** — 每次备份、恢复、清理、安全拦截操作均有记录（含 SECURITY 级别）
- **`--force` 恢复旧备份（v0.3.0 新增）** — 对 v0.3.0 之前创建的旧备份（无 SHA256 记录），可用 `--force` 强制恢复（SHA256 存在性跳过，但 PATH 验证和遍历检测永远生效，v0.4.0 起不可绕过）

### English

- **Automatic backup before deletion** — Automatically backs up any file to a timestamped folder before deletion
- **Manifest retrieval index (NEW in v0.5.0)** — On backup, filename, brief description (≤6 chars), and path are written to `manifest.jsonl`; `search` command enables fast keyword lookup by filename/description/path; index entries are automatically removed on successful restore; stale entries pruned on script startup or cleanup
- **Mandatory SHA256 integrity check (fixed in v0.3.0)** — Computes hash during backup and verifies during recovery; missing or empty SHA256 record now blocks restore by default
- **PATH cross-validation (NEW in v0.3.0)** — SHA256 file stores FILE_HASH + PATH; restore performs cross-check between `.sha256` record and `.path` file, fully preventing `.path` redirection attacks
- **`--force` PATH safety enforcement (FIXED in v0.4.0 — A4)** — `--force` bypasses SHA256 *existence* check, but PATH cross-validation and traversal detection always run, even when SHA256 record is absent
- **Log injection prevention (fixed in v0.3.0)** — `\n`, `\r`, `[` stripped from detail, preventing fake log entries
- **Path traversal protection** — Detects `../` escape sequences and blocks restores outside the valid directory range
- **One-click recovery** — Restores accidentally deleted files to their original location
- **Multi-file safe handling** — When a backup folder contains multiple files, all must be restored before deleting the backup
- **Time-triggered cleanup (NEW in v0.6.0)** — Backups are deleted after 7 days and logs after 30 days; now time-triggered (default 24-hour interval) instead of running a full scan on every command, significantly improving response speed
- **Incremental manifest operations (NEW in v0.6.0)** — restore/delete_backup use on-demand manifest compaction (≤100 entries: full rewrite; >100: append tombstones); list/search/log auto-check and trigger incremental compaction; backup operation is completely unaffected
- **Conflict-protected recovery** — If a file already exists at the restore destination, it is automatically moved to `temp_existing/` for staging
- **Complete operation logs** — Every backup, restore, cleanup, and security interception operation is logged (including SECURITY level)
- **`--force` for legacy backups (NEW in v0.3.0)** — Use `--force` to restore pre-v0.3.0 backups that lack SHA256 records (SHA256 existence check bypassed; PATH validation and traversal detection always run and are non-bypassable from v0.4.0)

---

## 安装方式 / Installation

### 中文

### 通过 ClawdHub 安装（推荐）

```bash
# 安装最新版（v0.5.0）
clawdhub install delete-recovery

# 安装指定版本
clawdhub install delete-recovery --version 0.5.0
```

### 手动安装

将 `delete-recovery` 文件夹复制到本地 Agent 的 OpenClaw workspace 的 `skills/` 目录下，并将文件夹重命名为 `delete-recovery`（保持与脚本内部路径一致）。

### English

### Install via ClawdHub (Recommended)

```bash
# Install latest version (v0.6.0)
clawdhub install delete-recovery

# Install specific version
clawdhub install delete-recovery --version 0.6.0
```

### Manual Installation

Copy the `delete-recovery` folder to the `skills/` directory in your local Agent's OpenClaw workspace and rename it to `delete-recovery` (to match the internal script path).

---

## 快速开始 / Quick Start

### 中文

### 1. 删除前备份

```bash
python delete_recovery.py backup <file_path> [original_path] [description]
```

```bash
# 示例（建议加上功能简介，便于后续检索）
python delete_recovery.py backup "C:\Users\user\Desktop\report.docx" "C:\Users\user\Desktop\report.docx" "工作报告"
# → {"ok": true, "folder": "202603261130", "file": "C__Users__user__Desktop__report.docx", "description": "工作报告"}
```

### 2. 搜索已删除文件（v0.5.0 新增）

```bash
python delete_recovery.py search <keyword>
```

在 manifest.jsonl 中按文件名、功能简介或路径关键字模糊搜索（大小写不敏感）。

```bash
python delete_recovery.py search "报告"
# → {"keyword": "报告", "results": [...], "count": 1}
# 根据返回的 folder + safe_name 执行 restore
```

### 3. 恢复误删文件

```bash
python delete_recovery.py restore <backup_folder> <safe_name> [--keep-backup] [--force]
```

```bash
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx"
# → {"ok": true, "restored_to": "C:\\Users\\user\\Desktop\\report.docx", "backup_deleted": true}
# 恢复成功后 manifest 中的索引自动被剔除

# 恢复 v0.3.0 之前的旧备份（无 SHA256 记录）
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --force
```

### 4. 验证备份完整性

```bash
python delete_recovery.py verify <backup_folder> <safe_name>
```

不执行恢复，仅检查备份文件是否被篡改（SHA256 完整性 + PATH 交叉验证）。

### 5. 查看所有备份

```bash
python delete_recovery.py list
```

### 6. 手动删除指定备份

```bash
python delete_recovery.py delete_backup <backup_folder>
```

### 7. 手动触发清理

```bash
python delete_recovery.py cleanup
```

### 8. 查看操作日志

```bash
python delete_recovery.py log [lines]
```

### English

### 1. Backup Before Deletion

```bash
python delete_recovery.py backup <file_path> [original_path] [description]
```

```bash
# Example (description recommended for easier later search)
python delete_recovery.py backup "C:\Users\user\Desktop\report.docx" "C:\Users\user\Desktop\report.docx" "Work Report"
# → {"ok": true, "folder": "202603261130", "file": "C__Users__user__Desktop__report.docx", "description": "Work Report"}
```

### 2. Search Deleted Files (NEW in v0.5.0)

```bash
python delete_recovery.py search <keyword>
```

Case-insensitive substring search over manifest.jsonl (filename, description, or path).

```bash
python delete_recovery.py search "report"
# → {"keyword": "report", "results": [...], "count": 1}
# Use the returned folder + safe_name to call restore
```

### 3. Restore Accidentally Deleted Files

```bash
python delete_recovery.py restore <backup_folder> <safe_name> [--keep-backup] [--force]
```

```bash
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx"
# → {"ok": true, "restored_to": "C:\\Users\\user\\Desktop\\report.docx", "backup_deleted": true}
# Index entry is automatically removed from manifest on successful restore

# Restore pre-v0.3.0 backup (no SHA256 record) using --force
python delete_recovery.py restore 202603261130 "C__Users__user__Desktop__report.docx" --force
```

### 4. Verify Backup Integrity

```bash
python delete_recovery.py verify <backup_folder> <safe_name>
```

Does not perform recovery. Checks SHA256 integrity AND PATH cross-validation to detect any tampering.

### 5. List All Backups

```bash
python delete_recovery.py list
```

### 6. Manually Delete Specified Backup

```bash
python delete_recovery.py delete_backup <backup_folder>
```

### 7. Manually Trigger Cleanup

```bash
python delete_recovery.py cleanup
```

### 8. View Operation Logs

```bash
python delete_recovery.py log [lines]
```

---

## 安全机制详解（v0.5.0）/ Security Mechanisms Explained (v0.5.0)

### 中文

### 场景1：备份被替换

攻击者先备份一个正常文件，然后用恶意文件替换备份目录中的文件，诱导恢复。

**防御：** backup 时计算 SHA256 并存储；restore 时验证哈希，不匹配则拒绝恢复。即使攻击者删除了 `.sha256` 文件，restore 也会被阻止（除非使用 `--force`，但 PATH 验证和遍历检测仍然生效，v0.4.0 起不可绕过）。

### 场景2：.path 文件被篡改

攻击者修改 `.path` 文件内容，将恢复目标指向系统目录（如 `C:\Windows\System32\evil.exe`）。

**防御：** v0.3.0 新增 `.sha256` 文件中的 PATH 字段。restore 时读取 `.sha256` 中存储的原始路径，与 `.path` 文件内容进行交叉验证，二者不一致则拒绝恢复。

### 场景3：SHA256 记录被删除绕过

攻击者直接删除或置空 `.sha256` 文件，试图绕过完整性检查。

**防御：** v0.3.0 修复此漏洞——SHA256 记录缺失或为空时，restore 默认阻止并报错，不再跳过完整性检查。唯一出口是 `--force`，但 PATH 交叉验证和遍历检测永远执行，v0.4.0 起不可绕过。

### 场景4：路径遍历

攻击者在目标路径中构造 `../../../dangerous/evil.exe`，试图逃逸到合法目录范围外。

**防御：** `_is_path_safe()` 检测 `..` 成分，resolve 后路径不在合法范围则拒绝。

### English

### Scenario 1: Backup Replaced

An attacker first backs up a normal file, then replaces the file in the backup directory with a malicious one to induce recovery.

**Defense:** Compute and store SHA256 during backup; verify hash during restore and reject if mismatched. If the attacker also deletes the `.sha256` file, restore is still blocked by default (unless `--force` is used, and PATH validation and traversal detection always run and are non-bypassable from v0.4.0).

### Scenario 2: .path File Tampered

An attacker modifies the `.path` file content to point the restore target to a system directory (e.g., `C:\Windows\System32\evil.exe`).

**Defense:** v0.3.0 stores the original path in the `.sha256` file (in the `PATH:` line). On restore, the path from `.sha256` is cross-checked against the `.path` file — any mismatch is blocked.

### Scenario 3: SHA256 Record Deleted to Bypass Check

An attacker deletes or empties the `.sha256` file to bypass integrity checks.

**Defense:** v0.3.0 fixes this — missing or empty SHA256 record now blocks restore by default. The only escape hatch is `--force`, but PATH cross-validation and traversal detection always run and are non-bypassable from v0.4.0.

### Scenario 4: Path Traversal

An attacker constructs `../../../dangerous/evil.exe` in the target path to escape outside the allowed directory.

**Defense:** `_is_path_safe()` detects `..` components and rejects if the resolved path is outside the valid range.

---

## SHA256 文件格式（v0.3.0）/ SHA256 File Format (v0.3.0)

### 中文

`.sha256` 文件采用结构化格式，同时存储文件哈希和原始路径：

```
#v3
FILE_HASH:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
PATH:C:\Users\user\Desktop\report.docx
```

- **`#v3`**：格式版本号，用于未来兼容升级
- **`FILE_HASH:`**：备份文件的 SHA256 哈希（64位十六进制）
- **`PATH:`**：备份时的原始文件路径（与 `.path` 文件内容一致，用于交叉验证）

### English

The `.sha256` file uses a structured format that stores both the file hash and original path:

```
#v3
FILE_HASH:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
PATH:C:\Users\user\Desktop\report.docx
```

- **`#v3`**: Format version marker for future compatibility
- **`FILE_HASH:`**: SHA256 hash of the backup file (64 hex characters)
- **`PATH:`**: Original file path at backup time (mirrors `.path` file; used for cross-validation)

---

## 文件结构 / File Structure

### 中文

```
**v0.6.0 重大变更：备份和日志存储位置移至 workspace 根目录**，技能目录被删除时备份仍可存活。

```
workspace1/                          ← 工作区根目录（备份独立于技能目录）
├── delete_backup/                   ← 备份存储（7天自动清理）
│   ├── .cleanup_timer              ← 上次清理时间记录（v0.6.0 新增）
│   ├── manifest.jsonl              ← 检索索引：文件名/功能简介/路径
│   ├── YYYYMMDDHHMM/             ← 时间戳备份文件夹
│   │   ├── C__Users__...         ← 备份文件
│   │   ├── C__Users__...path     ← 原始路径记录
│   │   ├── C__Users__...sha256   ← SHA256 完整性 + PATH 交叉验证记录（v0.3.0）
│   │   └── .restored              ← 已恢复文件清单
│   └── temp_existing/             ← 恢复时暂存冲突文件
└── log_delete_recovery.txt        ← 操作日志（30天自动清理）

{workspace}/skills/delete-recovery/   ← 技能目录（可独立删除，不影响备份）
├── SKILL.md                        — Skill 定义
├── README.md                      — 使用指南（本文）
├── scripts/
│   ├── delete_recovery.py          — 核心脚本（含安全验证，v0.6.0）
│   └── safe_path.py               — 路径安全验证模块（v0.3.1）
└── example/                       — 示例文件
```

### English

**v0.6.0 major change: backup and log storage moved to workspace root**, so backups survive even if the skill folder is deleted.

```
workspace1/                          ← Workspace root (backups independent of skill directory)
├── delete_backup/                   ← Backup storage (7-day auto-cleanup)
│   ├── .cleanup_timer              ← Last cleanup timestamp (NEW in v0.6.0)
│   ├── manifest.jsonl              ← Retrieval index: filename / description / path
│   ├── YYYYMMDDHHMM/             ← Timestamped backup folder
│   │   ├── C__Users__...         ← Backup file
│   │   ├── C__Users__...path     ← Original path record
│   │   ├── C__Users__...sha256   ← SHA256 + PATH cross-validation record (v0.3.0)
│   │   └── .restored              ← Restored files manifest
│   └── temp_existing/             ← Conflict files staged during recovery
└── log_delete_recovery.txt        ← Operation logs (30-day auto-cleanup)

{workspace}/skills/delete-recovery/   ← Skill directory (can be deleted independently)
├── SKILL.md                        — Skill definition
├── README.md                      — User guide (this document)
├── scripts/
│   ├── delete_recovery.py             — Core script (with security checks, v0.6.0)
│   └── safe_path.py                  — Path safety validator module (v0.3.1)
└── example/                       — Example files
```
    ├── delete_recovery.py            — Core script (with security checks, v0.5.0)
    └── safe_path.py                  — Path safety validation module (v0.4.0)
```

---

## 工作流程 / Workflow

### 中文

```
用户决定删除文件
        │
        ▼
  ① backup 命令          ← 第一步必须做（v0.5.0 自动写入 manifest 索引）
        │
        ▼
  ② 用户执行删除操作
        │
        ▼（后续如需恢复）
  ③ search 命令           ← v0.5.0 新增：按文件名/功能/路径快速检索备份位置
        │
        ▼
  ④ restore 命令         ← v0.3.0+：完整性 + PATH 交叉验证 + 遍历检测（v0.4.0 起不可绕过）
        │                    成功后自动从 manifest 中剔除索引
        ▼
  备份自动删除            ←（除非使用了 --keep-backup）
```

### English

```
User decides to delete file
        │
        ▼
  ① backup command    ← Must do first (v0.5.0 auto-writes manifest index)
        │
        ▼
  ② User performs deletion
        │
        ▼（If recovery needed later）
  ③ search command     ← NEW in v0.5.0: fast lookup by filename / description / path
        │
        ▼
  ④ restore command ← v0.3.0+: integrity + PATH cross-validation + traversal detection
        │              (PATH validation is non-bypassable from v0.4.0)
        │              Index entry automatically removed from manifest on success
        ▼
  Backup auto-deleted  ←（Unless --keep-backup is used）
```

---

## 依赖环境 / Dependencies

### 中文

- Python 3.8+
- OpenClaw 1.0+（含 skill 支持）

### English

- Python 3.8+
- OpenClaw 1.0+ (with skill support)

---

## 安全设计决策说明 / Security Design Decisions

### 中文

本节直接回应审查中提出的三个设计关切。

#### Q1：为什么不默认限制恢复目标目录（`allowed_roots`）？

**A：** 作为文件恢复工具，核心需求是将文件恢复到**原始位置**——而原始位置可能是用户硬盘上的任意目录。强制限定 `allowed_roots` 会使工具无法恢复原本不在"白名单"内的文件，根本上违背工具的设计目的。替代安全方案：SHA256 完整性验证 + PATH 交叉验证 + 路径遍历检测，即使恢复目标是任意目录也能防止恶意替换和路径重定向。`allowed_roots` 可选配置，有更严格需求的用户可在实例化 `SafePathValidator` 时传入此参数。

#### Q2：`--force` 参数为什么不跳过所有安全检查？

**A：** v0.4.0 修复 A4 漏洞后，`--force` 仅豁免「SHA256 记录不存在」这件事本身（因为 v0.3.0 前的旧备份本身就没有 SHA256）。以下检查**永远不可绕过**：SHA256 完整性验证、PATH 交叉验证、路径遍历检测。

#### Q3：manifest.jsonl 存储原始路径是否泄露敏感信息？

**A：** manifest 位于技能完全管控的 `delete_backup/` 目录内，不向外部暴露。原始路径是 `search` 按路径关键字检索的必要字段，不含任何文件内容或凭证，如极度敏感可自行省略该字段（仅失去按路径检索的能力，文件名/功能简介检索不受影响）。

### English

#### Q1: Why no directory restrictions by default (`allowed_roots`)?

**A:** This is intentional — a recovery tool must restore files to their original locations, which may be anywhere on the filesystem. The security model relies on SHA256 integrity + PATH cross-validation instead. `allowed_roots` is optional and available for users who need stricter confinement.

#### Q2: Why doesn't `--force` skip all security checks?

**A:** After the v0.4.0 A4 fix, `--force` only waives the SHA256 *existence* check (for legacy pre-v0.3.0 backups). SHA256 integrity verification, PATH cross-validation, and path traversal detection are **always enforced and non-bypassable**.

#### Q3: Does storing original paths in manifest.jsonl leak sensitive information?

**A:** The manifest lives inside the skill-controlled `delete_backup/` directory — it is not externally exposed. Paths are necessary for path-keyword search. No file content or credentials are stored. The field can be omitted if path information is considered highly sensitive.

---

## 更新日志 / Changelog

### 中文

### v0.6.0（2026-03-30） — **当前版本**

**性能优化（功能完全不变）：**

- 【优化 — 核心】**方案一：时间触发清理** — 7天备份清理和30天日志清理改为按时间触发（默认24小时间隔），不再在每次 backup/restore/search/list 时都执行全量扫描；cleanup 命令本身不受影响，仍立即执行全量清理
- 【优化 — 核心】**方案二：manifest 增量操作** — restore/delete_backup 时按需压缩 manifest（候选集≤100条时全量rewrite，>100条时追加墓碑标记）；list/search/log 时自动检查并触发增量压缩；`_remove_manifest_entry()` 根据 manifest 大小自动选择 rewrite 策略；新增 `_mark_manifest_entries_removed()` / `_maybe_compact_manifest()` / `_count_manifest_entries()` 辅助函数
- 【优化】所有文件写入改用原子写入（`os.replace`），避免写入中途崩溃导致文件损坏

**完整变更：**
- `delete_recovery.py`：`main()` 中清理逻辑改为时间触发；`_prune_stale_manifest_entries()` 改为保留 tombstone 条目；新增 `_load_timer()` / `_save_timer()` / `_should_run_backup_cleanup()` / `_should_run_log_cleanup()` / `_touch_backup_cleanup()` / `_touch_log_cleanup()` / `_atomic_write_text()` / `_mark_manifest_entries_removed()` / `_maybe_compact_manifest()` / `_count_manifest_entries()`；`_remove_manifest_entry()` 改为阈值策略；版本升至 v0.6.0
- SKILL.md / README.md：版本升至 v0.6.0，补全性能优化文档
- TOOLS.md：更新执行流程规范（方案四：backup+delete 打包一次exec）

### English

### v0.6.0 (2026-03-30) — **Current Version**

**Performance optimizations (no functional changes):**

- 【Optimization — Core】**Scheme 1: Time-triggered cleanup** — 7-day backup cleanup and 30-day log cleanup are now time-triggered (default 24-hour interval), no longer running a full scan on every backup/restore/search/list call; new `.cleanup_timer` file records last cleanup timestamps; `cleanup` command itself is unaffected and still runs full cleanup immediately
- 【Optimization — Core】**Scheme 2: Incremental manifest operations** — restore/delete_backup use on-demand manifest compaction (≤100 entries: full rewrite; >100: append tombstones); list/search/log auto-check and trigger incremental compaction; `_remove_manifest_entry()` auto-selects rewrite strategy based on manifest size; new helper functions `_mark_manifest_entries_removed()` / `_maybe_compact_manifest()` / `_count_manifest_entries()`
- 【Optimization】All file writes now use atomic write (`os.replace`) to prevent corruption from mid-write crashes

**Complete changes:**
- `delete_recovery.py`: `main()` cleanup logic changed to time-triggered; `_prune_stale_manifest_entries()` now preserves tombstone entries; new functions `_load_timer()` / `_save_timer()` / `_should_run_backup_cleanup()` / `_should_run_log_cleanup()` / `_touch_backup_cleanup()` / `_touch_log_cleanup()` / `_atomic_write_text()` / `_mark_manifest_entries_removed()` / `_maybe_compact_manifest()` / `_count_manifest_entries()`; `_remove_manifest_entry()` changed to threshold-based strategy; version bumped to v0.6.0
- SKILL.md / README.md: version bumped to v0.6.0, performance optimization docs added
- TOOLS.md: execution workflow updated (Scheme 4: backup+delete packaged in one exec)

### v0.5.0（2026-03-28） — Current Version

**新功能：**

- 【新增 — 核心】新增 manifest 检索索引：备份时自动将（文件名、功能简介≤6字、原始路径）写入 `delete_backup/manifest.jsonl`，支持 `search <keyword>` 快速检索；恢复成功后自动剔除对应索引；过期备份的残留索引在脚本启动或 cleanup 时自动清理
- 【新增】`search` 命令：大小写不敏感 substring 匹配，可按文件名/功能简介/路径关键字搜索
- 【新增】`backup` 命令支持第三个参数 `[description]`：功能简介，建议 ≤6 字，默认为文件名
- 【新增】`delete_backup` 命令删除备份时同步清理 manifest 中对应的索引

**完整变更：**
- `delete_recovery.py`：新增 `_append_manifest_entry()` / `_remove_manifest_entry()` / `_prune_stale_manifest_entries()` / `_search_manifest()` 四个函数；`backup` → 追加索引；`restore` → 成功后剔除索引；`delete_backup` → 清理索引；脚本每次启动自动清理过期残留；新增 `search` CLI 命令；版本升至 v0.5.0
- SKILL.md：版本升至 v0.5.0，补全所有新增功能文档
- README.md：版本升至 v0.5.0，补全所有新增功能文档

### v0.4.0（2026-03-27）

**安全修复：**

- 【A4 修复 — 关键】`--force` 参数不再能绕过所有检查 — SHA256 缺失时，PATH 交叉验证和路径遍历检测**永远执行**，关闭了"删除 SHA256 → --force → 完全绕过"这一攻击链路
- 【A10 说明】日志注入防护（`\n` `\r` `[` 过滤）已在 v0.3.0 代码中存在，渗透测试时针对的是更早版本，当前版本不受影响

**完整变更：**
- `safe_path.py`：重写 `verify_integrity_and_path()` 中 SHA256 缺失分支，新增"无 SHA256 时强制 PATH 安全验证"逻辑，版本升至 v0.3.1
- `delete_recovery.py`：版本注释同步更新至 v0.4.0
- 更新 SKILL.md / README.md

### v0.3.0（2026-03-27） — 上一版本

**安全修复：**

- 【最关键】SHA256 记录改为**强制要求** — 缺失或为空时 restore **默认阻止**，修复了"删除 `.sha256` 文件即可绕过完整性检查"的严重漏洞
- 【安全增强】`.sha256` 文件新增 `PATH:` 行 — restore 时双向交叉验证 `.sha256` 中存储的路径与 `.path` 文件内容，彻底防止 `.path` 篡改攻击
- 【Bug 修复】修复 `allowed_roots` 死代码 — `allowed_roots=[]`（空列表）现正确表示"无路径限制"（不再误判为禁止所有路径）
- 【安全调整】`allowed_roots` 默认为空 — 安全防护主要依赖完整性 + 路径交叉验证，而非固定目录限制，更适合恢复工具的实际场景
- 【接口变更】restore 新增 `--force` 参数 — 跳过 SHA256 存在性检查，用于强制恢复 v0.3.0 之前的旧备份（路径验证仍生效）
- 【Bug 修复】`verify` 命令新增 PATH 交叉验证结果 — 同时报告 hash_match 和 path_match 两个检查的结果
- 【安全修复】日志注入防护 — `log()` 函数过滤 detail 中的 `\n`、`\r`、`[`

**完整变更：**
- `safe_path.py`：完全重写 `verify_integrity_and_path()`，新增 `write_sha256_file()` / `read_sha256_file()`，格式改为 `#v3 / FILE_HASH: / PATH:`
- `delete_recovery.py`：集成新版安全 API，`--force` 参数，`verify` 返回 path_match
- 更新 SKILL.md / README.md / CLAWDHUB.md

### v0.2.0（2026-03-26）— 更早版本

- 新增 `safe_path.py` 路径安全验证模块
- backup 时自动计算并存储 SHA256 哈希（`.sha256` 文件）
- restore 时验证备份完整性（SHA256 比对），完整性不符拒绝恢复
- restore 时验证恢复路径（防止 `.path` 篡改 + 路径遍历）
- 所有安全拦截事件记录为 `SECURITY` 级别日志
- 新增 `verify` 命令：手动检查备份完整性（不执行恢复）
- 新增 `safe_path.py` 独立工具：可单独调用 `compute <file_path>` 计算 SHA256

### v0.1.0（2026-03-26）— 初始版本

- 基础备份/恢复/清理功能
- 7天自动清理备份，30天自动清理日志
- 多文件批量恢复保护
- 冲突保护恢复

### English

### v0.5.0 (2026-03-28) — Previous Version

**New features:**

- 【NEW — Core】Manifest retrieval index: on every backup, filename, brief description (≤6 chars), and original path are written to `delete_backup/manifest.jsonl`; `search <keyword>` enables fast lookup; index entry is automatically removed on successful restore; stale entries are pruned on script startup or cleanup
- 【NEW】`search` command: case-insensitive substring search over filename, description, or path
- 【NEW】`backup` command gains optional third argument `[description]`: brief note ≤6 chars, defaults to filename
- 【NEW】`delete_backup` command now removes corresponding manifest entries when deleting a backup folder

**Complete changes:**
- `delete_recovery.py`: Added `_append_manifest_entry()` / `_remove_manifest_entry()` / `_prune_stale_manifest_entries()` / `_search_manifest()`; `backup` → appends index; `restore` → removes index on success; `delete_backup` → cleans up manifest entries; stale manifest entries pruned on every script startup; new `search` CLI command; version bumped to v0.5.0
- SKILL.md: bumped to v0.5.0, all new features documented
- README.md: bumped to v0.5.0, all new features documented

### v0.4.0 (2026-03-27)

**Security fixes:**

- 【A4 fix — Critical】`--force` can no longer bypass all checks — When SHA256 is absent, PATH cross-validation and traversal detection **always run**, closing the "delete SHA256 → --force → complete bypass" attack chain
- 【A10 note】Log injection prevention (`\n` `\r` `[` stripping) was already present in v0.3.0 code; the penetration test targeted an earlier version

**Complete changes:**
- `safe_path.py`: Rewrote the SHA256-absent branch in `verify_integrity_and_path()`, added mandatory PATH safety validation when SHA256 is missing, version bumped to v0.3.1
- `delete_recovery.py`: Version comment updated to v0.4.0
- Updated SKILL.md / README.md

### v0.3.0 (2026-03-27) — Previous Version

**Security fixes:**

- 【Critical】SHA256 record is now **STRICTLY REQUIRED** — missing or empty SHA256 blocks restore by default, fixing the critical bypass vulnerability where deleting `.sha256` disabled integrity checks
- 【Security enhancement】`.sha256` file now stores `PATH:` line — restore performs cross-check between the path stored in `.sha256` and the `.path` file, fully preventing `.path` redirection attacks
- 【Bug fix】Fixed `allowed_roots` dead code — `allowed_roots=[]` (empty list) now correctly means "no restriction" (previously falsely blocked all paths)
- 【Security adjustment】`allowed_roots` defaults to empty — primary security comes from integrity + path cross-validation rather than fixed directory restrictions
- 【Interface change】restore command gains `--force` flag — bypasses SHA256 existence check to restore pre-v0.3.0 backups (path validation still applies)
- 【Bug fix】`verify` command now reports PATH cross-validation result — returns both hash_match and path_match
- 【Security fix】Log injection prevention — `log()` strips `\n`, `\r`, `[` from detail

**Complete changes:**
- `safe_path.py`: Fully rewritten `verify_integrity_and_path()`, new `write_sha256_file()` / `read_sha256_file()`, format changed to `#v3 / FILE_HASH: / PATH:`
- `delete_recovery.py`: Integrated new security API, `--force` flag, `verify` returns path_match
- Updated SKILL.md / README.md / CLAWDHUB.md

### v0.2.0 (2026-03-26) — Earlier Version

- Added `safe_path.py` path safety validation module
- SHA256 hash computed and stored on backup (`.sha256` file)
- Restore verifies SHA256 integrity — blocks restore if hash mismatch
- Restore validates destination path — prevents `.path` tampering and path traversal
- All security blocks logged at `SECURITY` level
- Added `verify` command: manually check backup integrity without restoring
- Added `safe_path.py` standalone tool: `python safe_path.py compute <file>`

### v0.1.0 (2026-03-26) — Initial Version

- Basic backup/restore/cleanup functionality
- 7-day auto backup cleanup, 30-day auto log cleanup
- Multi-file batch recovery protection
- Conflict-protected recovery

---

### 中文

*如有问题或建议，欢迎反馈！*

### English

*For questions or suggestions, feedback is welcome!*
