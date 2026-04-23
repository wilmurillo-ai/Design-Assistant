# 轨迹优化技巧

## 为什么需要模拟人类轨迹？

网站会分析鼠标移动的特征来识别机器人：

| 特征 | 机器人行为 | 人类行为 |
|------|------------|----------|
| 移动速度 | 匀速 | 变速（先快后慢） |
| 轨迹形状 | 直线 | 微小抖动/曲线 |
| 加速度 | 瞬间加速 | 平滑加减速 |
| 停顿 | 无 | 启动前、中间、结束后都有 |
| 回退 | 无 | 偶尔犹豫回退 |

## 人类拖动特征分析

### 1. 时间特征

```
启动停顿：0.1-0.3 秒
拖动过程：1.0-2.0 秒
结束微调：0.1-0.2 秒
总时长：1.2-2.5 秒
```

### 2. 速度曲线

```
速度
  ↑
  │     ╱│╲
  │    ╱ │ ╲
  │   ╱  │  ╲
  │  ╱   │   ╲
  │ ╱    │    ╲
  └─────────────→ 时间
   启动  中间  结束
```

**特点：**
- 启动阶段：缓慢加速（0.2-0.3 秒）
- 中间阶段：较快移动（0.8-1.2 秒）
- 结束阶段：减速并微调（0.2-0.3 秒）

### 3. 轨迹抖动

- 垂直方向：±2-5 像素（正态分布）
- 水平方向：偶尔回退 1-3 像素（5% 概率）

## Python 实现

### 基础版本

```python
import math
import random

def generate_trajectory(offset: int, duration: float = 1.5) -> list:
    """
    生成模拟人类拖动轨迹
    
    Args:
        offset: 目标移动距离（像素）
        duration: 拖动时长（秒）
    
    Returns:
        list: 轨迹点 [[x1,y1], [x2,y2], ...]
    """
    trajectory = []
    steps = int(duration * 60)  # 60 FPS
    
    for i in range(steps + 1):
        t = i / steps
        
        # 缓动函数：ease-out cubic（先快后慢）
        progress = 1 - math.pow(1 - t, 3)
        
        # 基础位置
        x = int(offset * progress)
        
        # 垂直抖动（正态分布）
        y = int(random.gauss(0, 2))
        
        trajectory.append([x, y])
    
    return trajectory
```

### 高级版本（带停顿和回退）

```python
def generate_advanced_trajectory(offset: int, duration: float = 1.5) -> list:
    """
    高级人类轨迹模拟
    
    特征：
    - 启动前停顿 0.1-0.3 秒
    - 先快后慢（ease-out）
    - 垂直抖动 ±2-5 像素
    - 随机回退 1-3 像素（5% 概率）
    - 到达后微调
    """
    trajectory = []
    steps = int(duration * 60)
    
    # === 阶段 1：启动前停顿 ===
    pause_duration = random.uniform(0.1, 0.3)
    pause_frames = int(pause_duration * 60)
    
    for _ in range(pause_frames):
        trajectory.append([0, int(random.gauss(0, 1))])
    
    # === 阶段 2：主拖动 ===
    for i in range(steps + 1):
        t = i / steps
        
        # ease-out cubic
        progress = 1 - math.pow(1 - t, 3)
        target_x = int(offset * progress)
        
        # 随机回退（模拟犹豫）
        if random.random() < 0.05 and 0.3 < t < 0.8:
            target_x = max(0, target_x - random.randint(1, 3))
        
        trajectory.append([target_x, int(random.gauss(0, 2))])
    
    # === 阶段 3：到达后微调 ===
    for _ in range(5):
        trajectory.append([
            offset + random.randint(-1, 1),
            int(random.gauss(0, 1))
        ])
    
    return trajectory
```

### 专业版本（带速度分析）

```python
def generate_professional_trajectory(offset: int) -> list:
    """
    专业级人类轨迹模拟
    
    基于真实人类拖动数据建模
    """
    trajectory = []
    
    # 阶段 1：启动停顿（0.2 秒）
    for _ in range(12):
        trajectory.append([0, int(random.gauss(0, 0.5))])
    
    # 阶段 2：加速（0.3 秒，移动到 30% 位置）
    for i in range(18):
        t = i / 18
        progress = t * t * (3 - 2*t)  # smoothstep
        x = int(offset * 0.3 * progress)
        y = int(random.gauss(0, 1.5))
        trajectory.append([x, y])
    
    # 阶段 3：匀速（0.6 秒，移动到 80% 位置）
    for i in range(36):
        t = i / 36
        x = int(offset * (0.3 + 0.5 * t))
        y = int(random.gauss(0, 2))
        
        # 5% 概率回退
        if random.random() < 0.05:
            x -= random.randint(1, 2)
        
        trajectory.append([x, y])
    
    # 阶段 4：减速（0.3 秒，移动到 100% 位置）
    for i in range(18):
        t = i / 18
        progress = 1 - math.pow(1 - t, 3)
        x = int(offset * (0.8 + 0.2 * progress))
        y = int(random.gauss(0, 1.5))
        trajectory.append([x, y])
    
    # 阶段 5：微调（0.1 秒）
    for _ in range(6):
        trajectory.append([
            offset + random.randint(-1, 1),
            int(random.gauss(0, 0.5))
        ])
    
    return trajectory
```

## 缓动函数对比

### 1. Linear（线性）

```python
def linear(t):
    return t
```
**特点：** 匀速，容易被检测

### 2. Ease-in（加速）

```python
def ease_in(t):
    return t * t
```
**特点：** 先慢后快

