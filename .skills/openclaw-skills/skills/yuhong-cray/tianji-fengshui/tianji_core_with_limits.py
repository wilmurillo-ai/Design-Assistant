#!/usr/bin/env python3
"""
天机·玄机子核心处理脚本（带用户限制）
智能模型路由：图像分析用豆包，聊天用DeepSeek
用户限制：管理员cray无限制，其他用户每天10问题/3图片
"""

import os
import sys
import json
import re
from pathlib import Path

# 添加用户限制模块
sys.path.insert(0, str(Path(__file__).parent))
from user_limits import UserLimitsManager

class TianjiProcessor:
    """天机处理器（带用户限制）"""
    
    def __init__(self, config_path=None):
        """初始化"""
        # 使用当前文件所在目录的父目录作为workspace
        current_file = Path(__file__).resolve()
        self.workspace_dir = current_file.parent.parent.parent
        self.config = self.load_config(config_path)
        self.persona = self.config.get("persona", {})
        
        # 初始化用户限制管理器
        self.limits_manager = UserLimitsManager()
        
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
        """从文本中提取文件路径"""
        # 查找文件路径模式
        patterns = [
            r'/tmp/[^\s]+\.(jpg|png|jpeg)',
            r'/home/[^\s]+\.(jpg|png|jpeg)',
            r'[^\s]+\.(jpg|png|jpeg)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    def check_user_limits(self, user_id, request_type):
        """
        检查用户使用限制
        返回: (是否允许, 错误信息, 用户统计)
        """
        # 确定请求类型
        if request_type == "image_analysis":
            limit_type = "image_analysis"
        else:
            limit_type = "question"
        
        # 检查限制
        allowed, error_msg = self.limits_manager.check_and_update_question(user_id, limit_type)
        
        # 获取用户统计
        user_stats = self.limits_manager.get_user_stats(user_id)
        
        return allowed, error_msg, user_stats
    
    def process_request(self, user_input, user_id=None, context=None):
        """
        处理用户请求（带限制检查）
        返回: (处理结果, 是否被限制, 用户统计)
        """
        # 如果没有提供user_id，使用默认
        if user_id is None:
            user_id = "anonymous"
        
        # 检测请求类型
        request_type, details = self.detect_request_type(user_input, context)
        
        # 检查用户限制
        allowed, error_msg, user_stats = self.check_user_limits(user_id, request_type)
        
        if not allowed:
            # 用户超过限制
            response = {
                "status": "limited",
                "message": error_msg,
                "request_type": request_type,
                "user_stats": user_stats
            }
            return response, True, user_stats
        
        # 用户允许使用，继续处理
        if request_type == "image_analysis":
            # 图像分析请求
            response = self.handle_image_analysis(user_input, details)
        elif request_type in ["bazi_analysis", "palm_analysis", "fengshui_analysis"]:
            # 专业分析请求
            response = self.handle_professional_analysis(request_type, user_input, details)
        else:
            # 普通聊天请求
            response = self.handle_chat(user_input)
        
        # 添加用户统计信息
        response["user_stats"] = user_stats
        response["request_type"] = request_type
        
        return response, False, user_stats
    
    def handle_image_analysis(self, user_input, details):
        """处理图像分析"""
        file_path = details.get("file_path")
        
        if file_path and os.path.exists(file_path):
            # 调用豆包视觉模型
            return {
                "status": "success",
                "type": "image_analysis",
                "model": "doubao-seed-2-0-pro-260215",
                "file_path": file_path,
                "message": f"将使用豆包视觉模型分析图片: {file_path}"
            }
        else:
            return {
                "status": "error",
                "type": "image_analysis",
                "message": "未找到图片文件，请提供有效的图片路径"
            }
    
    def handle_professional_analysis(self, analysis_type, user_input, details):
        """处理专业分析"""
        analysis_names = {
            "bazi_analysis": "八字分析",
            "palm_analysis": "掌纹分析",
            "fengshui_analysis": "风水分析"
        }
        
        return {
            "status": "success",
            "type": analysis_type,
            "name": analysis_names.get(analysis_type, "专业分析"),
            "model": "deepseek-chat",
            "message": f"将进行{analysis_names.get(analysis_type, '专业')}分析"
        }
    
    def handle_chat(self, user_input):
        """处理普通聊天"""
        return {
            "status": "success",
            "type": "chat",
            "model": "deepseek-chat",
            "message": "将使用DeepSeek模型进行对话"
        }
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        return self.limits_manager.get_user_stats(user_id)
    
    def get_all_users_info(self):
        """获取所有用户信息"""
        return self.limits_manager.get_all_stats()
    
    def reset_daily_limits(self):
        """重置每日限制"""
        return self.limits_manager.reset_daily_stats()


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="天机·玄机子（带用户限制）")
    parser.add_argument("input", nargs="?", help="用户输入")
    parser.add_argument("--user", "-u", default="anonymous", help="用户ID")
    parser.add_argument("--check", "-c", action="store_true", help="只检查限制，不处理")
    parser.add_argument("--stats", "-s", action="store_true", help="获取用户统计")
    parser.add_argument("--all-stats", "-a", action="store_true", help="获取所有用户统计")
    parser.add_argument("--reset", "-r", action="store_true", help="重置每日限制")
    
    args = parser.parse_args()
    
    processor = TianjiProcessor()
    
    if args.reset:
        # 重置每日限制
        reset_log = processor.reset_daily_limits()
        print(f"✅ 每日限制已重置")
        print(f"重置时间: {reset_log['reset_time']}")
        return
    
    if args.all_stats:
        # 获取所有用户统计
        all_stats = processor.get_all_users_info()
        print(json.dumps(all_stats, ensure_ascii=False, indent=2))
        return
    
    if args.stats:
        # 获取用户统计
        user_stats = processor.get_user_info(args.user)
        print(json.dumps(user_stats, ensure_ascii=False, indent=2))
        return
    
    if args.input:
        if args.check:
            # 只检查限制
            request_type, _ = processor.detect_request_type(args.input)
            allowed, error_msg, user_stats = processor.check_user_limits(args.user, request_type)
            
            if allowed:
                print(f"✅ 用户 {args.user} 允许访问")
                print(f"请求类型: {request_type}")
                print(f"今日剩余问题: {user_stats['today']['remaining_questions']}")
                print(f"今日剩余图片: {user_stats['today']['remaining_images']}")
            else:
                print(f"❌ 用户 {args.user} 拒绝访问")
                print(f"原因: {error_msg}")
        else:
            # 处理请求
            response, limited, user_stats = processor.process_request(args.input, args.user)
            
            if limited:
                print(f"❌ 请求被限制")
                print(f"原因: {response['message']}")
            else:
                print(f"✅ 请求处理成功")
                print(f"请求类型: {response['type']}")
                print(f"使用模型: {response.get('model', 'N/A')}")
                
                if response['type'] == 'image_analysis' and 'file_path' in response:
                    print(f"图片路径: {response['file_path']}")
                
                # 显示用户统计
                print(f"\n📊 用户统计:")
                print(f"  今日问题: {user_stats['today']['questions']}/{processor.limits_manager.limits_config['daily_questions']}")
                print(f"  今日图片: {user_stats['today']['images']}/{processor.limits_manager.limits_config['daily_images']}")
                print(f"  总问题数: {user_stats['total']['questions']}")
                print(f"  总图片数: {user_stats['total']['images']}")
    else:
        # 交互模式
        print("🧭 天机·玄机子（带用户限制）")
        print("=" * 50)
        
        user_id = input("请输入用户ID（默认: anonymous）: ").strip() or "anonymous"
        
        processor = TianjiProcessor()
        user_stats = processor.get_user_info(user_id)
        
        print(f"\n📊 用户 {user_id} 统计:")
        print(f"  管理员: {'是' if user_stats['is_admin'] else '否'}")
        print(f"  今日剩余问题: {user_stats['today']['remaining_questions']}")
        print(f"  今日剩余图片: {user_stats['today']['remaining_images']}")
        print(f"  总问题数: {user_stats['total']['questions']}")
        print(f"  总图片数: {user_stats['total']['images']}")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n请输入问题（输入 'quit' 退出）: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                response, limited, user_stats = processor.process_request(user_input, user_id)
                
                if limited:
                    print(f"\n❌ {response['message']}")
                else:
                    print(f"\n✅ 请求类型: {response['type']}")
                    print(f"📱 使用模型: {response.get('model', 'N/A')}")
                    
                    if response['type'] == 'image_analysis' and 'file_path' in response:
                        print(f"🖼️  图片路径: {response['file_path']}")
                    
                    print(f"\n📊 更新统计:")
                    print(f"  今日问题: {user_stats['today']['questions']}/{processor.limits_manager.limits_config['daily_questions']}")
                    print(f"  今日图片: {user_stats['today']['images']}/{processor.limits_manager.limits_config['daily_images']}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()