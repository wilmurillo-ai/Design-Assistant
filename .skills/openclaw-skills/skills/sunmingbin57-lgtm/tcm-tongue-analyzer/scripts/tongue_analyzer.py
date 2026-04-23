#!/usr/bin/env python3
"""
中医舌象分析核心脚本
功能：自动分析舌象照片，提供中医辨证建议
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 模拟分析函数（实际版本将使用深度学习模型）
def analyze_tongue_image(image_path):
    """
    分析舌象照片
    
    参数：
        image_path: 舌象照片路径
        
    返回：
        分析结果字典
    """
    # 检查文件是否存在
    if not os.path.exists(image_path):
        return {"error": f"文件不存在: {image_path}"}
    
    # 获取文件信息
    file_stats = os.stat(image_path)
    file_size_mb = file_stats.st_size / (1024 * 1024)
    
    # 模拟分析结果（实际版本将进行真实图像分析）
    # 这里使用基于文件名的简单模拟
    filename = os.path.basename(image_path).lower()
    
    # 根据文件名关键词模拟不同舌象
    analysis_result = {
        "image_info": {
            "filename": os.path.basename(image_path),
            "path": image_path,
            "size_mb": round(file_size_mb, 2),
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "tongue_analysis": {
            "tongue_color": "淡红",
            "color_confidence": 0.85,
            "tongue_shape": "正常",
            "shape_confidence": 0.82,
            "coating_color": "薄白",
            "coating_texture": "润",
            "coating_confidence": 0.78,
            "special_features": [],
            "features_confidence": 0.90
        },
        "tcm_diagnosis": {
            "pattern": "脾气虚弱证",
            "confidence": 0.75,
            "secondary_patterns": ["轻度湿浊内停"],
            "explanations": [
                "舌淡红提示轻度气虚",
                "舌形正常提示无明显形态异常",
                "薄白苔提示表证或正常"
            ]
        },
        "recommendations": {
            "formulas": ["运中补土", "祛湿降浊"],
            "acupoints": ["足三里", "阴陵泉", "中脘", "脾俞"],
            "lifestyle": [
                "饮食宜温补，避免生冷",
                "适当运动，增强脾胃功能",
                "保持情绪舒畅，避免思虑过度"
            ]
        }
    }
    
    # 根据文件名调整模拟结果
    if "red" in filename or "红" in filename:
        analysis_result["tongue_analysis"]["tongue_color"] = "红"
        analysis_result["tcm_diagnosis"]["pattern"] = "热证"
        analysis_result["tcm_diagnosis"]["explanations"].append("舌红提示热证")
        
    if "pale" in filename or "淡白" in filename:
        analysis_result["tongue_analysis"]["tongue_color"] = "淡白"
        analysis_result["tcm_diagnosis"]["pattern"] = "阳虚证"
        analysis_result["tcm_diagnosis"]["explanations"].append("舌淡白提示阳虚")
        
    if "swollen" in filename or "胖大" in filename:
        analysis_result["tongue_analysis"]["tongue_shape"] = "胖大"
        analysis_result["tcm_diagnosis"]["secondary_patterns"].append("水湿内停")
        
    if "teeth" in filename or "齿痕" in filename:
        analysis_result["tongue_analysis"]["tongue_shape"] = "齿痕"
        analysis_result["tcm_diagnosis"]["secondary_patterns"].append("脾虚湿盛")
    
    return analysis_result

def generate_report(result, output_format="text"):
    """
    生成分析报告
    
    参数：
        result: 分析结果字典
        output_format: 输出格式（text/json/html）
        
    返回：
        格式化报告
    """
    if "error" in result:
        return f"错误: {result['error']}"
    
    if output_format == "json":
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    # 文本格式报告
    report = []
    report.append("=" * 50)
    report.append("中医舌象分析报告")
    report.append("=" * 50)
    report.append("")
    
    # 患者信息
    report.append("【患者信息】")
    report.append(f"  文件: {result['image_info']['filename']}")
    report.append(f"  大小: {result['image_info']['size_mb']} MB")
    report.append(f"  分析时间: {result['image_info']['analysis_time']}")
    report.append("")
    
    # 舌象分析
    report.append("【舌象分析】")
    tongue = result['tongue_analysis']
    report.append(f"  舌色: {tongue['tongue_color']} (置信度: {tongue['color_confidence']*100:.1f}%)")
    report.append(f"  舌形: {tongue['tongue_shape']} (置信度: {tongue['shape_confidence']*100:.1f}%)")
    report.append(f"  舌苔: {tongue['coating_color']}{tongue['coating_texture']} (置信度: {tongue['coating_confidence']*100:.1f}%)")
    
    if tongue['special_features']:
        report.append(f"  特殊特征: {', '.join(tongue['special_features'])}")
    report.append("")
    
    # 中医辨证
    report.append("【中医辨证】")
    diagnosis = result['tcm_diagnosis']
    report.append(f"  主证: {diagnosis['pattern']} (置信度: {diagnosis['confidence']*100:.1f}%)")
    
    if diagnosis['secondary_patterns']:
        report.append(f"  兼证: {', '.join(diagnosis['secondary_patterns'])}")
    
    report.append("")
    report.append("  辨证依据:")
    for i, explanation in enumerate(diagnosis['explanations'], 1):
        report.append(f"  {i}. {explanation}")
    report.append("")
    
    # 治疗建议
    report.append("【治疗建议】")
    rec = result['recommendations']
    report.append("  推荐组方:")
    for formula in rec['formulas']:
        report.append(f"  • {formula}")
    
    report.append("")
    report.append("  推荐穴位 (4穴):")
    for acupoint in rec['acupoints']:
        report.append(f"  • {acupoint}")
    
    report.append("")
    report.append("  生活调理:")
    for i, tip in enumerate(rec['lifestyle'], 1):
        report.append(f"  {i}. {tip}")
    
    report.append("")
    report.append("=" * 50)
    report.append("免责声明: 本分析结果仅供参考，临床决策请咨询执业中医师")
    report.append("=" * 50)
    
    return "\n".join(report)

def batch_analyze(folder_path, output_format="text"):
    """
    批量分析文件夹中的舌象照片
    
    参数：
        folder_path: 文件夹路径
        output_format: 输出格式
        
    返回：
        批量分析结果
    """
    if not os.path.exists(folder_path):
        return {"error": f"文件夹不存在: {folder_path}"}
    
    results = []
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in image_extensions):
            result = analyze_tongue_image(file_path)
            results.append(result)
    
    if not results:
        return {"error": "文件夹中没有找到图片文件"}
    
    # 生成汇总报告
    summary = {
        "total_images": len(results),
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "results": results
    }
    
    if output_format == "json":
        return json.dumps(summary, ensure_ascii=False, indent=2)
    
    # 文本格式汇总
    report = []
    report.append("=" * 50)
    report.append(f"批量舌象分析报告 - 共 {len(results)} 张照片")
    report.append("=" * 50)
    report.append("")
    
    for i, result in enumerate(results, 1):
        if "error" in result:
            report.append(f"{i}. {result['error']}")
        else:
            tongue = result['tongue_analysis']
            diagnosis = result['tcm_diagnosis']
            report.append(f"{i}. {result['image_info']['filename']}")
            report.append(f"   舌象: {tongue['tongue_color']}舌, {tongue['tongue_shape']}形, {tongue['coating_color']}苔")
            report.append(f"   辨证: {diagnosis['pattern']}")
            report.append("")
    
    report.append("=" * 50)
    return "\n".join(report)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="中医舌象分析工具")
    parser.add_argument("--image", help="舌象照片路径")
    parser.add_argument("--folder", help="舌象照片文件夹路径（批量分析）")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text", 
                       help="输出格式（默认: text）")
    parser.add_argument("--output", help="输出文件路径（可选）")
    
    args = parser.parse_args()
    
    if not args.image and not args.folder:
        parser.print_help()
        print("\n示例:")
        print("  分析单张照片: python tongue_analyzer.py --image 舌象.jpg")
        print("  批量分析: python tongue_analyzer.py --folder 舌象文件夹")
        return
    
    try:
        if args.image:
            result = analyze_tongue_image(args.image)
            report = generate_report(result, args.format)
        elif args.folder:
            report = batch_analyze(args.folder, args.format)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        else:
            print(report)
            
    except Exception as e:
        print(f"分析过程中出现错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()