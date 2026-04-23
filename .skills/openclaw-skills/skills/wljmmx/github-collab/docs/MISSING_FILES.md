## 缺失的模块文件

### 在 main-controller.js 中引用但不存在的文件：

1. `./dev-agent` - 应该创建 `src/core/dev-agent.js`
2. `./test-agent` - 应该创建 `src/core/test-agent.js`
3. `./task-manager-enhanced` - 应该创建 `src/core/task-manager-enhanced.js`

### 在 index.js 中引用但不存在的文件：

1. `./task-manager-enhanced` - 已检查，不存在
2. `./stp-integrator` - 已检查，不存在
3. `./stp-integrator-enhanced` - 已检查，不存在
4. `./qq-notifier` - 已检查，不存在

### 解决方案：

1. 创建缺失的 Agent 类文件
2. 更新 index.js 的导出列表
3. 修复所有引用路径
