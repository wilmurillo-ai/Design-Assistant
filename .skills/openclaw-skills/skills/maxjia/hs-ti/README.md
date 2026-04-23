# hs-ti - 云瞻威胁情报查询技能 / Hillstone Threat Intelligence Skill

## 概述 / Overview
hs-ti是一个OpenClaw技能，提供与山石网科云瞻威胁情报平台的集成。它允许用户查询IP地址、域名、URL和文件哈希的威胁情报。

hs-ti is an OpenClaw skill that provides integration with Hillstone Threat Intelligence Platform. It allows users to query threat intelligence for IP addresses, domains, URLs, and file hashes.

## 功能特性 / Features

### 支持的IOC类型 / Supported IOC Types

#### 中文 / Chinese
- **IP地址**：查询IPv4或IPv6地址的威胁情报
- **域名**：查询域名的威胁情报
- **URL**：查询完整URL的威胁情报
- **文件哈希**：支持MD5、SHA1、SHA256格式的文件哈希查询

#### English
- **IP Address**: Query threat intelligence for IPv4 or IPv6 addresses
- **Domain**: Query threat intelligence for domain names
- **URL**: Query threat intelligence for complete URLs
- **File Hash**: Support file hash queries in MD5, SHA1, SHA256 formats

### 高级功能 / Advanced Features

#### 中文 / Chinese
- **IOC类型自动识别**：自动识别IP、域名、URL、哈希等IOC类型
- **批量查询**：支持多个IOC同时查询
- **并发查询**：支持并发批量查询，大幅提升查询性能（3-5倍提升）
- **智能缓存**：内置缓存机制，提升查询性能
- **线程安全**：缓存和响应时间统计完全线程安全
- **实时响应时间统计**：显示本次调用的平均、最大、最小、中位数响应时间
- **累计性能监控**：跟踪所有历史调用的性能指标
- **详细威胁信息**：返回威胁类型、可信度、具体分类等信息
- **结果格式化**：支持文本、JSON、表格等多种格式
- **结果导出**：支持导出为CSV、JSON、HTML、Markdown等格式
- **日志记录**：完整的操作日志记录
- **错误处理**：完善的错误处理和重试机制

#### English
- **Automatic IOC Type Detection**: Automatically detect IP, domain, URL, hash, and other IOC types
- **Batch Query**: Support for querying multiple IOCs at once
- **Concurrent Query**: Support concurrent batch queries for 3-5x performance improvement
- **Smart Caching**: Built-in caching mechanism to improve query performance
- **Thread-Safe**: Thread-safe caching and response time tracking
- **Real-time Response Time Statistics**: Display average, max, min, and median response times for current query
- **Cumulative Performance Monitoring**: Track performance metrics for all historical queries
- **Detailed Threat Information**: Return threat type, credibility, and specific classification
- **Result Formatting**: Support for text, JSON, table, and other formats
- **Result Export**: Support for exporting to CSV, JSON, HTML, Markdown, and other formats
- **Logging**: Complete operation logging
- **Error Handling**: Comprehensive error handling and retry mechanisms

## 语言切换 / Language Switching

默认语言：英文 / Default Language: English

切换到中文 / Switch to Chinese:
```
/hs-ti cn
```

切换到英文 / Switch to English:
```
/hs-ti en
```

## 安装 / Installation

### 通过OpenClaw安装 / Install via OpenClaw

#### 中文 / Chinese
```bash
# 在OpenClaw配置文件中添加技能
{
  "skills": {
    "entries": {
      "hs-ti": {
        "enabled": true
      }
    }
  }
}
```

#### English
```bash
# Add skill to OpenClaw configuration file
{
  "skills": {
    "entries": {
      "hs-ti": {
        "enabled": true
      }
    }
  }
}
```

### 手动安装 / Manual Installation

#### 中文 / Chinese
1. 将hs-ti目录复制到OpenClaw的skills目录
2. 配置API密钥（见下文）
3. 重启OpenClaw服务

#### English
1. Copy hs-ti directory to OpenClaw's skills directory
2. Configure API key (see below)
3. Restart OpenClaw service

## 配置 / Configuration

在 `config.json` 中配置有效的 API Key：
You need to configure a valid API Key in `config.json`:

**注意 / Note**: 复制 `config.example.json` 为 `config.json` 并填入您的API密钥。
Copy `config.example.json` to `config.json` and fill in your API key.

