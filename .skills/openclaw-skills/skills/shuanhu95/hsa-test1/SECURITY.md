# 安全与隐私说明 (Security & Privacy Notice)

## 🔐 Token 管理说明

### Token 缓存行为

**默认行为**:
- ✅ Token 会缓存到系统临时目录（`/tmp/ezviz_global_token_cache/global_token_cache.json`）
- ✅ 缓存有效期 7 天（与 Token 实际有效期一致）
- ✅ 到期前 5 分钟自动刷新
- ✅ 缓存文件权限 600（仅当前用户可读写）

**为什么缓存 Token**:
- ⚡ **性能**: 避免每次运行都调用 API 获取 Token（减少等待时间）
- 🌐 **稳定性**: 减少 API 调用次数，降低网络失败风险
- 💰 **限流保护**: 避免频繁调用触发 API 限流

### 禁用 Token 缓存

如果您不希望 Token 被持久化，可以通过以下方式禁用缓存：

**方法 1: 环境变量**
```bash
export EZVIZ_TOKEN_CACHE=0
python3 scripts/device_capture.py ...
```

**方法 2: 修改代码**
```python
from token_manager import get_cached_token

# 禁用缓存
token_result = get_cached_token(app_key, app_secret, use_cache=False)
```

### 缓存文件位置

| 系统 | 路径 |
|------|------|
| macOS | `/var/folders/xx/xxxx/T/ezviz_global_token_cache/` |
| Linux | `/tmp/ezviz_global_token_cache/` |
| Windows | `C:\Users\{user}\AppData\Local\Temp\ezviz_global_token_cache\` |

**查看缓存**:
```bash
# macOS/Linux
ls -la /tmp/ezviz_global_token_cache/
cat /tmp/ezviz_global_token_cache/global_token_cache.json

# 清除缓存
rm -rf /tmp/ezviz_global_token_cache/
```

---

## 📡 数据流出说明

### 发送到第三方的数据

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `openai.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `openai.ys7.com` (萤石) | 请求抓图/语音下发 | ✅ 必需 |
| 音频文件 | `openai.ys7.com` (萤石) | 语音上传（仅广播技能） | ✅ 必需 |

### 不发送的数据

- ❌ **不发送** appKey/appSecret 到其他第三方
- ❌ **不发送** 抓图图片到第三方（图片存储在萤石服务器）
- ❌ **不发送** Token 到非萤石端点
- ❌ **不记录** 完整 API 响应到日志

---

## 🔒 安全建议

### 1. 使用最小权限凭证

- 创建专用的 appKey/appSecret，仅开通必要的 API 权限
- 不要使用主账号凭证
- 定期轮换凭证

### 2. 环境变量安全

```bash
# 推荐：使用 .env 文件（不要提交到版本控制）
echo "EZVIZ_APP_KEY=your_key" >> .env
echo "EZVIZ_APP_SECRET=your_secret" >> .env
chmod 600 .env

# 加载环境变量
source .env
```

### 3. 禁用缓存（高安全场景）

如果您在共享计算机或高安全环境中使用：

```bash
export EZVIZ_TOKEN_CACHE=0  # 禁用缓存
python3 scripts/device_capture.py ...
```

### 4. 定期清理缓存

```bash
# 清除所有缓存的 Token
rm -rf /tmp/ezviz_global_token_cache/
```

---

## 📋 文档与实现一致性

### 已修复的问题

| 问题 | 状态 | 修复 |
|------|------|------|
| Token 存储描述不一致 | ✅ 已修复 | 文档现在准确说明 Token 会缓存到临时文件 |
| 缓存行为未说明 | ✅ 已修复 | 添加了 EZVIZ_TOKEN_CACHE 环境变量说明 |
| 无法禁用缓存 | ✅ 已修复 | 现在可以通过环境变量禁用缓存 |

### 当前文档准确性

- ✅ SKILL.md 准确描述 Token 缓存行为
- ✅ 文档说明缓存文件位置和权限
- ✅ 文档提供禁用缓存的方法
- ✅ 数据流出说明完整准确

---

## 🧪 验证命令

```bash
# 1. 验证缓存文件权限
ls -la /tmp/ezviz_global_token_cache/global_token_cache.json
# 应该显示：-rw------- (600)

# 2. 验证缓存内容
cat /tmp/ezviz_global_token_cache/global_token_cache.json | python3 -m json.tool

# 3. 验证禁用缓存
export EZVIZ_TOKEN_CACHE=0
python3 scripts/device_capture.py ...
# 应该显示 "Getting access token from Ezviz API" 而不是 "Using cached global token"

# 4. 清除缓存
python3 lib/token_manager.py clear
```

---

## 📞 联系与反馈

如果您发现任何安全问题或文档不准确的地方，请报告：

1. 检查 SKILL.md 和 lib/README_TOKEN_MANAGER.md
2. 提交 issue 或 pull request
3. 我们会及时修复并更新文档

---

**最后更新**: 2026-03-18  
**版本**: 1.0.0
