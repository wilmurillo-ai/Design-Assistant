#!/usr/bin/env python3
"""
公众号爆款标题生成器数据查询脚本
"""

import sys
import argparse
import json
import requests


def fetch_api_data(base_url: str, params: dict, headers: dict, timeout: int = 60):
    """
    使用 requests 发起 HTTPS 请求（保持证书与主机名校验）
    """
    response = requests.get(
        base_url,
        params=params,
        headers=headers,
        timeout=timeout,
    )
    return response.status_code, response.text


def fetch_official_account_trends(keyword: str, debug: bool = False, max_retries: int = 3, days: int = 7):
    """
    调用新接口获取公众号爆款标题数据

    Args:
        keyword: 搜索关键词（多个关键词用逗号分隔，最多5个，总长度不超过200）
        debug: 是否打印调试信息
        max_retries: 最大重试次数
        days: 查询最近几天的数据，默认7天，最大30天

    Returns:
        dict: 包含3类爆款数据

    Raises:
        Exception: 当API调用失败时抛出异常
    """
    from datetime import datetime, timedelta

    # 确保天数不超过30天
    days = min(days, 30)

    # 计算开始日期（今天 - (days-1) 天）
    end_date = datetime.now()
    start_date_obj = end_date - timedelta(days=days-1)
    start_date_str = start_date_obj.strftime('%Y-%m-%d')

    if debug:
        print(f"DEBUG: 查询最近 {days} 天数据，开始日期: {start_date_str}", file=sys.stderr)

    base_url = "https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData"
    params = {
        "keyword": keyword,
        "source": "公众号爆款标题生成-ClawHub",
        "startDate": start_date_str,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)

            status_code, body = fetch_api_data(base_url, params, headers)

            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(body)} 字节", file=sys.stderr)

            if status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {status_code}")

            data = json.loads(body)

            if debug:
                print("=== DEBUG: 完整 API 响应 ===", file=sys.stderr)
                print(json.dumps(data, ensure_ascii=False, indent=2), file=sys.stderr)

            # 检查业务错误码
            code = data.get("code", 0)
            if code != 2000:  # 2000 表示成功
                error_msg = data.get("msg", "未知错误")
                raise Exception(f"API 错误: {error_msg}")

            if "data" not in data or data["data"] is None:
                raise Exception("API 返回数据为空")

            result_data = data.get("data", {})

            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)

            # 返回新的三个榜单数据（根据实际返回的字段名）
            return {
                "keyword": keyword,
                "low_fan_explosive": result_data.get("lowPowderExplosiveArticle", []),
                "100k_read": result_data.get("tenWReadingRank", []),
                "original": result_data.get("originalRank", [])
            }

        except Exception as e:
            last_error = str(e)
            if debug:
                import traceback
                print(f"  错误: {type(e).__name__}: {str(e)}", file=sys.stderr)
                print(f"  堆栈: {traceback.format_exc()}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def get_cover_urls(data, max_per_category=5):
    """提取所有标题链接"""
    urls = []
    categories = [
        ('low_fan_explosive', '低粉爆文榜'),
        ('100k_read', '10w+阅读榜'),
        ('original', '原创榜')
    ]
    for key, name in categories:
        items = data.get(key, [])[:max_per_category]
        for item in items:
            title = item.get('title', '')[:20]
            # 优先使用 oriUrl 字段
            article_url = item.get('oriUrl', '')
            if not article_url:
                # 如果没有 oriUrl，回退到使用 photoId
                photo_id = item.get('photoId', '')
                if photo_id:
                    article_url = f"https://mp.weixin.qq.com/s/{photo_id}"
            if article_url:
                urls.append({
                    'category': name,
                    'title': title,
                    'link': article_url
                })
    return urls


def format_output(data: dict, max_items: int = None, days: int = 7):
    """
    格式化输出热门数据（表格形式）

    Args:
        data: 原始数据
        max_items: 每类爆款数据最多展示数量，None 表示展示所有数据
        days: 查询的天数，用于显示统计时间范围
    """
    # 计算统计时间范围
    def get_time_range(days):
        if days <= 1:
            return "近1天"
        elif days <= 7:
            return f"近{days}天"
        else:
            return f"近{days}天"

    time_range = get_time_range(days)

    def process_title(item):
        """处理标题：转义特殊字符"""
        title = item.get('title', '')
        if not title or title.strip() == '':
            title = '无标题'

        # 转义 Markdown 表格特殊字符（|）
        title = title.replace('|', '\\|')
        # 移除换行符
        title = title.replace('\n', ' ').replace('\r', ' ')
        # 移除多余空格
        title = ' '.join(title.split())

        return title

    def format_time(item):
        """格式化发布时间为 X月X日"""
        pub_time = item.get('publicTime', '')
        if pub_time:
            # publicTime 格式: "2026-03-06 13:03:56"
            try:
                month = int(pub_time[5:7])
                day = int(pub_time[8:10])
                return f"{month}月{day}日"
            except:
                pass
        return '--'

    def format_article_link(item):
        """生成文章链接"""
        title = process_title(item)
        # 优先使用 oriUrl 字段
        ori_url = item.get('oriUrl', '')
        if ori_url:
            return f"[{title}]({ori_url})"
        # 如果没有 oriUrl，回退到使用 photoId
        photo_id = item.get('photoId', '')
        if photo_id:
            article_url = f"https://mp.weixin.qq.com/s/{photo_id}"
            return f"[{title}]({article_url})"
        return title

    def get_latest_date(data):
        """获取数据中最新的发布日期"""
        all_items = []
        for key in ['low_fan_explosive', '100k_read', 'original']:
            all_items.extend(data.get(key, []))

        latest_date = None
        for item in all_items:
            pub_time = item.get('publicTime', '')
            if pub_time:
                try:
                    date_str = pub_time[:10]  # 取 "YYYY-MM-DD" 部分
                    if latest_date is None or date_str > latest_date:
                        latest_date = date_str
                except:
                    pass
        return latest_date

    output = []

    # 检查数据日期
    latest_date = get_latest_date(data)

    # 去重（用photoId作为唯一标识）
    def dedup_items(items):
        seen = set()
        result = []
        for item in items:
            photo_id = item.get('photoId', '')
            if photo_id and photo_id not in seen:
                seen.add(photo_id)
                result.append(item)
        return result

    # 按时间倒序排序
    def sort_by_time_desc(items):
        """按发布时间倒序排列"""
        def get_time_key(item):
            pub_time = item.get('publicTime', '')
            if pub_time:
                return pub_time
            return '0'
        return sorted(items, key=get_time_key, reverse=True)

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    read100k_items = dedup_items(data.get("100k_read", []))
    original_items = dedup_items(data.get("original", []))

    total_count = len(low_fan_items) + len(read100k_items) + len(original_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"**关键词**：{keyword}\n\n")
        output.append("---\n\n")
        output.append("## 暂无相关爆款数据\n\n")
        output.append(f"很抱歉，当前关键词 **「{keyword}」** 尚未有足够的爆款文章数据。\n\n")
        output.append("### 可能原因\n\n")
        output.append("- 该关键词相对小众或新兴，爆款内容积累较少\n")
        output.append("- 近期该赛道热度较低，暂无突出爆款文章\n")
        output.append("- 关键词表述方式可以更加具体或热门\n\n")
        output.append("### 建议操作\n\n")
        output.append("- 更换为更热门的关键词，如：**\"职场干货\"**、**\"情感故事\"**、**\"生活小技巧\"** 等\n")
        output.append("- 尝试更细分的长尾关键词\n")
        output.append("- 输入其他感兴趣的领域或赛道进行追踪\n\n")
        output.append("---\n\n")
        output.append("*数据来源：公众号爆款雷达，每日更新最新热门内容*\n")
        return "\n".join(output)

    # 1. 低粉爆文榜
    items = sort_by_time_desc(low_fan_items)
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **低粉爆文榜**")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | 阅读 | 在看 | 点赞 | **阅读总数** |")
        output.append("|------|----------|------|------|------|------|------|-------------|")

        for idx, item in enumerate(items, 1):
            author_name = item.get('userName', '未知')
            title_with_link = format_article_link(item)
            pub_time = format_time(item)

            # 公众号数据字段
            clicks_count = item.get('clicksCount', 0)
            watch_count = item.get('watchCount', 0)
            like_count = item.get('likeCount', 0)
            comment_count = item.get('commentCount', 0)
            share_count = item.get('shareCount', 0)
            interactive_count = item.get('interactiveCount', 0)

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_name} | {clicks_count} | {watch_count} | {like_count} | **{interactive_count}** |")

    # 2. 10w+阅读榜
    items = sort_by_time_desc(read100k_items)
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **10w+阅读榜**")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | **阅读** | 在看 | 点赞 | 评论 | 阅读总数 |")
        output.append("|------|----------|------|------|--------|------|------|------|------------|")

        for idx, item in enumerate(items, 1):
            author_name = item.get('userName', '未知')
            title_with_link = format_article_link(item)
            pub_time = format_time(item)

            clicks_count = item.get('clicksCount', 0)
            watch_count = item.get('watchCount', 0)
            like_count = item.get('likeCount', 0)
            comment_count = item.get('commentCount', 0)
            share_count = item.get('shareCount', 0)
            interactive_count = item.get('interactiveCount', 0)

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_name} | **{clicks_count}** | {watch_count} | {like_count} | {comment_count} | {interactive_count} |")

    # 3. 原创榜
    items = sort_by_time_desc(original_items)
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **原创榜**")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | 阅读 | 在看 | 点赞 | 评论 | 阅读总数 |")
        output.append("|------|----------|------|------|------|------|------|------|------------|")

        for idx, item in enumerate(items, 1):
            author_name = item.get('userName', '未知')
            title_with_link = format_article_link(item)
            pub_time = format_time(item)

            clicks_count = item.get('clicksCount', 0)
            watch_count = item.get('watchCount', 0)
            like_count = item.get('likeCount', 0)
            comment_count = item.get('commentCount', 0)
            share_count = item.get('shareCount', 0)
            interactive_count = item.get('interactiveCount', 0)

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_name} | {clicks_count} | {watch_count} | {like_count} | {comment_count} | {interactive_count} |")

    return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='公众号爆款标题数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10,
                       help='每类爆款内容最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'markdown'],
                       default='markdown', help='输出格式：text（文本表格）、json（JSON格式）或 markdown（Markdown格式，默认）')
    parser.add_argument('--output-file', type=str, default=None,
                       help='输出文件路径（默认：关键词_爆款数据.md）')
    parser.add_argument('--days', type=int, default=7,
                       help='查询最近几天的数据（默认7天，最大30天）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数（默认3次）')

    args = parser.parse_args()

    try:
        data = fetch_official_account_trends(args.keyword, debug=args.debug, max_retries=args.max_retries, days=args.days)

        # 生成输出内容
        if args.output_format == 'json':
            output_content = json.dumps(data, ensure_ascii=False, indent=2)
        elif args.output_format == 'markdown':
            # Markdown 格式添加关键词信息
            markdown_header = f"**关键词**：{args.keyword}\n\n"
            output_content = markdown_header + format_output(data, max_items=args.max_items, days=args.days)
        else:
            output_content = format_output(data, max_items=args.max_items, days=args.days)

        # 确定输出文件路径（markdown 格式默认输出到文件）
        output_file = args.output_file
        if output_file is None and args.output_format == 'markdown':
            # 默认文件名：关键词_爆款数据.md
            output_file = f"{args.keyword}_爆款数据.md"

        # 输出到文件或控制台
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✓ 结果已保存到: {output_file}", file=sys.stderr)
            print(f"✓ 关键词: {args.keyword}", file=sys.stderr)
            # 统计数据
            total_items = (
                len(data.get('low_fan_explosive', [])) +
                len(data.get('100k_read', [])) +
                len(data.get('original', []))
            )
            print(f"✓ 总计: {total_items} 条数据", file=sys.stderr)
            # 显示每类数据量
            print(f"  - 低粉爆文榜: {len(data.get('low_fan_explosive', []))} 条", file=sys.stderr)
            print(f"  - 10w+阅读榜: {len(data.get('100k_read', []))} 条", file=sys.stderr)
            print(f"  - 原创榜: {len(data.get('original', []))} 条", file=sys.stderr)
        else:
            print(output_content)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
