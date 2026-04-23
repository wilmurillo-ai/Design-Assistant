#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 简单连接测试
"""

import asyncio
import json
import time
import uuid
import websockets

async def test_connection():
    uri = "ws://10.10.10.12:9900"
    
    print("=" * 70)
    print("🤖 八界机器人 - 连接测试")
    print("=" * 70)
    
    try:
        async with websockets.connect(uri) as ws:
            print("✅ 已连接到机器人")
            
            # 测试 1: 发送 oneshot 请求
            print("\n【测试 1】单次获取状态")
            print("-" * 70)
            
            oneshot_request = {
                "header": {
                    "mode": "event",
                    "type": "request",
                    "cmd": "oneshot",
                    "ts": int(time.time()),
                    "uuid": str(uuid.uuid4())
                },
                "body": {
                    "name": "robot_info",
                    "task_id": f"oneshot_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "topics": ["pos", "battery", "workState"]
                    }
                }
            }
            
            print("发送请求:")
            print(json.dumps(oneshot_request, indent=2, ensure_ascii=False))
            
            await ws.send(json.dumps(oneshot_request))
            
            # 接收所有响应（最多 5 条）
            print("\n接收响应:")
            for i in range(5):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    response = json.loads(msg)
                    print(f"\n[{i+1}] 收到消息:")
                    print(json.dumps(response, indent=2, ensure_ascii=False))
                except asyncio.TimeoutError:
                    print(f"[{i+1}] 超时，没有更多消息")
                    break
            
            # 测试 2: 发送搜索请求
            print("\n" + "=" * 70)
            print("【测试 2】搜索玩具")
            print("-" * 70)
            
            search_request = {
                "header": {
                    "mode": "mission",
                    "type": "request",
                    "cmd": "start",
                    "ts": int(time.time()),
                    "uuid": str(uuid.uuid4())
                },
                "body": {
                    "name": "search",
                    "task_id": f"search_{uuid.uuid4().hex[:8]}",
                    "data": {
                        "object": {
                            "item": "玩具",
                            "color": "",
                            "shape": "",
                            "person": "",
                            "type": [],
                            "subtype": []
                        },
                        "area": {
                            "area_name": "地上",
                            "area_id": ""
                        }
                    }
                }
            }
            
            print("发送请求:")
            print(json.dumps(search_request, indent=2, ensure_ascii=False))
            
            await ws.send(json.dumps(search_request))
            
            # 接收所有响应
            print("\n接收响应:")
            for i in range(10):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    response = json.loads(msg)
                    header = response.get("header", {})
                    body = response.get("body", {})
                    
                    print(f"\n[{i+1}] {header.get('type')}/{header.get('cmd')}:")
                    
                    if header.get("type") == "response":
                        error_code = body.get("data", {}).get("error_code", {})
                        print(f"   错误码：0x{error_code.get('code', 0):08X} - {error_code.get('msg', '')}")
                    
                    elif header.get("type") == "notify":
                        data = body.get("data", {})
                        if "position" in data:
                            print(f"   找到物体位置：{data.get('position')}")
                        elif "summary" in data:
                            print(f"   进度：{data.get('summary')}")
                    
                    if header.get("cmd") == "finish":
                        error_code = body.get("data", {}).get("error_code", {})
                        print(f"   ✅ 任务完成：0x{error_code.get('code', 0):08X}")
                        break
                        
                except asyncio.TimeoutError:
                    print(f"[{i+1}] 超时")
                    break
            
            print("\n" + "=" * 70)
            print("✅ 测试完成")
            
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
