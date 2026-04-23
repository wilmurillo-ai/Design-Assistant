#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 完整搜索测试（等待 finish）
"""

import asyncio
import json
import time
import uuid
import websockets

async def test_search():
    uri = "ws://10.10.10.12:9900"
    
    print("=" * 70)
    print("🤖 八界机器人 - 完整搜索测试")
    print("=" * 70)
    
    async with websockets.connect(uri) as ws:
        print("✅ 已连接到机器人")
        
        # 发送搜索请求
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
        
        print("\n发送搜索请求...")
        await ws.send(json.dumps(search_request))
        
        search_data = None
        msg_count = 0
        
        print("\n等待响应...")
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
                response = json.loads(msg)
                header = response.get("header", {})
                body = response.get("body", {})
                
                msg_count += 1
                msg_type = header.get("type", "unknown")
                cmd = header.get("cmd", "unknown")
                
                print(f"\n[{msg_count}] {msg_type}/{cmd}")
                
                if msg_type == "response":
                    error_code = body.get("data", {}).get("error_code", {})
                    code = error_code.get("code", 0)
                    print(f"   启动：0x{code:08X} - {error_code.get('msg', '')}")
                
                elif msg_type == "notify":
                    data = body.get("data", {})
                    
                    # 检查是否有 position 数据
                    if "position" in data:
                        search_data = data
                        print(f"   📍 找到物体!")
                        print(f"      位置：{data.get('position')}")
                        print(f"      朝向：{data.get('orientation')}")
                        print(f"      尺寸：{data.get('box_length')}")
                        print(f"      frame_id: {data.get('frame_id')}")
                    elif "summary" in data:
                        print(f"   进度：{data.get('summary')}")
                    else:
                        print(f"   数据：{json.dumps(data, ensure_ascii=False)[:200]}")
                
                # 检查是否完成
                if cmd == "finish":
                    error_code = body.get("data", {}).get("error_code", {})
                    code = error_code.get("code", 0)
                    msg_text = error_code.get("msg", "")
                    print(f"\n✅ 任务完成：0x{code:08X} - {msg_text}")
                    break
            
            except asyncio.TimeoutError:
                print("\n❌ 超时")
                break
        
        print("\n" + "=" * 70)
        if search_data:
            print("✅ 成功获取到物体数据！")
            print("\n完整数据:")
            print(json.dumps(search_data, indent=2, ensure_ascii=False))
        else:
            print("❌ 未获取到物体数据")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_search())
