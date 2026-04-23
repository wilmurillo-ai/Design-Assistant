#!/usr/bin/env python3
"""
玄机子·通用图片分析脚本
基于豆包视觉模型的专业图片分析系统
支持各种图片类型：环境、物品、人物、场景等
"""

import sys
import os
import json
import base64
import time
from PIL import Image
import requests

def compress_image_keep_original(image_path, max_dimension=1024, quality=85):
    """
    压缩图片但保持原貌
    保持原始比例，只减小尺寸和文件大小
    """
    print(f"📸 压缩图片: {os.path.basename(image_path)}")
    print(f"   原则: 保持原貌，只减小尺寸")
    
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            original_format = img.format
            original_mode = img.mode
            
            print(f"   原始尺寸: {original_width}x{original_height}")
            print(f"   原始格式: {original_format}")
            print(f"   原始模式: {original_mode}")
            
            # 计算压缩后的尺寸（保持比例）
            if max(original_width, original_height) > max_dimension:
                ratio = max_dimension / max(original_width, original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # 使用高质量重采样保持清晰度
                compressed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"   压缩后尺寸: {new_width}x{new_height}")
                print(f"   压缩比例: {ratio:.2%}")
            else:
                # 图片已经小于最大尺寸，不改变尺寸
                compressed_img = img.copy()
                new_width, new_height = original_width, original_height
                print(f"   尺寸不变: {new_width}x{new_height} (已小于{max_dimension}px)")
            
            # 保存压缩后的图片（保持原格式）
            compressed_path = f"/tmp/compressed_image_{int(time.time())}.jpg"
            
            # 保存参数
            save_params = {'quality': quality, 'optimize': True, 'progressive': True}
            compressed_img.save(compressed_path, 'JPEG', **save_params)
            
            # 验证压缩结果
            compressed_size = os.path.getsize(compressed_path)
            original_size = os.path.getsize(image_path)
            compression_ratio = compressed_size / original_size
            
            print(f"   原始大小: {original_size:,}字节")
            print(f"   压缩后大小: {compressed_size:,}字节")
            print(f"   压缩率: {compression_ratio:.2%}")
            print(f"   保存路径: {compressed_path}")
            
            return compressed_path, new_width, new_height
            
    except Exception as e:
        print(f"❌ 压缩图片时出错: {e}")
        return None, None, None

def get_global_api_config():
    """
    从OpenClaw全局配置读取API密钥
    安全架构：密钥不硬编码在技能文件中
    """
    try:
        # 动态获取OpenClaw配置路径
        global_config_path = self.get_openclaw_config_path()
        with open(global_config_path, 'r') as f:
            global_config = json.load(f)
        
        # 从volcengine或doubao配置读取
        providers = global_config.get("models", {}).get("providers", {})
        
        # 优先使用volcengine配置
        if "volcengine" in providers:
            config = providers["volcengine"]
            print("✅ 从全局配置读取volcengine API密钥")
            return config
        
        # 备选：使用doubao配置
        elif "doubao" in providers:
            config = providers["doubao"]
            print("✅ 从全局配置读取doubao API密钥")
            return config
        
        else:
            print("❌ 在全局配置中未找到volcengine或doubao配置")
            return None
            
    except Exception as e:
        print(f"❌ 读取全局配置时出错: {e}")
        print("💡 请检查 ~/.openclaw/openclaw.json 配置文件")
        return None

