#!/usr/bin/env python3
"""
Session Context Monitor - Gateway Proxy Server
Proxies /sessions RPC via openclaw CLI, serves static HTML.
Supports triggering compaction on sessions and saving transcripts.
"""
import json
import subprocess
import threading
import time
import os
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
from datetime import datetime

PORT = 18790
GATEWAY_TOKEN = "68336d55b874dec0dcbb7f949f60ab2af24160b92d1cd63b"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTS_DIR = os.path.join(SCRIPT_DIR, "transcripts")
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# Cached session data
sessions_cache = []
sessions_lock = threading.Lock()

def strip_ansi(text):
    """Remove ANSI color codes from text."""
    ansi = re.compile(r'\x1b\[[0-9;]*m')
    return ansi.sub('', text)

def gateway_rpc_json(method, params=None):
    """Make a gateway RPC call via openclaw CLI returning JSON."""
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": method,
        "params": params or {}
    }
    
    req = urllib.request.Request(
        f"http://127.0.0.1:18789/rpc",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_TOKEN}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def fetch_sessions():
    """Fetch all sessions from gateway via openclaw CLI."""
    try:
        proc = subprocess.run(
            ["openclaw", "sessions", "--json"],
            capture_output=True, text=True, timeout=15,
            env={**os.environ, "NO_COLOR": "1"}
        )
        if proc.returncode == 0 and proc.stdout.strip():
            clean = strip_ansi(proc.stdout)
            start = clean.find('{')
            end = clean.rfind('}') + 1
            if start >= 0 and end > start:
                data = json.loads(clean[start:end])
                if isinstance(data, dict) and "sessions" in data:
                    return data["sessions"]
                return data
    except Exception as e:
        print(f"CLI error: {e}")
    return []

def get_transcript_path(session_key, sessionId):
    """Get the transcript file path for a session."""
    # From sessions.json, transcriptPath is available
    return f"/Users/godspeed/.openclaw/agents/dawang/sessions/{sessionId}.jsonl"

def read_transcript(session_key, sessionId):
    """Read the transcript JSONL file for a session."""
    path = get_transcript_path(session_key, sessionId)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading transcript: {e}"

def save_transcript(session_key, sessionId, content, label):
    """Save transcript content to a file."""
    safe_key = session_key.replace('/', '_').replace(':', '_')
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_key}_{label}_{ts}.jsonl"
    path = os.path.join(TRANSCRIPTS_DIR, filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return filename
    except Exception as e:
        return None

def compact_session(session_key, sessionId, instructions):
    """Trigger compaction on a session via Gateway WebSocket."""
    import websocket
    
    # Read pre-compaction transcript
    pre_content = read_transcript(session_key, sessionId)
    pre_file = save_transcript(session_key, sessionId, pre_content, "pre")
    
    ws = None
    try:
        ws = websocket.create_connection(
            "ws://127.0.0.1:18789",
            timeout=30
        )
        
        # Receive challenge
        challenge = ws.recv()
        challenge_data = json.loads(challenge)
        nonce = challenge_data.get('payload', {}).get('nonce', '')
        
        # Send connect
        connect_req = {
            "type": "req",
            "id": "1",
            "method": "connect",
            "params": {
                "minProtocol": 3,
                "maxProtocol": 3,
                "client": {"id": "compact-proxy", "version": "1.0", "platform": "python", "mode": "operator"},
                "role": "operator",
                "scopes": ["operator.read", "operator.write"],
                "auth": {"token": GATEWAY_TOKEN},
                "locale": "zh-CN",
                "userAgent": "compact-proxy/1.0"
            }
        }
        ws.send(json.dumps(connect_req))
        
        # Receive connect response
        connect_resp = ws.recv()
        
        # Send chat.send with /compact
        msg_id = str(int(time.time()))
        chat_req = {
            "type": "req",
            "id": msg_id,
            "method": "chat.send",
            "params": {
                "sessionKey": session_key,
                "message": f"/compact {instructions}" if instructions else "/compact",
                "streaming": False
            }
        }
        ws.send(json.dumps(chat_req))
        
        # Wait for response (non-blocking read with timeout)
        ws.settimeout(15)
        try:
            resp = ws.recv()
            resp_data = json.loads(resp)
        except:
            resp_data = {"status": "sent"}
        
        ws.close()
        ws = None
        
        # Give it a moment to complete compaction
        time.sleep(5)
        
        # Read post-compaction transcript
        post_content = read_transcript(session_key, sessionId)
        post_file = save_transcript(session_key, sessionId, post_content, "post")
        
        return {
            "success": True,
            "pre_file": pre_file,
            "post_file": post_file,
            "result": resp_data
        }
        
    except Exception as e:
        if ws:
            try: ws.close()
            except: pass
        return {"success": False, "error": str(e)}

def poll_sessions():
    """Background thread to poll sessions every 5s."""
    global sessions_cache
    while True:
        try:
            sessions = fetch_sessions()
            with sessions_lock:
                sessions_cache = sessions
        except Exception as e:
            print(f"Poll error: {e}")
        time.sleep(5)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        
        if path == "/sessions.json":
            with sessions_lock:
                data = sessions_cache
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
            return
        
        elif path == "/transcripts/" or path == "/transcripts":
            # List available transcript files
            files = []
            try:
                for f in os.listdir(TRANSCRIPTS_DIR):
                    fp = os.path.join(TRANSCRIPTS_DIR, f)
                    if os.path.isfile(fp):
                        files.append({
                            "name": f,
                            "size": os.path.getsize(fp),
                            "modified": int(os.path.getmtime(fp))
                        })
            except:
                pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(sorted(files, key=lambda x: -x['modified']), default=str).encode())
            return
        
        elif path.startswith("/transcript/"):
            # Serve a specific transcript file
            filename = path[len("/transcript/"):]
            safe_filename = os.path.basename(filename)  # prevent path traversal
            filepath = os.path.join(TRANSCRIPTS_DIR, safe_filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"File not found")
            return
        
        elif path == "/" or path == "/session-monitor.html":
            return super().do_GET()
        
        else:
            return super().do_GET()
    
    def do_POST(self):
        path = self.path.split('?')[0]
        
        if path == "/compact":
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                session_key = data.get('sessionKey', '')
                sessionId = data.get('sessionId', '')
                instructions = data.get('instructions', '')
                
                result = compact_session(session_key, sessionId, instructions)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result, default=str).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            return
        
        else:
            self.send_response(404)
            self.end_headers()
            return
    
    def log_message(self, format, *args):
        pass

def run_server():
    # Start polling thread
    t = threading.Thread(target=poll_sessions, daemon=True)
    t.start()

    os.chdir(SCRIPT_DIR)
    httpd = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
