#!/usr/bin/env python3
"""
Asus Router management via asusrouter library.
Works with any Asus router running AsusWRT or Merlin firmware.

Configuration: Copy config.example.yaml to config.yaml and fill in your details.
"""
import asyncio
import aiohttp
import json
import sys
import os
import argparse
from datetime import datetime, timezone
from asusrouter import AsusRouter, AsusData

# ── Config loading ────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yaml")

def load_config():
    """Load config from config.yaml. Falls back to env vars."""
    config = {
        "router": {
            "host": os.environ.get("ASUS_ROUTER_HOST", "192.168.1.1"),
            "username": os.environ.get("ASUS_ROUTER_USER", "admin"),
            "password": os.environ.get("ASUS_ROUTER_PASS", ""),
            "ssl": False,
        },
        "known_devices": {},
        "ping_targets": [],
    }

    try:
        import yaml
        with open(CONFIG_PATH, 'r') as f:
            file_config = yaml.safe_load(f) or {}
        if "router" in file_config:
            config["router"].update(file_config["router"])
        if "known_devices" in file_config:
            config["known_devices"] = file_config["known_devices"]
        if "ping_targets" in file_config:
            config["ping_targets"] = file_config["ping_targets"]
    except FileNotFoundError:
        pass
    except ImportError:
        # PyYAML not installed — try JSON fallback or env vars only
        json_path = os.path.join(SCRIPT_DIR, "config.json")
        try:
            with open(json_path, 'r') as f:
                file_config = json.load(f)
            if "router" in file_config:
                config["router"].update(file_config["router"])
            if "known_devices" in file_config:
                config["known_devices"] = file_config["known_devices"]
            if "ping_targets" in file_config:
                config["ping_targets"] = file_config["ping_targets"]
        except FileNotFoundError:
            pass

    if not config["router"]["password"]:
        print("ERROR: No router password configured.")
        print("Either:")
        print(f"  1. Copy config.example.yaml to {CONFIG_PATH} and fill in your details")
        print("  2. Set ASUS_ROUTER_PASS environment variable")
        sys.exit(1)

    return config


CONFIG = load_config()

# ── Router connection ─────────────────────────────────────────────────────────

async def get_router():
    session = aiohttp.ClientSession()
    router = AsusRouter(
        hostname=CONFIG["router"]["host"],
        username=CONFIG["router"]["username"],
        password=CONFIG["router"]["password"],
        use_ssl=CONFIG["router"].get("ssl", False),
        session=session,
    )
    await router.async_connect()
    return router, session


async def close(router, session):
    await router.async_disconnect()
    await session.close()


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_status(args):
    """Overall router health: WAN, CPU, RAM, mesh nodes, client count."""
    router, session = await get_router()
    try:
        wan = await router.async_get_data(AsusData.WAN)
        cpu = await router.async_get_data(AsusData.CPU)
        ram = await router.async_get_data(AsusData.RAM)
        clients = await router.async_get_data(AsusData.CLIENTS)

        online = sum(1 for c in clients.values() if c.state.value == 1)

        # WAN info
        wan_info = wan.get('internet', {})
        wan_ip = wan.get(0, {}).get('main', {}).get('ip_address', '?')
        wan_gw = wan.get(0, {}).get('main', {}).get('gateway', '?')
        wan_link = str(wan_info.get('link', '?'))

        # Mesh nodes
        try:
            aimesh = await router.async_get_data(AsusData.AIMESH)
            mesh_total = len(aimesh)
            mesh_online = sum(1 for node in aimesh.values() if hasattr(node, 'status') and node.status)
            mesh_details = []
            for mac, node in aimesh.items():
                mesh_details.append({
                    'mac': mac,
                    'alias': node.alias if hasattr(node, 'alias') else None,
                    'model': node.model if hasattr(node, 'model') else None,
                    'ip': node.ip if hasattr(node, 'ip') else None,
                    'online': node.status if hasattr(node, 'status') else None,
                })
        except Exception:
            node_macs = set()
            for c in clients.values():
                node = c.connection.node if hasattr(c.connection, 'node') else None
                if node:
                    node_macs.add(node)
            mesh_total = len(node_macs)
            mesh_online = mesh_total
            mesh_details = [{'mac': m} for m in node_macs]

        result = {
            'wan': {'status': wan_link, 'ip': wan_ip, 'gateway': wan_gw},
            'cpu': {'cores': 4, 'usage_pct': round(cpu['total']['used'] / max(cpu['total']['total'], 1) * 100, 1)},
            'ram': {'total_mb': round(ram['total'] / 1024), 'used_pct': round(ram['usage'], 1), 'free_mb': round(ram['free'] / 1024)},
            'clients': {'total': len(clients), 'online': online},
            'mesh_nodes': mesh_online,
            'mesh_total': mesh_total,
            'mesh_details': mesh_details,
        }

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"🌐 WAN: {wan_link} | IP: {wan_ip} | GW: {wan_gw}")
            print(f"🖥️  CPU: {result['cpu']['usage_pct']}% | RAM: {result['ram']['used_pct']}% ({result['ram']['free_mb']}MB free)")
            print(f"📡 Clients: {online} online / {len(clients)} total | Mesh nodes: {mesh_online}")
    finally:
        await close(router, session)


