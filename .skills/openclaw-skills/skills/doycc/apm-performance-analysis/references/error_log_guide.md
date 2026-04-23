# 错误日志详细说明

当 MCP 工具调用出现错误时，脚本会自动将错误信息写入日志文件。

## 日志位置

| 配置方式 | 日志路径 |
|---------|---------|
| 默认 | `./logs/apm_error.log`（相对于脚本执行目录） |
| 自定义 | 通过 `.env` 中的 `APM_ERROR_LOG_DIR` 变量指定目录 |

## 日志格式

MCP 工具调用错误日志：

```json
{
    "timestamp": "2026-03-11T14:30:00Z",
    "action": "DescribeApmInstances",
    "error_code": "AuthFailure",
    "error_message": "认证失败，请检查 SecretId 和 SecretKey",
    "request_id": "eac6b301-a322-493a-8e36-83b295459397",
    "extra": {
        "region": "ap-guangzhou",
        "params": {"Limit": 10}
    }
}
```

异常类错误（含堆栈信息）：

```json
{
    "timestamp": "2026-03-11T14:30:00Z",
    "action": "DescribeApmInstances",
    "exception_type": "ConnectionError",
    "exception_message": "...",
    "traceback": "Traceback (most recent call last): ..."
}
```

## 日志安全

- 日志文件创建后自动设置权限为 `600`
- 日志内容**不会记录** SecretId 或 SecretKey
- 建议将 `logs/` 加入 `.gitignore`

## 排错指引

```bash
# 查看最近的错误
tail -20 logs/apm_error.log

# 按错误码搜索
grep "AuthFailure" logs/apm_error.log

# 按 RequestId 搜索
grep "eac6b301" logs/apm_error.log
```
