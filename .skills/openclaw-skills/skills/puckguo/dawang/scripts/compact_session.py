#!/usr/bin/env python3
"""Directly trigger compaction on a session via Gateway WebSocket."""
import json, websocket, time

WS_URL = "ws://127.0.0.1:18789"
TOKEN = "68336d55b874dec0dcbb7f949f60ab2af24160b92d1cd63b"
SESSION_KEY = "agent:dawang:feishu:direct:ou_c21e29357d595092f4fa51addc3a22c5"
INSTRUCTIONS = "保留代码决策、技术方案、工具调用记录。丢弃闲聊和调试输出。"

def main():
    ws = websocket.create_connection(WS_URL, timeout=30)
    
    # Receive challenge
    challenge = ws.recv()
    print(f"Challenge received")
    
    # Connect with valid client.id
    connect_req = {
        "type": "req", "id": "1", "method": "connect",
        "params": {
            "minProtocol": 3, "maxProtocol": 3,
            "client": {"id": "cli", "version": "1.0", "platform": "python"},
            "role": "operator",
            "scopes": ["operator.read", "operator.write"],
            "auth": {"token": TOKEN},
            "locale": "zh-CN",
            "userAgent": "compact-cli/1.0"
        }
    }
    ws.send(json.dumps(connect_req))
    resp = ws.recv()
    resp_data = json.loads(resp)
    if not resp_data.get("ok"):
        print(f"Connect failed: {resp_data}")
        ws.close()
        return
    print(f"Connected successfully")
    
    # Send compact via chat.send
    msg_id = str(int(time.time()))
    chat_req = {
        "type": "req", "id": msg_id, "method": "chat.send",
        "params": {
            "sessionKey": SESSION_KEY,
            "message": f"/compact {INSTRUCTIONS}",
            "streaming": False
        }
    }
    ws.send(json.dumps(chat_req))
    print(f"Sent compact request (id={msg_id}), waiting for response...")
    
    # Wait for response
    ws.settimeout(30)
    try:
        resp = ws.recv()
        resp_data = json.loads(resp)
        print(f"Response: id={resp_data.get('id')} ok={resp_data.get('ok')} result={str(resp_data.get('result',''))[:200]}")
    except Exception as e:
        print(f"Recv exc: {e}")
    
    ws.close()
    print("Done")

if __name__ == "__main__":
    main()
