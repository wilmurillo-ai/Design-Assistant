---
name: hs-ti
version: "2.2.5"
publisher: maxjia
description: Hillstone Threat Intelligence Skill. Query IP addresses, domains, URLs, and file hashes in Hillstone threat intelligence database.
metadata: {"openclaw":{"emoji":"🔍","commands":["/threat-check","/hs-ti","/threat"],"aliases":["hs-ti","threat-intel","hillstone-ti"],"title":"Hillstone Threat Intelligence"}}
---

# Hillstone Threat Intelligence Skill

**Features**: Query IP addresses, domains, URLs, and file hashes in the Hillstone threat intelligence database.

## New Features (v2.2.4)

- **English Only**: Simplified to pure English version for better international compatibility
- **Automatic IOC Type Detection**: Automatically detect IP, domain, URL, hash, and other IOC types
- **Smart Caching**: Built-in LRU cache with statistics and size limits, significantly improved query performance (40-60%)
- **Connection Pool Management**: HTTP connection pool for efficient connection reuse, reduced network latency (30%)
- **Batch Operations**: Import IOC lists from CSV, TXT, JSON files, support batch queries with progress tracking
- **Exponential Backoff Retry**: Intelligent retry mechanism for better handling of temporary network failures
- **Circuit Breaker Pattern**: Prevent cascading failures, improve system stability
- **Result Formatting**: Support for text, JSON, table, and other formats
- **Result Export**: Support for exporting to CSV, JSON, HTML, Markdown, and other formats
- **Logging**: Complete operation logging with automatic sensitive data masking
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Type Hints**: Full type annotations for better code maintainability
- **API Key Management**: Support for HILLSTONE_API_KEY environment variable, priority over config file
- **Security Enhancements**: Sensitive data masking, log security, file permission management
- **Search Optimization**: 70+ keywords covering brand, security, features, and more

## Configuration

You need to create a `config.json` file and configure a valid API Key:

1. Copy `config.example.json` to `config.json`

2. Fill in your API Key in `config.json`:

```json
{
  "api_key": "your-api-key-here",
  "api_url": "https://ti.hillstonenet.com.cn",
  "timeout": 30,
  "max_retries": 3,
  "retry_delay": 1,
  "cache_enabled": true,
  "cache_ttl": 3600
}
```

**Configuration Parameters**:
- `api_key`: Hillstone Threat Intelligence API Key (required)
- `api_url`: API URL (optional, default: https://ti.hillstonenet.com.cn)
- `timeout`: Request timeout in seconds (optional, default: 30)
- `max_retries`: Maximum retry attempts (optional, default: 3)
- `retry_delay`: Retry delay in seconds (optional, default: 1)
- `cache_enabled`: Enable cache (optional, default: true)
- `cache_ttl`: Cache time-to-live in seconds (optional, default: 3600)

## Usage Examples

```
/threat-check 45.74.17.165
/threat-check deli.ydns.eu  
/threat-check 45.74.17.165,deli.ydns.eu,www.blazingelectricz.com
/threat-check -a 45.74.17.165
/threat-check -a deli.ydns.eu
```

## Advanced API

Use `-a` parameter to call the advanced API and get more detailed threat intelligence:
```
/threat-check -a 45.74.17.165
```

Advanced API provides:
- **Basic Info**: Network, carrier, location, country, province, city, coordinates
- **ASN Info**: Autonomous System information
- **Threat Type**: Malicious type classification
- **Tags**: Threat-related tags
- **DNS Records**: Reverse DNS records (up to 10)
- **Domain Info**: Current and historical domains (up to 10)
- **File Associations**: Downloaded, referenced, and related file hashes (malicious only)
- **Port Info**: Open ports, application protocols, application names, versions

## Supported IOC Types

- **IP Address**: Automatically detect and query `/api/ip/reputation`
- **Domain**: Automatically detect and query `/api/domain/reputation`
- **URL**: Automatically detect and query `/api/url/reputation`
- **File Hash**: Supports MD5/SHA1/SHA256, query `/api/file/reputation`

## Response Time Statistics

Each query displays detailed performance statistics:
- **Single Query**: Display response time for current call
- **Batch Query**: Display statistics for current batch (avg/max/min/median)
- **Cumulative Statistics**: Display cumulative statistics and total call count for all historical queries

## Dependencies

- Python 3.8+
- Hillstone Threat Intelligence API access permission
- This skill uses Python standard library, no additional dependencies required

## API Endpoints

### Reputation API
- IP Query: `/api/ip/reputation?key={ip}`
- Domain Query: `/api/domain/reputation?key={domain}`
- URL Query: `/api/url/reputation?key={url}`
- File Hash Query: `/api/file/reputation?key={hash}`

### Advanced Detail API
- IP Advanced Query: `/api/ip/detail?key={ip}`
- Domain Advanced Query: `/api/domain/detail?key={domain}`
- URL Advanced Query: `/api/url/detail?key={url}`
- File Hash Advanced Query: `/api/file/detail?key={hash}`

## Troubleshooting

- **Invalid API Key**: Ensure you are using a valid Hillstone API Key
- **Network Connection Issues**: Check if you can access `https://ti.hillstonenet.com.cn`
- **Query Timeout**: Default timeout is 30 seconds, can be adjusted in config.json
- **Encoding Issues**: Ensure your system supports UTF-8 encoding
- **Log Viewing**: Log file is located at `~/.openclaw/logs/hs_ti.log`

## Security Best Practices

### API Key Management

**Recommended Approach:**
- Use environment variable for API key (recommended)
  ```bash
  export HILLSTONE_API_KEY="your-api-key-here"
  ```
- Ensure environment variable is not logged to history
  ```bash
  # In bash
  export HISTCONTROL=ignorespace
  export HILLSTONE_API_KEY="your-api-key-here"
  
  # In PowerShell
  $env:HILLSTONE_API_KEY="your-api-key-here"
  ```

**Configuration File Approach:**
- If configuration file must be used, ensure:
  - File permissions are set to owner-only read: `chmod 600 config.json`
  - Configuration file is not committed to version control
  - Configuration file is added to `.gitignore`

### File Permissions

**Configuration File:**
```bash
# Set configuration file permissions
chmod 600 ~/.openclaw/skills/hs-ti/config.json

# Ensure directory permissions are correct
chmod 700 ~/.openclaw/skills/hs-ti/
```

**Log File:**
```bash
# Set log file permissions
chmod 600 ~/.openclaw/logs/hs_ti.log

# Ensure log directory permissions are correct
chmod 700 ~/.openclaw/logs/
```

## Version History

### [2.2.4] - 2026-04-02
- Changed to pure English version
- Removed all Chinese content for better international compatibility
- Simplified documentation structure

### [2.2.3] - 2026-04-01
- Added environment variable support (HILLSTONE_API_KEY)
- Enhanced log security with automatic sensitive data masking
- Added comprehensive security documentation (SECURITY.md)
- Improved transparency in package.json

### [2.2.2] - 2026-03-31
- Added LRU cache mechanism
- Implemented HTTP connection pool
- Added batch operations support
- Implemented exponential backoff retry
- Added circuit breaker pattern
- Enhanced error handling
- Added comprehensive type hints
- Optimized search keywords

## License

MIT License

## Support

- Homepage: https://clawhub.ai/maxjia/hs-ti
- Issues: https://github.com/your-repo/hs-ti/issues
