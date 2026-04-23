#!/usr/bin/env python3
"""
Whisper.cpp ASR 封装
 Whisper.cpp 二进制，进行语音识别
"""

import subprocess
from pathlib import Path
from typing import Optional


class WhisperASR:
    """Whisper.cpp 语音识别器"""
    
    def __init__(
        self,
        model_path: str,
        whisper_bin: str = "whisper.cpp/build/bin/main",
        language: str = "zh",
        threads: int = 8
    ):
        """
        初始化 Whisper ASR
        
        Args:
            model_path: ggml 模型文件路径（如 ggml-large-v3-turbo.bin）
            whisper_bin: whisper.cpp 可执行文件路径
            language: 语言代码（zh=中文，en=英文等）
            threads: 推理线程数（建议 CPU 核心数）
        """
        self.model_path = Path(model_path).expanduser().resolve()
        self.whisper_bin = Path(whisper_bin).expanduser().resolve()
        self.language = language
        self.threads = threads
        
        if not self.whisper_bin.exists():
            raise FileNotFoundError(f"Whisper binary not found: {self.whisper_bin}")
        if not self.model_path.exists():
            raise FileNotFoundError(f"Whisper model not found: {self.model_path}")
    
    def transcribe(self, wav_path: str, language: Optional[str] = None) -> str:
        """
        识别 WAV 文件，返回识别文本
        
        Args:
            wav_path: WAV 文件路径（16kHz, 16bit, mono 最佳）
            language: 语言代码（覆盖默认）
            
        Returns:
            识别的文本（UTF-8）
        """
        wav_path = Path(wav_path).resolve()
        if not wav_path.exists():
            raise FileNotFoundError(f"Audio file not found: {wav_path}")
        
        # 优先使用 whisper-cli（新接口）
        whisper_bin = self.whisper_bin
        if whisper_bin.name == "main" and (whisper_bin.parent / "whisper-cli").exists():
            whisper_bin = whisper_bin.parent / "whisper-cli"
        
        cmd = [
            str(whisper_bin),
            "-m", str(self.model_path),
            "-f", str(wav_path),
            "-l", language or self.language,
            "-t", str(self.threads),
            "--no-timestamps"  # 不输出时间戳，纯文本
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 最多 60 秒
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Whisper failed: {result.stderr}")
            
            # 清理输出：去除空行和前后空白
            text = result.stdout.strip()
            return text
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Whisper transcription timed out (60s)")
    
    def transcribe_with_details(self, wav_path: str, language: Optional[str] = None) -> dict:
        """
        识别并返回详细信息（包括时间戳）
        
        Returns:
            dict 包含 text, segments 等
        """
        wav_path = Path(wav_path).resolve()
        
        cmd = [
            str(self.whisper_bin),
            "-m", str(self.model_path),
            "-f", str(wav_path),
            "-l", language or self.language,
            "-t", str(self.threads),
            "-ojson"  # JSON 输出
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"Whisper failed: {result.stderr}")
        
        import json
        return json.loads(result.stdout)


def main():
    """命令行入口 - ASR 语音识别（支持 OGG/WAV）"""
    import argparse
    import tempfile
    import os
    import sys
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="ASR 语音识别（支持 OGG/WAV）")
    parser.add_argument("audio_file", help="音频文件路径（OGG 或 WAV）")
    parser.add_argument("--model", help="Whisper 模型路径")
    parser.add_argument("--bin", help="whisper-cli 可执行文件路径")
    parser.add_argument("--lang", default="zh", help="语言代码（默认: zh）")
    parser.add_argument("--threads", type=int, default=8, help="推理线程数（默认: 8）")
    
    args = parser.parse_args()
    
    # 初始化 ASR
    model_path = args.model or os.getenv("WHISPER_MODEL", "models/whisper/ggml-large-v3-turbo.bin")
    whisper_bin = args.bin or os.getenv("WHISPER_BIN", "/usr/local/bin/whisper-cli")
    
    asr = WhisperASR(
        model_path=model_path,
        whisper_bin=whisper_bin,
        language=args.lang,
        threads=args.threads
    )
    
    audio_path = Path(args.audio_file)
    
    # 如果是 OGG，先转换为 WAV
    if audio_path.suffix.lower() == '.ogg':
        print(f"检测到 OGG 格式，正在转换为 WAV...", file=sys.stderr)
        from converter import AudioConverter
        converter = AudioConverter()
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            wav_path = tmp.name
        try:
            converter.ogg_to_wav(str(audio_path), wav_path)
            text = asr.transcribe(wav_path)
        finally:
            Path(wav_path).unlink(missing_ok=True)
    else:
        # 直接识别 WAV
        text = asr.transcribe(str(audio_path))
    
    print(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
