# SSE SDK 快速开始指南

## 🚀 5分钟上手技能自进化引擎

---

## 1. 安装SDK

### Python

```bash
pip install sse-sdk
```

### JavaScript/TypeScript

```bash
npm install sse-sdk
# 或
yarn add sse-sdk
```

---

## 2. 初始化客户端

### Python

```python
from sse_sdk import SSEClient

# 创建客户端
client = SSEClient(
    api_key="your_api_key_here",
    endpoint="https://api.sse.example.com"
)

# 或使用配置对象
from sse_sdk import SSEConfig

config = SSEConfig(
    api_key="your_api_key",
    endpoint="https://api.sse.example.com",
    timeout=30,
    retry_count=3
)
client = SSEClient(config=config)
```

### JavaScript

```javascript
import { SSEClient } from 'sse-sdk';

const client = new SSEClient({
  apiKey: 'your_api_key_here',
  endpoint: 'https://api.sse.example.com'
});
```

---

## 3. 追踪技能使用

### Python

```python
# 记录技能使用
result = client.track(
    skill_id="my-awesome-skill",
    metrics={
        "duration_ms": 1500,
        "success": True,
        "satisfaction": 4,  # 1-5分
        "output_quality": 0.85
    },
    context={
        "user_id": "user_123",
        "session_id": "session_456",
        "input_params": {"query": "hello"}
    }
)

print(f"记录ID: {result['record_id']}")
```

### JavaScript

```javascript
const result = await client.track('my-awesome-skill', {
  durationMs: 1500,
  success: true,
  satisfaction: 4,
  outputQuality: 0.85
}, {
  userId: 'user_123',
  sessionId: 'session_456'
});

console.log(`记录ID: ${result.record_id}`);
```

---

## 4. 分析技能性能

### Python

```python
# 分析技能
analysis = client.analyze("my-awesome-skill", time_range="30d")

print(f"成功率: {analysis['summary']['success_rate']:.2%}")
print(f"健康度: {analysis['summary']['health_score']}")

# 查看瓶颈
for bottleneck in analysis.get('bottlenecks', []):
    print(f"⚠️  {bottleneck['type']}: {bottleneck['recommendation']}")
```

### JavaScript

```javascript
const analysis = await client.analyze('my-awesome-skill', '30d');

console.log(`成功率: ${(analysis.summary.success_rate * 100).toFixed(1)}%`);
console.log(`健康度: ${analysis.summary.health_score}`);

analysis.bottlenecks?.forEach(b => {
  console.log(`⚠️  ${b.type}: ${b.recommendation}`);
});
```

---

## 5. 生成进化计划

### Python

```python
# 生成进化计划
plan = client.plan("my-awesome-skill", strategy="balanced")

print(f"计划ID: {plan['plan_id']}")
print(f"优先级: {plan['priority']}")
print(f"预计时长: {plan['timeline']['estimated_duration']}")

for task in plan['tasks']:
    print(f"- {task['description']} ({task['type']})")
```

### JavaScript

```javascript
const plan = await client.plan('my-awesome-skill', 'balanced');

console.log(`计划ID: ${plan.plan_id}`);
console.log(`优先级: ${plan.priority}`);

plan.tasks.forEach(task => {
  console.log(`- ${task.description} (${task.type})`);
});
```

---

## 6. 执行技能进化

### Python

```python
# 试运行（不实际执行）
result = client.evolve(
    skill_id="my-awesome-skill",
    plan_id=plan['plan_id'],
    mode="dry_run"
)

print(f"模式: {result['mode']}")
print(f"完成任务: {result['results']['tasks_completed']}")

# 正式执行
result = client.evolve(
    skill_id="my-awesome-skill",
    plan_id=plan['plan_id'],
    mode="auto"  # 自动执行
)

print(f"新版本: {result['results']['new_version']}")
```

### JavaScript

```javascript
// 试运行
const dryRun = await client.evolve('my-awesome-skill', plan.plan_id, 'dry_run');
console.log(`试运行完成: ${dryRun.results.tasks_completed} 个任务`);

// 正式执行
const result = await client.evolve('my-awesome-skill', plan.plan_id, 'auto');
console.log(`新版本: ${result.results.new_version}`);
```

---

## 7. 技能间同步

### Python

```python
# 让多个技能相互学习
result = client.sync(
    skill_ids=["skill-a", "skill-b", "skill-c"],
    source_skill="skill-a"  # 可选：指定源技能
)

print(f"发现模式: {result['patterns_discovered']}")
print(f"应用模式: {result['patterns_applied']}")

# 查看各技能的改进
for skill, improvement in result['improvements'].items():
    print(f"{skill}: 健康度 +{improvement['health_delta']}")
```

### JavaScript

```javascript
const result = await client.sync(['skill-a', 'skill-b', 'skill-c']);

console.log(`发现模式: ${result.patterns_discovered}`);
console.log(`应用模式: ${result.patterns_applied}`);

Object.entries(result.improvements).forEach(([skill, imp]) => {
  console.log(`${skill}: 健康度 +${imp.health_delta}`);
});
```

---

## 8. 获取引擎状态

### Python

```python
status = client.status()

print(f"引擎版本: {status['engine']['version']}")
print(f"注册技能: {status['skills']['registered']}")
print(f"活跃技能: {status['skills']['active']}")

# 查看平台连接状态
for platform, state in status['platforms'].items():
    print(f"{platform}: {state}")
```

### JavaScript

```javascript
const status = await client.status();

console.log(`引擎版本: ${status.engine.version}`);
console.log(`注册技能: ${status.skills.registered}`);

Object.entries(status.platforms).forEach(([platform, state]) => {
  console.log(`${platform}: ${state}`);
});
```

---

## 9. 完整示例

### Python

```python
from sse_sdk import SSEClient

# 初始化
client = SSEClient(api_key="your_key")

# 1. 追踪使用
client.track("my-skill", {
    "duration_ms": 1000,
    "success": True
})

# 2. 分析性能
analysis = client.analyze("my-skill")

# 3. 如果健康度低于70，生成进化计划
if analysis['summary']['health_score'] < 70:
    plan = client.plan("my-skill")
    
    # 4. 执行进化
    result = client.evolve("my-skill", plan['plan_id'], mode="auto")
    
    print(f"✅ 进化完成！新版本: {result['results']['new_version']}")

# 5. 与其他技能同步
client.sync(["my-skill", "related-skill-1", "related-skill-2"])
```

---

## 10. 错误处理

### Python

```python
from sse_sdk import SSEError, AuthenticationError, RateLimitError

try:
    result = client.track("my-skill", {"duration_ms": 1000})
except AuthenticationError:
    print("❌ API密钥无效")
except RateLimitError:
    print("⏳ 请求太频繁，请稍后再试")
except SSEError as e:
    print(f"❌ 错误: {e}")
```

### JavaScript

```javascript
import { SSEError, SSEAuthenticationError, SSERateLimitError } from 'sse-sdk';

try {
  const result = await client.track('my-skill', { durationMs: 1000 });
} catch (error) {
  if (error instanceof SSEAuthenticationError) {
    console.error('❌ API密钥无效');
  } else if (error instanceof SSERateLimitError) {
    console.error('⏳ 请求太频繁');
  } else {
    console.error(`❌ 错误: ${error.message}`);
  }
}
```

---

## 📚 更多资源

- [完整API文档](./API-Reference.md)
- [SEP协议规范](./SEP-v2.0-Specification.md)
- [示例项目](../examples/)
- [GitHub仓库](https://github.com/zhang-lawyer-org/skill-evolution-system)

---

**让技能越用越聪明！** 🧬✨
