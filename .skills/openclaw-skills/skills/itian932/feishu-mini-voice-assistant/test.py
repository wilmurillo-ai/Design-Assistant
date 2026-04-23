#!/usr/bin/env python3
"""
语音助手完整测试脚本
支持：转换、ASR、TTS、端到端流程
"""

import sys
import asyncio
import argparse
import tempfile
from pathlib import Path

# 添加技能目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from handler import VoiceAssistant
from converter import AudioConverter
from asr import WhisperASR
from tts import EdgeTTS

def test_converter():
    """测试格式转换功能"""
    print("=== 测试音频格式转换 ===")
    converter = AudioConverter()
    
    # 使用已有的测试文件
    test_wav = Path("/tmp/test_1k.wav")
    if test_wav.exists():
        print(f"找到测试文件: {test_wav}")
        
        # 测试 WAV → OGG
        with tempfile.TemporaryDirectory() as tmpdir:
            opus_out = Path(tmpdir) / "test.ogg"
            print(f"转换: WAV → OGG")
            converter.wav_to_opus(str(test_wav), str(opus_out))
            
            if opus_out.exists() and opus_out.stat().st_size > 0:
                print(f"✅ OGG 转换成功: {opus_out.stat().st_size} bytes")
            else:
                print("❌ OGG 转换失败")
                return False
            
            # 测试 OGG → WAV（反向）
            wav_out = Path(tmpdir) / "back.wav"
            print(f"转换: OGG → WAV")
            converter.ogg_to_wav(str(opus_out), str(wav_out))
            
            if wav_out.exists() and wav_out.stat().st_size > 0:
                print(f"✅ WAV 转换成功: {wav_out.stat().st_size} bytes")
            else:
                print("❌ WAV 转换失败")
                return False
        
        return True
    else:
        print("⚠️  未找到测试文件 /tmp/test_1k.wav，跳过转换测试")
        return True

def test_asr():
    """测试 Whisper 识别"""
    print("\n=== 测试 Whisper ASR ===")
    try:
        asr = WhisperASR(
            model_path=Path(__file__).parent / "models/whisper/ggml-large-v3-turbo.bin",
            whisper_bin=Path.home() / ".openclaw/workspace/whisper.cpp/build/bin/whisper-cli",
            language="zh",
            threads=8
        )
        
        test_wav = Path("/tmp/test_1k.wav")
        if test_wav.exists():
            print(f"识别: {test_wav}")
            text = asr.transcribe(str(test_wav))
            print(f"✅ 识别结果: {text}")
            return True
        else:
            print("⚠️  未找到测试文件 /tmp/test_1k.wav，跳过 ASR 测试")
            return True
    except Exception as e:
        print(f"❌ ASR 测试失败: {e}")
        return False

def test_tts():
    """测试 Edge-TTS"""
    print("\n=== 测试 Edge-TTS ===")
    try:
        tts = EdgeTTS(voice="xiaoxiao")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.mp3"
            text = "你好，我是小梦，欢迎使用语音助手。"
            
            print(f"合成: {text}")
            success = tts.synthesize(text, str(test_file))
            
            if success and test_file.exists() and test_file.stat().st_size > 0:
                print(f"✅ TTS 成功: {test_file.stat().st_size} bytes")
                return True
            else:
                print("❌ TTS 失败")
                return False
    except Exception as e:
        print(f"❌ TTS 测试异常: {e}")
        return False

def test_full_pipeline():
    """测试完整流程（模拟）"""
    print("\n=== 测试完整流程 ===")
    
    try:
        assistant = VoiceAssistant()
        
        # 模拟飞书语音消息
        test_message = {
            "file_path": "/tmp/test_1k.wav",
            "chat_id": "test_chat_123",
            "message_id": "test_msg_001",
            "sender_id": "test_user_001"
        }
        
        print("🚀 开始处理模拟消息...")
        result = asyncio.run(assistant.handle_voice_message(test_message))
        
        if result["status"] == "success":
            print(f"✅ 流程成功")
            print(f"   ASR 文本: {result['asr_text']}")
            print(f"   回复文本: {result['reply_text']}")
            print(f"   音频路径: {result['audio_path']}")
            return True
        else:
            print(f"❌ 流程失败: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ 完整流程异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="语音助手测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    parser.add_argument("--converter", action="store_true", help="测试格式转换")
    parser.add_argument("--asr", action="store_true", help="测试 ASR")
    parser.add_argument("--tts", action="store_true", help="测试 TTS")
    parser.add_argument("--pipeline", action="store_true", help="测试完整流程")
    args = parser.parse_args()
    
    # 默认运行所有测试
    if not any([args.all, args.converter, args.asr, args.tts, args.pipeline]):
        args.all = True
    
    results = []
    
    if args.all or args.converter:
        results.append(("格式转换", test_converter()))
    
    if args.all or args.asr:
        results.append(("ASR", test_asr()))
    
    if args.all or args.tts:
        results.append(("TTS", test_tts()))
    
    if args.all or args.pipeline:
        results.append(("完整流程", test_full_pipeline()))
    
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    for name, ok in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_ok = all(ok for _, ok in results)
    if all_ok:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
            print(f"音色: {tts.voice}")
            
            tts.synthesize(text, str(test_file))
            
            if test_file.exists() and test_file.stat().st_size > 0:
                print(f"✅ 合成成功: {test_file} ({test_file.stat().st_size} bytes)")
                return True
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 合成失败: {e}")
        return False

def test_asr():
    """测试 Whisper ASR（需要模型就绪）"""
    print("\n=== 测试 Whisper ASR ===")
    try:
        from asr import WhisperASR
        import tempfile
        
        # 模型路径（从 config 读取或直接指定）
        model_path = Path("~/.openclaw/workspace/skills/voice-assistant/models/whisper/ggml-large-v3-turbo.bin").expanduser()
        bin_path = Path("~/.openclaw/workspace/whisper.cpp/build/bin/main").expanduser()
        
        if not model_path.exists() or not bin_path.exists():
            print(f"⚠️  模型或二进制未就绪")
            print(f"   模型: {model_path} {'✅' if model_path.exists() else '❌'}")
            print(f"   二进制: {bin_path} {'✅' if bin_path.exists() else '❌'}")
            return False
        
        asr = WhisperASR(model_path=str(model_path), whisper_bin=str(bin_path))
        
        # 创建一个简单的测试音频（1kHz 音，3秒）
        test_wav = Path("/tmp/voice_assistant_test.wav")
        if not test_wav.exists():
            print(f"生成测试 WAV: {test_wav}")
            import subprocess
            subprocess.run([
                'ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=3',
                '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(test_wav)
            ], capture_output=True, check=True)
        
        print(f"识别: {test_wav}")
        text = asr.transcribe(str(test_wav))
        print(f"📝 结果: {text}")
        
        if text.strip():
            print("✅ 识别成功（返回了文本）")
            return True
        else:
            print("❌ 识别结果为空")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("🚀 语音助手测试套件\n")
    
    results = []
    
    # 1. 转换测试（依赖飞书目录有文件）
    results.append(("格式转换", test_converter()))
    
    # 2. TTS 测试
    results.append(("Edge-TTS", test_tts()))
    
    # 3. ASR 测试
    results.append(("Whisper ASR", test_asr()))
    
    print("\n=== 测试结果 ===")
    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{name:12} {status}")
    
    all_ok = all(r[1] for r in results)
    if all_ok:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试未通过，请检查")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
