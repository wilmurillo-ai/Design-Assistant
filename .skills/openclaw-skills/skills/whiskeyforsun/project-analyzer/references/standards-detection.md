# 规范检测与自动创建指南

## 概述

project-analyzer 在生成文档时会自动检查项目中是否存在对应的规范文档，如果缺失则自动创建。

---

## 🔍 规范检测规则

### 扫描优先级

1. **docs/ 目录** (最高优先级)
   - `docs/development/`
   - `docs/standards/`
   - `docs/specs/`
   - `docs/rules/`

2. **根目录**
   - `CONTRIBUTING.md`
   - `CODE_OF_CONDUCT.md`
   - `STANDARDS.md`

3. **配置文件** (推断规范)
   - `.eslintrc*` → 代码风格规范
   - `.prettierrc*` → 代码格式化规范
   - `.editorconfig` → 编辑器规范
   - `stylelintrc*` → CSS 规范
   - `.commitlintrc*` → 提交信息规范

4. **CI/CD 配置**
   - `.github/workflows/` → GitHub Actions 规范
   - `Jenkinsfile` → CI 规范

---

## 📝 需检测的规范清单

### 通用开发规范

| 规范文件 | 说明 | 检测关键词 |
|----------|------|-----------|
| `coding-standards.md` | 代码编写规范 | code style, coding, linter |
| `naming-conventions.md` | 命名约定 | naming, convention |
| `git-workflow.md` | Git 工作流 | git workflow, branch |
| `code-review.md` | 代码审查规范 | review, PR, pull request |
| `test-standards.md` | 测试规范 | test, unit, coverage |
| `api-design.md` | API 设计规范 | api, rest, endpoint |
| `security-policy.md` | 安全规范 | security, auth, permission |
| `commit-message.md` | 提交信息规范 | commit, conventional |

### 数据库相关规范 ⭐ NEW

| 规范文件 | 说明 | 检测关键词 |
|----------|------|-----------|
| `database-standards.md` | 数据库设计规范 | database, schema, table, erd |
| `sql-coding-standards.md` | SQL 编码规范 | SQL, query, stored procedure |
| `data-migration.md` | 数据迁移规范 | migration, changelog, flyway, liquibase |
| `index-design.md` | 索引设计规范 | index, performance, optimization |

---

## 🤖 自动创建逻辑

### 触发条件

```
当以下条件同时满足时，自动创建规范文档：
1. 目标规范文件不存在
2. 用户未明确禁止自动创建
3. 项目技术栈已确定
```

### 创建流程

```python
def check_and_create_standards(project_path, tech_stack):
    """检查并创建缺失的规范文档"""
    
    # 1. 定义规范与对应的检测文件和创建模板
    standards = {
        "coding-standards.md": {
            "keywords": ["code style", "lint", "format"],
            "template": get_coding_template(tech_stack)
        },
        "naming-conventions.md": {
            "keywords": ["naming", "convention"],
            "template": get_naming_template(tech_stack)
        },
        # ... 其他规范
    }
    
    # 2. 扫描现有文件
    existing_docs = scan_project_docs(project_path)
    
    # 3. 检测缺失
    missing_standards = []
    for std_name, std_info in standards.items():
        if not find_standard(existing_docs, std_info["keywords"]):
            missing_standards.append(std_name)
    
    # 4. 生成并创建缺失规范
    if missing_standards:
        confirm_and_create(project_path, missing_standards, tech_stack)
    
    return missing_standards
```

---

## 📄 规范模板

### Java/Spring Boot 项目

自动创建时使用以下技术特定模板：

