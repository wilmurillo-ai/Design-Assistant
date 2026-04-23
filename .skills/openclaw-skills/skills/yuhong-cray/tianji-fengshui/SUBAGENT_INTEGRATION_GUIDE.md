# 天机·玄机子 Subagent集成指南

## 概述

本指南介绍如何将豆包视觉模型subagent功能集成到天机·玄机子技能中，实现专业的掌纹、面相、风水图片分析。

## 新增功能

### 1. Subagent集成处理器
- **文件**: `tianji_subagent_integration.py`
- **功能**: 自动创建OpenClaw subagent配置和脚本
- **支持的分析类型**:
  - `palm`: 掌纹分析
  - `face`: 面相分析  
  - `fengshui`: 风水格局分析
  - `general`: 通用图片分析

### 2. 核心功能更新
- **文件**: `tianji_core.py`
- **新增方法**: `analyze_with_subagent()`
- **更新方法**: `process_request()` 支持subagent参数
- **命令行参数**: 新增 `--subagent` 选项

### 3. 测试脚本
- **文件**: `test_subagent_integration.sh`
- **功能**: 验证subagent集成功能

## 快速开始

### 1. 环境要求
- Python 3.6+
- OpenClaw 2026.3.13+
- 豆包API密钥（已配置）

### 2. 基本使用

#### 方法一：使用集成工具
```bash
# 掌纹分析
python3 tianji_subagent_integration.py /tmp/palm.jpg palm

# 面相分析
python3 tianji_subagent_integration.py /tmp/face.jpg face

# 风水分析
python3 tianji_subagent_integration.py /tmp/house.jpg fengshui
```

#### 方法二：使用核心脚本（带subagent参数）
```bash
# 使用subagent分析掌纹
python3 tianji_core.py "分析 /tmp/palm.jpg" --subagent

# 使用subagent分析风水
python3 tianji_core.py "分析这个户型图 /tmp/house.jpg" --subagent
```

#### 方法三：使用原方法（无subagent）
```bash
# 使用原方法分析
python3 tianji_core.py "分析 /tmp/palm.jpg"
```

### 3. 输出说明

#### Subagent集成工具输出
```
🧭 天机·玄机子 Subagent 集成工具
====================================
📷 图片文件: /tmp/palm.jpg
🔍 分析类型: palm
📋 配置文件: /tmp/tianji_subagent_12345.json
📜 脚本文件: /tmp/tianji_analyze_palm_12345.sh

🚀 执行命令:
openclaw sessions spawn --config '/tmp/tianji_subagent_12345.json'

📝 任务描述摘要:
你是一位专业的掌相学大师玄机子。请分析这张掌纹图片...
```

#### 核心脚本输出（带subagent）
```json
{
  "method": "subagent",
  "command": "openclaw sessions spawn --config '/tmp/tianji_subagent_12345.json'",
  "analysis_type": "palm",
  "full_output": "..."
}
```

## 集成到OpenClaw工作流

### 1. 直接调用subagent

在OpenClaw会话中：
```python
# 分析掌纹
exec(command="python3 tianji_subagent_integration.py /tmp/palm.jpg palm")

# 使用核心脚本
exec(command="python3 tianji_core.py '分析 /tmp/palm.jpg' --subagent")
```

### 2. 使用生成的脚本

Subagent集成工具会生成可执行脚本：
```bash
# 执行生成的脚本
bash /tmp/tianji_analyze_palm_12345.sh

# 或直接执行命令
openclaw sessions spawn --config '/tmp/tianji_subagent_12345.json'
```

### 3. 集成代码示例

查看生成的OpenClaw集成代码：
```bash
cat /tmp/tianji_openclaw_integration.js
```

## 专业分析模板

### 掌纹分析模板
```python
task_description = """
你是一位专业的掌相学大师玄机子。请分析这张掌纹图片：

1. 主要掌纹特征：
   - 生命线（长度、清晰度、弧度）
   - 智慧线（走向、深度、分叉）
   - 感情线（形态、分支、断裂）
   - 事业线（位置、连续性）
   - 财运线、健康线等辅助纹路

2. 掌形分析：
   - 手掌形状（方形、圆形、长方形等）
   - 手指长度比例
   - 掌丘发育情况

3. 特殊符号：
   - 星纹、岛纹、十字纹等
   - 链状纹、断裂纹

4. 综合解读：
   - 健康状况
   - 性格特点
   - 事业财运
   - 感情婚姻
   - 整体运势
"""
```

### 面相分析模板
```python
task_description = """
你是一位专业的面相学大师玄机子。请分析这张面相图片：

1. 面部特征：
   - 脸型（圆形、方形、长形等）
   - 五官比例和位置
   - 额头、眉毛、眼睛、鼻子、嘴巴、耳朵

2. 面相分析：
   - 三停分布（上停、中停、下停）
   - 十二宫位（命宫、财帛宫、兄弟宫等）
   - 气色和光泽

3. 特殊特征：
   - 痣的位置和意义
   - 纹路和皱纹
   - 骨骼轮廓

4. 综合解读：
   - 性格特点
   - 事业运势
   - 财运状况
   - 感情婚姻
   - 健康状态
"""
```

