#!/usr/bin/env python3
"""会话管理脚本。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py create
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py query
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py dump --session-file ./session.json
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py restore --session-file ./session.json
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py valid --session-file ./session.json
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_session.py delete
"""

import argparse
import json
import os
import sys

from _client import add_common_args, dump_json, get_client


def _load_session_file(path):
    if not os.path.isfile(path):
        print(f"错误: 会话文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_session_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _restore_if_needed(client, path):
    if not path:
        return False
    dumped = _load_session_file(path)
    restored = client.restore_session(dumped)
    return restored


def cmd_create(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    result = client.session.create_session()
    dump_json(result)
    if args.session_file:
        dumped = client.dump_session()
        _save_session_file(args.session_file, dumped)


def cmd_query(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    _restore_if_needed(client, args.session_file)
    dump_json(client.session.query_session())


def cmd_info(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    _restore_if_needed(client, args.session_file)
    info = client.session.get_session_info()
    dump_json(info or {"data": None, "message": "当前进程中没有有效会话"})


def cmd_valid(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    restored = _restore_if_needed(client, args.session_file)
    result = {
        "restored": restored,
        "isValid": client.session.is_session_valid(),
        "sessionInfo": client.session.get_session_info(),
    }
    dump_json(result)


def cmd_dump(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    if args.session_file and os.path.isfile(args.session_file):
        _restore_if_needed(client, args.session_file)
    if not client.session.is_session_valid():
        client.session.create_session()
    dumped = client.dump_session()
    if args.session_file:
        _save_session_file(args.session_file, dumped)
    dump_json(dumped)


def cmd_restore(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    restored = _restore_if_needed(client, args.session_file)
    result = {
        "restored": restored,
        "sessionInfo": client.session.get_session_info(),
    }
    if restored and args.query_after_restore:
        result["serverSession"] = client.session.query_session()
    dump_json(result)


def cmd_delete(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    _restore_if_needed(client, args.session_file)
    dump_json(client.session.delete_session())


def main():
    parser = argparse.ArgumentParser(description="会话管理（创建/查询/删除/持久化恢复）")
    add_common_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="创建会话")
    p_create.add_argument("--session-file", help="创建后顺带保存会话到 JSON 文件")
    p_create.set_defaults(func=cmd_create)

    p_query = sub.add_parser("query", help="查询服务端当前会话")
    p_query.add_argument("--session-file", help="先从文件恢复会话，再查询")
    p_query.set_defaults(func=cmd_query)

    p_info = sub.add_parser("info", help="查看本地缓存会话信息")
    p_info.add_argument("--session-file", help="先从文件恢复会话，再查看")
    p_info.set_defaults(func=cmd_info)

    p_valid = sub.add_parser("valid", help="检查会话是否有效")
    p_valid.add_argument("--session-file", help="先从文件恢复会话，再检查")
    p_valid.set_defaults(func=cmd_valid)

    p_dump = sub.add_parser("dump", help="导出当前会话到 JSON")
    p_dump.add_argument("--session-file", default="./session.json", help="输出文件，默认 ./session.json")
    p_dump.set_defaults(func=cmd_dump)

    p_restore = sub.add_parser("restore", help="从 JSON 文件恢复会话")
    p_restore.add_argument("--session-file", default="./session.json", help="输入文件，默认 ./session.json")
    p_restore.add_argument("--query-after-restore", action="store_true", help="恢复后顺带查询服务端会话")
    p_restore.set_defaults(func=cmd_restore)

    p_delete = sub.add_parser("delete", help="删除当前会话")
    p_delete.add_argument("--session-file", help="先从文件恢复会话，再删除")
    p_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
