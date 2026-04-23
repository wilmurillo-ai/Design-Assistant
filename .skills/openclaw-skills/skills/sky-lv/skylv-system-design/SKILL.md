---
name: system-design
slug: skylv-system-design
version: 2.0.4
description: System design architect. 20+ classic architecture patterns (e-commerce/social/live streaming/payments) with diagrams and scalability guides. Triggers: system design, architecture, scalable system.
author: SKY-lv
license: MIT
tags: [system-design, architecture, distributed, scalable, backend]
keywords: architecture, system-design, scalability, distributed
triggers: system design
---

# System Design — 系统设计架构师

## 功能说明

提供 20+ 种生产级系统架构设计模板，每个包含完整架构图、技术选型、扩展性设计和容量估算。不是泛泛而谈的理论，而是可直接参考的实战方案。

## 20+ 种经典架构模式

### 1. 电商系统架构 (E-commerce Platform)

```
┌─────────────────────────────────────────────────────────────┐
│                        CDN (CloudFlare)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Load Balancer (Nginx)                      │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ API Gateway  │ │ API Gateway  │ │ API Gateway  │
    │   (Kong)     │ │   (Kong)     │ │   (Kong)     │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  User Svc   │  │ Product Svc │  │  Order Svc  │
    │  (Node.js)  │  │   (Java)    │  │  (Go)       │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Redis      │  │  MongoDB    │  │  MySQL      │
    │  (Cache)    │  │  (Catalog)  │  │  (Orders)   │
    └─────────────┘  └─────────────┘  └──────┬──────┘
                                             │
                    ┌────────────────────────┼────────────────────┐
                    ▼                        ▼                    ▼
            ┌───────────────┐       ┌───────────────┐   ┌───────────────┐
            │  Payment Svc  │       │ Inventory Svc │   │ Shipping Svc  │
            │  (Stripe)     │       │   (Redis)     │   │   (3rd Party) │
            └───────────────┘       └───────────────┘   └───────────────┘
```

**技术选型：**
| 层级 | 技术 | 理由 |
|------|------|------|
| CDN | CloudFlare | 全球加速，DDoS 防护 |
| LB | Nginx | 高性能，支持 HTTPS 终止 |
| API Gateway | Kong | 插件生态，限流熔断 |
| 服务 | Node.js/Java/Go | 按场景选型 |
| 缓存 | Redis | 高并发读写 |
| 数据库 | MySQL/MongoDB | 事务/文档混合 |

**容量估算：**
- 日活用户：100 万
- QPS 峰值：10,000
- 数据库 QPS：5,000（读写分离）
- 缓存命中率：>90%

**关键设计：**
1. **读写分离** — 主从复制，读多写少场景
2. **缓存策略** — 多级缓存（CDN → Redis → 本地）
3. **分库分表** — 订单表按用户 ID 分片
4. **消息队列** — Kafka 异步解耦（订单创建→库存扣减→发货）
5. **熔断降级** — Hystrix/Sentinel 防止雪崩

### 2. 社交网络架构 (Social Network)

```
核心挑战：
- 海量读（信息流）
- 海量写（动态发布）
- 关系图（关注/粉丝）
- 实时通知

解决方案：
1. 信息流设计
   - 推模式 (Push)：大 V 发推→写入粉丝收件箱
   - 拉模式 (Pull)：用户刷新→聚合关注的人动态
   - 混合模式：大 V 用拉，普通用户用推

2. 关系图存储
   - Neo4j / JanusGraph（图数据库）
   - 或 MySQL 邻接表 + Redis 缓存

3. 通知系统
   - Kafka 事件驱动
   - WebSocket 实时推送
```

### 3. 直播平台架构 (Live Streaming)

```
核心挑战：
- 高带宽（视频流）
- 低延迟（<3 秒）
- 高并发（百万观众）
- 实时互动（弹幕/礼物）

解决方案：
1. 视频流
   - RTMP 推流 → HLS/DASH 分发
   - CDN 边缘节点缓存
   - 自适应码率（ABR）

2. 弹幕系统
   - WebSocket 长连接
   - 消息队列削峰
   - 分房间隔离

3. 礼物系统
   - Redis 原子操作（防超卖）
   - 异步写入数据库
   - 排行榜实时计算
```

### 4. 支付系统架构 (Payment Platform)

```
核心挑战：
- 数据一致性（资金安全）
- 幂等性（防止重复扣款）
- 对账（多方核对）
- 风控（欺诈检测）

解决方案：
1. 事务设计
   - 本地事务 + 消息队列最终一致性
   - TCC（Try-Confirm-Cancel）分布式事务
   - 状态机（PENDING→PROCESSING→SUCCESS/FAILED）

2. 幂等性
   - 唯一请求 ID
   - 数据库唯一索引
   - Redis 分布式锁

3. 对账系统
   - T+1 对账（次日核对）
   - 三方核对（银行/支付渠道/内部）
   - 差异自动处理 + 人工审核

4. 风控系统
   - 规则引擎（频率/金额/地点）
   - 机器学习模型（异常检测）
   - 实时拦截 + 事后追溯
```

### 5. 即时通讯架构 (Instant Messaging)

### 6. 推荐系统架构 (Recommendation Engine)

### 7. 搜索系统架构 (Search Engine)

### 8. 短链服务架构 (URL Shortener)

### 9. 评论系统架构 (Comment System)

### 10. 点赞计数架构 (Like/Counter System)

### 11. 分布式 ID 生成器 (Distributed ID Generator)

### 12. 配置中心架构 (Configuration Center)

### 13. 任务调度架构 (Distributed Scheduler)

### 14. 数据仓库架构 (Data Warehouse)

### 15. 实时数仓架构 (Real-time Data Warehouse)

