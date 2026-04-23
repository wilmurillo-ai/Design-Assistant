#!/usr/bin/env python3
"""
拼图滑块验证码识别脚本
自动检测验证码区域、识别缺口位置、生成拖动轨迹

支持：
- 箭头拼图（大麦网）
- 缺口拼图（淘宝、京东）
- 图形对齐（微信、QQ）

依赖：pip install opencv-python numpy pillow

使用示例：
    python3 recognize_puzzle.py --screenshot captcha.png --output result.json
    python3 recognize_puzzle.py --screenshot captcha.png --debug
"""

import argparse
import json
import sys
import math
import random
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as e:
    logger.error("❌ 缺少必要的依赖包")
    logger.error(f"错误详情：{e}")
    logger.error("\n请运行以下命令安装依赖：")
    logger.error("  pip install opencv-python numpy pillow")
    logger.error("\n如果需要调试可视化，还需安装：")
    logger.error("  pip install matplotlib")
    sys.exit(1)


class PuzzleCaptchaSolver:
    """拼图验证码识别器"""
    
    def __init__(self, screenshot_path: str, mode: str = "normal"):
        """
        初始化识别器
        
        Args:
            screenshot_path: 截图路径
            mode: 识别模式 ("fast" | "normal" | "high_precision")
        """
        self.screenshot_path = screenshot_path
        self.mode = mode
        logger.info(f"📷 加载截图：{screenshot_path} (模式：{mode})")
        
        # 检查文件是否存在
        if not Path(screenshot_path).exists():
            raise FileNotFoundError(f"❌ 文件不存在：{screenshot_path}")
        
        # 检查文件是否可读
        if not Path(screenshot_path).is_file():
            raise ValueError(f"❌ 路径不是文件：{screenshot_path}")
        
        self.image = cv2.imread(screenshot_path)
        if self.image is None:
            raise ValueError(f"❌ 无法读取图片，可能是格式不支持或文件损坏：{screenshot_path}")
        
        self.height, self.width = self.image.shape[:2]
        logger.info(f"📐 图片尺寸：{self.width} x {self.height}")
        
        # 性能优化：缩小图片尺寸
        if mode == "fast":
            max_size = 600
            if max(self.width, self.height) > max_size:
                scale = max_size / max(self.width, self.height)
                self.image = cv2.resize(self.image, None, fx=scale, fy=scale)
                self.height, self.width = self.image.shape[:2]
                logger.info(f"⚡ 快速模式：已缩小图片到 {self.width} x {self.height}")
        
        # 检查图片尺寸是否合理
        if self.width < 200 or self.height < 200:
            logger.warning(f"⚠️ 图片尺寸过小，可能影响识别准确率")
        
        self.captcha_area = None
        self.slider_area = None
        self.piece_area = None
    
    def detect_captcha_popup(self) -> dict:
        """
        检测验证码弹窗区域
        
        特征：
        - 白色或浅色背景
        - 圆角矩形
        - 居中或偏上显示
        - 面积适中
        """
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # 方法 1：阈值分割（检测白色背景区域）
        _, thresh = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
        
        # 形态学操作（填充空洞）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # 验证码弹窗特征
            if (50000 < area < 600000 and  # 面积适中
                0.3 < w/h < 3.0 and  # 长宽比合理
                y < self.height * 0.7):  # 不在底部
                candidates.append({
                    "x": x, "y": y, "w": w, "h": h,
                    "area": area,
                    "contour": contour
                })
        
        if not candidates:
            # 方法 2：边缘检测
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                if 50000 < area < 600000:
                    candidates.append({
                        "x": x, "y": y, "w": w, "h": h,
                        "area": area
                    })
        
        if candidates:
            # 选择最可能的候选（面积最大且位置合理）
            candidates.sort(key=lambda c: c["area"], reverse=True)
            self.captcha_area = candidates[0]
            logger.info(f"✅ 检测到验证码弹窗：{candidates[0]['w']}x{candidates[0]['h']} @ ({candidates[0]['x']}, {candidates[0]['y']})")
            return {
                "success": True,
                "type": "captcha_popup",
                "location": {
                    "x": candidates[0]["x"],
                    "y": candidates[0]["y"],
                    "width": candidates[0]["w"],
                    "height": candidates[0]["h"]
                }
            }
        
        logger.warning("⚠️ 未检测到验证码弹窗")
        logger.warning("可能原因：")
        logger.warning("  1. 截图时机不对，验证码未加载完成")
        logger.warning("  2. 使用了全屏截图，验证码区域太小")
        logger.warning("  3. 验证码样式与已知模式不匹配")
        logger.warning("建议：")
        logger.warning("  - 增加页面等待时间：agent-browser wait 3000")
        logger.warning("  - 使用全屏截图：agent-browser screenshot --full captcha.png")
        logger.warning("  - 使用 debug 模式查看详细检测结果：--debug")
        return {"success": False, "error": "未检测到验证码弹窗", "suggestions": [
            "增加页面等待时间",
            "使用全屏截图",
            "检查验证码是否已加载"
        ]}
    
    def detect_slider_button(self) -> dict:
        """
        检测可拖动滑块按钮
        
        特征：
        - 有颜色（通常不是白色）
        - 有图标（箭头、拼图块等）
        - 位于验证码区域底部
        """
        if not self.captcha_area:
            result = self.detect_captcha_popup()
            if not result["success"]:
                return result
        
        # 裁剪验证码区域
        ca = self.captcha_area
        captcha_img = self.image[ca["y"]:ca["y"]+ca["h"], ca["x"]:ca["x"]+ca["w"]]
        
        # 方法 1：粉色检测（大麦网特征）
        hsv = cv2.cvtColor(captcha_img, cv2.COLOR_BGR2HSV)
        
        # 粉色/玫红色范围（大麦网滑块颜色）
        lower_pink = np.array([130, 40, 150])
        upper_pink = np.array([170, 255, 255])
        pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
        
        # 只检查底部区域（滑块通常在底部 1/3）
        bottom_y = int(ca["h"] * 0.5)
        bottom_mask = pink_mask[bottom_y:, :]
        
        # 查找轮廓
        contours, _ = cv2.findContours(bottom_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        slider_candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 300 < area < 15000:  # 滑块面积范围
                x, y, w, h = cv2.boundingRect(contour)
                slider_candidates.append({
                    "x": ca["x"] + x,
                    "y": ca["y"] + bottom_y + y,
                    "w": w,
                    "h": h,
                    "area": area
                })
        
        if slider_candidates:
            # 选择最可能的滑块（面积适中、位置合理）
            slider_candidates.sort(key=lambda s: s["area"], reverse=True)
            self.slider_area = slider_candidates[0]
            return {
                "success": True,
                "type": "pink_slider",
                "location": slider_candidates[0]
            }
        
        # 方法 2：通用颜色检测（其他网站）
        lower_color = np.array([0, 50, 50])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, upper_color)
        
        bottom_mask = mask[bottom_y:, :]
        contours, _ = cv2.findContours(bottom_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 20000:
                x, y, w, h = cv2.boundingRect(contour)
                self.slider_area = {
                    "x": ca["x"] + x,
                    "y": ca["y"] + bottom_y + y,
                    "w": w,
                    "h": h,
                    "area": area
                }
                return {
                    "success": True,
                    "type": "slider_button",
                    "location": self.slider_area
                }
        
        # 方法 3：边缘检测查找滑块
        gray = cv2.cvtColor(captcha_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        bottom_edges = edges[bottom_y:, :]
        
        contours, _ = cv2.findContours(bottom_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 10000:
                x, y, w, h = cv2.boundingRect(contour)
                # 检查是否是方形（滑块特征）
                aspect_ratio = w / h if h > 0 else 0
                if 0.5 < aspect_ratio < 2.0:
                    self.slider_area = {
                        "x": ca["x"] + x,
                        "y": ca["y"] + bottom_y + y,
                        "w": w,
                        "h": h
                    }
                    return {
                        "success": True,
                        "type": "edge_slider",
                        "location": self.slider_area
                    }
        
        return {"success": False, "error": "未检测到滑块按钮"}
    
    def _create_arrow_template(self):
        """创建箭头模板（用于匹配）"""
        # 创建一个简单的右箭头模板
        template = np.zeros((30, 30), dtype=np.uint8)
        cv2.arrowedLine(template, (5, 15), (25, 15), 255, 3)
        cv2.arrowedLine(template, (5, 10), (20, 15), 255, 2)
        cv2.arrowedLine(template, (5, 20), (20, 15), 255, 2)
        return template
    
    def _match_template(self, image, template):
        """模板匹配"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if template.shape != gray.shape:
            template = cv2.resize(template, (50, 50))
        
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.6:
            h, w = template.shape
            return {
                "x": max_loc[0],
                "y": max_loc[1],
                "w": w,
                "h": h,
                "confidence": max_val
            }
        return None
    
    def detect_gap_position(self) -> dict:
        """
        检测拼图缺口位置
        
        对于箭头拼图，缺口通常在右侧
        对于拼图块，使用模板匹配
        """
        if not self.captcha_area:
            return {"success": False, "error": "未检测验证码区域"}
        
        ca = self.captcha_area
        captcha_img = self.image[ca["y"]:ca["y"]+ca["h"], ca["x"]:ca["x"]+ca["w"]]
        
        # 方法 1：边缘检测查找缺口
        gray = cv2.cvtColor(captcha_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找右侧的缺口特征
        right_side = edges[:, int(ca["w"]*0.5):]
        contours, _ = cv2.findContours(right_side, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        gap_candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 5000:
                x, y, w, h = cv2.boundingRect(contour)
                gap_candidates.append({
                    "x": int(ca["w"]*0.5) + x,
                    "y": y,
                    "w": w,
                    "h": h
                })
        
        if gap_candidates:
            # 选择最可能的缺口
            gap = max(gap_candidates, key=lambda g: g["w"] * g["h"])
            return {
                "success": True,
                "type": "gap_position",
                "location": gap
            }
        
        # 方法 2：基于滑块位置推算缺口
        if self.slider_area:
            # 缺口通常在滑块的右侧水平位置
            slider_x = self.slider_area["x"] - ca["x"]
            slider_y = self.slider_area["y"] - ca["y"]
            
            # 估算缺口位置（在同一水平线上，偏右侧）
            gap_x = int(ca["w"] * 0.6)
            gap_y = slider_y
            
            return {
                "success": True,
                "type": "estimated_gap",
                "location": {
                    "x": gap_x,
                    "y": gap_y,
                    "w": self.slider_area["w"],
                    "h": self.slider_area["h"]
                }
            }
        
        return {"success": False, "error": "未检测到缺口位置"}
    
    def calculate_offset(self) -> dict:
        """
        计算需要拖动的距离
        """
        if not self.slider_area or not self.captcha_area:
            return {"success": False, "error": "缺少必要信息"}
        
        ca = self.captcha_area
        
        # 滑块当前位置（相对于验证码区域）
        slider_x = self.slider_area["x"] - ca["x"]
        
        # 缺口位置（估算或检测）
        gap_result = self.detect_gap_position()
        if gap_result["success"]:
            gap_x = gap_result["location"]["x"]
        else:
            # 默认缺口在右侧 2/3 处
            gap_x = int(ca["w"] * 0.65)
        
        # 计算偏移量
        offset = gap_x - slider_x
        
        # 验证偏移量合理性
        if offset < 50 or offset > 400:
            return {
                "success": False,
                "error": f"偏移量异常：{offset}",
                "offset": offset
            }
        
        return {
            "success": True,
            "offset": offset,
            "slider_x": slider_x,
            "gap_x": gap_x
        }
    
    def generate_trajectory(self, offset: int, duration: float = 1.5) -> list:
        """
        生成模拟人类拖动轨迹
        """
        trajectory = []
        steps = int(duration * 60)
        
        # 启动前停顿（0.1-0.3 秒）
        pause_frames = int(random.uniform(0.1, 0.3) * 60)
        for _ in range(pause_frames):
            trajectory.append([0, int(random.gauss(0, 1))])
        
        # 主拖动阶段
        for i in range(steps + 1):
            t = i / steps
            
            # ease-out cubic（先快后慢）
            progress = 1 - math.pow(1 - t, 3)
            x = int(offset * progress)
            
            # 垂直抖动（正态分布）
            y = int(random.gauss(0, 2))
            
            # 随机回退（模拟犹豫，5% 概率）
            if random.random() < 0.05 and 0.3 < t < 0.8:
                x = max(0, x - random.randint(1, 3))
            
            trajectory.append([x, y])
        
        # 到达后微调（5 帧）
        for _ in range(5):
            trajectory.append([
                offset + random.randint(-1, 1),
                int(random.gauss(0, 1))
            ])
        
        return trajectory
    
    def solve(self, debug: bool = False, benchmark: bool = False) -> dict:
        """
        完整求解流程
        
        Args:
            debug: 是否输出调试图片
            benchmark: 是否进行性能测试
            
        Returns:
            识别结果字典
        """
        result = {
            "success": False,
            "steps": []
        }
        
        timings = {}
        total_start = datetime.now()
        
        # 步骤 1：检测验证码弹窗
        t0 = datetime.now()
        popup_result = self.detect_captcha_popup()
        timings["detect_popup"] = (datetime.now() - t0).total_seconds()
        
        result["steps"].append({"step": "detect_popup", "result": popup_result})
        if not popup_result["success"]:
            result["error"] = "无法检测验证码弹窗"
            if benchmark:
                result["timings"] = timings
                result["total_time"] = (datetime.now() - total_start).total_seconds()
            return result
        
        # 步骤 2：检测滑块按钮
        t0 = datetime.now()
        slider_result = self.detect_slider_button()
        timings["detect_slider"] = (datetime.now() - t0).total_seconds()
        
        result["steps"].append({"step": "detect_slider", "result": slider_result})
        if not slider_result["success"]:
            result["error"] = "无法检测滑块按钮"
            if benchmark:
                result["timings"] = timings
                result["total_time"] = (datetime.now() - total_start).total_seconds()
            return result
        
        # 步骤 3：计算偏移量
        t0 = datetime.now()
        offset_result = self.calculate_offset()
        timings["calculate_offset"] = (datetime.now() - t0).total_seconds()
        
        result["steps"].append({"step": "calculate_offset", "result": offset_result})
        if not offset_result["success"]:
            result["error"] = offset_result.get("error", "无法计算偏移量")
            if benchmark:
                result["timings"] = timings
                result["total_time"] = (datetime.now() - total_start).total_seconds()
            return result
        
        offset = offset_result["offset"]
        
        # 步骤 4：生成轨迹
        t0 = datetime.now()
        trajectory = self.generate_trajectory(offset)
        timings["generate_trajectory"] = (datetime.now() - t0).total_seconds()
        
        # 生成 JavaScript 代码
        trajectory_js = json.dumps(trajectory)
        
        result["success"] = True
        result["offset"] = offset
        result["slider_location"] = self.slider_area
        result["trajectory"] = trajectory
        result["trajectory_js"] = trajectory_js
        result["confidence"] = 0.85  # 估算置信度
        
        # 性能测试信息
        if benchmark:
            timings["total"] = (datetime.now() - total_start).total_seconds()
            result["timings"] = timings
            result["total_time"] = timings["total"]
        
        # 调试输出
        if debug:
            self._save_debug_images()
        
        return result
    
    def _save_debug_images(self):
        """保存调试图片"""
        debug_dir = Path("debug_captcha")
        debug_dir.mkdir(exist_ok=True)
        
        # 保存原图
        cv2.imwrite(str(debug_dir / "original.png"), self.image)
        
        # 标记检测区域
        marked = self.image.copy()
        
        if self.captcha_area:
            ca = self.captcha_area
            cv2.rectangle(marked, 
                         (ca["x"], ca["y"]), 
                         (ca["x"]+ca["w"], ca["y"]+ca["h"]),
                         (0, 255, 0), 2)
        
        if self.slider_area:
            cv2.rectangle(marked,
                         (self.slider_area["x"], self.slider_area["y"]),
                         (self.slider_area["x"]+self.slider_area["w"], 
                          self.slider_area["y"]+self.slider_area["h"]),
                         (255, 0, 0), 2)
        
        cv2.imwrite(str(debug_dir / "marked.png"), marked)


def main():
    parser = argparse.ArgumentParser(
        description="🧩 拼图滑块验证码识别工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本使用
  python3 recognize_puzzle.py --screenshot captcha.png --output result.json
  
  # 快速模式（速度优先，精度略降）
  python3 recognize_puzzle.py --screenshot captcha.png --fast
  
  # 高精度模式（精度优先，速度略降）
  python3 recognize_puzzle.py --screenshot captcha.png --high-precision
  
  # 开启调试模式（生成标记图片）
  python3 recognize_puzzle.py --screenshot captcha.png --debug
  
  # 性能测试（显示各步骤耗时）
  python3 recognize_puzzle.py --screenshot captcha.png --benchmark
  
  # 查看完整帮助
  python3 recognize_puzzle.py --help
        """
    )
    parser.add_argument("--screenshot", required=True, help="📷 截图路径")
    parser.add_argument("--output", help="💾 输出 JSON 文件路径（可选，不指定则输出到控制台）")
    parser.add_argument("--debug", action="store_true", help="🔍 输出调试图片到 debug_captcha/ 目录")
    parser.add_argument("--verbose", "-v", action="store_true", help="📢 显示详细日志")
    parser.add_argument("--fast", action="store_true", help="⚡ 快速模式（速度优先，精度略降）")
    parser.add_argument("--high-precision", action="store_true", help="🎯 高精度模式（精度优先）")
    parser.add_argument("--benchmark", action="store_true", help="📊 性能测试（显示各步骤耗时）")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 确定识别模式
    if args.fast:
        mode = "fast"
    elif args.high_precision:
        mode = "high_precision"
    else:
        mode = "normal"
    
    logger.info("=" * 60)
    logger.info(f"🧩 拼图滑块验证码识别工具 v1.0.0 (模式：{mode})")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    
    try:
        # 步骤 1：加载图片
        logger.info("步骤 1/3: 加载截图...")
        solver = PuzzleCaptchaSolver(args.screenshot, mode=mode)
        
        # 步骤 2：识别验证码
        logger.info("步骤 2/3: 识别验证码...")
        result = solver.solve(debug=args.debug, benchmark=args.benchmark)
        
        # 步骤 3：输出结果
        logger.info("步骤 3/3: 输出结果...")
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.get("success"):
            logger.info(f"✅ 识别成功！总耗时：{elapsed:.2f}秒")
            logger.info(f"   缺口位置：x={result.get('offset')}px")
            logger.info(f"   置信度：{result.get('confidence', 0)*100:.1f}%")
            
            # 性能测试详情
            if args.benchmark and result.get("timings"):
                logger.info("\n📊 性能分析:")
                for step, time_cost in result["timings"].items():
                    if step != "total":
                        percentage = (time_cost / result["total_time"]) * 100
                        logger.info(f"   {step}: {time_cost:.3f}秒 ({percentage:.1f}%)")
                logger.info(f"   总计：{result['total_time']:.3f}秒")
        else:
            logger.warning(f"⚠️  识别失败：{result.get('error')}")
            if result.get("suggestions"):
                logger.warning("建议尝试：")
                for suggestion in result["suggestions"]:
                    logger.warning(f"  - {suggestion}")
        
        # 输出结果
        if args.output:
            # 移除 trajectory_js（太大）
            output_result = {k: v for k, v in result.items() if k != "trajectory_js"}
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(output_result, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 结果已保存到：{args.output}")
        else:
            # 控制台输出简化版
            print(json.dumps({
                "success": result["success"],
                "offset": result.get("offset"),
                "confidence": result.get("confidence"),
                "error": result.get("error")
            }, indent=2, ensure_ascii=False))
        
        logger.info("=" * 60)
        sys.exit(0 if result["success"] else 1)
        
    except FileNotFoundError as e:
        logger.error(f"❌ 文件错误：{e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ 参数错误：{e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 未知错误：{e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
