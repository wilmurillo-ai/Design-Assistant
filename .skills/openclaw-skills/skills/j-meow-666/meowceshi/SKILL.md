---
name: openclaw-manager
description: 企业级多租户OpenClaw管理工具；当用户需要创建新租户实例、查看所有租户状态或删除租户时使用
dependency:
  python:
    - docker>=6.1.0
    - pyyaml>=6.0
---

# OpenClaw 多租户管理工具

## 任务目标
- 本 Skill 用于：在单台物理服务器上管理多个 OpenClaw 租户实例
- 能力包含：一键创建租户、实例状态监控、完全数据隔离、GPU资源共享
- 触发条件：用户需要创建新租户、查看租户列表、删除租户、或管理多租户环境

## 前置准备
- 依赖说明：scripts 脚本所需的依赖包及版本
  ```
  docker>=6.1.0
  pyyaml>=6.0
  ```
- 系统要求：
  - Docker 和 docker-compose 已安装
  - NVIDIA Container Toolkit 已配置（用于 GPU 支持）
  - 基础目录结构：`/DATA/disk2/apps/openclaw-platform/`

## 操作步骤

### 标准流程

1. **创建新租户实例**
   - 调用 `scripts/create_tenant.py` 处理：
     - 用户名：`--username <tenant_name>`
     - GPU 配置：`--gpu-count <数量>` 或 `--gpu-memory <显存MB>`
     - 端口：自动分配（默认从 3001 开始）
   - 脚本自动完成：
     - 创建用户数据目录和配置目录
     - 生成 docker-compose.yml
     - 启动独立容器
     - 配置环境变量隔离
     - 设置 GPU 资源分配

2. **查看所有租户状态**
   - 调用 `scripts/list_tenants.py` 获取：
     - 租户列表及端口映射
     - 容器运行状态（CPU/内存/GPU 占用）
     - 数据存储位置
   - 智能体根据返回结果生成可视化状态报告

3. **删除租户实例**
   - 调用 `scripts/terminate_tenant.py` 处理：
     - 用户名：`--username <tenant_name>`
     - 清理选项：`--purge-all`（强制删除所有数据）
   - 脚本自动完成：
     - 停止并删除容器
     - 删除数据目录和配置目录
     - 释放端口资源
     - 清理日志文件

4. **用户级配置隔离**（创建后步骤）
   - 智能体指导用户进入各自容器执行：
     ```bash
     docker exec -it openclaw-<username> openclaw auth login
     ```
   - 各租户的飞书/钉钉 Key 存储在独立容器卷中

### 可选分支

- 当 **需要 GPU 优化配置**：创建时使用 `--gpu-memory` 参数精确分配显存
- 当 **需要反向代理**：参考 [references/architecture.md](references/architecture.md) 配置 Nginx
- 当 **需要 MCP 插件隔离**：参考 [references/mcp-guide.md](references/mcp-guide.md) 设置私有插件目录

## 资源索引

- 必要脚本：
  - [scripts/create_tenant.py](scripts/create_tenant.py)（用途：创建新租户实例，参数：username, gpu-count, gpu-memory）
  - [scripts/list_tenants.py](scripts/list_tenants.py)（用途：列出所有租户及状态，参数：无）
  - [scripts/terminate_tenant.py](scripts/terminate_tenant.py)（用途：删除租户实例，参数：username, purge-all）
- 领域参考：
  - [references/architecture.md](references/architecture.md)（何时读取：需要了解存储架构、网络规划、端口映射表时）
  - [references/mcp-guide.md](references/mcp-guide.md)（何时读取：需要配置 MCP 插件隔离时）

## 注意事项

- 端口自动分配从 3001 开始，脚本会检测已占用端口避免冲突
- GPU 资源默认共享，可通过参数配置显存切分
- 所有敏感信息（API Key）必须脱敏处理
- 删除租户操作不可逆，建议先备份再删除
- 零信任安全原则：禁止跨容器访问

## 使用示例

### 示例 1：创建新租户
```bash
# 创建租户 user1，分配 1 个 GPU
python scripts/create_tenant.py --username user1 --gpu-count 1

# 创建租户 user2，分配 8GB 显存
python scripts/create_tenant.py --username user2 --gpu-memory 8192
```

### 示例 2：查看租户状态
```bash
python scripts/list_tenants.py
```

### 示例 3：删除租户
```bash
# 停止并删除租户（保留数据）
python scripts/terminate_tenant.py --username user1

# 强制删除所有数据
python scripts/terminate_tenant.py --username user1 --purge-all
```
