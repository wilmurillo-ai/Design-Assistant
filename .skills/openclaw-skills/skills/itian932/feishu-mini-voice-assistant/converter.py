#!/usr/bin/env python3
"""
音频格式转换工具
封装 ffmpeg 命令，处理飞书语音格式转换
"""

import subprocess
from pathlib import Path
from typing import Optional


class AudioConverter:
    """音频格式转换器"""
    
    @staticmethod
    def ogg_to_wav(input_path: str, output_path: Optional[str] = None) -> str:
        """
        飞书 OGG (OPUS) → WAV (16kHz, 16bit, mono)
        
        Args:
            input_path: 输入 OGG 文件路径
            output_path: 输出 WAV 文件路径（可选，默认同路径 .wav）
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.with_suffix('.wav')
        else:
            output_path = Path(output_path)
        
        cmd = [
            'ffmpeg', '-y',  # 覆盖输出文件
            '-i', str(input_path),
            '-ar', '16000',     # 采样率 16kHz（Whisper 标准）
            '-ac', '1',         # 单声道
            '-c:a', 'pcm_s16le', # 16-bit signed PCM
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return str(output_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg conversion failed: {e.stderr}") from e
    
    @staticmethod
    def wav_to_opus(input_path: str, output_path: Optional[str] = None) -> str:
        """
        WAV/MP3 → OGG/Opus（飞书发送格式）
        
        Args:
            input_path: 输入 WAV/MP3 文件路径
            output_path: 输出 OGG 文件路径（可选）
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        if output_path is None:
            # 如果输入是 .wav 输出 .ogg，如果是 .mp3 也输出 .ogg
            output_path = input_path.with_suffix('.ogg')
        else:
            output_path = Path(output_path)
        
        cmd = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-c:a', 'libopus',
            '-b:a', '64k',      # 比特率 64kbps（质量/大小平衡）
            '-ar', '24000',     # 采样率 24kHz（飞书标准）
            '-ac', '1',         # 单声道（语音足够）
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            return str(output_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg OPUS conversion failed: {e.stderr}") from e
    
    # 别名 - opus 就是 ogg 容器
    opus_to_wav = ogg_to_wav
    wav_to_ogg = wav_to_opus
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """
        检测音频文件格式
        
        Returns:
            格式名称：'ogg', 'wav', 'mp3', 等
        """
        import mimetypes
        mime, _ = mimetypes.guess_type(file_path)
        if mime:
            if 'ogg' in mime:
                return 'ogg'
            elif 'wav' in mime or 'wave' in mime:
                return 'wav'
            elif 'mp3' in mime:
                return 'mp3'
        # 回退到扩展名判断
        ext = Path(file_path).suffix.lower()
        return ext.lstrip('.')
