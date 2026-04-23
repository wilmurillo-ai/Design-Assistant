# SCNet Chat Skill - Agent Development Guide

## Project Overview

SCNet Chat Skill (scnet-chat) is a Python-based automation skill for interacting with the **SCNet (国家超算互联网平台 - National Supercomputing Internet Platform)**. It enables AI agents to manage supercomputing resources through natural language conversations, including account management, job submission/monitoring, file operations, Notebook instances, and container lifecycle management.

**Key Characteristics:**
- This is a **Clawhub Skill** (version 1.0.2) distributed via https://clawhub.ai
- Designed specifically for AI coding agents to interact with SCNet APIs
- Supports multiple computing centers (华东一区【昆山】, 东北一区【哈尔滨】, 华东三区【乌镇】, 西北一区【西安】, etc.)
- All documentation and comments are in **Chinese (Simplified)**

## Technology Stack

- **Language**: Python 3 (no specific version constraint)
- **Core Dependencies**:
  - `requests` - HTTP client for API calls
  - Standard library: `hmac`, `hashlib`, `json`, `time`, `os`, `re`, `datetime`, `threading`, `pathlib`
- **No Package Manager Files**: No `pyproject.toml`, `requirements.txt`, or `setup.py` - dependencies are expected to be pre-installed
- **No Build Process**: Direct Python script execution

## Project Structure

```
.
├── _meta.json                    # Skill metadata (version, owner, slug)
├── SKILL.md                      # Comprehensive user documentation (Chinese)
├── AGENTS.md                     # This file
├── .clawhub/
│   └── origin.json               # Clawhub registry information
├── logs/
│   └── scnet-chat-YYYY-MM.log    # Monthly rotating logs
└── scripts/                      # Main source code directory
    ├── scnet_chat.py             # Main module (~3000 lines) - Core functionality
    ├── config_manager.py         # Configuration management (env file I/O)
    ├── scnet_file.py             # Standalone file management module
    ├── scnet_notebook.py         # Standalone Notebook management module
    ├── scnet_container.py        # Standalone container management module
    ├── job_monitor.py            # Job monitoring with Feishu notifications
    ├── job_monitor_service.py    # Cross-platform monitoring service (CLI)
    ├── job_monitor_daemon.py     # Daemon version of job monitor
    └── check_job_status.py       # Cron-friendly job status checker
```

## Code Organization

### Main Module (`scripts/scnet_chat.py`)

This is the primary module containing all core functionality:

1. **SCNetLogger** (lines 44-167): Monthly-rotating log system
   - Logs stored in `~/.openclaw/workspace/skills/scnet-chat/logs/`
   - Format: `scnet-chat-YYYY-MM.log`
   
2. **Authentication Functions** (lines 169-389):
   - HMAC-SHA256 signature generation
   - Token retrieval and caching
   - API: `POST https://api.scnet.cn/api/user/v3/tokens`

3. **Job Management Functions** (lines 392-580):
   - `get_cluster_info()` - Query cluster information
   - `query_user_queues()` - Get available queues
   - `submit_job()` - Submit new job
   - `delete_job()` - Cancel/delete job
   - `query_job_detail()` - Get job details
   - `query_jobs()` - List running jobs
   - `query_history_jobs()` - List historical jobs

4. **File Management Functions** (lines 582-737):
   - `list_files()`, `create_folder()`, `create_file()`
   - `upload_file()`, `download_file()`, `delete_file()`
   - `check_file_exists()`

5. **Manager Classes**:
   - **FileManager** (lines 741-967): File operations wrapper
   - **NotebookManager** (lines 971-1314): Notebook lifecycle management
   - **ContainerManager** (lines 1316-1599): Container lifecycle management
   - **SCNetClient** (lines 1603-2406): Unified client with caching

6. **IntentParser** (lines 2408-2704): Natural language processing for user commands

7. **Wizard Classes**:
   - **JobSubmitWizard** (lines 2708-2858): Interactive job submission
   - **NotebookCreateWizard** (lines 2860-2919): Interactive notebook creation

### Configuration Module (`scripts/config_manager.py`)

- **Config Path**: `~/.scnet-chat.env`
- **Required Keys**:
  - `SCNET_ACCESS_KEY` - Access Key from SCNet
  - `SCNET_SECRET_KEY` - Secret Key from SCNet  
  - `SCNET_USER` - Username
- **File Permissions**: 600 (owner-only read/write)

### Cache System

- **Cache Path**: `~/.scnet-chat-cache.json`
- Stores: tokens, cluster info (hpcUrls, aiUrls, efileUrls), user home paths, default cluster marker
- **Default Cluster**: One cluster marked with `"default": true`

## API Endpoints

The skill interacts with three service types per computing center:

1. **hpcUrl** - Job management APIs
   - Cluster info: `GET /hpc/openapi/v2/cluster`
   - Queues: `GET /hpc/openapi/v2/queuenames/users/{username}`
   - Submit job: `POST /hpc/openapi/v2/apptemplates/BASIC/BASE/job`
   - Delete job: `DELETE /hpc/openapi/v2/jobs`
   - Job detail: `GET /hpc/openapi/v2/jobs/{job_id}`

2. **efileUrl** - File management APIs
   - List: `GET /openapi/v2/file/list`
   - Mkdir: `POST /openapi/v2/file/mkdir`
   - Upload: `POST /openapi/v2/file/upload`
   - Download: `GET /openapi/v2/file/download`
   - Delete: `POST /openapi/v2/file/remove`

3. **aiUrl** - Notebook and Container APIs
   - Notebook create: `POST /ac/openapi/v2/notebook/actions/create`
   - Notebook start/stop: `POST /ac/openapi/v2/notebook/actions/{start|stop}`
   - Container create: `POST /ai/openapi/v2/instance-service/task`
   - Container list: `GET /ai/openapi/v2/instance-service/task/list`

