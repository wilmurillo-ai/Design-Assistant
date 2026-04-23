# 天机·玄机子使用示例

## 基本使用

### 1. 图像分析
```bash
# 分析掌纹
python3 tianji_core.py "分析 /tmp/掌纹.jpg"

# 分析风水格局
python3 tianji_core.py "分析这个户型图 /tmp/house.jpg"

# 分析办公环境
python3 tianji_core.py "帮我分析这张办公室图片 /tmp/office.jpg"
```

### 2. 八字分析
```bash
# 完整八字分析
python3 tianji_core.py "八字分析 姓名:张三 性别:男 出生:1990年1月1日 子时"

# 简略分析
python3 tianji_core.py "帮我分析八字 1985年5月15日 午时 女"
```

### 3. 掌纹分析
```bash
# 掌纹分析
python3 tianji_core.py "分析掌纹 /tmp/palm.jpg"

# 手相分析
python3 tianji_core.py "看看这个手相 /tmp/hand.jpg"
```

### 4. 风水分析
```bash
# 房屋风水
python3 tianji_core.py "分析这个房屋的风水格局"

# 办公风水
python3 tianji_core.py "这个办公室布局怎么样"
```

### 5. 普通聊天
```bash
# 普通对话
python3 tianji_core.py "你好，玄机子"

# 咨询问题
python3 tianji_core.py "今天运势如何"

# 专业问题
python3 tianji_core.py "什么是青龙白虎位"
```

## 集成到OpenClaw

### 作为子技能调用
在OpenClaw会话中，可以通过exec调用：

```python
# 在OpenClaw工具调用中
exec(command="python3 tianji_core.py '分析 /tmp/image.jpg'")
```

### 配置模型路由
确保OpenClaw配置中包含以下模型：

```json
{
  "models": {
    "default": "deepseek/deepseek-chat",
    "providers": {
      "volcengine": {
        "enabled": true,
        "apiKey": "您的豆包API密钥",
        "models": [
          {
            "id": "doubao-seed-2-0-pro-260215",
            "name": "豆包视觉模型",
            "capabilities": ["text", "vision"]
          }
        ]
      },
      "deepseek": {
        "enabled": true,
        "apiKey": "您的DeepSeek API密钥"
      }
    }
  }
}
```

## 智能模型路由示例

### 示例1：图像分析自动路由
**输入**: "分析这张掌纹图片 /tmp/palm.jpg"
**路由**: 检测到图片路径 → 使用豆包视觉模型
**输出**: 豆包模型分析结果 + 玄机子专业解读

### 示例2：八字分析自动路由
**输入**: "八字分析 姓名:李四 性别:女 出生:1988年8月8日 辰时"
**路由**: 检测到八字关键词 → 使用DeepSeek模型
**输出**: DeepSeek模型分析 + 传统八字解读

### 示例3：混合请求
**输入**: "先分析这张户型图 /tmp/house.jpg，再根据户主的八字1980年1月1日给出建议"
**路由**: 
1. 图片部分 → 豆包视觉模型
2. 八字部分 → DeepSeek模型
**输出**: 综合分析和建议

## 高级功能

### 批量处理
```bash
# 批量分析图片
for img in /tmp/*.jpg; do
    python3 tianji_core.py "分析 $img"
done
```

### 结果格式化
```bash
# JSON格式输出
python3 tianji_core.py "分析 /tmp/image.jpg" | jq .
```

### 集成到工作流
```bash
#!/bin/bash
# 风水分析工作流

# 1. 分析房屋图片
house_analysis=$(python3 tianji_core.py "分析 $1")

# 2. 分析户主八字
bazi_analysis=$(python3 tianji_core.py "八字分析 $2")

# 3. 生成综合报告
echo "风水综合报告"
echo "=============="
echo "$house_analysis"
echo ""
echo "$bazi_analysis"
```

## 故障排除

### 常见问题

1. **图片分析失败**
   - 检查图片路径是否正确
   - 确认豆包API密钥已配置
   - 检查图片格式是否支持

2. **模型路由错误**
   - 检查config.json配置
   - 确认关键词检测逻辑

3. **依赖缺失**
   - 运行安装脚本: `bash install.sh`
   - 安装Pillow: `pip install pillow`

### 调试模式
```bash
# 启用详细输出
DEBUG=1 python3 tianji_core.py "测试输入"
```

## 性能优化

### 图片预处理
- 自动优化图片尺寸
- PNG转JPG格式
- 质量压缩

### 缓存机制
- 相同图片缓存分析结果
- 八字结果缓存

### 并发处理
- 支持批量请求处理
- 异步模型调用

---

*天机玄妙，智慧无穷。玄机子随时为您服务！*