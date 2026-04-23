#!/usr/bin/env python3
"""
数字人生成工具
流程：
1. 输入 mp3 路径/URL
2. 输入 mp4 路径/URL
3. 输入文字内容
4. 用户确认 → 重新操作/提交
5. 重新操作 → 回到第1步
6. 提交 → 直接发送URL+文字给后端
7. 进度到99%等待结果，返回后输出视频链接
"""
import requests
import time
import sys
import json

API_ENDPOINT = "https://yunji.focus-jd.cn"
#API_ENDPOINT = "http://localhost:8564"

def prompt(message):
    print(f"\n{message}", end='')
    sys.stdout.flush()
    return input().strip()

def main():
    print("=" * 50)
    print("       数字人生成工具")
    print("=" * 50)

    while True:
        # 1. 输入MP3
        mp3 = ""
        while not mp3:
            mp3 = prompt("1️⃣  请输入 MP3 路径/URL: ")
            if not mp3:
                print("❌ 不能为空，请重新输入")

        # 2. 输入MP4
        mp4 = ""
        while not mp4:
            mp4 = prompt("2️⃣  请输入 MP4 路径/URL: ")
            if not mp4:
                print("❌ 不能为空，请重新输入")

        # 3. 输入文字
        text = ""
        while not text:
            text = prompt("3️⃣  请输入需要合成的文字内容: ")
            if not text:
                print("❌ 不能为空，请重新输入")

        # 4. 确认
        print("\n📋 请确认信息：")
        print(f"  MP3: {mp3}")
        print(f"  MP4: {mp4}")
        print(f"  文字: {text}")
        print()

        confirm = ""
        while confirm not in ["1", "2"]:
            confirm = prompt("请选择：[1] 提交  [2] 重新输入\n选择: ")
            if confirm not in ["1", "2"]:
                print("❌ 请输入 1 或 2")

        if confirm == "2":
            print("\n🔄 重新开始...")
            continue

        # 7. 提交到后端
        print("\n🚀 正在提交...")
        try:
            payload = {"mp3": mp3, "mp4": mp4, "text": text}
            resp = requests.post(API_ENDPOINT + "/skill/api/submit", json=payload, timeout=300000)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            print(f"\n❌ 提交失败: {str(e)}")
            return

        # 直接返回结果
        if "videoUrl" in result:
            print("\n✅ 生成完成!")
            print(f"\n📺 视频链接: {result['videoUrl']}")
            return

        # 需要等待，开始进度（每 0.5 秒增加 1%）
        print("\n⚙️  生成中...")
        progress = 0
        while progress < 99:
            progress += 1
            print(f"\r正在提交... {int(progress)}%", end='')
            sys.stdout.flush()
            # time.sleep(2)
            time.sleep(0.1)

        # 停在99%
        print(f"\r正在生成... 99% (等待后端处理)", end='')
        sys.stdout.flush()

        # 轮询
        if "orderNo" in result:
            task_id = result["orderNo"]
            status_url = API_ENDPOINT + "/skill/api/api/result"


            print("\n🚀 查询任务中结果...")
            while True:
                try:
                    r = requests.post(status_url, json={"orderNo": task_id}, timeout=30)
                    raw = r.json()
                    # 后端可能返回字符串形式的 JSON，需再解析一次
                    data = json.loads(raw) if isinstance(raw, str) else raw

                    # progress 可能为空或不存在，安全解析
                    progress_val = data.get("progress")
                    if progress_val is not None and progress_val != "":
                        try:
                            p = min(int(progress_val), 99)
                            print(f"\r正在生成... {p}% (等待后端处理)", end='')
                            sys.stdout.flush()
                        except (TypeError, ValueError):
                            pass

                    if data.get("status") == "done" and "videoUrl" in data:
                        print("\n✅ 生成完成!")
                        print(f"\n📺 视频链接: {data['videoUrl']}")
                        return
                    elif data.get("status") == "error":
                        print(f"\n❌ 生成失败: {data.get('message', '未知错误')}")
                        return
                    else:
                        time.sleep(2)
                except Exception:
                    time.sleep(3)
        else:
            print(f"\n📄 后端返回: {result}")
            return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
