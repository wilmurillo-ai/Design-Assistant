#!/usr/bin/env python3
"""Market Sentiment Analyzer - 市场情绪分析

分析加密货币新闻和社交媒体情绪
"""

import sys
import json
import re
import requests
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False

# RSS新闻源
RSS_FEEDS = {
    'cointelegraph': 'https://cointelegraph.com/rss',
    'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
}

# 关键词权重
BULLISH_KEYWORDS = [
    'bull', 'bullish', 'buy', 'rising', 'gain', 'surge', 'rally', 'high',
    '上涨', '牛市', '买入', '突破', '新高', '利好'
]
BEARISH_KEYWORDS = [
    'bear', 'bearish', 'sell', 'fall', 'drop', 'crash', 'plunge', 'low',
    '下跌', '熊市', '卖出', '跌破', '新低', '利空'
]


def fetch_rss_feed(url, max_entries=10):
    """获取RSS源"""
    if not HAS_FEEDPARSER:
        # 备用方案：使用requests获取
        try:
            resp = requests.get(url, timeout=10)
            # 简单提取标题
            titles = re.findall(r'<title>([^<]+)</title>', resp.text)[:max_entries]
            return [{'title': t, 'summary': '', 'published': '', 'link': ''} for t in titles]
        except Exception as e:
            print(f"[WARN] Failed to fetch {url}: {e}")
            return []
    
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:max_entries]:
            entries.append({
                'title': entry.get('title', ''),
                'summary': entry.get('summary', '')[:200],
                'published': entry.get('published', ''),
                'link': entry.get('link', '')
            })
        return entries
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return []


def analyze_text_sentiment(text):
    """分析文本情绪"""
    text_lower = text.lower()
    
    bullish_count = 0
    bearish_count = 0
    
    for keyword in BULLISH_KEYWORDS:
        if keyword.lower() in text_lower:
            bullish_count += 1
    
    for keyword in BEARISH_KEYWORDS:
        if keyword.lower() in text_lower:
            bearish_count += 1
    
    total = bullish_count + bearish_count
    if total == 0:
        return 0.0
    
    # 返回 -1 到 1 之间的分数
    score = (bullish_count - bearish_count) / total
    return max(-1.0, min(1.0, score))


def analyze_sentiment(symbol='BTC'):
    """分析指定币种的情绪"""
    all_entries = []
    
    # 获取新闻
    for name, url in RSS_FEEDS.items():
        entries = fetch_rss_feed(url, max_entries=5)
        all_entries.extend(entries)
    
    # 简单过滤相关币种
    symbol_upper = symbol.upper()
    relevant_entries = []
    for entry in all_entries:
        text = f"{entry['title']} {entry['summary']}".upper()
        if symbol_upper in text or 'CRYPTO' in text or 'BITCOIN' in text or 'CRYPTO' in text:
            relevant_entries.append(entry)
    
    if not relevant_entries:
        relevant_entries = all_entries[:5]  # 使用全部
    
    # 分析情绪
    sentiments = []
    for entry in relevant_entries:
        text = f"{entry['title']} {entry['summary']}"
        sentiment = analyze_text_sentiment(text)
        sentiments.append({
            'title': entry['title'][:60],
            'sentiment': sentiment,
            'published': entry.get('published', '')
        })
    
    # 综合得分
    avg_sentiment = sum(s['sentiment'] for s in sentiments) / len(sentiments) if sentiments else 0
    
    # 分类标签
    if avg_sentiment >= 0.5:
        label = "very_bullish"
        emoji = "🟢🟢"
    elif avg_sentiment >= 0.2:
        label = "bullish"
        emoji = "🟢"
    elif avg_sentiment >= -0.2:
        label = "neutral"
        emoji = "🟡"
    elif avg_sentiment >= -0.5:
        label = "bearish"
        emoji = "🔴"
    else:
        label = "very_bearish"
        emoji = "🔴🔴"
    
    return {
        'symbol': symbol,
        'score': round(avg_sentiment, 2),
        'label': label,
        'emoji': emoji,
        'articles_analyzed': len(relevant_entries),
        'sources': list(RSS_FEEDS.keys()),
        'top_articles': sentiments[:3],
        'timestamp': datetime.now().isoformat()
    }


def format_sentiment_report(result):
    """格式化情绪报告"""
    return f"""
📊 **市场情绪报告** - {result['symbol']}

{result['emoji']} 情绪评分: {result['score']} ({result['label']})

📰 分析来源: {', '.join(result['sources'])}
📝 分析文章: {result['articles_analyzed']}篇

📌 最新文章情绪:
"""
    # 添加文章列表
    for i, article in enumerate(result['top_articles'], 1):
        sentiment_icon = "🟢" if article['sentiment'] > 0 else "🔴" if article['sentiment'] < 0 else "🟡"
        print(f"  {i}. {sentiment_icon} {article['sentiment']:+.1f} - {article['title']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Market Sentiment Analyzer')
    parser.add_argument('--symbol', '-s', default='BTC', help='Symbol to analyze')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='text', help='Output format')
    
    args = parser.parse_args()
    
    print(f"[情绪分析] 分析 {args.symbol} 市场情绪...")
    
    result = analyze_sentiment(args.symbol)
    
    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(format_sentiment_report(result))
        print(f"\n⏰ 更新时间: {result['timestamp']}")


if __name__ == "__main__":
    main()
