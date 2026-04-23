# meta-skill-weaver - 技能编织器【自研元能力】

**版本**：v0.4.0（状态持久化重大升级版）  
**定位**：AI 技能编排引擎 - 让多个技能协作完成复杂任务

**ClawHub 技能 ID**：k97crgc87wvax43azvp82qp0rs83px7x

---

## 🎯 适用场景

✅ 多步骤任务（研究→分析→报告）
✅ 多技能协作（需要 3+ 技能）
✅ 需要进度追踪的长程任务
✅ 需要中断恢复的长时任务
✅ 需要事件驱动的松耦合协作

---

## 🔧 核心功能

**v0.4.0 新增**（2026-04-02）：
- ✅ **状态机系统** - 完整的任务状态管理（pending/running/completed/failed/paused/cancelled）
- ✅ **状态持久化** - JSON 状态机追踪任务状态，支持中断恢复
- ✅ **自动备份** - 状态变更自动创建备份，支持回滚
- ✅ **状态中间件** - 将状态持久化作为 Middleware 链的一部分
- ✅ **可恢复任务列表** - 列出所有可恢复的暂停/运行中任务

**v0.3.0 功能**：
- ✅ EventBus 事件系统 - 完整订阅/发布模式，支持事件拦截器和上下文保持
- ✅ Jest 单元测试框架 - 92 个测试用例，覆盖率≥73%
- ✅ 第一性原理任务分解器 - 5 Why 分析，假设识别，任务重构

**v0.2.0 功能**：
- ✅ Middleware 链（7 个内置中间件）
- ✅ 虚拟路径系统（线程隔离）
- ✅ 并发执行（限制 3 个并发）
- ✅ 超时控制（默认 15 分钟）

**原有功能**：
- ✅ 任务分解与编排
- ✅ 技能分配与调度
- ✅ 状态追踪（6 种状态）
- ✅ 中断恢复
- ✅ 数据收集

---

## 🏗️ 技术架构

### 模块结构
```
src/
├── task-tracker.js                  # 核心任务追踪器
├── event-bus.js                     # 事件总线
├── first-principle-decomposer.js    # 任务分解器
├── middleware-chain.js              # 中间件链
├── parallel-execution.js            # 并行执行
├── virtual-path-system.js           # 虚拟路径
├── state-machine.js                 # 状态机（v0.4.0 新增）
├── state-persistence.js             # 状态持久化（v0.4.0 新增）
└── state-persistence-middleware.js  # 状态中间件（v0.4.0 新增）
```

### 测试覆盖
```
tests/
├── task-tracker.test.js             # 任务追踪测试
├── event-bus.test.js                # 事件系统测试
├── first-principle-decomposer.test.js  # 分解器测试
├── middleware-chain.test.js         # 中间件测试
├── state-machine.test.js            # 状态机测试（v0.4.0 新增）
└── state-persistence.test.js        # 持久化测试（v0.4.0 新增）
```

**总测试用例**：92 个  
**覆盖率**：73.72%（语句）、56.84%（分支）、85.12%（函数）

---

## 📋 工作流程

```
1. 接收复杂任务
   ↓
2. 第一性原理分解（识别假设→5Why 分析→重构任务）
   ↓
3. 分解为原子任务
   ↓
4. 通过 EventBus 分配合适技能
   ↓
5. 并行/串行执行（Middleware 链处理）
   ↓
6. 状态机追踪与状态持久化（v0.4.0 新增）
   ↓
7. 合成最终结果
   ↓
8. 交付报告
```

---

## 🔌 State Machine API（v0.4.0 新增）

