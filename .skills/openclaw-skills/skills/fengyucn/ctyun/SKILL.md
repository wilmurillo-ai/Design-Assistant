---
name: ctyun-cli
description: "天翼云CLI工具 - 企业级命令行工具，帮助您轻松管理天翼云资源。支持ECS、VPC、EBS、ELB、CCE、Redis、监控、账务等11大服务模块，覆盖217+个API，210+个命令。"
homepage: https://github.com/fengyucn/ctyun-cli
pypi: https://pypi.org/project/ctyun-cli/
metadata: {"clawdbot":{"emoji":"☁️","requires":{"bins":["ctyun-cli"]},"install":[{"id":"pip","kind":"pip","package":"ctyun-cli","bins":["ctyun-cli"],"label":"Install ctyun-cli (pip)"}]}}
---

# 天翼云 CLI (ctyun-cli)

天翼云 CLI 工具，功能强大的企业级命令行工具，帮助您轻松管理天翼云资源。支持云服务器(ECS)、监控告警、安全防护、Redis分布式缓存、弹性负载均衡(ELB)、容器引擎(CCE)、VPC网络、费用查询等核心功能。

**规模统计：** 35,000+行代码，217+个API，210+个命令，11大服务模块

## 安装

### 使用 pip 安装（推荐）
```bash
pip install ctyun-cli
```

### 使用 pipx 安装（隔离环境）
```bash
pipx install ctyun-cli
```

### 从源码安装
```bash
git clone https://github.com/fengyucn/ctyun-cli.git
cd ctyun-cli
pip install -e .
```

### 验证安装
```bash
ctyun-cli --version
ctyun-cli --help
```

## 配置与认证

### 方式一：环境变量（推荐，更安全）
```bash
export CTYUN_ACCESS_KEY=your_access_key
export CTYUN_SECRET_KEY=your_secret_key
```

将上述命令添加到 `~/.bashrc` 或 `~/.zshrc` 以实现永久配置。

### 方式二：交互式配置
```bash
ctyun-cli configure --access-key YOUR_ACCESS_KEY --secret-key YOUR_SECRET_KEY --region cn-north-1
```

### 查看当前配置
```bash
ctyun-cli show-config
```

### 列出所有配置文件
```bash
ctyun-cli list-profiles
```

### 测试 API 连接
```bash
ctyun-cli test
```

## 全局选项

所有命令都支持以下全局选项：
- `--profile TEXT`: 指定配置文件名称
- `--access-key TEXT`: 访问密钥
- `--secret-key TEXT`: 密钥
- `--region TEXT`: 区域
- `--endpoint TEXT`: API 端点
- `--output [table|json|yaml]`: 输出格式（默认 table）
- `--debug`: 启用调试模式

## 云服务器 (ECS) 管理

### 列出云主机实例
```bash
ctyun-cli ecs list
ctyun-cli ecs list --region cn-north-1 --output json
```

### 查询云主机详情
```bash
ctyun-cli ecs detail --instance-id YOUR_INSTANCE_ID
```

### 查询多台云主机详细信息
```bash
ctyun-cli ecs multidetail --instance-ids ID1,ID2,ID3
```

### 查询云主机统计信息
```bash
ctyun-cli ecs statistics
```

### 查询资源池列表
```bash
ctyun-cli ecs regions
```

### 订单询价
```bash
ctyun-cli ecs query-price --flavor-id FLAVOR_ID --quantity 1
```

## 虚拟私有云 (VPC) 管理

### 列出 VPC
```bash
ctyun-cli vpc list
ctyun-cli vpc new-list
```

### 查询 VPC 详情
```bash
ctyun-cli vpc show --vpc-id YOUR_VPC_ID
```

### 子网查询
```bash
ctyun-cli vpc subnet --vpc-id YOUR_VPC_ID
```

### 安全组查询
```bash
ctyun-cli vpc security --vpc-id YOUR_VPC_ID
```

### 路由表查询
```bash
ctyun-cli vpc route-table --vpc-id YOUR_VPC_ID
```

### 弹性公网 IP 查询
```bash
ctyun-cli vpc eip
```

### NAT 网关查询
```bash
ctyun-cli vpc nat-gateway
```

### VPC 对等连接查询
```bash
ctyun-cli vpc peering
```

### 流日志查询
```bash
ctyun-cli vpc flow-log
```

## 云硬盘 (EBS) 管理

### 列出云硬盘
```bash
ctyun-cli ebs list
ctyun-cli ebs list --region cn-north-1 --output json
```

## 弹性负载均衡 (ELB) 管理

### 负载均衡器管理
```bash
ctyun-cli elb loadbalancer --help
ctyun-cli elb loadbalancer list
```

### 监听器管理
```bash
ctyun-cli elb listener --help
```

### 目标组管理
```bash
ctyun-cli elb targetgroup --help
```

### 健康检查管理
```bash
ctyun-cli elb health-check --help
```

### 监控数据管理
```bash
ctyun-cli elb monitor --help
```

## 容器引擎 (CCE) 管理

### 列出集群
```bash
ctyun-cli cce list-clusters
```

### 查询集群详情
```bash
ctyun-cli cce describe-cluster --cluster-id YOUR_CLUSTER_ID
```

### 获取 Kubeconfig
```bash
ctyun-cli cce get-kubeconfig --cluster-id YOUR_CLUSTER_ID
```

### 列出节点
```bash
ctyun-cli cce list-nodes --cluster-id YOUR_CLUSTER_ID
```

