#!/usr/bin/env python3
"""
智能压缩模块

自动压缩上下文，保留关键信息
参考 Claude Code 的 wU2 压缩算法
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


@dataclass
class Message:
    """消息"""
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5  # 0-1 重要性


@dataclass
class CompressionResult:
    """压缩结果"""
    original_count: int
    compressed_count: int
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    preserved_items: List[Message]
    removed_items: List[Message]


class ImportanceScorer:
    """重要性评分器"""
    
    # 关键词权重
    IMPORTANT_KEYWORDS = {
        "重要": 0.8,
        "记住": 0.9,
        "用户": 0.7,
        "喜欢": 0.7,
        "配置": 0.6,
        "设置": 0.6,
        "错误": 0.8,
        "修复": 0.8,
        "完成": 0.5,
        "新增": 0.5,
    }
    
    # 低重要性关键词
    LOW_IMPORTANCE_KEYWORDS = {
        "你好": 0.2,
        "谢谢": 0.2,
        "收到": 0.2,
        "好的": 0.3,
        "嗯": 0.1,
        "啊": 0.1,
    }
    
    @classmethod
    def score(cls, message: Message) -> float:
        """计算重要性分数"""
        content = message.content.lower()
        score = message.importance
        
        # 检查重要关键词
        for keyword, weight in cls.IMPORTANT_KEYWORDS.items():
            if keyword in content:
                score = max(score, weight)
        
        # 检查低重要性关键词
        for keyword, weight in cls.LOW_IMPORTANCE_KEYWORDS.items():
            if keyword in content:
                score = min(score, weight)
        
        # 长度加权（太短或太长都降低分数）
        length = len(content)
        if length < 10:
            score *= 0.8
        elif length > 2000:
            score *= 0.9
        
        # 用户消息权重稍高
        if message.role == "user":
            score *= 1.1
        
        return min(1.0, max(0.0, score))
    
    @classmethod
    def rank_messages(cls, messages: List[Message]) -> List[Message]:
        """对消息按重要性排序"""
        scored = [(msg, cls.score(msg)) for msg in messages]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [msg for msg, _ in scored]


class ContextCompressor:
    """上下文压缩器"""
    
    def __init__(self, 
                 token_limit: int = 100000,
                 compression_threshold: float = 0.92,
                 preserve_ratio: float = 0.3):
        self.token_limit = token_limit
        self.compression_threshold = compression_threshold
        self.preserve_ratio = preserve_ratio
    
    def estimate_tokens(self, text: str) -> int:
        """估算 token 数量（简化版：中文约1.5 token/字，英文约1.2 token/词）"""
        # 简单估算：中文字符 * 1.5 + 英文单词 * 1.2
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        return int(chinese_chars * 1.5 + english_words * 1.2)
    
    def compress(self, messages: List[Message]) -> CompressionResult:
        """压缩消息列表"""
        original_count = len(messages)
        original_tokens = sum(self.estimate_tokens(m.content) for m in messages)
        
        # 检查是否需要压缩
        if original_tokens < self.token_limit * self.compression_threshold:
            return CompressionResult(
                original_count=original_count,
                compressed_count=original_count,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                preserved_items=messages,
                removed_items=[]
            )
        
        # 计算保留数量
        target_tokens = int(self.token_limit * self.preserve_ratio)
        
        # 按重要性排序
        ranked_messages = ImportanceScorer.rank_messages(messages)
        
        # 保留高重要性的消息
        preserved = []
        preserved_tokens = 0
        
        for msg in ranked_messages:
            msg_tokens = self.estimate_tokens(msg.content)
            
            if preserved_tokens + msg_tokens <= target_tokens:
                preserved.append(msg)
                preserved_tokens += msg_tokens
            else:
                # 尝试保留消息的头部（摘要）
                if msg_tokens > 100:
                    # 保留前200字符
                    msg.content = msg.content[:200] + "... [已压缩]"
                    preserved.append(msg)
                    preserved_tokens += self.estimate_tokens(msg.content)
                else:
                    break
        
        # 按时间顺序重新排序
        preserved.sort(key=lambda m: m.timestamp)
        
        removed_count = original_count - len(preserved)
        
        return CompressionResult(
            original_count=original_count,
            compressed_count=len(preserved),
            original_tokens=original_tokens,
            compressed_tokens=preserved_tokens,
            compression_ratio=preserved_tokens / original_tokens if original_tokens > 0 else 1.0,
            preserved_items=preserved,
            removed_items=ranked_messages[len(preserved):]
        )
    
    def compress_summary(self, messages: List[Message]) -> str:
        """生成压缩摘要"""
        if not messages:
            return ""
        
        # 取最近的和最重要的
        recent = messages[-5:]
        summary_parts = ["[上下文已压缩]"]
        
        summary_parts.append(f"共 {len(messages)} 条消息")
        
        # 关键信息提取
        important_keywords = []
        for msg in messages:
            for keyword in ImportanceScorer.IMPORTANT_KEYWORDS:
                if keyword in msg.content:
                    important_keywords.append(keyword)
        
        if important_keywords:
            keywords = list(set(important_keywords))[:5]
            summary_parts.append(f"关键主题: {', '.join(keywords)}")
        
        return " | ".join(summary_parts)


class SmartCompressor:
    """智能压缩器（高级版）"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.compressor = ContextCompressor(
            token_limit=self.config.get("token_limit", 100000),
            compression_threshold=self.config.get("threshold", 0.92),
            preserve_ratio=self.config.get("preserve_ratio", 0.3)
        )
        self.compression_history: List[CompressionResult] = []
    
    def should_compress(self, messages: List[Message]) -> bool:
        """判断是否需要压缩"""
        total_tokens = sum(
            self.compressor.estimate_tokens(m.content) 
            for m in messages
        )
        
        threshold = self.compressor.token_limit * self.compressor.compression_threshold
        return total_tokens > threshold
    
    def compress(self, messages: List[Message]) -> CompressionResult:
        """执行压缩"""
        result = self.compressor.compress(messages)
        self.compression_history.append(result)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        if not self.compression_history:
            return {"count": 0}
        
        total_original = sum(r.original_tokens for r in self.compression_history)
        total_compressed = sum(r.compressed_tokens for r in self.compression_history)
        
        return {
            "count": len(self.compression_history),
            "total_original_tokens": total_original,
            "total_compressed_tokens": total_compressed,
            "avg_compression_ratio": total_compressed / total_original if total_original > 0 else 1.0,
            "messages_removed": sum(r.original_count - r.compressed_count for r in self.compression_history)
        }


