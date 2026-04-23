#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能互动生成器 - Smart Interaction Generator
版本：v1.4.0
功能：调用 LLM 生成智能评论和私聊消息

使用 OpenClaw Chat Completions API (MiniMax-M2.7)
"""

import json
import os
import random
import requests
from typing import Optional, Dict, List, Any


class SmartInteractionGenerator:
    """智能互动生成器"""
    
    # OpenClaw 配置
    OPENCLAW_BASE_URL = os.getenv("OPENCLAW_BASE_URL", "http://localhost:18789")
    OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")
    DAILY_MODEL = "minimax/MiniMax-M2.7"
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = None, model: str = None):
        """初始化生成器"""
        self.api_key = api_key or self.OPENCLAW_TOKEN
        self.base_url = base_url or self.OPENCLAW_BASE_URL
        self.model = model or self.DAILY_MODEL
        self.available = True
    
    def _call_openclaw(self, prompt: str) -> str:
        """调用 OpenClaw Chat Completions API"""
        try:
            url = f"{self.base_url}/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150,
                "temperature": 0.8
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return content.strip().strip('"').strip("'")
            
            print(f"OpenClaw API 调用失败: {response.status_code} - {response.text[:200]}")
            raise Exception(f"API 调用失败: {response.status_code}")
            
        except Exception as e:
            print(f"OpenClaw API 错误: {e}")
            raise
    
    def _call_llm(self, prompt: str) -> str:
        """统一调用入口"""
        return self._call_openclaw(prompt)
    
    def generate_comment(self, post_content: str, ai_personality: str = "阳光开朗") -> str:
        """根据帖子内容生成智能评论"""
        prompt = f"""你是一个{ai_personality}的AI，请根据以下帖子内容生成一条简短、友好、有趣的评论（30字以内）。

帖子内容：
{post_content}

请直接输出评论内容，不要解释："""
        
        try:
            return self._call_llm(prompt)
        except:
            return self._generate_smart_fallback_comment(post_content)
    
    def generate_chat_message(self, target_message: str, chat_history: List[Dict] = None, ai_personality: str = "热情友好") -> str:
        """生成私聊回复消息"""
        history_text = ""
        if chat_history:
            recent = chat_history[-3:]
            for msg in recent:
                role = "对方" if msg.get("role") == "user" else "我"
                history_text += f"{role}：{msg.get('content', '')}\n"
        
        prompt = f"""你是一个热情、友好的AI，请根据对方的消息生成一条简短的私聊回复（20字以内）。

对方消息：{target_message}

{history_text}
请直接输出回复内容，不要解释："""
        
        try:
            return self._call_llm(prompt)
        except:
            return self._generate_smart_fallback_chat(target_message)
    
    def generate_comment_reply(self, comment: str, post_content: str = "", ai_personality: str = "", author_name: str = "") -> str:
        """生成评论回复"""
        prompt = f"""你是一个热情、友好的AI，请回复以下评论（20字以内）。

评论：{comment}
帖子：{post_content}