### 查询节点详情
```bash
ctyun-cli cce get-node-detail --cluster-id CLUSTER_ID --node-id NODE_ID
```

### 列出 Pod
```bash
ctyun-cli cce list-pods --cluster-id CLUSTER_ID
```

### 列出 Deployment
```bash
ctyun-cli cce list-deployments --cluster-id CLUSTER_ID
```

### 列出 Service
```bash
ctyun-cli cce list-services --cluster-id CLUSTER_ID
```

### 集群日志管理
```bash
ctyun-cli cce logs --help
```

### 节点池管理
```bash
ctyun-cli cce nodepool --help
```

### 弹性伸缩管理
```bash
ctyun-cli cce autoscaling --help
```

### ConfigMap 管理
```bash
ctyun-cli cce configmap --help
```

### 标签管理
```bash
ctyun-cli cce tag --help
```

## Redis 分布式缓存服务

### 列出 Redis 实例
```bash
ctyun-cli redis list
```

### 查询实例详情
```bash
ctyun-cli redis describe --instance-id YOUR_INSTANCE_ID
```

### 创建 Redis 实例
```bash
ctyun-cli redis create-instance --help
```

### 查询可用区
```bash
ctyun-cli redis zones
```

### 监控数据查询
```bash
ctyun-cli redis monitor-history --instance-id INSTANCE_ID
```

### 诊断服务
```bash
ctyun-cli redis diagnose --instance-id INSTANCE_ID
```

### 客户端连接管理
```bash
ctyun-cli redis clients --instance-id INSTANCE_ID
```

## 云监控服务管理

### 查询监控数据
```bash
ctyun-cli monitor list
```

### 查询告警规则
```bash
ctyun-cli monitor query-alarm-rules
```

### 查询告警历史
```bash
ctyun-cli monitor query-alert-history
```

### 查询资源组
```bash
ctyun-cli monitor query-resource-groups
```

### 自定义监控指标查询
```bash
ctyun-cli monitor query-custom-trend
```

### CPU Top 排名
```bash
ctyun-cli monitor cpu-top
```

### 内存 Top 排名
```bash
ctyun-cli monitor mem-top
```

### 磁盘 Top 排名
```bash
ctyun-cli monitor disk-top
```

## 账务中心管理

### 查询账户余额
```bash
ctyun-cli billing balance
```

### 查询欠费信息
```bash
ctyun-cli billing arrears
```

### 查询账户账单
```bash
ctyun-cli billing account-bill --bill-cycle 202503
```

### 查询消费类型汇总
```bash
ctyun-cli billing bill-summary --bill-cycle 202503
```

### 查询按需流水账单
```bash
ctyun-cli billing ondemand-flow --bill-cycle 202503
```

### 查询包周期流水账单
```bash
ctyun-cli billing cycle-flow --bill-cycle 202503
```

### 查询消费明细
```bash
ctyun-cli billing consumption
```

## 统一身份认证 (IAM) 管理

### 查询企业项目列表
```bash
ctyun-cli iam list-projects
```

### 查询企业项目详情
```bash
ctyun-cli iam get-project --project-id PROJECT_ID
```

### 分页查询资源信息
```bash
ctyun-cli iam list-resources
```

## 服务器安全卫士

### 查看使用示例
```bash
ctyun-cli security examples
```

### 主机防护
```bash
ctyun-cli security wrapper --help
```

### 防篡改更新
```bash
ctyun-cli security tamper-update --help
```

## 云专线 (CDA) 管理

### 物理专线管理
```bash
ctyun-cli cda physical-line --help
```

### 专线网关管理
```bash
ctyun-cli cda gateway --help
```

### VPC 管理
```bash
ctyun-cli cda vpc --help
```

### BGP 路由管理
```bash
ctyun-cli cda bgp-route --help
```

### 静态路由管理
```bash
ctyun-cli cda static-route --help
```

### 健康检查和链路探测管理
```bash
ctyun-cli cda health-check --help
```

### 跨账号授权管理
```bash
ctyun-cli cda account-auth --help
```

## 网络管理

```bash
ctyun-cli network --help
```

## 存储管理

```bash
ctyun-cli storage --help
```

## 缓存管理

### 清空所有缓存
```bash
ctyun-cli clear-cache
```

## 使用技巧

### JSON 输出便于脚本处理
```bash
ctyun-cli ecs list --output json | jq '.[] | select(.status=="running")'
```

### YAML 输出便于阅读
```bash
ctyun-cli vpc show --vpc-id vpc-xxx --output yaml
```

### 调试模式排查问题
```bash
ctyun-cli ecs list --debug
```

### 使用指定配置文件
```bash
ctyun-cli ecs list --profile production
```

## 注意事项

1. 首次使用前必须先配置认证信息（推荐使用环境变量方式）
2. 大部分命令需要指定资源 ID（如 instance-id、vpc-id 等）
3. 建议使用 `--help` 查看具体子命令的详细参数
4. 使用 JSON 输出格式便于与其他工具集成
5. 按需查询大量数据时建议分页或使用过滤参数

## 相关链接

- **PyPI 包**: https://pypi.org/project/ctyun-cli/
- **GitHub 仓库**: https://github.com/fengyucn/ctyun-cli
- **问题反馈**: https://github.com/fengyucn/ctyun-cli/issues
- **作者邮箱**: popfrog@gmail.com

## 版本信息

- **当前版本**: v1.7.16
- **开源协议**: MIT
- **Python 要求**: Python 3.8+
- **API 覆盖**: 217+ 个 API
- **命令数量**: 210+ 个命令