### 3. Ease-out（减速）⭐推荐

```python
def ease_out(t):
    return 1 - math.pow(1 - t, 3)
```
**特点：** 先快后慢，最接近人类行为

### 4. Ease-in-out（先加速后减速）

```python
def ease_in_out(t):
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - math.pow(-2*t + 2, 3) / 2
```
**特点：** 对称加减速

### 5. Smoothstep

```python
def smoothstep(t):
    return t * t * (3 - 2*t)
```
**特点：** 平滑过渡

## Playwright 实现

```javascript
async function dragWithHumanTrajectory(slider, offset) {
    const trajectory = generateTrajectory(offset);
    
    // 获取滑块位置
    const box = await slider.boundingBox();
    const startX = box.x + box.width / 2;
    const startY = box.y + box.height / 2;
    
    // 移动到滑块
    await page.mouse.move(startX, startY);
    await sleep(100);
    
    // 按下鼠标
    await page.mouse.down();
    await sleep(50);
    
    // 按轨迹移动
    for (const [dx, dy] of trajectory) {
        await page.mouse.move(startX + dx, startY + dy);
        await sleep(16); // 60 FPS
    }
    
    // 停顿后释放
    await sleep(100);
    await page.mouse.up();
}

function generateTrajectory(offset) {
    const trajectory = [];
    const steps = 90; // 1.5 秒 * 60 FPS
    
    for (let i = 0; i <= steps; i++) {
        const t = i / steps;
        
        // ease-out cubic
        const progress = 1 - Math.pow(1 - t, 3);
        const x = Math.floor(offset * progress);
        
        // 垂直抖动
        const y = Math.floor(gaussianRandom() * 2);
        
        trajectory.push([x, y]);
    }
    
    return trajectory;
}

// Box-Muller 变换生成正态分布随机数
function gaussianRandom() {
    let u = 0, v = 0;
    while(u === 0) u = Math.random();
    while(v === 0) v = Math.random();
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
```

## 检测规避技巧

### 1. 速度变化检测

**网站检测：** 检查速度是否恒定

**规避方法：**
```python
# 使用缓动函数，确保速度变化
progress = 1 - math.pow(1 - t, 3)  # 速度从快到慢
```

### 2. 轨迹直线检测

**网站检测：** 检查轨迹是否是完美直线

**规避方法：**
```python
# 添加垂直抖动
y = int(random.gauss(0, 2))  # 正态分布抖动
```

### 3. 加速度检测

**网站检测：** 检查是否有瞬间加速

**规避方法：**
```python
# 添加启动停顿
for _ in range(12):  # 0.2 秒
    trajectory.append([0, 0])
```

### 4. 事件完整性检测

**网站检测：** 检查 mouse 事件序列

**规避方法：**
```javascript
// 确保完整的事件序列
await mouse.move(startX, startY);  // 移动到起点
await sleep(100);                   // 停顿
await mouse.down();                 // 按下
await sleep(50);                    // 停顿
// ... 移动 ...
await mouse.up();                   // 释放
```

## 调试技巧

### 1. 可视化轨迹

```python
import matplotlib.pyplot as plt

def visualize_trajectory(trajectory):
    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    
    plt.figure(figsize=(12, 4))
    
    # 轨迹图
    plt.subplot(1, 2, 1)
    plt.plot(xs, ys, 'b-', linewidth=0.5)
    plt.scatter(xs[0], ys[0], c='green', s=100, label='Start', zorder=5)
    plt.scatter(xs[-1], ys[-1], c='red', s=100, label='End', zorder=5)
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.title('Drag Trajectory')
    
    # 速度图
    plt.subplot(1, 2, 2)
    speeds = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
    plt.plot(speeds, 'g-', linewidth=0.5)
    plt.xlabel('Frame')
    plt.ylabel('Speed (pixels/frame)')
    plt.title('Speed Profile')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('trajectory_analysis.png', dpi=150)
    plt.show()
```

### 2. 分析轨迹特征

```python
def analyze_trajectory(trajectory):
    """分析轨迹特征"""
    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    
    # 计算速度
    speeds = [xs[i+1] - xs[i] for i in range(len(xs)-1)]
    
    # 计算加速度
    accelerations = [speeds[i+1] - speeds[i] for i in range(len(speeds)-1)]
    
    # 计算抖动
    y_variance = np.var(ys)
    
    # 检查回退
    backward_count = sum(1 for s in speeds if s < 0)
    
    return {
        "total_frames": len(trajectory),
        "total_distance": xs[-1],
        "avg_speed": np.mean(speeds),
        "max_speed": np.max(speeds),
        "speed_variance": np.var(speeds),
        "avg_acceleration": np.mean(accelerations),
        "y_variance": y_variance,
        "backward_count": backward_count,
        "duration_seconds": len(trajectory) / 60
    }
```

### 3. 录制视频调试

```bash
# 使用 headed 模式（可视化浏览器）
agent-browser --headed open https://example.com

# 录制视频
agent-browser record start debug.webm

# ... 执行拖动 ...

# 停止录制
agent-browser record stop
```

## 最佳实践总结

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 总时长 | 1.2-2.0 秒 | 不要太快或太慢 |
| FPS | 60 | 每帧 16ms |
| 启动停顿 | 0.1-0.3 秒 | 模拟思考 |
| 垂直抖动 | ±2-5 像素 | 正态分布 |
| 回退概率 | 3-8% | 模拟犹豫 |
| 回退距离 | 1-3 像素 | 小幅回退 |
| 结束微调 | 3-6 帧 | 精确定位 |