def analyze_image_with_doubao(image_path, analysis_type="general"):
    """
    使用豆包视觉模型分析图片
    analysis_type: general(通用), environment(环境), object(物品), person(人物), scene(场景)
    """
    print(f"\n🔍 开始分析图片: {os.path.basename(image_path)}")
    print(f"   分析类型: {analysis_type}")
    
    # 1. 压缩图片（保持原貌）
    compressed_path, new_width, new_height = compress_image_keep_original(image_path)
    if not compressed_path:
        return None
    
    # 2. 读取全局API配置
    api_config = get_global_api_config()
    if not api_config:
        return None
    
    # 3. 准备API请求
    api_key = api_config.get("apiKey")
    base_url = api_config.get("baseUrl", "https://ark.cn-beijing.volces.com/api/v3")
    model = api_config.get("model", "doubao-seed-2-0-pro-260215")
    
    # 4. 读取并编码图片
    with open(compressed_path, "rb") as f:
        image_data = f.read()
    
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # 5. 根据分析类型准备提示词
    if analysis_type == "environment":
        prompt = """【玄机子·环境分析指令】
请详细分析这张图片中的环境场景：

1. **场景识别**：这是什么地方？（办公室、家居、户外、商业场所等）
2. **环境特征**：空间布局、光线、色彩、装饰风格
3. **功能分析**：空间的主要功能和用途
4. **氛围评估**：环境给人的感觉（舒适、专业、温馨、现代等）
5. **优化建议**：如何改善或优化这个环境
6. **风水元素**（可选）：如果有明显的风水元素，请分析

请提供专业、详细的分析报告。"""
    
    elif analysis_type == "object":
        prompt = """【玄机子·物品分析指令】
请详细分析这张图片中的物品：

1. **物品识别**：这是什么物品？品牌、型号、材质
2. **功能分析**：物品的主要功能和用途
3. **设计评估**：外观设计、工艺质量、美学价值
4. **使用状态**：物品的新旧程度、使用痕迹
5. **价值评估**：市场价值、实用价值、收藏价值
6. **改进建议**：如何更好地使用或维护这个物品

请提供专业、详细的分析报告。"""
    
    elif analysis_type == "person":
        prompt = """【玄机子·人物分析指令】
请详细分析这张图片中的人物：

1. **基本信息**：年龄范围、性别、大致职业
2. **外貌特征**：面部特征、体型、衣着风格
3. **表情神态**：表情、眼神、姿态传达的信息
4. **环境关系**：人物与环境的互动关系
5. **气质评估**：人物给人的整体印象和气质
6. **专业建议**：形象提升或优化建议

注意：尊重隐私，仅分析可见特征。"""
    
    elif analysis_type == "scene":
        prompt = """【玄机子·场景分析指令】
请详细分析这张图片中的场景：

1. **场景类型**：这是什么类型的场景？（自然风光、城市景观、活动场景等）
2. **构图分析**：画面构图、视角、焦点
3. **色彩光线**：色彩搭配、光线效果、氛围营造
4. **故事性**：场景传达的故事或情感
5. **美学价值**：艺术价值、拍摄技巧
6. **改进建议**：如何更好地表现这个场景

请提供专业、详细的分析报告。"""
    
    else:  # general
        prompt = """【玄机子·通用图片分析指令】
请详细分析这张图片：

1. **内容识别**：图片中有什么？主要元素和次要元素
2. **场景理解**：这是什么场景？在什么环境下拍摄的？
3. **技术分析**：拍摄角度、光线、构图、色彩
4. **情感氛围**：图片传达的情感或氛围
5. **细节观察**：注意到哪些有趣的细节
6. **综合评估**：对图片的整体评价和分析

请提供专业、详细的分析报告。"""
    
    # 6. 构建请求数据
    request_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.7,
        "timeout": 120
    }
    
    # 7. 发送API请求
    print(f"🌐 调用豆包视觉模型...")
    print(f"   模型: {model}")
    # [安全] 已移除API密钥打印
    print(f"   超时: 120秒")
    
    start_time = time.time()
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        api_url = f"{base_url}/chat/completions"
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=120
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            analysis_result = result["choices"][0]["message"]["content"]
            
            # 提取token使用信息
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
            
            print(f"✅ 分析完成！")
            print(f"   响应时间: {response_time:.2f}秒")
            # [安全] 已移除API密钥打印
            print(f"   状态码: {response.status_code}")
            
            return {
                "analysis": analysis_result,
                "response_time": response_time,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "image_info": {
                    "original": os.path.basename(image_path),
                    "compressed": os.path.basename(compressed_path),
                    "dimensions": f"{new_width}x{new_height}",
                    "analysis_type": analysis_type
                }
            }
            
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"❌ API调用超时（120秒）")
        return None
    except Exception as e:
        print(f"❌ API调用出错: {e}")
        return None

def save_analysis_report(result, output_path=None):
    """保存分析报告到文件"""
    if not result:
        return None
    
    if not output_path:
        timestamp = int(time.time())
        output_path = f"/tmp/image_analysis_report_{timestamp}.txt"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("玄机子·图片分析报告\n")
            f.write("=" * 60 + "\n\n")
            
            # 图片信息
            f.write("📸 图片信息\n")
            f.write("-" * 40 + "\n")
            image_info = result["image_info"]
            f.write(f"原始图片: {image_info['original']}\n")
            f.write(f"压缩后图片: {image_info['compressed']}\n")
            f.write(f"图片尺寸: {image_info['dimensions']}\n")
            f.write(f"分析类型: {image_info['analysis_type']}\n\n")
            
            # 技术信息
            f.write("⚙️ 技术信息\n")
            f.write("-" * 40 + "\n")
            f.write(f"响应时间: {result['response_time']:.2f}秒\n")
            tokens = result["tokens"]
            f.write(f"Token使用: 输入{tokens['input']} + 输出{tokens['output']} = 总计{tokens['total']}\n\n")
            
            # 分析结果
            f.write("🔍 分析结果\n")
            f.write("-" * 40 + "\n")
            f.write(result["analysis"])
            f.write("\n\n")
            
            # 报告信息
            f.write("=" * 60 + "\n")
            f.write(f"报告生成时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n")
            f.write(f"分析系统: 玄机子通用图片分析系统\n")
            f.write("=" * 60 + "\n")
        
        print(f"📄 分析报告已保存: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ 保存报告时出错: {e}")
        return None

def main():
    """主函数"""
    print("🧭 玄机子·通用图片分析系统")
    print("=" * 50)
    
    # 检查参数
    if len(sys.argv) < 2:
        print("使用方法: python3 analyze_general_image.py <图片路径> [分析类型]")
        print("分析类型: general(默认), environment, object, person, scene")
        print("示例: python3 analyze_general_image.py /path/to/image.jpg environment")
        return
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ 图片不存在: {image_path}")
        return
    
    # 确定分析类型
    analysis_type = "general"
    if len(sys.argv) >= 3:
        analysis_type = sys.argv[2]
        if analysis_type not in ["general", "environment", "object", "person", "scene"]:
            print(f"⚠️ 未知的分析类型: {analysis_type}，使用默认值: general")
            analysis_type = "general"
    
    # 分析图片
    result = analyze_image_with_doubao(image_path, analysis_type)
    
    if result:
        # 保存报告
        report_path = save_analysis_report(result)
        
        # 显示分析结果摘要
        print("\n" + "=" * 50)
        print("📋 分析结果摘要")
        print("=" * 50)
        print(f"图片: {os.path.basename(image_path)}")
        print(f"类型: {analysis_type}")
        print(f"耗时: {result['response_time']:.2f}秒")
        # [安全] 已移除API密钥打印
        print(f"报告: {report_path}")
        print("\n📝 分析内容预览:")
        print("-" * 40)
        
        # 显示前500字符的预览
        analysis_text = result["analysis"]
        preview = analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text
        print(preview)
        
    else:
        print("❌ 图片分析失败")

if __name__ == "__main__":
    main()