# ============ 使用示例 ============

def example():
    """示例"""
    print(f"{Fore.CYAN}=== 智能压缩示例 ==={Fore.RESET}\n")
    
    # 创建测试消息
    messages = [
        Message("user", "你好"),
        Message("assistant", "你好！有什么可以帮你的？"),
        Message("user", "记住我的名字叫主人"),
        Message("assistant", "好的，我记住你的名字叫主人"),
        Message("user", "我喜欢瓦罗兰特游戏"),
        Message("assistant", "瓦罗兰特是一款很有趣的 FPS 游戏"),
        Message("user", "我的配置是 RTX 4080"),
        Message("assistant", "RTX 4080 是很强大的显卡"),
        Message("user", "今天天气真好啊"),
        Message("assistant", "是的，天气很不错"),
        Message("user", "上次我让你帮我写一个 Python 脚本"),
        Message("assistant", "是的，那是一个文件处理的脚本"),
        Message("user", "配置一下我的开发环境"),
        Message("assistant", "好的，我来帮你配置"),
    ]
    
    # 1. 重要性评分
    print("1. 消息重要性评分:")
    scored = ImportanceScorer.rank_messages(messages)
    for msg in scored[:5]:
        score = ImportanceScorer.score(msg)
        print(f"   [{score:.2f}] {msg.role}: {msg.content[:30]}...")
    
    # 2. 压缩
    print("\n2. 上下文压缩:")
    compressor = SmartCompressor({"token_limit": 1000, "threshold": 0.5, "preserve_ratio": 0.3})
    result = compressor.compress(messages)
    
    print(f"   原始消息: {result.original_count} 条")
    print(f"   压缩后: {result.compressed_count} 条")
    print(f"   原始 token: {result.original_tokens}")
    print(f"   压缩后 token: {result.compressed_tokens}")
    print(f"   压缩率: {result.compression_ratio:.1%}")
    print(f"   删除消息: {result.original_count - result.compressed_count} 条")
    
    # 3. 生成摘要
    print("\n3. 压缩摘要:")
    summary = compressor.compress_summary(messages)
    print(f"   {summary}")
    
    # 4. 统计
    print("\n4. 压缩统计:")
    stats = compressor.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n{Fore.GREEN}✓ 智能压缩示例完成!{Fore.RESET}")


if __name__ == "__main__":
    example()