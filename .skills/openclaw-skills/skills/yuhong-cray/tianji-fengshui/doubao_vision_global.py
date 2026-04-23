#!/usr/bin/env python3
"""
豆包视觉模型分析器（全局配置版）
从OpenClaw全局配置读取API密钥，不在技能文件中硬编码
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from PIL import Image
import time

class DoubaoVisionGlobalAnalyzer:
    """豆包视觉模型分析器（从全局配置读取）"""
    
    def __init__(self, config_path=None):
        """初始化分析器，从全局配置读取API密钥"""
        self.config = self.load_config(config_path)
        self.api_config = self.get_global_api_config()
        self.image_config = self.config.get("image_processing", {})
        
        if not self.api_config.get("api_key"):
            print("⚠️  警告: 未找到豆包API密钥，请检查全局配置")
        
    def load_config(self, config_path):
        """加载技能配置（不包含API密钥）"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置（不包含API密钥）
        return {
            "image_processing": {
                "optimize_size": True,
                "max_width": 768,
                "max_height": 768,
                "quality": 85,
                "convert_png_to_jpg": True
            }
        }
    
    def get_openclaw_config_path(self):
        """获取OpenClaw配置路径，支持多种环境"""
        # 方法1: 环境变量
        env_path = os.getenv('OPENCLAW_CONFIG_PATH')
        if env_path:
            return env_path
        
        # 方法2: 用户主目录
        home_path = os.path.expanduser('~/.openclaw/openclaw.json')
        if os.path.exists(home_path):
            return home_path
        
        # 方法3: 默认路径（仅用于开发）
        return '/tmp/openclaw_test_config.json'
    
    def get_global_api_config(self):
        """从OpenClaw全局配置读取API密钥"""
        # 动态获取OpenClaw配置路径
        global_config_path = self.get_openclaw_config_path()
        
        try:
            if os.path.exists(global_config_path):
                with open(global_config_path, 'r', encoding='utf-8') as f:
                    global_config = json.load(f)
                
                # 尝试从volcengine配置读取
                volcengine = global_config.get("models", {}).get("providers", {}).get("volcengine", {})
                if volcengine.get("apiKey"):
                    return {
                        "api_key": volcengine.get("apiKey"),
                        "base_url": volcengine.get("baseUrl", "https://ark.cn-beijing.volces.com/api/v3"),
                        "model": "doubao-seed-2-0-pro-260215"
                    }
                
                # 尝试从doubao配置读取
                doubao = global_config.get("models", {}).get("providers", {}).get("doubao", {})
                if doubao.get("apiKey"):
                    return {
                        "api_key": doubao.get("apiKey"),
                        "base_url": doubao.get("baseUrl", "https://ark.cn-beijing.volces.com/api/v3"),
                        "model": "doubao-seed-2-0-pro-260215"
                    }
                
                print("❌ 在全局配置中未找到豆包API密钥")
                # [安全] 已移除API密钥打印
                
        except Exception as e:
            print(f"❌ 读取全局配置失败: {e}")
        
        # 返回空配置
        return {
            "api_key": "",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model": "doubao-seed-2-0-pro-260215"
        }
    
    def set_api_key_from_env(self):
        """从环境变量读取API密钥（备选方案）"""
        api_key = os.getenv("DOUBAO_API_KEY") or os.getenv("VOLCENGINE_API_KEY")
        if api_key:
            self.api_config["api_key"] = api_key
            # [安全] 已移除API密钥打印
            return True
        return False
    
    def optimize_image(self, image_path, output_path=None):
        """优化图片尺寸和质量"""
        try:
            with Image.open(image_path) as img:
                # 获取原始尺寸
                width, height = img.size
                
                # 获取配置参数
                max_width = self.image_config.get("max_width", 768)
                max_height = self.image_config.get("max_height", 768)
                quality = self.image_config.get("quality", 85)
                
                # 调整尺寸（保持宽高比）
                if max(width, height) > max(max_width, max_height):
                    ratio = min(max_width/width, max_height/height)
                    new_size = (int(width * ratio), int(height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # 确定输出路径
                if not output_path:
                    output_path = f"/tmp/optimized_{int(time.time())}.jpg"
                
                # 保存优化后的图片
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                
                print(f"✅ 图片优化完成: {img.size} (原始: {width}x{height})")
                return output_path
                
        except Exception as e:
            print(f"❌ 图片优化失败: {e}")
            return image_path  # 返回原始路径
    
    def analyze_image(self, image_path, prompt, max_tokens=2000, temperature=0.7):
        """
        使用豆包视觉模型分析图片
        
        参数:
            image_path: 图片文件路径
            prompt: 分析提示词
            max_tokens: 最大输出token数
            temperature: 温度参数
        
        返回:
            dict: 包含分析结果和状态信息
        """
        # 检查API密钥
        api_key = self.api_config.get("api_key")
        if not api_key:
            # 尝试从环境变量获取
            if not self.set_api_key_from_env():
                return {
                    "success": False,
                    "error": "未配置豆包API密钥",
                    "suggestion": "请在OpenClaw全局配置中设置 models.providers.volcengine.apiKey"
                }
            api_key = self.api_config.get("api_key")
        
        # 检查图片文件
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图片文件不存在: {image_path}"
            }
        
        try:
            # 1. 优化图片
            print("🔄 优化图片...")
            optimized_path = self.optimize_image(image_path)
            
            # 2. 读取并编码图片
            print("🔄 编码图片...")
            with open(optimized_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            print(f"📊 图片数据: {len(image_data)} 字节, Base64: {len(image_base64)} 字符")
            
            # 3. 准备API请求
            api_request = {
                "model": self.api_config.get("model", "doubao-seed-2-0-pro-260215"),
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # 4. 调用API
            print("🚀 调用豆包视觉模型API...")
            base_url = self.api_config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=api_request,
                timeout=120  # 120秒超时
            )
            elapsed_time = time.time() - start_time
            
            print(f"✅ API响应时间: {elapsed_time:.2f}秒")
            print(f"📡 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # 提取分析内容
                if "choices" in result and len(result["choices"]) > 0:
                    analysis = result["choices"][0]["message"]["content"]
                    usage = result.get("usage", {})
                    
                    return {
                        "success": True,
                        "analysis": analysis,
                        "usage": {
                            "prompt_tokens": usage.get("prompt_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "total_tokens": usage.get("total_tokens")
                        },
                        "response_time": elapsed_time,
                        "image_size": len(image_data),
                        "optimized_path": optimized_path,
                        "api_source": "global_config"  # 标记API来源
                    }
                else:
                    return {
                        "success": False,
                        "error": "API响应格式异常",
                        "response": result
                    }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code}",
                    "response_text": response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "API调用超时（120秒）"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": f"连接错误: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"分析过程中出现错误: {type(e).__name__}: {e}"
            }
    
    def analyze_palm(self, image_path, detailed=True):
        """分析掌纹图片"""
        if detailed:
            prompt = """【玄机子掌纹分析专家指令】

请作为玄机子（风水大师智慧助手）专业分析这张掌纹图片，提供详细、专业的掌纹分析报告。

报告要求结构：

一、掌纹基础识别
1. 清晰识别并描述以下掌纹线：
   - 生命线（位置、长度、深度、清晰度、特殊特征）
   - 智慧线（位置、走向、与生命线关系、末端特征）
   - 感情线（位置、长度、形态、清晰度）
   - 其他重要掌纹线（事业线、财运线、健康线等）

二、掌相学专业分析
1. 性格特征与天赋才能分析
2. 健康状况评估与养生建议
3. 事业发展趋势与适合领域
4. 财运特征与理财建议
5. 感情婚姻状况与人际关系
6. 人生重要阶段提示

三、特殊纹路解读
1. 识别特殊纹路（十字纹、星纹、三角纹、岛纹等）
2. 分析特殊纹路的含义和影响
3. 掌丘发育情况与能量分布

四、五行八卦对应
1. 手掌各区域五行属性评估
2. 掌纹特征的八卦方位对应
3. 五行平衡状态与调理建议

五、综合运势报告
1. 当前运势状态评估
2. 优势领域与发展建议
3. 需要注意的方面与化解方法
4. 人生发展指导

请以专业、详细、实用的方式进行分析，结合传统掌相学智慧和现代心理学，提供正面、建设性的分析报告。"""
        else:
            prompt = "请分析这张掌纹图片，简要描述主要掌纹线特征，并提供简要的掌相学解读。"
        
        return self.analyze_image(image_path, prompt, max_tokens=3000 if detailed else 1500)
    
    def analyze_fengshui(self, image_path, scene_type="office"):
        """分析风水图片（办公室、家居等）"""
        prompts = {
            "office": """请分析这张办公室工位图片，提供专业的风水分析报告。

报告要求：
一、环境布局分析
1. 工位位置与朝向
2. 家具摆放与空间利用
3. 光线与通风情况

二、五行八卦分析
1. 各方位五行对应
2. 八卦方位能量评估
3. 五行平衡状态

三、风水问题识别
1. 有利的风水特征
2. 需要改善的问题
3. 冲煞与化解方法

四、优化建议
1. 布局调整建议
2. 五行平衡建议
3. 能量提升方法

请以专业风水师的角度进行分析，提供实用、可操作的改进建议。""",
            
            "home": """请分析这张家居环境图片，提供专业的风水分析报告。

报告要求：
一、整体环境分析
1. 房屋格局与朝向
2. 功能区划分
3. 能量流动路径

二、五行八卦分析
1. 各房间五行属性
2. 八卦方位对应
3. 能量平衡评估

三、风水优化建议
1. 布局调整方案
2. 色彩搭配建议
3. 装饰物品选择

请提供专业、详细的风水分析报告。"""
        }
        
        prompt = prompts.get(scene_type, prompts["office"])
        return self.analyze_image(image_path, prompt, max_tokens=2500)
    
    def analyze_general(self, image_path, description):
        """通用图片分析"""
        prompt = f"请分析这张图片：{description}\n\n请提供详细、专业的分析报告。"
        return self.analyze_image(image_path, prompt, max_tokens=2000)


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 doubao_vision_global.py <图片路径> [分析类型]")
        print("")
        print("分析类型:")
        print("  palm       掌纹分析（默认）")
        print("  palm-brief 简要掌纹分析")
        print("  office     办公室风水分析")
        print("  home       家居风水分析")
        print("  custom     自定义分析（需提供描述）")
        print("")
        print("示例:")
        print("  python3 doubao_vision_global.py /tmp/palm.jpg palm")
        print("  python3 doubao_vision_global.py /tmp/office.jpg office")
        print("")
        print("⚠️  API密钥从OpenClaw全局配置自动读取")
        print("    配置文件: ~/.openclaw/openclaw.json")
        return
    
    image_path = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "palm"
    
    print("🧭 玄机子·豆包视觉分析（全局配置版）")
    print("=" * 50)
    print("🔒 API密钥来源: OpenClaw全局配置")
    
    # 初始化分析器
    analyzer = DoubaoVisionGlobalAnalyzer()
    
    # 显示API密钥状态
    api_key = analyzer.api_config.get("api_key", "")
    if api_key:
        print("✅ API密钥已配置")
    else:
        print("❌ API密钥未配置")
        return
    
    # 执行分析
    if analysis_type == "palm":
        print("🖐️ 执行详细掌纹分析...")
        result = analyzer.analyze_palm(image_path, detailed=True)
    elif analysis_type == "palm-brief":
        print("🖐️ 执行简要掌纹分析...")
        result = analyzer.analyze_palm(image_path, detailed=False)
    elif analysis_type == "office":
        print("🏢 执行办公室风水分析...")
        result = analyzer.analyze_fengshui(image_path, "office")
    elif analysis_type == "home":
        print("🏠 执行家居风水分析...")
        result = analyzer.analyze_fengshui(image_path, "home")
    elif analysis_type == "custom" and len(sys.argv) > 3:
        description = " ".join(sys.argv[3:])
        print(f"📸 执行自定义分析: {description}")
        result = analyzer.analyze_general(image_path, description)
    else:
        print("❌ 无效的分析类型")
        return
    
    # 输出结果
    print("\n" + "=" * 50)
    print("分析结果:")
    print("=" * 50)
    
    if result["success"]:
        print("✅ 分析成功!")
        print(f"⏱️  响应时间: {result.get('response_time', 0):.2f}秒")
        print(f"🔒 API来源: {result.get('api_source', 'global_config')}")
        
        usage = result.get("usage", {})
        if usage:
            print(f"📊 API用量: 输入{usage.get('prompt_tokens')}, 输出{usage.get('completion_tokens')}, 总计{usage.get('total_tokens')}")
        
        print("\n📋 分析报告:")
        print("-" * 50)
        print(result["analysis"])
        print("-" * 50)
        
        # 保存到文件
        timestamp = int(time.time())
        report_file = f"/tmp/analysis_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("玄机子·豆包视觉分析报告（全局配置版）\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"图片路径: {image_path}\n")
            f.write(f"分析类型: {analysis_type}\n")
            f.write(f"API来源: {result.get('api_source', 'global_config')}\n")
            f.write(f"响应时间: {result.get('response_time', 0):.2f}秒\n")
            f.write("\n" + "=" * 50 + "\n\n")
            f.write(result["analysis"])
            f.write("\n" + "=" * 50 + "\n")
        
        print(f"\n💾 报告已保存到: {report_file}")
    else:
        error_msg = result.get('error', '未知错误')
        print(f"❌ 分析失败: {error_msg}")
        if "response_text" in result:
            print(f"响应: {result['response_text'][:200]}")


if __name__ == "__main__":
    main()