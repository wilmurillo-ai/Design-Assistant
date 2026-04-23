# 文档生成模板

## 架构文档模板

```markdown
# 系统架构文档

## 1. 项目概述

**项目名称：** {project_name}  
**技术栈：** {tech_stack}  
**版本：** {version}

## 2. 系统架构

### 2.1 整体架构

{architecture_diagram}

### 2.2 技术选型

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | {framework} | {version} | {description} |
| 数据库 | {database} | {version} | {description} |
| 缓存 | {cache} | {version} | {description} |
| 消息队列 | {mq} | {version} | {description} |

## 3. 模块说明

### 3.1 核心模块

{#modules}
#### {module_name}

**职责：** {responsibility}  
**依赖：** {dependencies}  
**关键类：** {key_classes}

{/modules}

## 4. 数据流

{data_flow_diagram}

## 5. 部署架构

{deployment_diagram}

## 6. 安全架构

- 认证方式：{auth_method}
- 授权机制：{authorization}
- 数据加密：{encryption}
```

---

## 数据库文档模板

```markdown
# 数据库设计文档

## 1. 数据库概览

**数据库类型：** {db_type}  
**版本：** {db_version}  
**字符集：** {charset}

## 2. ER 图

{er_diagram}

## 3. 表结构

{#tables}
### {table_name}

**描述：** {description}

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
{#columns}
| {name} | {type} | {constraints} | {default} | {comment} |
{/columns}

**索引：**
{#indexes}
- {index_name}: {index_columns} ({index_type})
{/indexes}

**关系：**
{#relations}
- {relation_type}: {target_table} ({foreign_key})
{/relations}

{/tables}

## 4. 索引策略

{index_strategy}

## 5. 数据迁移

{migration_guide}
```

---

## 开发规范模板

```markdown
# 开发规范

## 1. 代码规范

### 1.1 命名规范

**类命名：**
- PascalCase
- 语义化命名
- 示例：`UserService`、`OrderController`

**方法命名：**
- camelCase
- 动词开头
- 示例：`getUserById`、`createOrder`

**变量命名：**
- camelCase
- 有意义的名称
- 避免缩写

### 1.2 注释规范

**类注释：**
```java
/**
 * 用户服务类
 * @author {author}
 * @date {date}
 */
```

**方法注释：**
```java
/**
 * 根据ID获取用户
 * @param id 用户ID
 * @return 用户对象
 * @throws UserNotFoundException 用户不存在时抛出
 */
```

## 2. 目录结构规范

```
{project_structure}
```

## 3. Git 提交规范

### 3.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type 类型：**
- feat: 新功能
- fix: Bug 修复
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

### 3.2 分支规范

- main: 主分支
- develop: 开发分支
- feature/*: 功能分支
- hotfix/*: 热修复分支

## 4. 代码审查规范

### 4.1 审查清单

- [ ] 代码符合规范
- [ ] 有单元测试
- [ ] 无安全漏洞
- [ ] 性能可接受
- [ ] 文档已更新

## 5. 日志规范

**日志级别：**
- ERROR: 错误信息
- WARN: 警告信息
- INFO: 关键信息
- DEBUG: 调试信息

**日志格式：**
```
[{timestamp}] [{level}] [{class}] - {message}
```
```

---

## 快速启动模板

```markdown
# 快速启动指南

## 1. 环境要求

| 软件 | 版本 | 必需 |
|------|------|------|
| JDK | 17+ | ✅ |
| Maven | 3.8+ | ✅ |
| MySQL | 8.0+ | ✅ |
| Redis | 7.0+ | ✅ |
| Node.js | 18+ | ❌ |

## 2. 安装步骤

### 2.1 克隆项目

```bash
git clone {repo_url}
cd {project_name}
```

### 2.2 配置数据库

```sql
CREATE DATABASE {db_name} CHARACTER SET utf8mb4;
```

### 2.3 配置文件

复制配置文件模板：
```bash
cp application.yml.template application.yml
```

修改配置：
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/{db_name}
    username: {username}
    password: {password}
```

### 2.4 安装依赖

```bash
mvn clean install
```

### 2.5 启动服务

```bash
mvn spring-boot:run
```

## 3. 验证启动

访问：http://localhost:{port}/actuator/health

## 4. 常见问题

### Q1: 端口被占用

