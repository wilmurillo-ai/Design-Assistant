#!/usr/bin/env python3
"""
天机·玄机子核心处理脚本
智能模型路由：图像分析用豆包，聊天用DeepSeek
"""

import os
import sys
import json
import re
from pathlib import Path

class TianjiProcessor:
    """天机处理器"""
    
    def __init__(self, config_path=None):
        """初始化"""
        # 使用当前文件所在目录的父目录作为workspace
        current_file = Path(__file__).resolve()
        self.workspace_dir = current_file.parent.parent.parent
        self.config = self.load_config(config_path)
        self.persona = self.config.get("persona", {})
        
    def load_config(self, config_path):
        """加载配置"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认配置
        return {
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
    
    def detect_request_type(self, user_input, context=None):
        """
        检测请求类型
        返回: request_type, details
        """
        input_text = user_input.lower().strip()
        
        # 图像分析关键词
        image_keywords = [
            '分析.*图片', '分析.*图像', '分析.*照片', '分析.*掌纹',
            '分析.*手相', '分析.*户型', '分析.*风水', '分析.*格局',
            '/tmp/', '.jpg', '.png', '.jpeg', '图片分析', '图像识别'
        ]
        
        # 八字分析关键词
        bazi_keywords = [
            '八字', '生辰', '出生', '命理', '排盘', '年柱', '月柱',
            '日柱', '时柱', '大运', '十神', '五行', '命局'
        ]
        
        # 掌纹分析关键词
        palm_keywords = [
            '掌纹', '手相', '生命线', '智慧线', '感情线', '手掌'
        ]
        
        # 风水分析关键词
        fengshui_keywords = [
            '风水', '方位', '格局', '气场', '阴阳', '五行', '八卦',
            '青龙', '白虎', '朱雀', '玄武', '明堂', '靠山'
        ]
        
        # 检查是否包含文件路径
        if any(ext in input_text for ext in ['.jpg', '.png', '.jpeg', '/tmp/', '/home/']):
            return "image_analysis", {"file_path": self.extract_file_path(input_text)}
        
        # 检查图像分析关键词
        for keyword in image_keywords:
            if re.search(keyword, input_text):
                return "image_analysis", {"keyword": keyword}
        
        # 检查八字分析
        for keyword in bazi_keywords:
            if keyword in input_text:
                return "bazi_analysis", {"keyword": keyword}
        
        # 检查掌纹分析
        for keyword in palm_keywords:
            if keyword in input_text:
                return "palm_analysis", {"keyword": keyword}
        
        # 检查风水分析
        for keyword in fengshui_keywords:
            if keyword in input_text:
                return "fengshui_analysis", {"keyword": keyword}
        
        # 默认聊天
        return "chat", {}
    
    def extract_file_path(self, text):
        """从文本中提取文件路径（安全版本）"""
        # 安全路径模式：仅允许明确的、受信任的路径
        # 使用更灵活但安全的模式，配合后续的安全验证
        patterns = [
            # 模式1: /tmp/目录下的图片文件
            r'(/tmp/[^\s]*\.(?:jpg|png|jpeg|JPG|PNG|JPEG|gif|webp|bmp))',
            # 模式2: 当前用户home目录下的图片文件
            r'(/home/[^/\s]+/[^\s]*\.(?:jpg|png|jpeg|JPG|PNG|JPEG|gif|webp|bmp))',
            # 模式3: 用户主目录下的图片（~扩展）
            r'(~/[^\s]*\.(?:jpg|png|jpeg|JPG|PNG|JPEG|gif|webp|bmp))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                file_path = matches[0]
                # 扩展~为完整路径
                if file_path.startswith('~'):
                    import os
                    file_path = os.path.expanduser(file_path)
                
                # 基本安全验证：检查路径是否包含危险模式
                if self.is_basic_safe_path(file_path):
                    return file_path
        
        return None
    
    def is_basic_safe_path(self, file_path):
        """基本路径安全检查（不检查文件存在性）"""
        import os
        import re
        
        # 拒绝危险路径模式
        dangerous_patterns = [
            r'\.\./',  # 目录遍历
            r'\.\\.',  # Windows目录遍历
            r'^/etc/',  # 系统配置文件
            r'^/var/',  # 系统目录
            r'^/usr/',  # 系统程序
            r'^/bin/',  # 系统二进制
            r'^/sbin/',  # 系统管理二进制
            r'^/proc/',  # 进程信息
            r'^/sys/',  # 系统信息
            r'^/dev/',  # 设备文件
            r'^/boot/',  # 启动文件
            r'^/lib/',  # 系统库
            r'^/opt/',  # 可选软件
            r'^/srv/',  # 服务数据
            r'^/media/',  # 可移动媒体
            r'^/mnt/',  # 挂载点
            r'^/root/',  # root用户目录
        ]
        
        # 转换为绝对路径并规范化
        abs_path = os.path.abspath(file_path)
        
        # 验证1: 不在危险目录中
        for pattern in dangerous_patterns:
            if re.search(pattern, abs_path):
                return False
        
        # 验证2: 文件扩展名检查
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP', '.BMP']
        file_ext = os.path.splitext(abs_path)[1]
        if file_ext not in allowed_extensions:
            return False
        
        return True
    
    def is_safe_file_path(self, file_path):
        """验证文件路径是否安全（增强版）"""
        import os
        
        # 拒绝危险路径模式
        dangerous_patterns = [
            r'\.\./',  # 目录遍历
            r'\.\\.',  # Windows目录遍历
            r'^/etc/',  # 系统配置文件
            r'^/var/',  # 系统目录
            r'^/usr/',  # 系统程序
            r'^/bin/',  # 系统二进制
            r'^/sbin/',  # 系统管理二进制
            r'^/proc/',  # 进程信息
            r'^/sys/',  # 系统信息
            r'^/dev/',  # 设备文件
            r'^/boot/',  # 启动文件
            r'^/lib/',  # 系统库
            r'^/opt/',  # 可选软件
            r'^/srv/',  # 服务数据
            r'^/media/',  # 可移动媒体
            r'^/mnt/',  # 挂载点
            r'^/root/',  # root用户目录
            r'^/home/[^/]+/\.(ssh|bash|profile|history)',  # 用户敏感文件
            r'^/home/[^/]+/\.openclaw/openclaw\.json$',  # 配置文件（需特殊权限）
        ]
        
        # 转换为绝对路径并规范化
        abs_path = os.path.abspath(file_path)
        
        # 获取用户主目录
        user_home = os.path.expanduser('~')
        
        # 显式白名单目录
        allowed_prefixes = [
            '/tmp/',
            f'{user_home}/.openclaw/workspace/',
            f'{user_home}/.openclaw/media/inbound/',  # 仅限inbound目录
            f'{user_home}/Downloads/',
            f'{user_home}/Desktop/',
            f'{user_home}/Documents/',
            f'{user_home}/Pictures/',
        ]
        
        # 验证1: 不在危险目录中
        for pattern in dangerous_patterns:
            if re.search(pattern, abs_path):
                print(f"🚫 路径安全拒绝: 匹配危险模式 {pattern}")
                return False
        
        # 验证2: 在允许的目录下
        is_allowed = False
        for prefix in allowed_prefixes:
            if abs_path.startswith(prefix):
                is_allowed = True
                break
        
        if not is_allowed:
            print(f"🚫 路径安全拒绝: 不在白名单目录中")
            print(f"   允许的目录: {allowed_prefixes}")
            return False
        
        # 验证3: 文件存在且可读
        if not os.path.exists(abs_path):
            print(f"🚫 路径安全拒绝: 文件不存在")
            return False
        
        if not os.access(abs_path, os.R_OK):
            print(f"🚫 路径安全拒绝: 文件不可读")
            return False
        
        # 验证4: 是普通文件（不是目录、符号链接等）
        if not os.path.isfile(abs_path):
            print(f"🚫 路径安全拒绝: 不是普通文件")
            return False
        
        # 验证5: 文件大小限制（最大50MB）
        file_size = os.path.getsize(abs_path)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            print(f"🚫 路径安全拒绝: 文件过大 ({file_size} > {max_size} bytes)")
            return False
        
        # 验证6: 文件扩展名检查
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        file_ext = os.path.splitext(abs_path)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"🚫 路径安全拒绝: 不支持的文件扩展名 {file_ext}")
            print(f"   允许的扩展名: {allowed_extensions}")
            return False
        
        print(f"✅ 路径安全检查通过: {abs_path}")
        return True
        
        return False
    
    def get_recommended_model(self, request_type):
        """获取推荐模型"""
        routing = self.config.get("model_routing", {})
        
        if request_type == "image_analysis":
            return routing.get("image_analysis", {}).get("model", "doubao-seed-2-0-pro-260215")
        elif request_type in ["bazi_analysis", "palm_analysis", "fengshui_analysis"]:
            return routing.get("fengshui_analysis", {}).get("model", "deepseek-chat")
        else:
            return routing.get("default_chat", {}).get("model", "deepseek-chat")
    
    def optimize_image(self, image_path):
        """优化图像尺寸和质量"""
        try:
            from PIL import Image
            import os
            
            img = Image.open(image_path)
            width, height = img.size
            
            config = self.config.get("image_processing", {})
            max_width = config.get("max_width", 400)
            max_height = config.get("max_height", 400)
            quality = config.get("quality", 60)
            
            # 调整尺寸
            if width > max_width or height > max_height:
                img.thumbnail((max_width, max_height))
            
            # 转换PNG到JPG
            if config.get("convert_png_to_jpg", True) and image_path.lower().endswith('.png'):
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                output_path = image_path.replace('.png', '_optimized.jpg')
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
                return output_path
            
            # 保存优化版本
            output_path = image_path.replace('.jpg', '_optimized.jpg').replace('.jpeg', '_optimized.jpg')
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            return output_path
            
        except Exception as e:
            print(f"图像优化失败: {e}")
            return image_path
    
    def analyze_with_doubao(self, image_path, prompt):
        """使用豆包模型分析图像"""
        try:
            # 调用现有的图片分析技能
            skill_path = self.workspace_dir / "skills" / "video-image-file-analysis" / "scripts" / "vision.py"
            if skill_path.exists():
                import subprocess
                cmd = [
                    "python3", str(skill_path),
                    "analyze",
                    "--image", image_path,
                    "--prompt", prompt,
                    "--model", "doubao"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_dir)
                return result.stdout
            else:
                return "图片分析技能未安装，请先安装 video-image-file-analysis 技能"
        except Exception as e:
            return f"豆包模型分析失败: {e}"
    
    def analyze_with_subagent(self, image_path, analysis_type="palm"):
        """使用subagent分析图像"""
        try:
            # 调用subagent集成工具
            subagent_script = Path(__file__).parent / "tianji_subagent_integration.py"
            if subagent_script.exists():
                import subprocess
                cmd = [
                    "python3", str(subagent_script),
                    image_path,
                    analysis_type
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace_dir)
                
                # 解析结果
                output = result.stdout
                if "执行命令:" in output:
                    # 提取命令
                    lines = output.split('\n')
                    for i, line in enumerate(lines):
                        if "执行命令:" in line and i+1 < len(lines):
                            command = lines[i+1].strip()
                            return {
                                "method": "subagent",
                                "command": command,
                                "analysis_type": analysis_type,
                                "full_output": output
                            }
                
                return output
            else:
                return "Subagent集成工具未找到，请确保tianji_subagent_integration.py存在"
        except Exception as e:
            return f"Subagent分析失败: {e}"
    
    def generate_response(self, request_type, user_input, context=None):
        """生成响应"""
        persona = self.persona
        recommended_model = self.get_recommended_model(request_type)
        
        # 构建基础响应
        response = {
            "persona": persona.get("name", "玄机子"),
            "emoji": persona.get("emoji", "🧭"),
            "request_type": request_type,
            "recommended_model": recommended_model,
            "response": ""
        }
        
        # 根据请求类型生成响应内容
        if request_type == "image_analysis":
            response["response"] = f"{persona.get('emoji', '🧭')} **玄机子检测到图像分析请求**\n\n"
            response["response"] += f"**推荐模型**: {recommended_model}\n"
            response["response"] += "我将使用豆包视觉模型进行专业分析..."
            
        elif request_type == "bazi_analysis":
            response["response"] = f"{persona.get('emoji', '🧭')} **玄机子检测到八字分析请求**\n\n"
            response["response"] += f"**推荐模型**: {recommended_model}\n"
            response["response"] += "我将结合传统八字命理和现代AI进行分析..."
            
        elif request_type == "palm_analysis":
            response["response"] = f"{persona.get('emoji', '🧭')} **玄机子检测到掌纹分析请求**\n\n"
            response["response"] += f"**推荐模型**: {recommended_model}\n"
            response["response"] += "我将结合掌相学和现代AI进行专业解读..."
            
        elif request_type == "fengshui_analysis":
            response["response"] = f"{persona.get('emoji', '🧭')} **玄机子检测到风水分析请求**\n\n"
            response["response"] += f"**推荐模型**: {recommended_model}\n"
            response["response"] += "我将结合风水原理和现代环境学进行分析..."
            
        else:
            response["response"] = f"{persona.get('emoji', '🧭')} **玄机子**\n\n"
            response["response"] += f"**推荐模型**: {recommended_model}\n"
            response["response"] += "您好，我是玄机子，风水大师智慧助手。有什么可以帮您？"
        
        return response
    
    def process_request(self, user_input, context=None, use_subagent=False):
        """处理用户请求
        use_subagent: 是否使用subagent（True=使用，False=使用原方法）
        """
        # 检测请求类型
        request_type, details = self.detect_request_type(user_input, context)
        
        # 如果是图像分析且有文件路径
        if request_type == "image_analysis" and "file_path" in details:
            file_path = details["file_path"]
            if file_path and os.path.exists(file_path):
                
                # 判断是否使用subagent
                if use_subagent:
                    # 确定分析类型
                    analysis_type = "general"
                    if "掌纹" in user_input or "手相" in user_input:
                        analysis_type = "palm"
                    elif "面相" in user_input or "人脸" in user_input:
                        analysis_type = "face"
                    elif "风水" in user_input or "户型" in user_input or "房屋" in user_input:
                        analysis_type = "fengshui"
                    
                    # 使用subagent分析
                    analysis_result = self.analyze_with_subagent(file_path, analysis_type)
                    return analysis_result
                else:
                    # 使用原方法
                    # 优化图像
                    optimized_path = self.optimize_image(file_path)
                    
                    # 生成分析提示
                    prompt = "详细分析这张图片的内容"
                    if "掌纹" in user_input or "手相" in user_input:
                        prompt = "详细分析这张手掌的掌纹，包括生命线、智慧线、感情线等主要纹路"
                    elif "风水" in user_input or "户型" in user_input:
                        prompt = "详细分析这张图片的风水格局和空间布局"
                    
                    # 使用豆包模型分析
                    analysis_result = self.analyze_with_doubao(optimized_path, prompt)
                    return analysis_result
        
        # 生成标准响应
        return self.generate_response(request_type, user_input, context)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 tianji_core.py \"用户输入\" [--subagent]")
        print("选项:")
        print("  --subagent    使用subagent进行图像分析")
        sys.exit(1)
    
    user_input = sys.argv[1]
    use_subagent = "--subagent" in sys.argv
    
    # 初始化处理器
    config_path = Path(__file__).parent / "config.json"
    processor = TianjiProcessor(config_path)
    
    # 处理请求
    result = processor.process_request(user_input, use_subagent=use_subagent)
    
    # 输出结果
    if isinstance(result, dict):
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)

if __name__ == "__main__":
    main()