# 🔒 安全审计说明 / Security Audit Notes

**版本 / Version**: 3.1.2  
**日期 / Date**: 2026-03-22  
**作者 / Author**: Krislu

---

## 📋 安全扫描说明 / Security Scan Notes

本技能在 VirusTotal 等安全扫描工具中可能被标记为"可疑"，原因如下：

### 1. HTTP URL（非 HTTPS）/ HTTP URL (Non-HTTPS)

**检测位置 / Detected in**: 
- `SKILL.md` (行 81)
- `github_reader_v3_secure.py` (行 444)

**URL**: `http://localhost:8080/?repo=...`

**说明 / Explanation**:
- 这是**本地回环地址**（localhost），不会访问外部网络
- GitView 是用户自己运行的本地服务（可选功能）
- 使用 HTTP 是因为本地服务通常不配置 HTTPS
- **安全等级**: ✅ 安全（仅本地通信）

**为什么需要 / Why Needed**:
```python
# GitView 是一个本地 Web UI，用于快速查看项目结构
gitview_url = f'http://localhost:8080/?repo={owner}/{repo}'
```

---

### 2. 外部 API 调用 / External API Calls

**检测位置 / Detected in**: 
- `github_reader_v3_secure.py` (GitHub API, Zread)

**URLs**:
- `https://api.github.com/repos/{owner}/{repo}` - GitHub 官方 API
- `https://zread.ai/{owner}/{repo}` - 第三方代码解读服务

**说明 / Explanation**:
- GitHub API 是官方公开的 API（无需认证即可访问公开仓库）
- Zread 是公开的代码解读服务
- 所有请求都有超时控制和速率限制
- **安全等级**: ✅ 安全（公开 API，仅读取）

**安全措施 / Security Measures**:
```python
# 速率限制
GITHUB_API_DELAY = 1.0  # 至少间隔 1 秒

# 超时控制
GITHUB_API_TIMEOUT = 10  # 10 秒超时
BROWSER_TIMEOUT = 30  # 30 秒超时

# 输入验证
if not validate_repo_name(owner) or not validate_repo_name(repo):
    return None
```

---

### 3. 文件系统操作 / File System Operations

**检测位置 / Detected in**: 
- `github_reader_v3_secure.py` (缓存系统)

**说明 / Explanation**:
- 仅写入 `/tmp/gitview_cache` 目录（临时文件夹）
- 使用安全的文件路径生成（防止路径遍历攻击）
- 缓存文件有大小限制（最大 1MB）
- 使用原子写入（临时文件 + 重命名）
- **安全等级**: ✅ 安全（受限的文件操作）

**安全措施 / Security Measures**:
```python
def safe_file_path(base_dir: str, filename: str) -> str:
    """安全的文件路径生成 - 防止路径遍历攻击"""
    # 移除所有危险字符
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # 确保结果仍在基础目录内
    if not file_path.startswith(base_dir):
        raise ValueError(f"Invalid file path: {filename}")
    
    return file_path
```

---

## ✅ 安全特性总结 / Security Features Summary

### 已实现的安全措施 / Implemented Security Measures

| 类别 / Category | 措施 / Measure | 状态 / Status |
|----------------|---------------|--------------|
| **输入验证** | repo 名称白名单验证 | ✅ |
| **URL 安全** | 使用 `quote()` 编码路径组件 | ✅ |
| **路径安全** | 防止路径遍历攻击 | ✅ |
| **速率限制** | GitHub API 调用间隔 1 秒 | ✅ |
| **超时控制** | API 10 秒，浏览器 30 秒 | ✅ |
| **并发限制** | 最多 3 个并发浏览器 | ✅ |
| **缓存安全** | 数据验证 + 大小限制 | ✅ |
| **原子写入** | 临时文件 + 重命名 | ✅ |
| **错误处理** | 完善的异常捕获 | ✅ |
| **日志记录** | 关键操作日志 | ✅ |

---

## 🔍 如何验证安全性 / How to Verify Security

### 1. 检查输入验证
```bash
# 尝试注入恶意输入（应该被拒绝）
/github-read ../../../etc/passwd
/github-read ; rm -rf /
```

### 2. 检查网络请求
```bash
# 监控网络流量（应该只有 GitHub 和 Zread）
tcpdump -i any host api.github.com or zread.ai
```

### 3. 检查文件系统
```bash
# 查看缓存目录权限（应该是 700）
ls -ld /tmp/gitview_cache
```

---

## 📞 报告安全问题 / Report Security Issues

如发现任何安全问题，请通过以下方式报告：

- **GitHub Issues**: https://github.com/Krislu1221/github-reader-skill/issues
- **邮件 / Email**: (待添加)

---

## 📜 许可证 / License

MIT License - 详见 LICENSE 文件