async def cmd_clients(args):
    """List connected devices with details."""
    router, session = await get_router()
    try:
        clients = await router.async_get_data(AsusData.CLIENTS)

        devices = []
        for mac, client in clients.items():
            conn = client.connection
            desc = client.description
            is_online = client.state.value == 1

            if args.online and not is_online:
                continue

            d = {
                'name': desc.name or 'Unknown',
                'mac': mac,
                'ip': conn.ip_address,
                'online': is_online,
                'type': str(conn.type.value) if hasattr(conn.type, 'value') else str(conn.type),
                'node': conn.node if hasattr(conn, 'node') else None,
            }

            if hasattr(conn, 'rssi'):
                d['rssi'] = conn.rssi
                d['rx_speed'] = conn.rx_speed
                d['tx_speed'] = conn.tx_speed
                d['guest'] = getattr(conn, 'guest', False)

            if args.filter and args.filter.lower() not in (d['name'] + d['ip'] + mac).lower():
                continue

            devices.append(d)

        devices.sort(key=lambda x: (not x['online'], x['name'].lower()))

        if args.json:
            print(json.dumps(devices, indent=2, default=str))
        else:
            print(f"{'Name':<30} {'IP':<17} {'Type':<10} {'Signal':<8} {'Online'}")
            print("-" * 80)
            for d in devices:
                sig = f"{d.get('rssi', '')}dBm" if d.get('rssi') else "-"
                status = "✅" if d['online'] else "❌"
                guest = " 👤G" if d.get('guest') else ""
                print(f"{d['name']:<30} {d['ip']:<17} {d['type']:<10} {sig:<8} {status}{guest}")
            print(f"\nTotal: {len(devices)} devices")
    finally:
        await close(router, session)


async def cmd_who_home(args):
    """Check which known people/devices are on the network (presence detection)."""
    router, session = await get_router()
    try:
        clients = await router.async_get_data(AsusData.CLIENTS)
        known = CONFIG.get("known_devices", {})

        if not known:
            print("⚠️  No known devices configured.")
            print(f"Add devices to known_devices in {CONFIG_PATH}")
            return

        print("🏠 Who's home?\n")
        for label, pattern_groups in known.items():
            found = False
            for mac, client in clients.items():
                name = (client.description.name or '').lower()
                if any(all(p in name for p in group) for group in pattern_groups) and client.state.value == 1:
                    conn = client.connection
                    sig = f" (signal: {conn.rssi}dBm)" if hasattr(conn, 'rssi') and conn.rssi else ""
                    node = f" via {conn.node}" if hasattr(conn, 'node') else ""
                    print(f"  ✅ {label}: {conn.ip_address}{sig}{node}")
                    found = True
            if not found:
                print(f"  ❌ {label}: not connected")
    finally:
        await close(router, session)


