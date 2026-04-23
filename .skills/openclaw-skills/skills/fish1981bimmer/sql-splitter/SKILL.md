---
name: sql-splitter
description: 拆分 SQL 文件为独立文件（存储过程、函数、视图、触发器、表结构、索引、约束），自动分析依赖并生成合并脚本
---

# SQL 文件拆分工具 v2.0

将包含多个 SQL 对象的单一文件或目录拆分为独立的 .sql 文件，
并自动分析对象间依赖关系，生成按依赖排序的合并脚本。

## 支持的 SQL 方言

- MySQL
- PostgreSQL
- Oracle
- SQL Server
- 达梦 (DM)
- 通用 (Generic)

## 支持的 SQL 对象类型

| 类型 | 前缀 | 说明 |
|------|------|------|
| 存储过程 | `proc_` | CREATE PROCEDURE |
| 函数 | `func_` | CREATE FUNCTION |
| 视图 | `view_` | CREATE VIEW |
| 触发器 | `trig_` | CREATE TRIGGER |
| 表结构 | `table_` | CREATE TABLE |
| 包 | `pkg_` | CREATE PACKAGE |
| 索引 | `idx_` | CREATE INDEX |
| 唯一索引 | `uidx_` | CREATE UNIQUE INDEX |
| 约束 | `con_` | ALTER TABLE ADD CONSTRAINT |
| 序列 | `seq_` | CREATE SEQUENCE |
| 同义词 | `syn_` | CREATE SYNONYM (Oracle) |
| 事件 | `evt_` | CREATE EVENT (MySQL) |
| 物化视图 | `mv_` | CREATE MATERIALIZED VIEW (PostgreSQL) |
| 类型 | `type_` | CREATE TYPE |

## v2.0 核心改进

### 边界检测重写
- 使用 **BEGIN...END 深度匹配**确定存储过程/函数/触发器边界
- 支持 IF...THEN...END IF、CASE...END CASE、LOOP...END LOOP 嵌套
- 不再依赖"下一个 CREATE 位置"做上界，**正确处理过程体内的嵌套 CREATE 语句**
- Oracle/DM: 通过 `/` 终止符定位；SQL Server: 通过 `GO` 定位
- PostgreSQL: 支持 `$$...$$` 包裹语法
- 字符串和注释内的分号/关键字不会干扰边界检测

### 依赖分析改进
- 函数调用检测改为**限定上下文模式**（:= 赋值、WHERE/HAVING 子句等），大幅减少误报
- SQL 关键字过滤表扩展到 150+ 个，涵盖内置函数、控制流、聚合等
- 自引用自动排除
- 循环依赖不再报错，按类型优先级追加

### 合并脚本方言适配
- Oracle/DM: `@@filename` + `SET DEFINE OFF`
- SQL Server: `:r filename` + `GO`
- PostgreSQL: `\i filename` + `ON_ERROR_STOP`
- MySQL: `source filename`
- 通用: 注释方式

### 架构优化
- 提取 `common.py` 共享模块：SQLDialect 枚举、对象前缀、类型优先级、关键字表
- `dependency_analyzer.py` 不再重复定义枚举，直接引用 common
- 拆分后自动调用依赖分析，生成 `merge_all.sql`
- 新增 37 个单元测试

## 使用方法

### 单文件拆分
```bash
python3 ~/.openclaw/skills/sql-splitter/scripts/split_sql.py <input.sql> [output_dir]
```

### 批量拆分（目录）
```bash
python3 ~/.openclaw/skills/sql-splitter/scripts/split_sql.py --batch <目录路径> [输出目录]
```

### 批量拆分（多个文件）
```bash
python3 ~/.openclaw/skills/sql-splitter/scripts/split_sql.py --batch "file1.sql,file2.sql,file3.sql" [输出目录]
```

### 指定方言
```bash
python3 ~/.openclaw/skills/sql-splitter/scripts/split_sql.py --dialect oracle input.sql
```

支持的方言：`mysql`, `postgresql`, `oracle`, `sqlserver`, `dm`, `generic`

### 不生成合并脚本
```bash
python3 ~/.openclaw/skills/sql-splitter/scripts/split_sql.py --no-merge input.sql
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `input.sql` | 要拆分的 SQL 文件路径（单文件模式必需） |
| `--batch` | 批量模式标志 |
| `--dialect` | 指定 SQL 方言 |
| `--no-merge` | 不生成依赖排序的合并脚本 |
| `-q`, `--quiet` | 静默模式 |
| `output_dir` | 输出目录（可选，默认：原文件名_split） |

### 运行测试
```bash
cd ~/.openclaw/skills/sql-splitter/scripts
python3 -m unittest test_sql_splitter -v
```

## 输出示例

假设输入文件 `myapp.sql` 包含：
- 表 `users`
- 视图 `v_users`（依赖 users）
- 存储过程 `sp_update`（依赖 users）

输出：
```
myapp_split/
├── table_users.sql
├── view_v_users.sql
├── proc_sp_update.sql
└── merge_all.sql          ← 按依赖排序的合并脚本
```

`merge_all.sql` 内容（以 Oracle 为例）：
```sql
-- [1/3] table: users
@@table_users.sql

-- [2/3] view: v_users  -- depends on: users
@@view_v_users.sql

-- [3/3] procedure: sp_update  -- depends on: users
@@proc_sp_update.sql
```

## 文件结构

```
sql-splitter/
├── SKILL.md                       ← 本文档
└── scripts/
    ├── common.py                  ← 共享模块（枚举、常量、工具函数）
    ├── split_sql.py               ← 主拆分脚本
    ├── dependency_analyzer.py     ← 依赖分析器
    └── test_sql_splitter.py       ← 单元测试（37个）
```

## 注意事项

- 使用正则+深度匹配识别 SQL 对象边界，对极复杂嵌套语法可能有局限
- 默认 UTF-8 编码，遇到编码问题自动 replace
- 建议先备份原文件
- 批量模式会自动创建以原文件名命名的子目录
- 自动检测 SQL 方言，也可手动指定
- 同名文件自动追加序号（如 `proc_sp_init_2.sql`）

## 更新日志

### v2.0.0 (2026-04-19)
- 重写对象边界检测：BEGIN/END/IF/CASE/LOOP 深度匹配
- 不再依赖"下一个 CREATE"作为上界，修复嵌套 CREATE 截断问题
- 提取 common.py 共享模块，消除枚举重复定义
- 依赖分析器：限定上下文检测、扩展关键字过滤、自引用排除
- 合并脚本按方言适配（Oracle/SQL Server/PostgreSQL/MySQL/DM）
- 拆分后自动生成 merge_all.sql
- 新增 37 个单元测试
- SQL Server 正则修复：方括号标识符匹配

### v1.1.0 (2026-04-13)
- 新增索引支持：CREATE INDEX, CREATE UNIQUE INDEX
- 新增约束支持：ALTER TABLE ADD CONSTRAINT
- 所有 6 种方言均支持索引/约束识别
- 支持 CLUSTERED/NONCLUSTERED (SQL Server)
- 支持 BITMAP 索引 (Oracle/达梦)

### v1.0.0
- 初始版本
