#!/usr/bin/env python3
"""
天机·玄机子 - Subagent集成模块
集成豆包视觉模型subagent调用功能
"""

import os
import sys
import json
import base64
import tempfile
from pathlib import Path

class TianjiSubagentIntegration:
    """天机Subagent集成处理器"""
    
    def __init__(self, workspace_dir=None):
        """初始化"""
        if workspace_dir:
            self.workspace_dir = Path(workspace_dir)
        else:
            # 使用当前文件所在目录的父目录作为workspace
            current_file = Path(__file__).resolve()
            self.workspace_dir = current_file.parent.parent.parent
        self.temp_dir = Path(tempfile.gettempdir())
        
    def analyze_palm_with_subagent(self, image_path, analysis_type="palm"):
        """
        使用subagent分析掌纹/图片
        analysis_type: palm(掌纹), face(面相), fengshui(风水), general(通用)
        """
        try:
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 根据分析类型生成任务描述
            task_description = self._generate_task_description(image_path, analysis_type)
            
            # 构建subagent调用参数
            subagent_config = {
                "task": task_description,
                "runtime": "subagent",
                "model": "volcengine/doubao-seed-2-0-pro-260215",
                "label": f"玄机子-{analysis_type}分析",
                "attachments": [
                    {
                        "name": os.path.basename(image_path),
                        "content": image_base64,
                        "encoding": "base64",
                        "mimeType": "image/jpeg"
                    }
                ]
            }
            
            # 保存配置到临时文件
            config_file = self.temp_dir / f"tianji_subagent_{os.getpid()}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(subagent_config, f, ensure_ascii=False, indent=2)
            
            # 生成OpenClaw命令
            command = self._generate_openclaw_command(config_file)
            
            return {
                "success": True,
                "config_file": str(config_file),
                "command": command,
                "task_description": task_description
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_task_description(self, image_path, analysis_type):
        """生成任务描述"""
        filename = os.path.basename(image_path)
        
        if analysis_type == "palm":
            return f"""你是一位专业的掌相学大师玄机子。请分析这张掌纹图片，使用你的掌相学专业知识，详细分析以下内容：

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

请结合传统掌相学知识，给出专业、详细的分析报告。图片文件名：{filename}"""
        
        elif analysis_type == "face":
            return f"""你是一位专业的面相学大师玄机子。请分析这张面相图片，使用你的面相学专业知识，详细分析以下内容：

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

请结合传统面相学知识，给出专业、详细的分析报告。图片文件名：{filename}"""
        
        elif analysis_type == "fengshui":
            return f"""你是一位专业的风水大师玄机子。请分析这张风水格局图片，使用你的风水学专业知识，详细分析以下内容：

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

请结合传统风水学知识，给出专业、详细的分析报告。图片文件名：{filename}"""
        
        else:  # general
            return f"""你是一位专业的图像分析大师玄机子。请分析这张图片，结合你的专业知识，详细分析图片内容并提供专业解读。

请从以下角度进行分析：
1. 图片主要内容识别
2. 细节特征分析
3. 专业领域解读
4. 综合建议和评价

图片文件名：{filename}"""
    
    def _generate_openclaw_command(self, config_file):
        """生成OpenClaw命令"""
        return f"""openclaw sessions spawn --config '{config_file}'"""
    
    def create_analysis_script(self, image_path, analysis_type="palm"):
        """创建分析脚本"""
        result = self.analyze_palm_with_subagent(image_path, analysis_type)
        
        if not result["success"]:
            return f"创建分析脚本失败: {result['error']}"
        
        # 创建执行脚本
        script_content = f'''#!/bin/bash
# 天机·玄机子图片分析脚本
# 分析类型: {analysis_type}
# 图片文件: {image_path}

echo "🧭 玄机子开始分析图片..."
echo "分析类型: {analysis_type}"
echo "图片路径: {image_path}"
echo ""

# 检查图片文件
if [ ! -f "{image_path}" ]; then
    echo "错误: 图片文件不存在"
    exit 1
fi

echo "✅ 图片文件检查通过"
echo ""

# 执行subagent分析
echo "🚀 启动豆包视觉模型分析..."
echo "任务描述:"
echo "{result['task_description'][:200]}..."
echo ""

# 这里需要实际调用OpenClaw sessions spawn
# 由于权限问题，这里只显示命令
echo "执行命令:"
echo "{result['command']}"
echo ""

echo "📋 配置已保存到: {result['config_file']}"
echo ""
echo "💡 提示: 请手动执行以上命令或集成到OpenClaw工作流中"
echo "🧭 玄机子分析完成"
'''

        script_file = self.temp_dir / f"tianji_analyze_{analysis_type}_{os.getpid()}.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(script_file, 0o755)
        
        return {
            "success": True,
            "script_file": str(script_file),
            "config_file": result["config_file"],
            "command": result["command"],
            "task_description": result["task_description"]
        }
    
    def generate_openclaw_integration_code(self):
        """生成OpenClaw集成代码"""
        integration_code = '''// OpenClaw集成代码 - 天机·玄机子图片分析

// 1. 在OpenClaw配置中添加模型
const config = {
  models: {
    providers: {
      volcengine: {
        baseUrl: "https://ark.cn-beijing.volces.com/api/v3",
        apiKey: process.env.DOUBAO_API_KEY,
        api: "openai-completions",
        models: [
          {
            id: "doubao-seed-2-0-pro-260215",
            name: "豆包视觉模型"
          }
        ]
      }
    }
  }
};

// 2. 图片分析处理函数
async function analyzeImageWithTianji(imagePath, analysisType = "palm") {
  const fs = require('fs');
  const path = require('path');
  
  // 读取图片
  const imageBuffer = fs.readFileSync(imagePath);
  const imageBase64 = imageBuffer.toString('base64');
  
  // 生成任务描述
  const taskDescription = generateTaskDescription(path.basename(imagePath), analysisType);
  
  // 调用subagent
  const result = await openclaw.sessions.spawn({
    task: taskDescription,
    runtime: "subagent",
    model: "volcengine/doubao-seed-2-0-pro-260215",
    label: `玄机子-${analysisType}分析`,
    attachments: [
      {
        name: path.basename(imagePath),
        content: imageBase64,
        encoding: "base64",
        mimeType: "image/jpeg"
      }
    ]
  });
  
  return result;
}

// 3. 任务描述生成函数
function generateTaskDescription(filename, analysisType) {
  const templates = {
    palm: `你是一位专业的掌相学大师玄机子。请分析这张掌纹图片...`,
    face: `你是一位专业的面相学大师玄机子。请分析这张面相图片...`,
    fengshui: `你是一位专业的风水大师玄机子。请分析这张风水格局图片...`
  };
  
  return templates[analysisType] || `分析图片: ${filename}`;
}

// 4. 使用示例
async function exampleUsage() {
  // 分析掌纹
  const palmResult = await analyzeImageWithTianji("/tmp/palm.jpg", "palm");
  console.log("掌纹分析结果:", palmResult);
  
  // 分析面相
  const faceResult = await analyzeImageWithTianji("/tmp/face.jpg", "face");
  console.log("面相分析结果:", faceResult);
  
  // 分析风水
  const fengshuiResult = await analyzeImageWithTianji("/tmp/house.jpg", "fengshui");
  console.log("风水分析结果:", fengshuiResult);
}

module.exports = {
  analyzeImageWithTianji,
  generateTaskDescription
};
'''
        
        code_file = self.temp_dir / "tianji_openclaw_integration.js"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(integration_code)
        
        return str(code_file)

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 tianji_subagent_integration.py <图片路径> <分析类型>")
        print("分析类型: palm(掌纹), face(面相), fengshui(风水), general(通用)")
        print("示例: python3 tianji_subagent_integration.py /tmp/palm.jpg palm")
        sys.exit(1)
    
    image_path = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "palm"
    
    if not os.path.exists(image_path):
        print(f"错误: 图片文件不存在: {image_path}")
        sys.exit(1)
    
    if analysis_type not in ["palm", "face", "fengshui", "general"]:
        print(f"错误: 不支持的分析类型: {analysis_type}")
        print("支持的类型: palm, face, fengshui, general")
        sys.exit(1)
    
    # 创建集成处理器
    processor = TianjiSubagentIntegration()
    
    # 创建分析脚本
    result = processor.create_analysis_script(image_path, analysis_type)
    
    if isinstance(result, str):
        print(result)
        sys.exit(1)
    
    print("=" * 60)
    print("🧭 天机·玄机子 Subagent 集成工具")
    print("=" * 60)
    print(f"📷 图片文件: {image_path}")
    print(f"🔍 分析类型: {analysis_type}")
    print(f"📋 配置文件: {result['config_file']}")
    print(f"📜 脚本文件: {result['script_file']}")
    print("")
    print("🚀 执行命令:")
    print(result['command'])
    print("")
    print("📝 任务描述摘要:")
    print(result['task_description'][:300] + "...")
    print("")
    print("💡 使用方法:")
    print(f"1. 执行脚本: bash {result['script_file']}")
    print(f"2. 或直接执行命令: {result['command']}")
    print("3. 或集成到OpenClaw工作流中")
    print("=" * 60)
    
    # 生成OpenClaw集成代码
    integration_code = processor.generate_openclaw_integration_code()
    print(f"📦 OpenClaw集成代码已生成: {integration_code}")
    print("=" * 60)

if __name__ == "__main__":
    main()