async def cmd_wan(args):
    """Detailed WAN status including dual-WAN and DNS."""
    router, session = await get_router()
    try:
        wan = await router.async_get_data(AsusData.WAN)

        if args.json:
            print(json.dumps(wan, indent=2, default=str))
        else:
            w0 = wan.get(0, {})
            main = w0.get('main', {})
            dualwan = wan.get('dualwan', {})

            print(f"🌐 WAN Status")
            print(f"  Link: {wan.get('internet', {}).get('link', '?')}")
            print(f"  IP: {main.get('ip_address', '?')}")
            print(f"  Gateway: {main.get('gateway', '?')}")
            print(f"  DNS: {', '.join(main.get('dns', []))}")
            print(f"  Lease: {main.get('lease', '?')}s (expires in {main.get('expires', '?')}s)")
            print(f"  Protocol: {w0.get('protocol', '?')}")
            print(f"  Dual-WAN: {dualwan.get('mode', '?')} (active: {dualwan.get('state', '?')})")
    finally:
        await close(router, session)


async def cmd_mesh(args):
    """Show AiMesh node info and which clients connect to each."""
    router, session = await get_router()
    try:
        clients = await router.async_get_data(AsusData.CLIENTS)

        try:
            aimesh = await router.async_get_data(AsusData.AIMESH)
        except Exception:
            aimesh = {}

        node_clients = {}
        for mac, client in clients.items():
            node = client.connection.node if hasattr(client.connection, 'node') else 'unknown'
            if node not in node_clients:
                node_clients[node] = {'clients': [], 'online': 0}
            if client.state.value == 1:
                node_clients[node]['online'] += 1
                node_clients[node]['clients'].append({
                    'name': client.description.name or mac,
                    'ip': client.connection.ip_address,
                    'type': str(client.connection.type.value) if hasattr(client.connection.type, 'value') else '?',
                })

        result = {}
        for node_mac, node_obj in aimesh.items():
            alias = node_obj.alias if hasattr(node_obj, 'alias') else None
            model = node_obj.model if hasattr(node_obj, 'model') else None
            ip = node_obj.ip if hasattr(node_obj, 'ip') else None
            status = node_obj.status if hasattr(node_obj, 'status') else None
            client_info = node_clients.get(node_mac, {'clients': [], 'online': 0})
            result[node_mac] = {
                'alias': alias, 'model': model, 'ip': ip, 'status': status,
                'clients': client_info['clients'], 'client_count': client_info['online'],
            }

        for node_mac, info in node_clients.items():
            if node_mac not in result and node_mac != 'unknown':
                result[node_mac] = {
                    'alias': None, 'model': None, 'ip': None, 'status': None,
                    'clients': info['clients'], 'client_count': info['online'],
                }

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            for node_mac, info in sorted(result.items(), key=lambda x: (x[1].get('alias') or x[0] or '').lower()):
                alias = info.get('alias') or '?'
                model = info.get('model') or '?'
                status = "✅" if info.get('status') else "❌"
                ip = info.get('ip') or '?'
                print(f"\n{status} {alias} ({model}) — {node_mac} [{ip}] — {info['client_count']} clients")
                for c in sorted(info['clients'], key=lambda x: x['name'].lower()):
                    print(f"    {c['name']:<30} {c['ip']:<17} {c['type']}")
    finally:
        await close(router, session)


