# Apifox 集成指南

## 前置准备

### 1. 安装 Apifox CLI

```bash
# npm 安装
npm install -g apifox-cli

# 或使用 yarn
yarn global add apifox-cli

# 验证安装
apifox --version
```

### 2. 获取 API Token

1. 登录 Apifox
2. 进入「个人设置」→「API 访问令牌」
3. 创建新令牌
4. 复制令牌值

### 3. 配置环境变量

```bash
# Linux/macOS
export APIFOX_API_TOKEN=your_token_here

# Windows PowerShell
$env:APIFOX_API_TOKEN="your_token_here"

# 或写入配置文件 ~/.apifoxrc
APIFOX_API_TOKEN=your_token_here
```

---

## OpenAPI 文档生成

### Spring Boot

```yaml
# application.yml
springdoc:
  api-docs:
    enabled: true
    path: /v3/api-docs
  swagger-ui:
    enabled: true
    path: /swagger-ui.html
```

**访问地址：**
- OpenAPI JSON: http://localhost:8080/v3/api-docs
- Swagger UI: http://localhost:8080/swagger-ui.html

**导出命令：**
```bash
curl http://localhost:8080/v3/api-docs -o openapi.json
```

### NestJS

```typescript
// main.ts
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

const config = new DocumentBuilder()
    .setTitle('API Documentation')
    .setVersion('1.0')
    .build();
const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('api-docs', app, document);
```

**访问地址：**
- OpenAPI JSON: http://localhost:3000/api-docs-json

### FastAPI

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# 自动生成 OpenAPI
# 访问: http://localhost:8000/openapi.json
```

---

## 同步到 Apifox

### 方式一：文件同步

```bash
# 同步 OpenAPI 文件
apifox sync \
    --project-id 12345 \
    --file ./docs/api/openapi.yaml

# 同步 JSON 格式
apifox sync \
    --project-id 12345 \
    --file ./docs/api/openapi.json
```

### 方式二：URL 同步

```bash
# 从运行中的服务同步
apifox sync \
    --project-id 12345 \
    --url http://localhost:8080/v3/api-docs
```

### 方式三：手动导入

1. 登录 Apifox
2. 进入项目设置
3. 选择「导入数据」
4. 上传 OpenAPI 文件

---

## 自动测试执行

### 运行测试用例

```bash
# 运行所有测试
apifox run \
    --project-id 12345 \
    --all

# 运行特定测试套件
apifox run \
    --project-id 12345 \
    --suite smoke-test

# 运行单个用例
apifox run \
    --project-id 12345 \
    --case login-test

# 指定环境
apifox run \
    --project-id 12345 \
    --env staging \
    --all
```

### 测试报告

```bash
# 生成 HTML 报告
apifox run \
    --project-id 12345 \
    --all \
    --report html \
    --output ./test-reports/

# 生成 JUnit XML（用于 CI/CD）
apifox run \
    --project-id 12345 \
    --all \
    --report junit \
    --output ./test-reports/junit.xml
```

---

## CI/CD 集成

### GitHub Actions

```yaml
name: API Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  api-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install Apifox CLI
        run: npm install -g apifox-cli
      
      - name: Sync API Docs
        env:
          APIFOX_API_TOKEN: ${{ secrets.APIFOX_API_TOKEN }}
        run: |
          apifox sync \
            --project-id ${{ secrets.APIFOX_PROJECT_ID }} \
            --file ./docs/api/openapi.yaml
      
      - name: Run API Tests
        env:
          APIFOX_API_TOKEN: ${{ secrets.APIFOX_API_TOKEN }}
        run: |
          apifox run \
            --project-id ${{ secrets.APIFOX_PROJECT_ID }} \
            --env staging \
            --all \
            --report junit \
            --output ./test-reports/junit.xml
      
      - name: Publish Test Report
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: API Test Report
          path: ./test-reports/junit.xml
          reporter: java-junit
```

### GitLab CI

```yaml
# .gitlab-ci.yml
api-test:
  stage: test
  image: node:20
  before_script:
    - npm install -g apifox-cli
  script:
    - apifox sync --project-id $APIFOX_PROJECT_ID --file ./docs/api/openapi.yaml
    - apifox run --project-id $APIFOX_PROJECT_ID --all --report html --output ./test-reports/
  artifacts:
    paths:
      - test-reports/
    expire_in: 1 week
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('API Test') {
            steps {
                sh 'npm install -g apifox-cli'
                sh '''
                    apifox sync \
                        --project-id ${APIFOX_PROJECT_ID} \
                        --file ./docs/api/openapi.yaml
                    
                    apifox run \
                        --project-id ${APIFOX_PROJECT_ID} \
                        --all \
                        --report junit \
                        --output ./test-reports/junit.xml
                '''
            }
            post {
                always {
                    junit 'test-reports/junit.xml'
                }
            }
        }
    }
}
```

---

## 测试用例生成

### 自动生成规则

根据 OpenAPI 规范自动生成测试用例：

```yaml
# apifox-test-generator.yaml
rules:
  # 成功场景
  success:
    - status: 200
      description: 正常请求
    - status: 201
      description: 创建成功
  
  # 错误场景
  error:
    - status: 400
      description: 参数错误
      params:
        email: "invalid-email"
    - status: 401
      description: 未授权
      headers:
        Authorization: ""
    - status: 404
      description: 资源不存在
  
  # 边界条件
  boundary:
    - name: 空字符串
      params:
        name: ""
    - name: 超长字符串
      params:
        name: "a" * 1000
    - name: 特殊字符
      params:
        name: "<script>alert(1)</script>"
```

### 生成命令

```bash
apifox generate \
    --project-id 12345 \
    --file ./docs/api/openapi.yaml \
    --output ./test-cases/
```

---

## 最佳实践

### 1. 环境隔离

```
开发环境 → 自动测试 → 无需审批
测试环境 → 自动测试 → 生成报告
生产环境 → 禁止自动测试
```

### 2. 测试数据管理

```
使用测试数据库
使用 Mock 数据
避免使用真实用户数据
```

### 3. 测试报告归档

```
保留最近 30 天报告
重要版本永久保留
生成趋势分析图表
```

### 4. 告警配置

```
测试失败 → 钉钉/企微通知
成功率 < 80% → 邮件通知
响应时间 > 1s → 性能告警
```
