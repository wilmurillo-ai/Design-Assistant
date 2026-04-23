# 故障排查指南

本文档帮助您快速定位和解决省钱购物助手 Skill 使用过程中遇到的常见问题。

---

## 常见错误及解决方案

### 1. 口令解析失败

**错误信息**:
```
❌ 口令解析失败
```

**可能原因**:
- 口令已过期（通常7-15天有效期）
- 口令格式不正确
- 商品已下架
- API服务异常

**解决方案**:
1. **检查口令有效期**
   - 京东口令：7-15天
   - 淘宝口令：15-30天
   - 过期后重新获取

2. **验证口令格式**
   - 确保口令完整，没有截断
   - 检查是否包含特殊字符

3. **尝试其他方式**
   - 直接发送商品链接
   - 使用搜索功能查找商品

4. **检查API服务**
   ```bash
   # 测试API是否正常
   curl http://op.squirrel2.cn/health
   ```

---

### 2. 链接无法识别

**错误信息**:
```
❌ 无法识别的链接格式
```

**可能原因**:
- 链接不完整
- 不支持的链接格式
- 链接被截断

**解决方案**:
1. **检查链接完整性**
   - 确保链接以 `http://` 或 `https://` 开头
   - 检查链接是否被截断

2. **确认支持的格式**
   - 京东: `item.jd.com/xxx.html`, `u.jd.com/xxx`, `3.cn/xxx`
   - 淘宝: `item.taobao.com/item.htm?id=xxx`, `m.tb.cn/xxx`
   - 拼多多: `mobile.yangkeduo.com/goods.html?goods_id=xxx`, `p.pinduoduo.com/xxx`

3. **尝试短链接**
   - 如果长链接失败，尝试使用短链接
   - 或使用商品ID直接搜索

---

### 3. 商品搜索无结果

**错误信息**:
```
❌ 未找到相关商品
```

**可能原因**:
- 关键词过于具体
- 商品名称错误
- API返回空结果

**解决方案**:
1. **优化关键词**
   - 使用更通用的搜索词
   - 去除品牌前缀
   - 使用商品核心关键词

2. **检查拼写**
   - 确认关键词拼写正确
   - 避免使用特殊字符

3. **更换平台**
   - 尝试在不同平台搜索
   - 使用价格对比功能

---

### 4. API调用失败

**错误信息**:
```
⚠️ 系统繁忙，请稍后重试
```

**可能原因**:
- API服务未启动
- 网络连接问题
- API超时
- 服务器错误

**解决方案**:
1. **检查API服务状态**
   ```bash
   # 测试健康检查接口
   curl http://op.squirrel2.cn/health
   
   # 预期响应
   {"status": "healthy"}
   ```

2. **启动API服务**
   ```bash
   cd server
   python main.py
   ```

3. **检查网络连接**
   - 确认可以访问API地址
   - 检查防火墙设置

4. **查看日志**
   ```bash
   # 查看服务器日志
   tail -f logs/server.log
   ```

---

### 5. 价格对比失败

**错误信息**:
```
❌ 价格对比失败
```

**可能原因**:
- 关键词不明确
- 多个平台都无结果
- API返回异常

**解决方案**:
1. **使用更明确的关键词**
   - 添加品牌名称
   - 添加型号信息

2. **单独搜索**
   - 先在单个平台搜索
   - 确认商品存在后再对比

3. **检查API响应**
   - 查看API返回的详细错误信息
   - 根据错误信息调整

---

## 调试技巧

### 1. 启用详细日志

在 `config.py` 中设置：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 测试API连接

```python
import requests

# 测试API连接
response = requests.get('http://op.squirrel2.cn/health')
print(response.json())

# 测试搜索接口
response = requests.post(
    'http://op.squirrel2.cn/api/v1/search',
    json={'platform': 'jd', 'keyword': 'iPhone'}
)
print(response.json())
```

### 3. 检查配置

```python
from config import API_BASE_URL, API_TIMEOUT

print(f"API地址: {API_BASE_URL}")
print(f"超时时间: {API_TIMEOUT}")
```

---

## 性能优化

### 1. 响应时间过长

**原因**:
- 网络延迟
- API处理慢
- 数据量大

**解决方案**:
- 减少每页返回数量
- 使用缓存
- 优化网络连接

### 2. 内存占用高

**原因**:
- 缓存数据过多
- 大量并发请求

**解决方案**:
- 定期清理缓存
- 限制并发请求数

---

## 错误代码参考

| 错误代码 | 说明 | 解决方案 |
|---------|------|---------|
| `parse_failed` | 口令解析失败 | 重新获取口令 |
| `invalid_link` | 链接格式错误 | 检查链接格式 |
| `no_results` | 无搜索结果 | 更换关键词 |
| `api_error` | API调用失败 | 检查API服务 |
| `platform_not_supported` | 平台不支持 | 使用支持的平台 |

---

## 联系支持

如果以上方法都无法解决问题，请：

1. 收集错误信息
2. 记录复现步骤
3. 查看日志文件
4. 联系技术支持

---

**更新时间**: 2026-04-08