### 基本用法
```javascript
const { StateMachine, TaskState } = require('./src/state-machine');

const machine = new StateMachine();

// 状态转换
machine.start();           // PENDING → RUNNING
machine.pause();           // RUNNING → PAUSED
machine.resume();          // PAUSED → RUNNING
machine.complete();        // RUNNING → COMPLETED
machine.fail();            // RUNNING → FAILED
machine.retry();           // FAILED → PENDING
machine.cancel();          // 任何状态 → CANCELLED

// 状态检查
machine.getState();        // 获取当前状态
machine.isTerminal();      // 是否为终态
machine.canResume();       // 是否可恢复
machine.canRetry();        // 是否可重试

// 状态历史
const history = machine.getHistory();
```

### 状态持久化
```javascript
const { StatePersistence } = require('./src/state-persistence');

const persistence = new StatePersistence('./state-storage');

// 保存状态
persistence.save('task-123', machine.toJSON());

// 加载状态
const data = persistence.load('task-123');

// 恢复状态机
const restored = persistence.restoreStateMachine('task-123');

// 列出可恢复任务
const recoverable = persistence.listRecoverable();
```

### 状态中间件
```javascript
const { 
  createStatePersistenceMiddleware,
  createStateRestoreMiddleware,
  createStateCheckMiddleware 
} = require('./src/state-persistence-middleware');

// 在 Middleware 链中使用
chain.use(createStatePersistenceMiddleware({ storagePath: './states' }));
chain.use(createStateRestoreMiddleware());
chain.use(createStateCheckMiddleware());
```

---

## 🧪 测试

```bash
# 运行测试
npm test

# 带覆盖率报告
npm run test:coverage

# 监视模式
npm run test:watch
```

**测试命令**：`npx jest --coverage`

---

## 📊 六维评估

| 维度 | v0.3.0 | v0.4.0 | 改进 | 目标 |
|------|--------|--------|------|------|
| T（技术深度） | 0.70 | 0.78 | +0.08 | 0.80 |
| C（认知增强） | 0.65 | 0.68 | +0.03 | 0.80 |
| O（编排能力） | 0.80 | 0.85 | +0.05 | 0.90 |
| E（进化能力） | 0.62 | 0.70 | +0.08 | 0.80 |
| M（商业化） | 0.40 | 0.45 | +0.05 | 0.70 |
| U（用户体验） | 0.58 | 0.65 | +0.07 | 0.80 |
| **平均** | **0.63** | **0.69** | **+0.06** | **0.80** |

---

## 💼 服务定价

| 版本 | 价格 | 包含 |
|------|------|------|
| 个人版 | $99.9 | 永久使用 +1 年更新 |
| 商业版 | $299.9 | 商业用途 + 优先支持 |
| 企业版 | $999.9 | 定制 + 部署 + 培训 |

**企业联系**：business@cloud-shrimp.com

---

## 🏆 头部技能对标

**对标**：writing-assistant（3.641 分）

**我们的优势**：
- ✅ 更强大的编排能力（O 维度 0.85）
- ✅ 支持并发执行
- ✅ 完整的状态追踪与持久化（v0.4.0）
- ✅ 事件驱动架构
- ✅ 单元测试覆盖（92 个用例）
- ✅ 中断恢复能力（生产级特性）

---

## 📞 支持

- 📧 support@cloud-shrimp.com
- 💬 微信：CloudShrimpSupport

**响应**：24 小时内

---

## 📝 版本历史

**v0.4.0**（2026-04-02）- 状态持久化重大升级
- 新增 State Machine 状态机系统
- 新增 State Persistence 状态持久化
- 新增 State Persistence Middleware 状态中间件
- 新增 31 个测试用例（共 92 个）
- 六维评分 0.63→0.69

**v0.3.0**（2026-03-31）- 重大升级
- 新增 EventBus 事件系统
- 新增 Jest 单元测试框架
- 新增第一性原理任务分解器
- 六维评分 0.58→0.63

**v0.2.0**（2026-03-28）
- Middleware 链
- 虚拟路径系统
- 并发执行

**v0.1.0**（2026-03-27）- 初始版本

---

**版本**：v0.4.0 | **更新**：2026-04-02 | **维护者**：王的奴隶 · 严谨专业版