## Job Status Codes

| Code | Status | Description |
|------|--------|-------------|
| statR | 🟢 运行中 | Running |
| statQ | ⏳ 排队中 | Queued |
| statH | ⏸️ 保留 | Held |
| statS | ⏸️ 挂起 | Suspended |
| statE | ❌ 退出 | Exited |
| statC | ✅ 完成 | Completed |
| statW | ⏳ 等待 | Waiting |
| statT | 🛑 终止 | Terminated |
| statDE | 🗑️ 删除 | Deleted |

## Development Conventions

### Coding Style

- **Language**: All comments, docstrings, and user-facing messages in **Chinese**
- **Function Naming**: `snake_case` for Python functions
- **Class Naming**: `PascalCase` for classes
- **Line Length**: No strict limit, but typically under 120 characters
- **Encoding**: UTF-8 with `# -*- coding: utf-8 -*-` header

### Error Handling Pattern

```python
try:
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    # log success
    return result
except Exception as e:
    # log error with duration
    logger.log("GET", url, params, error=str(e), duration_ms=duration_ms)
    print(f"❌ 错误信息: {e}")
    return None
```

### Logging Pattern

All API calls are logged using the `SCNetLogger`:
```python
logger = get_logger()
start_time = time.time()
# ... API call ...
duration_ms = (time.time() - start_time) * 1000
logger.log(method, url, params, result, duration_ms=duration_ms)
```

### Authentication Flow

1. Load credentials from `~/.scnet-chat.env`
2. Generate HMAC-SHA256 signature with timestamp
3. Request token from `https://api.scnet.cn/api/user/v3/tokens`
4. Cache tokens and cluster URLs in `~/.scnet-chat-cache.json`
5. Use token in subsequent API calls via `token` header

## Testing

- **No Formal Test Framework**: No pytest, unittest, or similar
- **Test Code**: Embedded at module level in some files (e.g., `scnet_file.py` lines 786-915)
- **Manual Testing**: Scripts can be run directly: `python3 scripts/scnet_chat.py`

### Testing Approach

When making changes:
1. Test via direct script execution
2. Verify API responses match expected format
3. Check log files in `logs/` directory
4. Validate cache file updates correctly

## Security Considerations

1. **Credential Storage**:
   - Stored in `~/.scnet-chat.env` with 600 permissions
   - Never logged or printed
   
2. **Token Management**:
   - Tokens cached in `~/.scnet-chat-cache.json`
   - Tokens have expiration times (handled by API)
   
3. **API Security**:
   - HMAC-SHA256 signatures for authentication
   - HTTPS for all API calls
   - Token-based session management

4. **File Permissions**:
   - Config files: 600 (owner read/write only)
   - Log files: Created with default umask

## Usage Patterns

### Direct Script Execution
```bash
python3 scripts/scnet_chat.py
```

### As a Module
```python
from scnet_chat import SCNetClient, JobSubmitWizard
import config_manager

config = config_manager.load_config()
client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
client.init_tokens()

# Get default cluster info
default_cluster = client.get_default_cluster_name()
home_path = client.get_home_path()
```

### Job Submission with Monitoring
```python
# Submit and auto-monitor
job_config = {
    'job_name': 'test_job',
    'cmd': 'sleep 100',
    'nnodes': '1',
    'ppn': '1',
    'queue': 'comp',
    'wall_time': '00:10:00',
    'work_dir': '/public/home/user/job_example/'
}
result = client.submit_job_and_monitor(job_config, check_interval=180)
```

## Job Monitoring

The skill includes a sophisticated job monitoring system:

1. **JobMonitor Class** (`job_monitor.py`): Thread-based monitoring
2. **JobMonitorService** (`job_monitor_service.py`): Standalone CLI service
3. **check_job_status.py**: Cron-friendly checker

### Feishu Integration

- Requires `~/.openclaw/skills/feishu-notify/config.json`
- Sends notifications on job completion/failure
- Supports text, post, and interactive card message types

## Computing Centers (计算中心)

The skill supports multiple computing centers with keyword mapping:

| Keyword | Full Name |
|---------|-----------|
| 昆山, 华东一区 | 华东一区【昆山】 |
| 哈尔滨, 东北 | 东北一区【哈尔滨】 |
| 乌镇, 华东三区 | 华东三区【乌镇】 |
| 西安, 西北 | 西北一区【西安】 |
| 雄衡, 华北 | 华北一区【雄衡】 |
| 山东, 华东四区 | 华东四区【山东】 |
| 四川, 西南 | 西南一区【四川】 |
| 核心, 分区一 | 核心节点【分区一】 |
| 分区二 | 核心节点【分区二】 |

## Important Notes for Agents

1. **Always Display Current Context**: Every response MUST include:
   ```
   当前计算中心：{default cluster name}
   家目录：{home path}
   ```
   Source: `~/.scnet-chat-cache.json`

2. **Cache First**: Always prefer cached data; use `use_cache_first=False` only when explicitly refreshing

3. **Default Cluster**: Operations without explicit cluster names use the default cluster (marked with `"default": true` in cache)

4. **Path Handling**: Remote paths are absolute (e.g., `/public/home/ac1npa3sf2/workspace`)

5. **Job Monitoring**: Long-running jobs should use `submit_job_and_monitor()` with appropriate intervals (60-600 seconds)

6. **Error Messages**: User-facing messages are in Chinese; internal logs can be in English

## Version History

- **1.0.2** (Current): Stable release with full feature set
- Installed at: 1774350736024 (Unix timestamp)
- Registry: https://clawhub.ai
