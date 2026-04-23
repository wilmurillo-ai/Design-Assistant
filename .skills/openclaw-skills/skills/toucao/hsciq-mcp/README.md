# HSCIQ MCP - 海关编码查询服务

专业的中国商品海关编码查询与归类服务。

## 功能

- 🔍 **搜索海关编码** - 按商品名称查询 HS 编码
- 📋 **获取编码详情** - 税率、申报要素、监管条件
- 📚 **搜索归类实例** - 查看历史归类案例
- 🌐 **统一搜索** - CIQ 项目/危化品/港口信息

## 快速开始

### 配置 API Key

创建配置文件 `~/.openclaw/workspace/hsciq-mcp-config.json`：

```json
{
  "baseUrl": "https://www.hsciq.com",
  "apiKey": "your_api_key"
}
```

或使用环境变量：
```bash
export HSCIQ_API_KEY=your_api_key
```

### 使用示例

**Node.js:**
```bash
node ~/.openclaw/skills/hsciq-mcp/hsciq-client.js search-code --keywords "塑料软管"
```

**Python:**
```bash
python3 ~/.openclaw/skills/hsciq-mcp/hsciq_client.py search-code --keywords "塑料软管"
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `search-code` | 搜索海关编码 |
| `get-detail` | 获取编码详情 |
| `search-instance` | 搜索归类实例 |
| `search-unified` | 统一搜索 |

## API 文档

完整文档：https://www.hsciq.com/MCP/Docs

## License

MIT