```json
{
  "api_key": "your-api-key-here",
  "api_url": "https://ti.hillstonenet.com.cn",
  "timeout": 30,
  "max_retries": 3,
  "retry_delay": 1,
  "cache_enabled": true,
  "cache_ttl": 3600,
  "max_workers": 5
}
```

**配置参数说明 / Configuration Parameters**:
- `api_key`: 云瞻威胁情报API密钥 / Hillstone Threat Intelligence API Key (必需/required)
- `api_url`: API地址 / API URL (可选/optional, 默认/default: https://ti.hillstonenet.com.cn)
- `timeout`: 请求超时时间（秒）/ Request timeout in seconds (可选/optional, 默认/default: 30)
- `max_retries`: 最大重试次数 / Maximum retry attempts (可选/optional, 默认/default: 3)
- `retry_delay`: 重试延迟（秒）/ Retry delay in seconds (可选/optional, 默认/default: 1)
- `cache_enabled`: 是否启用缓存 / Enable cache (可选/optional, 默认/default: true)
- `cache_ttl`: 缓存有效期（秒）/ Cache time-to-live in seconds (可选/optional, 默认/default: 3600)
- `max_workers`: 并发查询最大线程数 / Maximum concurrent query threads (可选/optional, 默认/default: 5)

**获取API密钥 / Get API Key**:
#### 中文 / Chinese
- 访问山石网科云瞻威胁情报平台
- 注册账号并申请API访问权限
- 获取API密钥并配置到config.json中

#### English
- Visit Hillstone Threat Intelligence Platform
- Register account and apply for API access permission
- Get API key and configure it in config.json

## 使用方法 / Usage

### 命令调用 / Command Invocation

#### 中文 / Chinese
```
/threat-check 45.74.17.165
/threat-check deli.ydns.eu
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
/threat-check -a 45.74.17.165
/threat-check -a deli.ydns.eu
```

#### English
```
/threat-check 45.74.17.165
/threat-check deli.ydns.eu
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
/threat-check -a 45.74.17.165
/threat-check -a deli.ydns.eu
```

### 别名支持 / Alias Support

#### 中文 / Chinese
- `/threat-check` - 威胁检查
- `/hs-ti` - 云瞻威胁情报
- `/threat` - 威胁情报

#### English
- `/threat-check` - Threat check
- `/hs-ti` - Hillstone threat intelligence
- `/threat` - Threat intelligence

### Python API调用 / Python API Call

```python
from hs_ti_plugin import YunzhanThreatIntel, IOCTypeDetector
from result_formatter import ResultFormatter, ResultExporter

# 初始化客户端 / Initialize client
intel = YunzhanThreatIntel()

# 自动识别IOC类型查询 / Auto-detect IOC type query
result = intel.query_ioc_auto('45.74.17.165')
print(ResultFormatter.format_text(result))

# 指定类型查询 / Query with specified type
result = intel.query_ioc('example.com', 'domain')
print(ResultFormatter.format_json(result))

# 批量查询 / Batch query
iocs = [
    {"value": "example.com", "type": "domain"},
    {"value": "8.8.8.8", "type": "ip"}
]
batch_result = intel.batch_query(iocs)
print(ResultFormatter.format_batch_results(batch_result))

# 导出结果 / Export results
ResultExporter.export_csv(batch_result['results'], 'report.csv')
ResultExporter.export_html(batch_result['results'], 'report.html', 
                          batch_result['batch_stats'], 
                          batch_result['total_stats'])
```

## 新功能使用 / New Features Usage

### IOC类型自动识别 / Automatic IOC Type Detection

#### 中文 / Chinese
```python
from hs_ti_plugin import IOCTypeDetector

# 自动识别IOC类型 / Auto-detect IOC type
ioc_type = IOCTypeDetector.detect("192.168.1.1")  # 返回 "ip"
ioc_type = IOCTypeDetector.detect("example.com")      # 返回 "domain"
ioc_type = IOCTypeDetector.detect("https://example.com")  # 返回 "url"
ioc_type = IOCTypeDetector.detect("d41d8cd98f00b204e9800998ecf8427e")  # 返回 "hash"
```

#### English
```python
from hs_ti_plugin import IOCTypeDetector

# Auto-detect IOC type
ioc_type = IOCTypeDetector.detect("192.168.1.1")  # Returns "ip"
ioc_type = IOCTypeDetector.detect("example.com")      # Returns "domain"
ioc_type = IOCTypeDetector.detect("https://example.com")  # Returns "url"
ioc_type = IOCTypeDetector.detect("d41d8cd98f00b204e9800998ecf8427e")  # Returns "hash"
```

### 缓存管理 / Cache Management

#### 中文 / Chinese
```python
# 查询时使用缓存 / Use cache during query
result = intel.query_ioc("example.com", use_cache=True)

# 清空缓存 / Clear cache
intel.clear_cache()

# 获取缓存统计 / Get cache statistics
stats = intel.get_cache_stats()
print(f"总条目: {stats['total_entries']}")
print(f"有效条目: {stats['valid_entries']}")
```

#### English
```python
# Use cache during query
result = intel.query_ioc("example.com", use_cache=True)

# Clear cache
intel.clear_cache()

# Get cache statistics
stats = intel.get_cache_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Valid entries: {stats['valid_entries']}")
```

### 结果格式化 / Result Formatting

#### 中文 / Chinese
```python
from result_formatter import ResultFormatter

# 文本格式 / Text format
text = ResultFormatter.format_text(result, 'en')

# JSON格式 / JSON format
json_str = ResultFormatter.format_json(result)

# 表格格式 / Table format
table = ResultFormatter.format_table(results, 'en')

# 批量结果格式化 / Batch result formatting
formatted = ResultFormatter.format_batch_results(batch_result, 'en')
```

#### English
```python
from result_formatter import ResultFormatter

# Text format
text = ResultFormatter.format_text(result, 'en')

# JSON format
json_str = ResultFormatter.format_json(result)

# Table format
table = ResultFormatter.format_table(results, 'en')

# Batch result formatting
formatted = ResultFormatter.format_batch_results(batch_result, 'en')
```

### 结果导出 / Result Export

#### 中文 / Chinese
```python
from result_formatter import ResultExporter

# 导出为CSV / Export to CSV
ResultExporter.export_csv(results, 'report.csv', 'en')

# 导出为JSON / Export to JSON
ResultExporter.export_json(results, 'report.json', batch_stats, total_stats)

# 导出为HTML / Export to HTML
ResultExporter.export_html(results, 'report.html', 'en', batch_stats, total_stats)

# 导出为Markdown / Export to Markdown
ResultExporter.export_markdown(results, 'report.md', 'en', batch_stats, total_stats)
```

#### English
```python
from result_formatter import ResultExporter

# Export to CSV
ResultExporter.export_csv(results, 'report.csv', 'en')

# Export to JSON
ResultExporter.export_json(results, 'report.json', batch_stats, total_stats)

# Export to HTML
ResultExporter.export_html(results, 'report.html', 'en', batch_stats, total_stats)

# Export to Markdown
ResultExporter.export_markdown(results, 'report.md', 'en', batch_stats, total_stats)
```

## 响应格式 / Response Format

### 成功响应 / Success Response

```json
{
  "data": {
    "result": "malicious",
    "threat_type": ["Scanner", "Exploit"],
    "flow_direction": 1,
    "credibility": 33,
    "lifecycle": {
      "status": 1,
      "start_time": 1766801777913,
      "window_ms": 7776000000
    },
    "ip_address": "45.74.17.165"
  },
  "response_code": 0,
  "response_msg": "OK",
  "response_time_ms": 207
}
```

### 字段说明 / Field Description

#### 中文 / Chinese
- `result`: 查询结果（malicious/benign/unknown）
- `threat_type`: 威胁类型列表
- `credibility`: 可信度评分（0-100）
- `response_time_ms`: 响应时间（毫秒）

#### English
- `result`: Query result (malicious/benign/unknown)
- `threat_type`: List of threat types
- `credibility`: Credibility score (0-100)
- `response_time_ms`: Response time in milliseconds

## 性能统计 / Performance Statistics

每次查询都会显示详细的性能统计：
Each query displays detailed performance statistics:

### 单次查询 / Single Query

#### 中文 / Chinese
- 显示本次调用的响应时间

#### English
- Display response time for current call

### 批量查询 / Batch Query

#### 中文 / Chinese
- 显示本次批量的统计（平均/最大/最小/中位数）

#### English
- Display statistics for current batch (avg/max/min/median)

### 累计统计 / Cumulative Statistics

#### 中文 / Chinese
- 显示所有历史调用的累计统计和总调用次数

#### English
- Display cumulative statistics and total call count for all historical queries

## 日志记录 / Logging

#### 中文 / Chinese
日志文件位置：`~/.openclaw/logs/hs_ti.log`

日志级别：
- INFO: 正常操作信息
- WARNING: 警告信息
- ERROR: 错误信息

#### English
Log file location: `~/.openclaw/logs/hs_ti.log`

Log levels:
- INFO: Normal operation information
- WARNING: Warning information
- ERROR: Error information

## 依赖项 / Dependencies

#### 中文 / Chinese
- Python 3.8+
- 山石网科云瞻威胁情报 API 访问权限
- 本技能使用Python标准库，无需额外安装依赖

#### English
- Python 3.8+
- Hillstone Threat Intelligence API access permission
- This skill uses Python standard library, no additional dependencies required

## API端点 / API Endpoints

#### 中文 / Chinese
- IP查询: `/api/ip/reputation` 或 `/api/ip/detail`
- 域名查询: `/api/domain/reputation` 或 `/api/domain/detail`
- URL查询: `/api/url/reputation` 或 `/api/url/detail`
- 文件哈希查询: `/api/file/reputation` 或 `/api/file/detail`

#### English
- IP Query: `/api/ip/reputation` or `/api/ip/detail`
- Domain Query: `/api/domain/reputation` or `/api/domain/detail`
- URL Query: `/api/url/reputation` or `/api/url/detail`
- File Hash Query: `/api/file/reputation` or `/api/file/detail`

## 故障排除 / Troubleshooting

### API Key无效 / Invalid API Key

#### 中文 / Chinese
**症状**：查询返回认证错误
**解决**：确保使用有效的云瞻API Key

#### English
**Symptoms**: Query returns authentication error
**Solution**: Ensure you are using a valid Hillstone API Key

### 网络连接问题 / Network Connection Issues

#### 中文 / Chinese
**症状**：查询超时或连接失败
**解决**：检查能否访问 `https://ti.hillstonenet.com.cn`

#### English
**Symptoms**: Query timeout or connection failure
**Solution**: Check if you can access `https://ti.hillstonenet.com.cn`

### 查询超时 / Query Timeout

#### 中文 / Chinese
**症状**：查询长时间无响应
**解决**：默认超时30秒，可在config.json中调整timeout参数

#### English
**Symptoms**: Query takes long time without response
**Solution**: Default timeout is 30 seconds, can be adjusted in config.json

### 编码问题 / Encoding Issues

#### 中文 / Chinese
**症状**：中文显示乱码
**解决**：确保系统支持UTF-8编码

#### English
**Symptoms**: Chinese characters display as garbled text
**Solution**: Ensure your system supports UTF-8 encoding

## 示例 / Examples

### 查询单个IP / Query Single IP

#### 中文 / Chinese
```
/threat-check 8.8.8.8
```

#### English
```
/threat-check 8.8.8.8
```

### 批量查询 / Batch Query

#### 中文 / Chinese
```
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

#### English
```
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
```

### 查询域名 / Query Domain

#### 中文 / Chinese
```
/threat-check example.com
```

#### English
```
/threat-check example.com
```

### 查询URL / Query URL

#### 中文 / Chinese
```
/threat-check https://example.com/malware
```

#### English
```
/threat-check https://example.com/malware
```

### 查询文件哈希 / Query File Hash

#### 中文 / Chinese
```
/threat-check d41d8cd98f00b204e9800998ecf8427e
```

#### English
```
/threat-check d41d8cd98f00b204e9800998ecf8427e
```

### 高级查询 / Advanced Query

#### 中文 / Chinese
```
/threat-check -a 45.74.17.165
```

#### English
```
/threat-check -a 45.74.17.165
```

## 测试 / Testing

#### 中文 / Chinese
运行测试套件：
```bash
python tests/test_hs_ti.py
```

运行示例程序：
```bash
python examples/query_ioc.py
```

#### English
Run test suite:
```bash
python tests/test_hs_ti.py
```

Run example program:
```bash
python examples/query_ioc.py
```

## 许可证 / License

MIT License

## 作者 / Author

Hillstone

## 版本历史 / Version History

详见 [CHANGELOG.md](CHANGELOG.md) / See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 贡献 / Contributing

欢迎提交Issue和Pull Request！
Welcome to submit Issues and Pull Requests!

## 联系方式 / Contact

如有问题或建议，请联系Hillstone技术支持团队。
For questions or suggestions, please contact Hillstone technical support team.