async def cmd_find(args):
    """Find a device by name, IP, or MAC."""
    if not args.query:
        print("Usage: router.py find <name|ip|mac>")
        return

    router, session = await get_router()
    try:
        clients = await router.async_get_data(AsusData.CLIENTS)
        q = args.query.lower()

        found_any = False
        for mac, client in clients.items():
            name = client.description.name or ''
            ip = client.connection.ip_address or ''
            if q in name.lower() or q in ip.lower() or q in mac.lower():
                conn = client.connection
                online = "✅ Online" if client.state.value == 1 else "❌ Offline"
                print(f"{online}: {name}")
                print(f"  MAC: {mac}")
                print(f"  IP: {ip}")
                print(f"  Connection: {conn.type.value if hasattr(conn.type, 'value') else conn.type}")
                print(f"  Mesh node: {conn.node if hasattr(conn, 'node') else '?'}")
                if hasattr(conn, 'rssi') and conn.rssi:
                    print(f"  Signal: {conn.rssi}dBm | RX: {conn.rx_speed} | TX: {conn.tx_speed}")
                if hasattr(conn, 'guest'):
                    print(f"  Guest network: {conn.guest}")
                print()
                found_any = True

        if not found_any:
            print(f"No devices matching '{args.query}' found.")
    finally:
        await close(router, session)


async def cmd_ping(args):
    """Network latency check — ping gateway + custom targets."""
    import subprocess

    gateway = CONFIG["router"]["host"]
    targets = [
        ('Gateway', gateway),
        ('Cloudflare', '1.1.1.1'),
        ('Google', '8.8.8.8'),
    ]

    # Add custom targets from config
    for t in CONFIG.get("ping_targets", []):
        targets.append((t.get('name', t['ip']), t['ip']))

    print("🏓 Network latency check\n")
    for name, ip in targets:
        try:
            result = subprocess.run(
                ['ping', '-c', '3', '-W', '2', ip],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                if 'avg' in line:
                    avg = line.split('=')[1].split('/')[1]
                    loss_line = [l for l in result.stdout.splitlines() if 'packet loss' in l]
                    loss = loss_line[0].split(',')[2].strip() if loss_line else '?'
                    print(f"  {name:<15} {ip:<17} {avg}ms  ({loss})")
                    break
            else:
                print(f"  {name:<15} {ip:<17} ❌ no response")
        except Exception as e:
            print(f"  {name:<15} {ip:<17} ❌ {e}")


async def cmd_reboot(args):
    """Reboot the router (requires --confirm)."""
    if not args.confirm:
        print("⚠️  This will reboot the router and disconnect all devices!")
        print("Run with --confirm to proceed.")
        return

    router, session = await get_router()
    try:
        await router.async_apply_settings({"action_mode": "reboot"})
        print("🔄 Router rebooting... expect 2-3 minutes of downtime.")
    except Exception as e:
        print(f"Reboot failed: {e}")
    finally:
        await close(router, session)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Asus Router Management (AsusWRT)")
    parser.add_argument('--json', action='store_true', help='JSON output')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('status', help='Router health overview')

    p_clients = sub.add_parser('clients', help='List connected devices')
    p_clients.add_argument('--online', action='store_true', help='Only show online devices')
    p_clients.add_argument('--filter', type=str, help='Filter by name/IP/MAC')

    sub.add_parser('who', help='Who is home (presence detection)')
    sub.add_parser('wan', help='WAN connection details')
    sub.add_parser('mesh', help='AiMesh node breakdown')

    p_find = sub.add_parser('find', help='Find a specific device')
    p_find.add_argument('query', nargs='?', help='Name, IP, or MAC to search')

    sub.add_parser('ping', help='Network latency check')

    p_reboot = sub.add_parser('reboot', help='Reboot router')
    p_reboot.add_argument('--confirm', action='store_true')

    args = parser.parse_args()

    commands = {
        'status': cmd_status,
        'clients': cmd_clients,
        'who': cmd_who_home,
        'wan': cmd_wan,
        'mesh': cmd_mesh,
        'find': cmd_find,
        'ping': cmd_ping,
        'reboot': cmd_reboot,
    }

    if not args.command:
        parser.print_help()
        return

    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()