请直接输出回复，不要解释："""
        
        try:
            return self._call_llm(prompt)
        except:
            return self._generate_smart_fallback_comment_reply(comment)
    
    # ==================== Fallback 智能随机回复 ====================
    
    COMMENT_TEMPLATES = [
        "说得太有道理了！👍",
        "这观点很棒，学到了！",
        "哈哈，太赞同了！",
        "确实是这样呢～",
        "感谢分享，受教了！",
        "太厉害了，点赞！",
        "这个真不错，mark一下",
        "说得太对了！",
        "有被戳到！",
        "太真实了哈哈哈",
        "我也是这么想的！",
        "必须支持！",
        "有点意思～",
        "哇，写得真好！",
        "厉害厉害！",
    ]
    
    CHAT_TEMPLATES = [
        "你好呀！😊",
        "哈哈，同感！",
        "说得对！",
        "嗯嗯！",
        "我也是！",
        "有意思！",
        "真的吗？",
        "那太棒了！",
        "了解～",
        "好的好的！",
        "明白了！",
        "很好！",
        "加油！💪",
        "期待！",
        "好呀好呀！",
    ]
    
    COMMENT_REPLY_TEMPLATES = [
        "谢谢！😊",
        "哈哈！",
        "是呀是呀！",
        "嗯嗯！",
        "感谢支持！",
        "必须的！",
    ]
    
    def _generate_smart_fallback_comment(self, post_content: str) -> str:
        """根据帖子内容选择合适的随机评论"""
        content = post_content.lower()
        
        if any(k in content for k in ["天气", "心情", "开心", "快乐", "高兴"]):
            templates = ["心情真好！😊", "开心最重要！", "快乐传染～"]
        elif any(k in content for k in ["工作", "加班", "上班", "学习"]):
            templates = ["加油！💪", "打工人不易！", "辛苦了！"]
        elif any(k in content for k in ["美食", "吃饭", "饿了", "餐厅"]):
            templates = ["看着好香！", "馋了馋了！", "吃货属性暴露～"]
        elif any(k in content for k in ["运动", "跑步", "健身", "锻炼"]):
            templates = ["生命在于运动！", "健身人！💪", "动起来！"]
        elif any(k in content for k in ["谢谢", "感谢"]):
            templates = ["不客气！😊", "一起加油！", "一起进步！"]
        elif any(k in content for k in ["问题", "求助", "怎么办"]):
            templates = ["加油！", "会好起来的！", "别灰心！"]
        elif any(k in content for k in ["爱", "喜欢", "恋爱"]):
            templates = ["甜甜的！💕", "好甜！", "羡慕！"]
        else:
            templates = self.COMMENT_TEMPLATES
        
        return random.choice(templates)
    
    def _generate_smart_fallback_chat(self, message: str) -> str:
        """根据消息内容选择合适的随机回复"""
        content = message.lower()
        
        if any(k in content for k in ["你好", "嗨", "hi", "hello"]):
            templates = ["你好呀！😊", "嗨！很高兴认识你！", "你好！"]
        elif any(k in content for k in ["谢谢", "感谢"]):
            templates = ["不客气！😊", "一起加油！", "客气啦！"]
        elif any(k in content for k in ["吃饭", "美食", "饿了"]):
            templates = ["我也饿了！😂", "一起吃呀！", "馋了～"]
        elif any(k in content for k in ["吗", "是不是", "对不对"]):
            templates = ["对呀！", "是呢！", "没错！"]
        elif any(k in content for k in ["哈哈", "笑", "搞笑"]):
            templates = ["哈哈哈！😂", "太逗了！", "笑死我了！"]
        elif any(k in content for k in ["困", "累", "睡觉", "晚安"]):
            templates = ["早点休息哦！😊", "晚安！💤", "好梦～"]
        elif any(k in content for k in ["开心", "高兴", "快乐"]):
            templates = ["开心最重要！😊", "好呀！", "太棒了！"]
        else:
            templates = self.CHAT_TEMPLATES
        
        return random.choice(templates)
    
    def _generate_smart_fallback_comment_reply(self, comment: str) -> str:
        """根据评论内容选择合适的回复"""
        content = comment.lower()
        
        if any(k in content for k in ["谢谢", "感谢"]):
            templates = ["不客气！😊", "一起加油！"]
        elif any(k in content for k in ["哈哈", "笑"]):
            templates = ["哈哈哈！😂", "太逗了！"]
        elif any(k in content for k in ["对", "是", "没错"]):
            templates = ["嗯嗯！", "是呢！"]
        else:
            templates = self.COMMENT_REPLY_TEMPLATES
        
        return random.choice(templates)


def create_generator_from_config(config: Dict[str, Any]) -> SmartInteractionGenerator:
    """从配置创建智能互动生成器"""
    return SmartInteractionGenerator()


if __name__ == "__main__":
    # 测试
    generator = SmartInteractionGenerator()
    
    print("=== SmartInteractionGenerator 测试 ===")
    print(f"API Type: OpenClaw")
    print(f"Base URL: {generator.base_url}")
    print(f"Model: {generator.model}")
    print()
    
    # 测试评论生成
    post = "今天天气真好，心情也跟着变好了！"
    comment = generator.generate_comment(post)
    print(f"帖子：{post}")
    print(f"评论：{comment}")
    print()
    
    # 测试聊天生成
    chat = generator.generate_chat_message("你好，很高兴认识你！", [])
    print(f"聊天回复：{chat}")
