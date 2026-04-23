# SCNet 作业监控方案

## 方案概述

为 SCNet 超算平台设计一个可靠的作业监控方案，支持：
- 实时监控作业状态变化
- 自动切换实时/历史作业查询
- 作业结束时主动通知
- 适用于几小时到几天的长时间运行作业

---

## 核心设计

### 1. 双模式查询

| 模式 | 接口 | 适用场景 | 说明 |
|------|------|----------|------|
| **实时查询** | `/hpc/openapi/v2/jobs/{jobId}` | 作业运行中 | 快速响应，秒级查询 |
| **历史查询** | `/hpc/openapi/v2/historyjobs` | 作业结束后5分钟+ | 归档数据，可查询已完成作业 |

**自动切换逻辑：**
1. 优先查询实时接口
2. 实时接口返回空时，自动切换到历史接口
3. 检测到归档后，增加查询频率（30秒）

### 2. 状态机管理

```
排队中(statQ) → 等待中(statW) → 运行中(statR)
                        ↓
              ┌──────────────────┐
              ↓                  ↓
        完成(statC)      终止(statT/其他)
```

**活跃状态：** statR(运行中)、statQ(排队中)、statW(等待中)
**结束状态：** statC(完成)、statT(终止)、statE(退出)、statDE(删除)、statX(其他)、statH(保留)、statS(挂起)

### 3. 监控流程

```
开始监控
    ↓
验证作业存在
    ↓
检查当前状态
    ↓
如果已结束 → 立即回调
    ↓
如果运行中 → 启动监控线程
    ↓
循环检查（每60秒）
    ↓
状态变化？→ 触发回调
    ↓
非活跃状态？→ 完成回调，结束监控
```

---

## 使用方法

### 基础使用

```python
from scnet_chat import SCNetClient
from job_monitor import JobMonitor
import config_manager

# 初始化客户端
config = config_manager.load_config()
client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
client.init_tokens()

# 创建监控器
monitor = JobMonitor(client)

# 定义回调函数
def on_status_change(info):
    print(f"状态变化: {info['status_name']}")

def on_completed(info):
    print(f"作业完成: {info['final_status']}")
    # 这里可以发送邮件、短信、Webhook通知

# 开始监控
monitor.start_monitoring(
    job_id="110230634",
    on_status_change=on_status_change,
    on_completed=on_completed,
    check_interval=60  # 每60秒检查一次
)
```

### 提交作业并监控

```python
# 提交作业
job_config = {
    'job_name': 'my_long_job',
    'cmd': 'python train.py',
    'nnodes': '2',
    'ppn': '8',
    'queue': 'comp',
    'wall_time': '48:00:00',  # 48小时
    'work_dir': '/public/home/ac1npa3sf2/my_project/'
}

result = client.submit_job(job_config)
job_id = result.get('data')

# 立即开始监控
monitor.start_monitoring(
    job_id=job_id,
    on_status_change=on_status_change,
    on_completed=on_completed,
    check_interval=300  # 长作业用5分钟间隔
)

# 监控会在作业完成后自动结束
```

---

## 配置建议

### 检查间隔配置

| 作业类型 | 预计时长 | 建议间隔 | 说明 |
|----------|----------|----------|------|
| 短作业 | < 1小时 | 60秒 | 快速响应 |
| 中作业 | 1-24小时 | 300秒 (5分钟) | 平衡资源 |
| 长作业 | > 24小时 | 600秒 (10分钟) | 节省资源 |

### 通知方式集成

```python
import requests

def send_webhook_notification(info):
    """Webhook通知示例"""
    webhook_url = "https://your-webhook-url.com/notify"
    payload = {
        "job_id": info["job_id"],
        "status": info["status_name"],
        "timestamp": info["timestamp"]
    }
    requests.post(webhook_url, json=payload)

def send_email_notification(info):
    """邮件通知示例"""
    import smtplib
    from email.mime.text import MIMEText
    # ... 邮件发送代码
```

---

## 可靠性保障

### 1. 异常处理

```python
try:
    result = query_job_detail(...)
except Exception as e:
    # 网络异常时等待后重试
    time.sleep(check_interval)
    continue
```

### 2. 线程安全

- 每个作业独立监控线程
- 使用 `stop_flags` 安全停止
- `daemon=True` 防止阻塞退出

### 3. 资源管理

- 作业完成后自动清理线程
- 支持手动停止指定作业
- 支持停止所有监控

---

## 测试验证

### 测试1: 已存在作业查询

```bash
cd ~/.openclaw/skills/scnet-chat
python3 -c "
from scripts.job_monitor import JobMonitor
from scnet_chat import SCNetClient
import config_manager

config = config_manager.load_config()
client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
client.init_tokens()

monitor = JobMonitor(client)
status, data, source = monitor._get_job_status('110230634')
print(f'状态: {status}, 来源: {source}')
"
```

### 测试2: 归档检测

```bash
python3 -c "
from scripts.job_monitor import JobMonitor
# ... 同上

# 测试实时查询
realtime = monitor._query_realtime_job('110230634')
print(f'实时查询: {realtime is not None}')

# 测试历史查询
history = monitor._query_history_job('110230634')
print(f'历史查询: {history is not None}')
"
```

### 测试3: 新作业监控

```bash
python3 scripts/job_monitor.py
# 选择 test_monitor_new_job() 测试
```

---

## 常见问题

### Q1: 作业ID不存在怎么办？

A: `start_monitoring()` 会先验证作业存在性，不存在则返回 False 并打印错误。

### Q2: 监控过程中网络断开？

A: 监控器会捕获异常，等待后重试，不会丢失监控状态。

### Q3: 如何监控多个作业？

A: 创建同一个监控器实例，多次调用 `start_monitoring()`，每个作业独立线程。

### Q4: 作业归档后还能监控吗？

A: 可以，监控器会自动切换到历史查询模式，继续监控直到确认结束状态。

### Q5: 如何避免重复通知？

A: 监控器内部维护 `last_status`，只有状态变化时才触发回调。

---

## 文件位置

- **监控器代码**: `~/.openclaw/workspace/skills/scnet-chat/scripts/job_monitor.py`
- **核心接口**: `~/.openclaw/workspace/skills/scnet-chat/scripts/scnet_chat.py`
  - `query_job_detail()` - 实时作业查询
  - `query_history_jobs()` - 历史作业查询

---

## 总结

本方案特点：
1. **智能切换** - 自动识别实时/历史查询
2. **低资源** - 单线程轮询，可配置间隔
3. **高可靠** - 异常恢复、网络重试
4. **易扩展** - 回调函数支持多种通知方式

适用于生产环境长时间作业监控。