```bash
# 查找占用端口的进程
netstat -ano | findstr :{port}

# 终止进程
taskkill /PID {pid} /F
```

### Q2: 数据库连接失败

检查：
- MySQL 服务是否启动
- 用户名密码是否正确
- 数据库是否创建
```

---

## 测试规范模板

```markdown
# 测试规范

## 1. 测试框架

| 类型 | 框架 | 用途 |
|------|------|------|
| 单元测试 | JUnit 5 | 方法级测试 |
| 集成测试 | Spring Boot Test | 集成测试 |
| E2E 测试 | RestAssured | API 测试 |

## 2. 测试覆盖率要求

| 类型 | 最低覆盖率 |
|------|-----------|
| 单元测试 | 80% |
| 集成测试 | 60% |
| 关键路径 | 100% |

## 3. 测试命名规范

```java
@Test
void should_return_user_when_find_by_id() {
    // given
    // when
    // then
}
```

## 4. 测试用例编写规范

### 4.1 单元测试

```java
@DisplayName("用户服务测试")
class UserServiceTest {
    
    @Mock
    private UserRepository repository;
    
    @InjectMocks
    private UserService service;
    
    @Test
    @DisplayName("根据ID查询用户 - 成功")
    void should_return_user_when_id_exists() {
        // given
        Long id = 1L;
        User expected = new User(id, "test@test.com");
        when(repository.findById(id)).thenReturn(Optional.of(expected));
        
        // when
        User actual = service.findById(id);
        
        // then
        assertThat(actual).isEqualTo(expected);
        verify(repository).findById(id);
    }
}
```

### 4.2 集成测试

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void should_create_user_when_post_valid_data() throws Exception {
        // given
        String userJson = "{\"email\":\"test@test.com\"}";
        
        // when & then
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(userJson))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("test@test.com"));
    }
}
```

## 5. Mock 规范

### 5.1 何时使用 Mock

- 外部服务调用
- 数据库访问（单元测试）
- 文件系统操作

### 5.2 何时不使用 Mock

- 集成测试
- 简单的工具类
- 数据对象

## 6. 测试数据管理

```java
// 使用 TestContainers 管理测试数据库
@Testcontainers
class UserRepositoryTest {
    
    @Container
    static MySQLContainer<?> mysql = new MySQLContainer<>("mysql:8.0");
    
    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", mysql::getJdbcUrl);
        registry.add("spring.datasource.username", mysql::getUsername);
        registry.add("spring.datasource.password", mysql::getPassword);
    }
}
```
```

---

## 配置项文档模板

```markdown
# 配置项说明文档

## 1. 配置文件

| 文件 | 位置 | 说明 |
|------|------|------|
| application.yml | src/main/resources/ | 主配置文件 |
| application-dev.yml | src/main/resources/ | 开发环境配置 |
| application-prod.yml | src/main/resources/ | 生产环境配置 |

## 2. 配置项清单

### 2.1 服务器配置

| 配置项 | 默认值 | 说明 | 是否必需 |
|--------|--------|------|----------|
| server.port | 8080 | 服务端口 | 否 |
| server.context-path | / | 上下文路径 | 否 |

### 2.2 数据库配置

| 配置项 | 默认值 | 说明 | 是否必需 |
|--------|--------|------|----------|
| spring.datasource.url | - | 数据库连接地址 | 是 |
| spring.datasource.username | - | 数据库用户名 | 是 |
| spring.datasource.password | - | 数据库密码 | 是 🔒 |

### 2.3 缓存配置

| 配置项 | 默认值 | 说明 | 是否必需 |
|--------|--------|------|----------|
| spring.redis.host | localhost | Redis 地址 | 否 |
| spring.redis.port | 6379 | Redis 端口 | 否 |
| spring.redis.password | - | Redis 密码 | 否 🔒 |

## 3. 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| DB_URL | 数据库地址 | jdbc:mysql://localhost:3306/db |
| DB_USERNAME | 数据库用户名 | root |
| DB_PASSWORD | 数据库密码 🔒 | password |
| REDIS_PASSWORD | Redis 密码 🔒 | password |

## 4. 敏感配置处理

标记为 🔒 的配置项为敏感配置，建议：
- 使用环境变量
- 使用配置中心（如 Nacos、Apollo）
- 不要提交到代码仓库
```
