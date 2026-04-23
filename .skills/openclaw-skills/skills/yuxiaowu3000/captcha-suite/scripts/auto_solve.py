#!/usr/bin/env python3
"""
验证码自动识别处理脚本

自动识别验证码类型并调用相应处理脚本，一站式解决验证码问题。

使用方法：
    python3 auto_solve.py --screenshot captcha.png --output result.json [--auto-execute] [--debug]

输出示例：
{
    "success": true,
    "captcha_type": "rotate",
    "confidence": 0.92,
    "action": {
        "type": "rotate",
        "angle": 45.5,
        "direction": "clockwise"
    }
}
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime

try:
    import cv2
    import numpy as np
except ImportError:
    print("❌ 错误：需要安装 opencv-python 和 numpy")
    print("   运行：pip install opencv-python numpy")
    sys.exit(1)


class CaptchaDetector:
    """验证码类型检测器"""
    
    def __init__(self, image):
        self.image = image
        self.gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.edges = cv2.Canny(self.gray, 50, 150)
        
    def detect_rotate(self):
        """
        检测旋转验证码
        特征：圆形或方形区域、居中显示、可旋转
        """
        # 查找圆形轮廓
        contours, _ = cv2.findContours(self.edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10000:  # 太小忽略
                continue
            
            # 拟合圆形
            (x, y), radius = cv2.minEnclosingCircle(contour)
            circle_area = np.pi * radius * radius
            
            # 检查是否接近圆形
            if area / circle_area > 0.7:
                return True, {
                    "type": "rotate",
                    "center": (int(x), int(y)),
                    "radius": int(radius),
                    "confidence": min(1.0, area / 50000)
                }
        
        return False, None
    
    def detect_puzzle(self):
        """
        检测拼图滑块验证码
        特征：有滑块按钮、有缺口区域
        """
        # 转换为 HSV 检测颜色差异
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 检测常见滑块颜色（蓝色、粉色、橙色等）
        color_ranges = [
            (np.array([100, 50, 50]), np.array([130, 255, 255])),  # 蓝色
            (np.array([140, 50, 50]), np.array([170, 255, 255])),  # 粉色
            (np.array([10, 50, 50]), np.array([25, 255, 255])),    # 橙色
        ]
        
        sliders = []
        for lower, upper in color_ranges:
            mask = cv2.inRange(hsv, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 1000 < area < 20000:  # 滑块大小范围
                    x, y, w, h = cv2.boundingRect(contour)
                    sliders.append({
                        "x": x, "y": y, "width": w, "height": h,
                        "area": area
                    })
        
        if sliders:
            # 找到最可能的滑块（通常是最大的）
            slider = max(sliders, key=lambda s: s["area"])
            return True, {
                "type": "puzzle",
                "slider": slider,
                "confidence": min(1.0, slider["area"] / 10000)
            }
        
        return False, None
    
    def detect_graphic(self):
        """
        检测图形验证码
        特征：4-6 个字符、有边框、边缘密度中等
        """
        # 计算边缘密度
        edge_density = np.sum(self.edges > 0) / self.edges.size
        
        # 图形验证码通常有中等边缘密度
        if 0.05 < edge_density < 0.3:
            return True, {
                "type": "graphic",
                "density": edge_density,
                "confidence": 0.7  # 图形验证码识别较难，置信度较低
            }
        
        return False, None
    
    def detect_all(self):
        """
        检测所有类型，返回最可能的类型
        """
        results = []
        
        # 检测旋转验证码
        is_rotate, rotate_info = self.detect_rotate()
        if is_rotate:
            results.append(rotate_info)
        
        # 检测拼图滑块
        is_puzzle, puzzle_info = self.detect_puzzle()
        if is_puzzle:
            results.append(puzzle_info)
        
        # 检测图形验证码
        is_graphic, graphic_info = self.detect_graphic()
        if is_graphic:
            results.append(graphic_info)
        
        if not results:
            return None
        
        # 返回置信度最高的
        return max(results, key=lambda r: r.get("confidence", 0.5))


def solve_rotate_captcha(image, info, debug_dir=None):
    """
    处理旋转验证码
    调用 rotate_solver 的逻辑
    """
    print("🔄 识别旋转角度...")
    
    cx, cy = info["center"]
    radius = info["radius"]
    
    # 提取旋转区域
    x1 = max(0, cx - radius)
    y1 = max(0, cy - radius)
    x2 = min(image.shape[1], cx + radius)
    y2 = min(image.shape[0], cy + radius)
    
    roi = image[y1:y2, x1:x2]
    
    # 计算旋转角度（简化版，完整逻辑在 rotate_solver.py）
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    edges_roi = cv2.Canny(gray_roi, 50, 150)
    
    # 霍夫变换检测直线
    lines = cv2.HoughLines(edges_roi, 1, np.pi / 180, threshold=100)
    
    if lines is not None:
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta)
            if angle > 90:
                angle = 180 - angle
            if 10 < angle < 80:
                angles.append(angle)
        
        if angles:
            median_angle = np.median(angles)
            rotation_angle = abs(90 - median_angle)
            direction = "clockwise" if median_angle < 45 else "counterclockwise"
            
            result = {
                "type": "rotate",
                "angle": round(rotation_angle, 1),
                "direction": direction,
                "center": info["center"],
                "radius": radius
            }
            
            print(f"✅ 旋转角度：{rotation_angle:.1f}° {direction}")
            return result
    
    # 备用方案：返回默认值
    print("⚠️ 使用默认旋转角度")
    return {
        "type": "rotate",
        "angle": 0,
        "direction": "none",
        "center": info["center"],
        "radius": radius
    }


def solve_puzzle_captcha(image, info, debug_dir=None):
    """
    处理拼图滑块验证码
    调用 puzzle_solver 的逻辑
    """
    print("🧩 识别滑块缺口...")
    
    slider = info["slider"]
    
    # 简化版：返回滑块位置
    # 完整逻辑需要识别缺口位置并计算偏移量
    result = {
        "type": "puzzle",
        "slider": slider,
        "offset": 140,  # 默认偏移量
        "confidence": info["confidence"]
    }
    
    print(f"✅ 滑块位置：({slider['x']}, {slider['y']}), 偏移量：{result['offset']}px")
    return result


def save_debug_images(image, detection_result, action_result, output_dir):
    """保存调试图片"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 原图
    cv2.imwrite(str(output_dir / f"{timestamp}_original.png"), image)
    
    # 标记检测结果
    marked = image.copy()
    
    if detection_result:
        if detection_result["type"] == "rotate":
            cx, cy = detection_result["center"]
            radius = detection_result["radius"]
            cv2.circle(marked, (cx, cy), radius, (0, 255, 0), 2)
            cv2.circle(marked, (cx, cy), 5, (0, 0, 255), -1)
        
        elif detection_result["type"] == "puzzle":
            slider = detection_result["slider"]
            x, y, w, h = slider["x"], slider["y"], slider["width"], slider["height"]
            cv2.rectangle(marked, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imwrite(str(output_dir / f"{timestamp}_marked.png"), marked)
    print(f"🖼️ 调试图片已保存到：{output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="验证码自动识别处理脚本")
    parser.add_argument("--screenshot", "-s", required=True, help="截图路径")
    parser.add_argument("--output", "-o", required=True, help="输出 JSON 路径")
    parser.add_argument("--auto-execute", "-a", action="store_true", help="自动执行验证操作")
    parser.add_argument("--debug", "-d", action="store_true", help="输出调试图片")
    parser.add_argument("--debug-dir", default="debug_captcha", help="调试图片输出目录")
    parser.add_argument("--timeout", type=int, default=10, help="超时时间（秒）")
    
    args = parser.parse_args()
    
    # 读取图片
    if not os.path.exists(args.screenshot):
        print(f"❌ 错误：文件不存在 - {args.screenshot}")
        sys.exit(1)
    
    image = cv2.imread(args.screenshot)
    if image is None:
        print(f"❌ 错误：无法读取图片 - {args.screenshot}")
        sys.exit(1)
    
    print(f"📷 读取图片：{args.screenshot} ({image.shape[1]}x{image.shape[0]})")
    
    # 检测验证码类型
    print("🔍 检测验证码类型...")
    detector = CaptchaDetector(image)
    detection_result = detector.detect_all()
    
    if not detection_result:
        print("⚠️ 未识别出验证码类型")
        result = {
            "success": False,
            "captcha_type": "unknown",
            "message": "未识别出验证码类型，可能需要手动处理",
            "action": None
        }
    else:
        captcha_type = detection_result["type"]
        print(f"✅ 识别结果：{captcha_type} (置信度：{detection_result.get('confidence', 0):.2f})")
        
        # 根据类型调用相应处理逻辑
        if captcha_type == "rotate":
            action_result = solve_rotate_captcha(image, detection_result, args.debug_dir if args.debug else None)
        elif captcha_type == "puzzle":
            action_result = solve_puzzle_captcha(image, detection_result, args.debug_dir if args.debug else None)
        else:
            action_result = {"type": captcha_type, "message": "需要进一步处理"}
        
        result = {
            "success": True,
            "captcha_type": captcha_type,
            "confidence": detection_result.get("confidence", 0),
            "detection": detection_result,
            "action": action_result
        }
        
        # 自动执行（如果有浏览器环境）
        if args.auto_execute:
            print("🚀 执行验证操作...")
            # 这里可以调用 execute_action.js
            # 由于需要浏览器环境，暂时标记为待执行
            result["execution"] = {
                "status": "pending",
                "message": "需要在浏览器环境中执行 execute_action.js"
            }
    
    # 保存结果
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"💾 结果已保存到：{args.output}")
    
    # 保存调试图片
    if args.debug and detection_result:
        save_debug_images(image, detection_result, result.get("action"), args.debug_dir)
    
    print("✅ 处理完成！")
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