```markdown
# [规范名称]

## 1. 适用范围

适用于 `{project_name}` 项目，基于 {tech_stack} 技术栈。

## 2. 代码规范

### 2.1 类命名
- 使用 PascalCase
- 以业务含义命名
- 示例：`UserService`, `OrderController`, `ProductRepository`

### 2.2 方法命名
- 使用 camelCase
- 动词/动词短语开头
- 查询方法：`get*`, `find*`, `load*`
- 创建方法：`create*`, `save*`, `add*`
- 更新方法：`update*`, `modify*`
- 删除方法：`delete*`, `remove*`

### 2.3 常量命名
- 使用 UPPER_SNAKE_CASE
- 使用有意义的单词组合
- 示例：`MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE`

## 3. 包结构规范

```
com.{company}.{project}
├── controller/     # 控制层
├── service/        # 服务层
├── repository/     # 数据访问层
├── entity/         # 实体类
├── dto/            # 数据传输对象
├── vo/             # 视图对象
├── config/         # 配置类
└── common/         # 公共工具类
```

## 4. Git 提交规范

### 4.1 分支命名
```
main              # 主分支
develop           # 开发分支
feature/*         # 功能分支
hotfix/*          # 热修复分支
release/*         # 发布分支
```

### 4.2 提交信息格式
```
<type>(<scope>): <subject>

feat(user): add user login feature
fix(order): correct order amount calculation
docs(api): update API documentation
```

### 4.3 Type 类型
| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| docs | 文档更新 |
| style | 代码格式 |
| refactor | 重构 |
| test | 测试 |
| chore | 构建/工具 |

## 5. API 设计规范

### 5.1 URL 规范
```
GET    /api/users          # 获取用户列表
GET    /api/users/{id}     # 获取单个用户
POST   /api/users          # 创建用户
PUT    /api/users/{id}     # 更新用户
DELETE /api/users/{id}     # 删除用户
```

### 5.2 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

---

## 🗄️ 数据库设计规范模板 ⭐ NEW

### Database Standards (数据库设计规范)

```markdown
# 数据库设计规范

## 1. 命名规范

### 1.1 表命名
- 使用小写字母和下划线
- 采用「模块_实体」或「实体」命名
- 示例：`sys_user`（系统用户）、`order_detail`（订单明细）
- 避免使用复数形式

### 1.2 字段命名
- 使用小写字母和下划线
- 语义化命名
- 示例：`user_id`、`create_time`、`is_deleted`

### 1.3 索引命名
```
idx_{table}_{column}     # 普通索引
uk_{table}_{column}      # 唯一索引
pk_{table}               # 主键索引
```

### 1.4 外键命名
```
fk_{table}_{ref_table}   # 外键约束
```

## 2. 表设计规范

### 2.1 必须包含的字段
```sql
CREATE TABLE example (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by  VARCHAR(64) COMMENT '创建人',
    updated_by  VARCHAR(64) COMMENT '更新人',
    is_deleted  TINYINT DEFAULT 0 COMMENT '逻辑删除标记'
);
```

### 2.2 字段类型选择
| 数据类型 | 适用场景 | 注意事项 |
|----------|----------|----------|
| VARCHAR | 字符串、可变长度 | 指定合理长度，避免 TEXT 滥用 |
| INT/BIGINT | 数字 ID | 主键用 BIGINT |
| DATETIME | 时间戳 | 优先使用 DATETIME |
| DECIMAL | 金额 | 金额必须用 DECIMAL，禁止使用 FLOAT/DOUBLE |
| TEXT | 长文本 | 仅用于超过 4000 字符的场景 |

### 2.3 主键规范
- 必须使用自增 BIGINT 主键
- 禁止使用业务主键作为主键
- 不使用 UUID 作为主键

### 2.4 索引规范
- 单表索引不超过 5 个
- 避免在区分度低的字段建索引
- 遵循最左前缀原则
- 定期分析慢查询，优化索引

## 3. 关联设计规范

### 3.1 外键使用
- 禁止使用外键约束（使用逻辑外键）
- 在应用层保证数据一致性

### 3.2 关联查询限制
- 关联表不超过 3 张
- 使用分页查询
- 避免 SELECT *

## 4. 安全规范

### 4.1 敏感数据处理
- 密码必须加密存储
- 手机号、身份证等脱敏处理
- 敏感日志脱敏

### 4.2 SQL 注入防护
- 使用参数化查询
- 禁止拼接 SQL
- 严格权限控制
```

### SQL Coding Standards (SQL 编码规范)

```markdown
# SQL 编码规范

## 1. 书写格式

### 1.1 关键字大写
```sql
SELECT user_name, email
FROM sys_user
WHERE status = 1
  AND is_deleted = 0;
```

### 1.2 缩进与换行
```sql
SELECT u.id,
       u.user_name,
       u.email,
       u.create_time
FROM sys_user u
     LEFT JOIN order o ON u.id = o.user_id
WHERE u.status = 1
ORDER BY u.create_time DESC
LIMIT 10;
```

### 1.3 表别名规范
- 使用有意义的别名
- 常用别名：`u`（user）、`o`（order）、`d`（dict）

## 2. 查询规范

### 2.1 禁止使用
```sql
-- ❌ 禁止
SELECT * FROM table;
SELECT COUNT(*) FROM table;
SELECT * FROM table1, table2;
```

```sql
-- ✅ 正确
SELECT id, name FROM table;
SELECT COUNT(1) FROM table;
SELECT t1.id FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id;
```

### 2.2 性能优化
- 使用 EXPLAIN 分析查询
- 避免在 WHERE 条件中对字段使用函数
- 使用 LIMIT 限制结果集
- 批量操作使用 INSERT/UPDATE VALUES

## 3. DDL 规范

### 3.1 建表规范
- 必须包含注释
- 必须指定字符集：`DEFAULT CHARSET=utf8mb4`
- 必须指定存储引擎：`ENGINE=InnoDB`

### 3.2 字段规范
```sql
CREATE TABLE example (
    -- 主键
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    
    -- 必填字段
    name VARCHAR(100) NOT NULL COMMENT '名称',
    
    -- 可选字段
    description VARCHAR(500) DEFAULT NULL COMMENT '描述',
    
    -- 金额字段
    amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '金额',
    
    -- 状态字段
    status TINYINT DEFAULT 1 COMMENT '状态：0-禁用 1-启用',
    
    -- 时间字段
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 主键索引
    PRIMARY KEY (id),
    
    -- 唯一索引
    UNIQUE KEY uk_name (name),
    
    -- 普通索引
    KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='示例表';
```

## 4. 事务规范

### 4.1 事务范围
- 保持事务简短
- 避免在事务中执行远程调用
- 超时时间不超过 30 秒

### 4.2 隔离级别
- 读已提交（RC）为默认隔离级别
- 按需提高隔离级别

## 5. 注释规范

```sql
-- 单行注释
/*
 * 多行注释
 * 用于复杂逻辑说明
 */
