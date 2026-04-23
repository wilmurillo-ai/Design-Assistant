# 技术栈检测规则

## Java 项目

### 识别文件
- `pom.xml` → Maven 项目
- `build.gradle` / `build.gradle.kts` → Gradle 项目

### 框架识别
```xml
<!-- Spring Boot -->
<dependency>
  <groupId>org.springframework.boot</groupId>
</dependency>

<!-- Spring Cloud -->
<dependency>
  <groupId>org.springframework.cloud</groupId>
</dependency>
```

### 配置文件
- `application.yml` / `application.yaml`
- `application.properties`
- `application-{profile}.yml`

### 数据库识别
- `spring.jpa` → JPA
- `mybatis` → MyBatis
- `mybatis-plus` → MyBatis Plus

### 项目结构
```
src/main/java/
├── controller/    # 控制器
├── service/       # 服务层
├── repository/    # 数据访问层
├── entity/        # 实体类
├── dto/           # 数据传输对象
├── config/        # 配置类
└── util/          # 工具类
```

---

## Node.js 项目

### 识别文件
- `package.json`

### 框架识别
```json
{
  "dependencies": {
    "express": "^4.x",        // Express
    "koa": "^2.x",            // Koa
    "@nestjs/core": "^10.x",  // NestJS
    "fastify": "^4.x"         // Fastify
  }
}
```

### 数据库识别
```json
{
  "dependencies": {
    "sequelize": "^6.x",      // Sequelize
    "typeorm": "^0.3.x",      // TypeORM
    "prisma": "^5.x",         // Prisma
    "mongoose": "^7.x"        // Mongoose (MongoDB)
  }
}
```

### 项目结构
```
src/
├── routes/        # 路由
├── controllers/   # 控制器
├── services/      # 服务层
├── models/        # 数据模型
├── middleware/    # 中间件
└── config/        # 配置
```

---

## Python 项目

### 识别文件
- `requirements.txt`
- `pyproject.toml`
- `setup.py`
- `Pipfile`

### 框架识别
```txt
# Django
Django>=4.0

# Flask
Flask>=2.0

# FastAPI
fastapi>=0.100
```

### 数据库识别
```txt
# SQLAlchemy
SQLAlchemy>=2.0

# Django ORM (已包含在 Django)

# MongoDB
pymongo>=4.0
```

### 项目结构
```
# Django
project/
├── apps/          # 应用模块
├── settings/      # 配置
├── urls.py        # 路由
└── wsgi.py

# FastAPI
app/
├── main.py        # 入口
├── routers/       # 路由
├── models/        # 模型
├── schemas/       # Schema
└── services/      # 服务
```

---

## Go 项目

### 识别文件
- `go.mod`

### 框架识别
```go
// Gin
github.com/gin-gonic/gin

// Echo
github.com/labstack/echo/v4

// Fiber
github.com/gofiber/fiber/v2
```

### 数据库识别
```go
// GORM
gorm.io/gorm

// sqlx
github.com/jmoiron/sqlx
```

### 项目结构
```
cmd/              # 应用入口
internal/         # 私有代码
├── handler/      # 处理器
├── service/      # 服务层
├── repository/   # 数据访问
└── model/        # 模型
pkg/              # 公共代码
configs/          # 配置
```

---

## 前端项目

### React
```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x"
  }
}
```

### Vue
```json
{
  "dependencies": {
    "vue": "^3.x"
  }
}
```

### Angular
```json
{
  "dependencies": {
    "@angular/core": "^17.x"
  }
}
```

### 项目结构
```
src/
├── components/   # 组件
├── pages/        # 页面
├── hooks/        # 自定义 Hooks
├── store/        # 状态管理
├── api/          # API 调用
├── utils/        # 工具函数
└── assets/       # 静态资源
```