### 16. A/B 测试平台架构 (A/B Testing Platform)

### 17. 用户画像架构 (User Profile System)

### 18. 广告系统架构 (Ad Platform)

### 19. O2O 调度架构 (On-demand Dispatch)

### 20. IoT 平台架构 (IoT Platform)

## 系统设计核心要素

### 1. 需求分析

```yaml
functional_requirements:
  - 用户能做什么（功能列表）
  - 核心业务流程

non_functional_requirements:
  - 性能：QPS、延迟、吞吐量
  - 可用性：99.9% / 99.99% / 99.999%
  - 扩展性：水平扩展能力
  - 一致性：强一致 / 最终一致
  - 安全性：认证、授权、加密

constraints:
  - 预算限制
  - 技术栈限制
  - 合规要求（GDPR/等保）
```

### 2. 容量估算

```yaml
估算方法:
  - DAU (日活用户)
  - 人均请求数
  - 峰值系数（通常 2-3 倍）
  
示例:
  DAU: 100 万
  人均请求：50 次/天
  总请求：5000 万/天
  平均 QPS: 5000 万 / 86400 ≈ 580
  峰值 QPS: 580 * 3 ≈ 1740
```

### 3. 数据模型设计

```yaml
数据库选型:
  - 关系型：MySQL/PostgreSQL（事务场景）
  - 文档型：MongoDB（灵活 schema）
  - 键值型：Redis（缓存/会话）
  - 列式：HBase/Cassandra（海量数据）
  - 图数据库：Neo4j（关系网络）

分库分表策略:
  - 水平分片：按用户 ID/地域/时间
  - 垂直拆分：按业务模块
  - 读写分离：主从复制
```

### 4. 扩展性设计

```yaml
水平扩展:
  - 无状态服务 → 负载均衡
  - 数据分片 → 一致性哈希
  - 消息队列 → 削峰填谷

垂直扩展:
  - 单机性能提升（CPU/内存/SSD）
  - 数据库索引优化
  - 缓存层加速
```

### 5. 高可用设计

```yaml
冗余:
  - 多副本（数据库主从/集群）
  - 多可用区（AZ）
  - 多地域（Region）

故障检测:
  - 心跳检测
  - 健康检查
  - 自动故障转移

降级熔断:
  - 限流（令牌桶/漏桶）
  - 熔断（失败阈值）
  - 降级（返回缓存/默认值）
```

## 系统设计面试框架

### 45 分钟面试流程

| 时间 | 环节 | 产出 |
|------|------|------|
| 0-5min | 需求澄清 | 功能列表 + 非功能需求 |
| 5-10min | 容量估算 | QPS、存储、带宽 |
| 10-25min | 高层设计 | 架构图 + 核心组件 |
| 25-40min | 详细设计 | 数据模型 + API 设计 |
| 40-45min | 总结优化 | 瓶颈分析 + 扩展方案 |

### 评估维度

1. **需求分析** — 能否准确识别核心需求
2. **架构设计** — 组件划分是否合理
3. **技术选型** — 技术是否匹配场景
4. **扩展性** — 是否考虑水平扩展
5. **权衡能力** — 能否分析 trade-off

## 工具函数

### architecture_template

```python
def architecture_template(system_type: str, scale: str) -> dict:
    """
    获取架构模板
    
    Args:
        system_type: 系统类型 (ecommerce/social/live/payment 等)
        scale: 规模 (small/medium/large)
    
    Returns:
        {
            "diagram": "架构图 ASCII/URL",
            "components": ["组件列表"],
            "tech_stack": {"layer": "technology"},
            "scaling": "扩展方案",
            "bottlenecks": ["潜在瓶颈"]
        }
    """
```

### capacity_planning

```python
def capacity_planning(dau: int, requests_per_user: int, peak_factor: float = 3.0) -> dict:
    """
    容量规划
    
    Args:
        dau: 日活用户数
        requests_per_user: 人均请求数
        peak_factor: 峰值系数
    
    Returns:
        {
            "total_requests": 50000000,
            "avg_qps": 580,
            "peak_qps": 1740,
            "servers_needed": 5,
            "database_tps": 500,
            "bandwidth_mbps": 100
        }
    """
```

### tech_stack_recommend

```python
def tech_stack_recommend(requirements: dict) -> dict:
    """
    技术栈推荐
    
    Args:
        requirements: 需求字典（QPS、一致性、延迟等）
    
    Returns:
        {
            "frontend": ["React", "Vue"],
            "backend": ["Node.js", "Go"],
            "database": ["MySQL", "Redis"],
            "message_queue": ["Kafka"],
            "cdn": ["CloudFlare"],
            "reasoning": "选型理由"
        }
    """
```

## 架构决策记录 (ADR)

每个重要决策应记录：

```markdown
# ADR-001: 数据库选型

## 背景
需要存储用户订单数据，要求：
- 事务支持（ACID）
- 高并发写入（5000 TPS）
- 水平扩展能力

## 决策
选择 MySQL + 分库分表方案

## 备选方案
- PostgreSQL：功能更强，但生态不如 MySQL
- MongoDB：不支持事务（当时）
- NewSQL：成本高，团队不熟悉

## 后果
- 需要实现分库分表中间件
- 跨分片查询复杂
- 但满足业务需求，团队熟悉
```

## 相关文件

- [awesome-system-design](https://github.com/donnemartin/system-design-primer)
- [System Design Interview](https://www.amazon.com/System-Design-Interview-insiders-Guide/dp/B08CMV2C28)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

## 触发词

- 自动：系统设计、架构设计、分布式、高并发、扩展性
- 手动：/system-design, /architecture, /scalable-design
- 短语：设计一个系统、架构方案、技术选型、容量估算

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
