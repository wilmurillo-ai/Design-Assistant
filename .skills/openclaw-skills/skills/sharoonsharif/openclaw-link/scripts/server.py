#!/usr/bin/env python3
"""
ClawLink Relay Server — The switchboard for cross-instance OpenClaw communication.

Supports:
  - HTTP REST API (universal, works through firewalls)
  - WebSocket real-time messaging (upgrade when available)
  - mDNS/Zeroconf broadcast for zero-config LAN discovery

Usage:
  python server.py                    # Start on default port 9077
  python server.py --port 8080        # Custom port
  python server.py --host 0.0.0.0     # Bind to all interfaces (LAN access)
  python server.py --no-mdns          # Disable mDNS broadcast
"""

import argparse
import asyncio
import json
import time
import uuid
import socket
import threading
from datetime import datetime, timezone
from typing import Dict, Optional

try:
    from aiohttp import web
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    from zeroconf import ServiceInfo, Zeroconf
    HAS_ZEROCONF = True
except ImportError:
    HAS_ZEROCONF = False


# ── Agent Registry ──────────────────────────────────────────────────────────

class AgentRegistry:
    """Tracks connected agents, their capabilities, and online status."""

    def __init__(self):
        self.agents: Dict[str, dict] = {}
        self.message_queues: Dict[str, list] = {}
        self.broadcast_log: list = []
        self.ws_connections: Dict[str, web.WebSocketResponse] = {}
        self.file_store: Dict[str, dict] = {}  # shared file content

    def register(self, agent_id: str, name: str, capabilities: list,
                 machine: str = "", description: str = "") -> dict:
        """Register or re-register an agent on the network."""
        agent = {
            "agent_id": agent_id,
            "name": name,
            "capabilities": capabilities,
            "machine": machine,
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "last_heartbeat": time.time(),
            "status": "online"
        }
        self.agents[agent_id] = agent
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = []
        return agent

    def heartbeat(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            self.agents[agent_id]["last_heartbeat"] = time.time()
            self.agents[agent_id]["status"] = "online"
            return True
        return False

    def deregister(self, agent_id: str):
        self.agents.pop(agent_id, None)
        self.message_queues.pop(agent_id, None)
        self.ws_connections.pop(agent_id, None)

    def get_online_agents(self, stale_seconds: float = 120.0) -> list:
        """Return agents that have heartbeated within stale_seconds."""
        now = time.time()
        online = []
        for aid, agent in self.agents.items():
            if now - agent["last_heartbeat"] < stale_seconds:
                agent["status"] = "online"
                online.append(agent)
            else:
                agent["status"] = "stale"
        return online

    def enqueue_message(self, to_agent: str, message: dict):
        """Queue a message for an agent (HTTP polling fallback)."""
        if to_agent not in self.message_queues:
            self.message_queues[to_agent] = []
        message["queued_at"] = datetime.now(timezone.utc).isoformat()
        self.message_queues[to_agent].append(message)

    def poll_messages(self, agent_id: str) -> list:
        """Retrieve and clear queued messages for an agent."""
        msgs = self.message_queues.get(agent_id, [])
        self.message_queues[agent_id] = []
        return msgs


registry = AgentRegistry()


# ── HTTP REST API ───────────────────────────────────────────────────────────

async def handle_register(request):
    """POST /register — Join the ClawLink network."""
    data = await request.json()
    agent_id = data.get("agent_id", str(uuid.uuid4())[:8])
    name = data.get("name", f"agent-{agent_id[:4]}")
    capabilities = data.get("capabilities", [])
    machine = data.get("machine", request.remote or "unknown")
    description = data.get("description", "")

    agent = registry.register(agent_id, name, capabilities, machine, description)

    # Broadcast join event
    join_msg = {
        "type": "agent_joined",
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await broadcast_to_websockets(join_msg, exclude=agent_id)

    return web.json_response({
        "status": "registered",
        "agent": agent,
        "server_time": datetime.now(timezone.utc).isoformat()
    })


async def handle_discover(request):
    """GET /discover — List all online agents."""
    agents = registry.get_online_agents()
    return web.json_response({
        "agents": agents,
        "count": len(agents),
        "server_time": datetime.now(timezone.utc).isoformat()
    })


async def handle_heartbeat(request):
    """POST /heartbeat — Keep agent alive."""
    data = await request.json()
    agent_id = data.get("agent_id")
    if not agent_id:
        return web.json_response({"error": "agent_id required"}, status=400)
    ok = registry.heartbeat(agent_id)
    return web.json_response({"status": "ok" if ok else "unknown_agent"})


async def handle_delegate(request):
    """POST /delegate — Send a task to a specific agent."""
    data = await request.json()
    from_agent = data.get("from_agent")
    to_agent = data.get("to_agent")
    task = data.get("task")
    context = data.get("context", {})
    priority = data.get("priority", "normal")

    if not all([from_agent, to_agent, task]):
        return web.json_response(
            {"error": "from_agent, to_agent, and task are required"}, status=400
        )

    message = {
        "type": "task_delegation",
        "message_id": str(uuid.uuid4())[:12],
        "from_agent": from_agent,
        "to_agent": to_agent,
        "task": task,
        "context": context,
        "priority": priority,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # Try WebSocket first for real-time delivery
    ws = registry.ws_connections.get(to_agent)
    if ws and not ws.closed:
        await ws.send_json(message)
        delivery = "websocket"
    else:
        registry.enqueue_message(to_agent, message)
        delivery = "queued"

    return web.json_response({
        "status": "delegated",
        "delivery": delivery,
        "message_id": message["message_id"]
    })


async def handle_broadcast(request):
    """POST /broadcast — Share knowledge with all connected agents."""
    data = await request.json()
    from_agent = data.get("from_agent")
    content = data.get("content")
    topic = data.get("topic", "general")
    tags = data.get("tags", [])

    if not all([from_agent, content]):
        return web.json_response(
            {"error": "from_agent and content required"}, status=400
        )

    message = {
        "type": "knowledge_broadcast",
        "message_id": str(uuid.uuid4())[:12],
        "from_agent": from_agent,
        "content": content,
        "topic": topic,
        "tags": tags,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    registry.broadcast_log.append(message)
    # Keep last 200 broadcasts
    if len(registry.broadcast_log) > 200:
        registry.broadcast_log = registry.broadcast_log[-200:]

    # Push to all websocket clients
    await broadcast_to_websockets(message, exclude=from_agent)

    # Also queue for HTTP pollers
    for aid in registry.agents:
        if aid != from_agent:
            registry.enqueue_message(aid, message)

    return web.json_response({
        "status": "broadcast_sent",
        "message_id": message["message_id"],
        "recipients": len(registry.agents) - 1
    })


async def handle_poll(request):
    """GET /poll/<agent_id> — Retrieve queued messages (HTTP fallback)."""
    agent_id = request.match_info["agent_id"]
    registry.heartbeat(agent_id)
    messages = registry.poll_messages(agent_id)
    return web.json_response({
        "messages": messages,
        "count": len(messages)
    })


async def handle_respond(request):
    """POST /respond — Send a task response back to the requester."""
    data = await request.json()
    from_agent = data.get("from_agent")
    to_agent = data.get("to_agent")
    message_id = data.get("message_id")
    result = data.get("result")
    status = data.get("status", "completed")

    message = {
        "type": "task_response",
        "message_id": message_id,
        "response_id": str(uuid.uuid4())[:12],
        "from_agent": from_agent,
        "to_agent": to_agent,
        "result": result,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    ws = registry.ws_connections.get(to_agent)
    if ws and not ws.closed:
        await ws.send_json(message)
        delivery = "websocket"
    else:
        registry.enqueue_message(to_agent, message)
        delivery = "queued"

    return web.json_response({"status": "response_sent", "delivery": delivery})


# ── Collaborative File Sync ─────────────────────────────────────────────────

async def handle_file_put(request):
    """POST /files — Create or update a shared file."""
    data = await request.json()
    file_key = data.get("file_key")
    content = data.get("content")
    agent_id = data.get("agent_id")
    file_type = data.get("file_type", "text")

    if not all([file_key, content, agent_id]):
        return web.json_response(
            {"error": "file_key, content, and agent_id required"}, status=400
        )

    version = registry.file_store.get(file_key, {}).get("version", 0) + 1

    registry.file_store[file_key] = {
        "file_key": file_key,
        "content": content,
        "file_type": file_type,
        "last_editor": agent_id,
        "version": version,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    # Notify others
    notify = {
        "type": "file_updated",
        "file_key": file_key,
        "version": version,
        "last_editor": agent_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await broadcast_to_websockets(notify, exclude=agent_id)
    for aid in registry.agents:
        if aid != agent_id:
            registry.enqueue_message(aid, notify)

    return web.json_response({"status": "saved", "version": version})


async def handle_file_get(request):
    """GET /files/<file_key> — Retrieve a shared file."""
    file_key = request.match_info["file_key"]
    file_data = registry.file_store.get(file_key)
    if not file_data:
        return web.json_response({"error": "file not found"}, status=404)
    return web.json_response(file_data)


async def handle_file_list(request):
    """GET /files — List all shared files."""
    files = [
        {k: v for k, v in f.items() if k != "content"}
        for f in registry.file_store.values()
    ]
    return web.json_response({"files": files, "count": len(files)})


# ── WebSocket Real-time Channel ─────────────────────────────────────────────

async def handle_websocket(request):
    """GET /ws/<agent_id> — Upgrade to WebSocket for real-time messaging."""
    agent_id = request.match_info["agent_id"]
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    registry.ws_connections[agent_id] = ws
    registry.heartbeat(agent_id)

    print(f"[ClawLink] WebSocket connected: {agent_id}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get("type")

                if msg_type == "heartbeat":
                    registry.heartbeat(agent_id)
                elif msg_type == "delegate":
                    data["from_agent"] = agent_id
                    to_agent = data.get("to_agent")
                    target_ws = registry.ws_connections.get(to_agent)
                    if target_ws and not target_ws.closed:
                        await target_ws.send_json(data)
                    else:
                        registry.enqueue_message(to_agent, data)
                elif msg_type == "broadcast":
                    data["from_agent"] = agent_id
                    data["timestamp"] = datetime.now(timezone.utc).isoformat()
                    await broadcast_to_websockets(data, exclude=agent_id)
                    for aid in registry.agents:
                        if aid != agent_id:
                            registry.enqueue_message(aid, data)

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[ClawLink] WS error for {agent_id}: {ws.exception()}")
    finally:
        registry.ws_connections.pop(agent_id, None)
        print(f"[ClawLink] WebSocket disconnected: {agent_id}")

    return ws


async def broadcast_to_websockets(message: dict, exclude: str = ""):
    """Push a message to all connected WebSocket clients."""
    for aid, ws in list(registry.ws_connections.items()):
        if aid != exclude and not ws.closed:
            try:
                await ws.send_json(message)
            except Exception:
                registry.ws_connections.pop(aid, None)


# ── Server Info ─────────────────────────────────────────────────────────────

async def handle_info(request):
    """GET / — Server info and status."""
    return web.json_response({
        "service": "ClawLink Relay",
        "version": "1.0.0",
        "agents_online": len(registry.get_online_agents()),
        "total_broadcasts": len(registry.broadcast_log),
        "shared_files": len(registry.file_store),
        "endpoints": {
            "register": "POST /register",
            "discover": "GET /discover",
            "heartbeat": "POST /heartbeat",
            "delegate": "POST /delegate",
            "broadcast": "POST /broadcast",
            "respond": "POST /respond",
            "poll": "GET /poll/<agent_id>",
            "files_put": "POST /files",
            "files_get": "GET /files/<file_key>",
            "files_list": "GET /files",
            "websocket": "GET /ws/<agent_id>"
        },
        "server_time": datetime.now(timezone.utc).isoformat()
    })


# ── mDNS/Zeroconf Broadcast ────────────────────────────────────────────────

def get_local_ip():
    """Get the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_mdns(port: int) -> Optional['Zeroconf']:
    """Advertise ClawLink relay via mDNS so LAN agents find it automatically."""
    if not HAS_ZEROCONF:
        print("[ClawLink] zeroconf not installed — skipping mDNS broadcast")
        print("           Install with: pip install zeroconf")
        return None

    local_ip = get_local_ip()
    hostname = socket.gethostname()

    info = ServiceInfo(
        "_clawlink._tcp.local.",
        f"ClawLink Relay ({hostname})._clawlink._tcp.local.",
        addresses=[socket.inet_aton(local_ip)],
        port=port,
        properties={
            "version": "1.0.0",
            "hostname": hostname,
        },
        server=f"{hostname}.local.",
    )

    zc = Zeroconf()
    zc.register_service(info)
    print(f"[ClawLink] mDNS broadcasting on {local_ip}:{port}")
    return zc


# ── Main ────────────────────────────────────────────────────────────────────

def create_app():
    app = web.Application()

    # Info
    app.router.add_get("/", handle_info)

    # Agent lifecycle
    app.router.add_post("/register", handle_register)
    app.router.add_get("/discover", handle_discover)
    app.router.add_post("/heartbeat", handle_heartbeat)

    # Messaging
    app.router.add_post("/delegate", handle_delegate)
    app.router.add_post("/broadcast", handle_broadcast)
    app.router.add_post("/respond", handle_respond)
    app.router.add_get("/poll/{agent_id}", handle_poll)

    # Collaborative files
    app.router.add_post("/files", handle_file_put)
    app.router.add_get("/files", handle_file_list)
    app.router.add_get("/files/{file_key}", handle_file_get)

    # WebSocket
    app.router.add_get("/ws/{agent_id}", handle_websocket)

    return app


def main():
    if not HAS_AIOHTTP:
        print("ERROR: aiohttp is required. Install with:")
        print("  pip install aiohttp")
        return

    parser = argparse.ArgumentParser(description="ClawLink Relay Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9077, help="Port (default: 9077)")
    parser.add_argument("--no-mdns", action="store_true", help="Disable mDNS broadcast")
    args = parser.parse_args()

    zc = None
    if not args.no_mdns:
        zc = start_mdns(args.port)

    local_ip = get_local_ip()
    print(f"""
╔══════════════════════════════════════════════════════╗
║              🔗 ClawLink Relay Server                ║
╠══════════════════════════════════════════════════════╣
║  HTTP API:    http://{local_ip}:{args.port:<5}                  ║
║  WebSocket:   ws://{local_ip}:{args.port:<5}/ws/<agent_id>     ║
║  mDNS:        {"ACTIVE" if zc else "DISABLED":<10}                           ║
╠══════════════════════════════════════════════════════╣
║  Connect your OpenClaw agents to this relay!         ║
║  Any machine on the network can join.                ║
╚══════════════════════════════════════════════════════╝
""")

    app = create_app()

    try:
        web.run_app(app, host=args.host, port=args.port, print=lambda _: None)
    except KeyboardInterrupt:
        pass
    finally:
        if zc:
            zc.unregister_all_services()
            zc.close()


if __name__ == "__main__":
    main()
