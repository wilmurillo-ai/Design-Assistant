# 省钱购物助手 Skill

一个用于 OpenClaw 的智能省钱购物助手 Skill，帮助用户找到最优惠的商品价格，通过优惠券和折扣节省购物开支。

## 📋 功能特性

- ✅ **商品搜索** - 支持京东、淘宝、拼多多三大平台
- ✅ **链接转换** - 自动转换为优惠链接
- ✅ **口令解析** - 智能识别各平台分享口令
- ✅ **价格对比** - 多平台价格对比，找到最优惠价格
- ✅ **智能识别** - 自动识别用户意图和平台

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置API地址

编辑 `config.py`，设置API地址：

```python
API_BASE_URL = 'http://op.squirrel2.cn'  # 生产环境
# API_BASE_URL = 'http://localhost:8000'  # 开发环境
```

### 3. 运行测试

```bash
python skill.py
```

## 📖 使用方法

### 商品搜索

```python
from skill import handle_message

# 搜索商品
result = handle_message("iPhone 16")
print(result)

# 指定平台搜索
result = handle_message("在京东搜索手机")
print(result)
```

### 链接转换

```python
# 转换京东链接
result = handle_message("https://item.jd.com/10021724657015.html")
print(result)
```

### 口令解析

```python
# 解析淘宝分享
result = handle_message("【淘宝】假一赔四 https://e.tb.cn/h.iVW7Wnbs5Woz1ZI")
print(result)
```

### 价格对比

```python
# 价格对比
result = handle_message("对比 iPhone 16")
print(result)
```

## 📁 项目结构

```
skill-openclaw/
├── SKILL.md                    # Skill 主文件（OpenClaw识别）
├── skill.py                    # Skill 实现代码
├── config.py                   # 配置文件
├── utils.py                    # 工具函数
├── formatters.py               # 格式化函数
├── references/                 # 参考文档
│   ├── api-guide.md           # API 使用指南
│   ├── user-guide.md          # 用户使用手册
│   └── troubleshooting.md     # 故障排查指南
└── tests/                      # 测试文件
    ├── test_skill.py          # Skill 测试
    └── test_data.json         # 测试数据
```

## 🔧 配置说明

### API配置

在 `config.py` 中配置：

```python
API_BASE_URL = 'http://op.squirrel2.cn'  # API地址
API_PREFIX = '/api/v1'                  # API前缀
API_TIMEOUT = 10                        # 超时时间（秒）
```

### 平台配置

```python
PLATFORMS = {
    'jd': {
        'name': '京东',
        'keywords': ['京东', 'jd.com', ...],
        'link_patterns': [...]
    },
    'taobao': {
        'name': '淘宝',
        'keywords': ['淘宝', '天猫', ...],
        'link_patterns': [...]
    },
    'pinduoduo': {
        'name': '拼多多',
        'keywords': ['拼多多', ...],
        'link_patterns': [...]
    }
}
```

## 📚 文档

- [API使用指南](references/api-guide.md) - API接口详细说明
- [用户使用手册](references/user-guide.md) - 用户使用指南
- [故障排查指南](references/troubleshooting.md) - 常见问题解决

## 🧪 测试

运行测试套件：

```bash
python tests/test_skill.py
```

## 📝 注意事项

1. **API服务**: 确保 API 服务已启动并可访问
2. **网络连接**: 确保可以访问 API 地址
3. **口令有效期**: 
   - 京东口令：7-15天
   - 淘宝口令：15-30天
4. **优惠链接有效期**:
   - 京东：15天
   - 淘宝：15天
   - 拼多多：7天

## 🎯 核心价值

帮助用户找到最优惠的价格，通过优惠券和折扣为用户节省购物开支。

## 📄 许可证

MIT License

## 👤 作者

AI Assistant

## 📅 更新日志

- 2026-04-08: v1.0.0 - 初始版本发布
