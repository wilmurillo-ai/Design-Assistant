#!/usr/bin/env python3
"""
Edge-TTS 封装
使用微软 Edge-TTS 服务进行语音合成
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional

# 确保可以导入 lib 目录的依赖
lib_path = Path(__file__).parent / 'lib'
if lib_path.exists() and str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

try:
    import edge_tts
except ImportError:
    raise ImportError("edge-tts not found. Install with: pip install edge-tts")


class EdgeTTS:
    """Edge-TTS 语音合成器"""
    
    # 音色配置（精选女声，涵盖多种语言和风格）
    VOICES = {
        # 🇨🇳 简体中文普通话
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 温暖、自然，非常通用
        "xiaohan": "zh-CN-XiaohanNeural",        # 自然女声
        "xiaomo": "zh-CN-XiaomoNeural",          # 成熟女声
        "xiaoxuan": "zh-CN-XiaoxuanNeural",      # 温暖女声
        "xiaorui": "zh-CN-XiaoruiNeural",        # 感性女声
        "xiaoyi": "zh-CN-XiaoyiNeural",          # 可爱、清新女声
        
        # 🇨🇳 方言女声
        "liaoning": "zh-CN-liaoning-XiaobeiNeural",  # 辽宁话，幽默
        "shaanxi": "zh-CN-shaanxi-XiaoniNeural",     # 陕西方言，明亮
        
        # 🇭🇰 粤语
        "hiugaai": "zh-HK-HiuGaaiNeural",             # 友好积极
        "hiumaan": "zh-HK-HiuMaanNeural",            # 粤语女声
        
        # 🇹🇼 台湾中文
        "hsiaochen": "zh-TW-HsiaoChenNeural",         # 友好积极
        
        # 🌍 其他语言（可选）
        # "jenny": "en-US-JennyNeural",              # 英语女声
        # "aria": "en-US-AriaNeural",                # 英语女声
        # "nanami": "ja-JP-NanamiNeural",            # 日语女声
        # "aoi": "ja-JP-AoiNeural",                  # 日语女声
        # "sunhi": "ko-KR-SunHiNeural",              # 韩语女声
    }
    
    def __init__(self, voice: str = "xiaoxiao", rate: str = "+0%", volume: str = "+0%"):
        """初始化 Edge-TTS"""
        if voice in self.VOICES:
            self.voice = self.VOICES[voice]
        else:
            self.voice = voice  # 直接使用提供的 voice ID
        self.rate = rate
        self.volume = volume
    
    async def synthesize_async(self, text: str, mp3_path: str) -> str:
        """异步合成 MP3"""
        output_path = Path(mp3_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, volume=self.volume)
            await communicate.save(str(output_path))
            return str(output_path)
        except Exception as e:
            raise RuntimeError(f"Edge-TTS failed: {e}")
    
    def synthesize(self, text: str, mp3_path: str) -> str:
        """同步合成 MP3"""
        return asyncio.run(self.synthesize_async(text, mp3_path))


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Edge-TTS 语音合成")
    parser.add_argument("--text", "-t", help="要合成的文本")
    parser.add_argument("--output", "-o", help="输出 OGG 文件路径")
    parser.add_argument("--voice", "-v", default="xiaoxiao", 
                       help="音色: xiaoxiao, liaoning, shaanxi, hiugaai, hsiaochen")
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用音色")
    
    args = parser.parse_args()
    
    # 优先处理列出音色
    if args.list_voices:
        tts = EdgeTTS()
        for key, vid in EdgeTTS.VOICES.items():
            print(f"{key}: {vid}")
        sys.exit(0)
    
    # 正常合成需要 text 和 output
    if not args.text or not args.output:
        parser.error("--text 和 --output 是必需的（除非使用 --list-voices）")
    
    tts = EdgeTTS(voice=args.voice)
    try:
        import tempfile
        import uuid
        from pathlib import Path
        from datetime import datetime
        from os import getenv
        
        # 确定 workspace 临时目录
        workspace = Path(getenv("OPENCLAW_WORKSPACE", str(Path(__file__).parent.parent.parent)))
        tmp_dir = workspace / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保输出路径在 workspace 下
        output_path = Path(args.output)
        if not str(output_path).startswith(str(workspace)):
            # 如果输出路径不在 workspace 内，重定向到 workspace/tmp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_path.name if output_path.name else f"tts-{timestamp}-{uuid.uuid4().hex[:8]}.ogg"
            output_path = tmp_dir / filename
        
        output_path = output_path.with_suffix('.ogg')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 先合成 MP3 到临时文件
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp_mp3 = Path(tmp.name)
        
        try:
            tts.synthesize(args.text, str(tmp_mp3))
            # 转换为 OGG - 需要导入 AudioConverter
            from converter import AudioConverter
            converter = AudioConverter()
            converter.wav_to_ogg(str(tmp_mp3), str(output_path))
        finally:
            tmp_mp3.unlink(missing_ok=True)
        
        print(str(output_path))  # 输出 OGG 文件路径
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
