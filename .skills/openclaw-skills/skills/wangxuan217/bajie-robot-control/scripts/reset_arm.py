#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 机械臂归位
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = "ws://10.10.10.12:9900"

def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_uuid() -> str:
    return str(uuid.uuid4())

def build_request(name: str, task_id: str, data: dict) -> dict:
    return {
        "header": {
            "mode": "mission",
            "type": "request",
            "cmd": "start",
            "ts": int(time.time()),
            "uuid": generate_uuid()
        },
        "body": {
            "name": name,
            "task_id": task_id,
            "data": data
        }
    }

async def reset_arm():
    print("=" * 70)
    print("🤖 八界机器人 - 机械臂归位")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人\n")
        
        # 使用 robot_ending_pose 让机械臂回到结束姿态
        print("【任务】机械臂归位 (robot_ending_pose)")
        print("-" * 70)
        
        task_id = generate_task_id("reset")
        request = build_request("robot_ending_pose", task_id, {})
        
        print("发送请求...")
        await ws.send(json.dumps(request))
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
                response = json.loads(msg)
                header = response["header"]
                body = response["body"]
                
                if header["type"] == "response":
                    code = body["data"]["error_code"]["code"]
                    if code == 0:
                        print("✓ 归位任务启动成功")
                    else:
                        print(f"❌ 启动失败：0x{code:08X}")
                
                elif header["type"] == "notify":
                    data = body["data"]
                    if "summary" in data:
                        print(f"执行中：{data['summary']}")
                
                if header["cmd"] == "finish":
                    code = body["data"]["error_code"]["code"]
                    msg = body["data"]["error_code"].get("msg", "")
                    print(f"\n完成：0x{code:08X} - {msg}")
                    
                    if code == 0:
                        print("\n✅ 机械臂已归位！")
                    else:
                        print("\n❌ 归位失败")
                    break
                    
            except asyncio.TimeoutError:
                print("⏱️  超时")
                break
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(reset_arm())
