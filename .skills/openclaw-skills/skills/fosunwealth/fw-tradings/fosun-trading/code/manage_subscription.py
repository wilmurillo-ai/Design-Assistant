#!/usr/bin/env python3
"""交易订阅管理脚本。

用法:
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_subscription.py create --endpoint https://host/webhook
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_subscription.py list
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_subscription.py update --subscription-id 123 --endpoint https://host/webhook/v2
  /Users/admin/.openclaw/workspace/.venv-fosun/bin/python manage_subscription.py delete --subscription-id 123
"""

import argparse

from _client import add_common_args, dump_json, get_client


def cmd_create(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    result = client.trade.create_subscription(
        event_type=args.event_type,
        endpoint=args.endpoint,
        channel_type=args.channel_type,
    )
    dump_json(result)


def cmd_list(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    result = client.trade.list_subscriptions(
        start=args.start,
        count=args.count,
        event_type=args.event_type,
    )
    dump_json(result)


def cmd_update(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    result = client.trade.update_subscription(
        subscription_id=args.subscription_id,
        endpoint=args.endpoint,
    )
    dump_json(result)


def cmd_delete(args):
    client = get_client(args.api_key, args.base_url, args.sdk_type)
    result = client.trade.delete_subscription(subscription_id=args.subscription_id)
    dump_json(result)


def main():
    parser = argparse.ArgumentParser(description="交易订阅管理（create/list/update/delete）")
    add_common_args(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="创建交易订阅")
    p_create.add_argument("--event-type", default="orderUpdate", help="当前仅支持 orderUpdate")
    p_create.add_argument("--channel-type", type=int, default=1, help="通道类型，默认 1=HTTP Webhook")
    p_create.add_argument("--endpoint", required=True, help="Webhook 回调地址")
    p_create.set_defaults(func=cmd_create)

    p_list = sub.add_parser("list", help="查询订阅列表")
    p_list.add_argument("--start", type=int, default=0, help="分页偏移")
    p_list.add_argument("--count", type=int, default=20, help="返回数量")
    p_list.add_argument("--event-type", help="按事件类型过滤，当前仅支持 orderUpdate")
    p_list.set_defaults(func=cmd_list)

    p_update = sub.add_parser("update", help="更新订阅回调地址")
    p_update.add_argument("--subscription-id", required=True, type=int, help="订阅 ID")
    p_update.add_argument("--endpoint", required=True, help="新的 Webhook 回调地址")
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="删除订阅")
    p_delete.add_argument("--subscription-id", required=True, type=int, help="订阅 ID")
    p_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
