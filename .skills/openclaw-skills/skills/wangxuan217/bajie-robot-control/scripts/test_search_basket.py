#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试搜索收纳筐
"""

import asyncio
import json
import time
import uuid
import websockets

async def test_search_basket():
    uri = "ws://10.10.10.12:9900"
    
    print("=" * 70)
    print("🤖 测试搜索收纳筐")
    print("=" * 70)
    
    async with websockets.connect(uri) as ws:
        print("✅ 已连接\n")
        
        # 搜索收纳筐
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
                        "item": "收纳筐",
                        "color": "",
                        "shape": "",
                        "person": "",
                        "type": [],
                        "subtype": []
                    },
                    "area": {
                        "area_name": "客厅",
                        "area_id": ""
                    }
                }
            }
        }
        
        print("发送搜索收纳筐请求...")
        await ws.send(json.dumps(search_request))
        
        search_data = None
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
                response = json.loads(msg)
                header = response["header"]
                body = response["body"]
                
                if header["type"] == "response":
                    code = body["data"]["error_code"]["code"]
                    print(f"启动：0x{code:08X}")
                
                elif header["type"] == "notify":
                    data = body["data"]
                    if "position" in data:
                        search_data = data
                        print(f"📍 找到收纳筐!")
                        print(f"   位置：{data['position']}")
                    elif header["cmd"] == "finish":
                        code = body["data"]["error_code"]["code"]
                        msg = body["data"]["error_code"].get("msg", "")
                        print(f"完成：0x{code:08X} - {msg}")
                        break
                
                if header["cmd"] == "finish":
                    break
            
            except asyncio.TimeoutError:
                print("超时")
                break
        
        print("\n" + "=" * 70)
        if search_data:
            print("✅ 成功找到收纳筐！")
            print(json.dumps(search_data, indent=2, ensure_ascii=False))
        else:
            print("❌ 未找到收纳筐")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_search_basket())