```

---

## ⚙️ 前端项目 (React/Vue)

```markdown
# 代码规范

## 组件命名
- PascalCase: `UserCard.vue`, `OrderList.jsx`
- 业务组件: `features/` 目录
- 通用组件: `components/` 目录

## 目录结构
```
src/
├── components/    # 通用组件
├── features/      # 业务功能
├── hooks/         # 自定义 Hooks
├── utils/         # 工具函数
├── api/           # API 接口
└── assets/        # 静态资源
```

## CSS 规范
- 使用 BEM 命名或 CSS Modules
- 使用语义化类名
- 避免使用行内样式
```

---

## 📋 用户确认流程

```
┌─────────────────────────────────────────┐
│  检测到缺失规范                          │
├─────────────────────────────────────────┤
│  📄 missing:                             │
│  - coding-standards.md                   │
│  - git-workflow.md                       │
├─────────────────────────────────────────┤
│  操作选项：                              │
│  [1] 全部自动创建                        │
│  [2] 选择性创建                          │
│  [3] 跳过（稍后手动创建）                │
│  [4] 查看将要创建的内容预览              │
└─────────────────────────────────────────┘
```

---

## 🔧 配置项

在 `project-analyzer.yaml` 中配置规范创建行为：

```yaml
standards:
  auto_create: true           # 是否自动创建缺失规范
  force_overwrite: false      # 是否覆盖已存在的规范
  confirm_before_create: true # 创建前是否确认
  templates_dir: references/standards  # 模板目录
```

---

## 📌 最佳实践

1. **优先复用**：如果项目已有类似规范，创建链接而非重复
2. **技术匹配**：根据检测到的技术栈选择对应模板
3. **渐进完善**：初始创建基础版本，后续迭代完善
4. **用户审核**：自动创建后提示用户审核确认

---

*让每个项目都有完整的开发规范 📋✨*