### 风水分析模板
```python
task_description = """
你是一位专业的风水大师玄机子。请分析这张风水格局图片：

1. 空间格局：
   - 房屋/房间形状和方位
   - 门窗位置和朝向
   - 家具布局和摆放

2. 风水要素：
   - 青龙、白虎、朱雀、玄武方位
   - 明堂、靠山、案山
   - 气流和水流走向

3. 五行分析：
   - 空间中的五行元素分布
   - 颜色搭配和材质选择
   - 光线和通风情况

4. 综合建议：
   - 优势区域和问题区域
   - 优化调整建议
   - 风水摆件推荐
"""
```

## 配置要求

### 1. OpenClaw模型配置
确保OpenClaw配置中包含豆包模型：
```json
{
  "models": {
    "providers": {
      "volcengine": {
        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
        "apiKey": "您的豆包API密钥",
        "auth": "api-key",
        "api": "openai-completions",
        "models": [
          {
            "id": "doubao-seed-2-0-pro-260215",
            "name": "豆包视觉模型"
          }
        ]
      }
    }
  }
}
```

### 2. 技能配置
检查 `config.json`：
```json
{
  "persona": {
    "name": "玄机子",
    "title": "风水大师智慧助手",
    "emoji": "🧭"
  },
  "model_routing": {
    "image_analysis": {"model": "doubao-seed-2-0-pro-260215"},
    "default_chat": {"model": "deepseek-chat"}
  }
}
```

## 测试验证

### 1. 运行测试脚本
```bash
# 进入技能目录（假设当前在OpenClaw workspace目录）
cd skills/tianji-fengshui
bash test_subagent_integration.sh
```

### 2. 验证输出
测试脚本会检查：
- Python环境
- 脚本文件存在性
- 帮助功能
- 各分析类型功能
- 生成的脚本和配置文件

### 3. 实际测试
```bash
# 使用真实图片测试
python3 tianji_subagent_integration.py /tmp/真实掌纹.jpg palm

# 验证生成的配置
cat /tmp/tianji_subagent_*.json

# 执行分析（需要OpenClaw环境）
bash /tmp/tianji_analyze_palm_*.sh
```

## 故障排除

### 常见问题

#### 1. 图片文件不存在
```
错误: 图片文件不存在: /tmp/palm.jpg
```
**解决方案**: 确保图片路径正确，文件存在且有读取权限。

#### 2. 豆包API未配置
```
豆包模型分析失败: API密钥错误
```
**解决方案**: 检查OpenClaw配置中的豆包API密钥。

#### 3. Subagent调用失败
```
Subagent分析失败: attachments are currently unsupported
```
**解决方案**: 确保使用正确的运行时和参数格式。

#### 4. 生成的脚本无法执行
```
bash: /tmp/tianji_analyze_palm_12345.sh: Permission denied
```
**解决方案**: 添加执行权限或使用 `bash` 命令执行。

### 调试模式

#### 启用详细输出
```bash
# 核心脚本调试
DEBUG=1 python3 tianji_core.py "测试输入" --subagent

# 集成工具调试
python3 tianji_subagent_integration.py --debug /tmp/test.jpg palm
```

#### 检查临时文件
```bash
# 查看生成的配置文件
ls -la /tmp/tianji_*.json
cat /tmp/tianji_subagent_*.json

# 查看生成的脚本
ls -la /tmp/tianji_*.sh
head -20 /tmp/tianji_analyze_*.sh
```

## 性能优化

### 1. 图片预处理
- 自动检测图片格式
- 优化图片尺寸和质量
- 支持常见图片格式：JPG、PNG、WebP

### 2. 缓存机制
- 相同图片缓存分析结果
- 配置文件复用
- 减少重复API调用

### 3. 并发处理
- 支持批量图片分析
- 异步subagent调用
- 并行处理多个请求

## 扩展开发

### 1. 添加新的分析类型
在 `tianji_subagent_integration.py` 中添加：
```python
def _generate_task_description(self, image_path, analysis_type):
    if analysis_type == "new_type":
        return """你的新分析类型模板..."""
```

### 2. 自定义任务描述
修改模板生成逻辑：
```python
# 在调用时传入自定义模板
processor.analyze_with_subagent(image_path, analysis_type, custom_template="...")
```

### 3. 集成其他模型
扩展模型支持：
```python
# 添加新的模型选项
models = {
    "doubao": "volcengine/doubao-seed-2-0-pro-260215",
    "qwen": "qwen/qwen-vl-max",
    "glm": "glm/glm-4v"
}
```

## 版本历史

### v1.1.0 (2026-03-25)
- 新增Subagent集成功能
- 支持掌纹、面相、风水图片分析
- 自动生成专业任务描述
- 创建OpenClaw subagent配置
- 新增测试脚本和文档

### v1.0.1 (2026-03-20)
- 基础功能优化
- 配置验证改进

### v1.0.0 (2026-03-17)
- 初始版本发布
- 玄机子人格设定
- 智能模型路由系统

---

*天机玄妙，智慧无穷。玄机子Subagent集成，让传统智慧与现代AI完美结合！*