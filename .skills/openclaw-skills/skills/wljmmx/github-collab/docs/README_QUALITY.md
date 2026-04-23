# 代码质量指南

## 快速开始

### 安装依赖
```bash
npm install
```

### 运行测试
```bash
npm test
```

### 生成覆盖率报告
```bash
npm run coverage
```

### 代码检查
```bash
npm run lint
npm run format
```

---

## 项目结构

```
gitwork/
├── tests/                 # 单元测试目录
│   ├── utils.test.js      # 工具函数测试
│   ├── config.test.js     # 配置管理测试
│   ├── logger.test.js     # 日志系统测试
│   ├── db.test.js         # 数据库操作测试
│   └── cache.test.js      # 缓存系统测试
├── .eslintrc.js          # ESLint 配置
├── .prettierrc           # Prettier 配置
├── jest.config.js        # Jest 配置
├── nyc.config.js         # NYC 配置
├── commitlint.config.js  # Commitlint 配置
├── .husky/               # Git 钩子
│   └── pre-commit        # 提交前检查
└── QUALITY_REPORT.md     # 质量报告
```

---

## 测试

### 运行所有测试
```bash
npm test
```

### 运行特定测试文件
```bash
npm test -- tests/utils.test.js
```

### 运行测试并监听变化
```bash
npm run test:watch
```

### 运行测试并生成覆盖率
```bash
npm run test:coverage
```

---

## 代码覆盖率

### 生成覆盖率报告
```bash
npm run coverage
```

### 打开 HTML 报告
```bash
npm run coverage:open
```

### 覆盖率阈值
- 语句覆盖：80%
- 分支覆盖：80%
- 函数覆盖：80%
- 行覆盖：80%

---

## 代码规范

### ESLint 检查
```bash
npm run lint
```

### ESLint 修复
```bash
npm run lint:fix
```

### Prettier 格式化
```bash
npm run format
```

### Prettier 检查
```bash
npm run format:check
```

---

## Git 钩子

### 提交前自动检查
提交代码时会自动运行：
1. Prettier 格式化
2. ESLint 检查并修复
3. 运行测试
4. 自动提交修复

### 提交规范
使用约定式提交：
```bash
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复 bug"
git commit -m "docs: 更新文档"
```

提交类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档变更
- `style`: 代码格式
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `build`: 构建系统
- `ci`: CI 配置
- `chore`: 其他变更
- `revert`: 回滚

---

## 测试示例

### 工具函数测试
```javascript
describe('formatTime', () => {
  test('应该格式化时间', () => {
    const result = formatTime(1609459200000);
    expect(result).toBe('2021-01-01 00:00:00');
  });
});
```

### 配置管理测试
```javascript
test('应该读取环境变量', () => {
  process.env.TEST_VAR = 'test_value';
  const result = getEnv('TEST_VAR', 'default');
  expect(result).toBe('test_value');
});
```

### 日志系统测试
```javascript
test('应该记录日志', () => {
  const logger = createLogger({ level: 'DEBUG' });
  logger.info('test');
  expect(consoleLogs[0]).toContain('[INFO]');
});
```

---

## 最佳实践

### 编写测试
1. 每个函数都有测试
2. 覆盖边界情况
3. 测试异常处理
4. 使用描述性测试名称

### 编写代码
1. 使用严格模式
2. 避免使用 var
3. 优先使用 const
4. 使用箭头函数
5. 使用模板字符串

### 提交代码
1. 使用约定式提交
2. 提交信息清晰
3. 关联 Issue/PR
4. 小步提交

---

## 故障排除

### 测试失败
```bash
# 查看详细错误
npm test -- --verbose

# 运行单个测试
npm test -- tests/utils.test.js -t "应该格式化时间"
```

### ESLint 错误
```bash
# 查看错误
npm run lint

# 自动修复
npm run lint:fix
```

### Prettier 冲突
```bash
# 格式化所有文件
npm run format

# 检查格式
npm run format:check
```

---

## 性能指标

### 测试性能
- 测试执行时间：< 10 秒
- 覆盖率生成时间：< 5 秒
- Lint 检查时间：< 2 秒
- 格式化时间：< 1 秒

### 代码性能
- 启动时间：< 1 秒
- 内存占用：< 100MB
- 缓存命中率：> 80%

---

## 相关文档

- [Jest 文档](https://jestjs.io/)
- [ESLint 文档](https://eslint.org/)
- [Prettier 文档](https://prettier.io/)
- [Husky 文档](https://typicode.github.io/husky/)
- [Commitlint 文档](https://commitlint.js.org/)
- [Istanbul 文档](https://istanbul.js.org/)

---

## 贡献

### 添加新测试
1. 在 `tests/` 目录创建测试文件
2. 编写测试用例
3. 运行测试确保通过
4. 提交代码

### 更新配置
1. 更新配置文件
2. 运行测试确保通过
3. 提交代码

### 报告问题
1. 创建 Issue
2. 描述问题
3. 提供复现步骤
4. 等待响应

---

**最后更新**: 2024 年
**版本**: v1.0.0
