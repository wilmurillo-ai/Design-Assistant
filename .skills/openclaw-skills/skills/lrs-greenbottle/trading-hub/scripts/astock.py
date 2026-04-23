#!/usr/bin/env python3
"""AStock Analysis - A股市场情绪分析

基于集思录数据，分析市场情绪和仓位建议
"""

import requests
import json
import sys
import re
from datetime import datetime


def get_jsq_data():
    """获取集思录实时数据"""
    try:
        # 涨停家数
        zt_resp = requests.get(
            "https://www.jisilu.cn/api/index/index_zts/",
            params={"market": "CN"},
            timeout=10
        )
        
        # 跌停家数
        dt_resp = requests.get(
            "https://www.jisilu.cn/api/index/index_dts/",
            params={"market": "CN"},
            timeout=10
        )
        
        data = {}
        if zt_resp.status_code == 200:
            zt_data = zt_resp.json()
            data['zt_count'] = int(zt_data.get('data', {}).get('zt_count', 0))
            data['zt_strong_count'] = int(zt_data.get('data', {}).get('zt_strong_count', 0))
        
        if dt_resp.status_code == 200:
            dt_data = dt_resp.json()
            data['dt_count'] = int(dt_data.get('data', {}).get('dt_count', 0))
        
        return data
    except Exception as e:
        print(f"[WARN] 集思录API错误: {e}")
        return {}


def get_baostock_data():
    """获取 BaoStock 数据（备用）"""
    try:
        # 使用东方财富数据源
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "cb": "jQuery",
            "pn": "1",
            "pz": "20",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0+t:6,m:0+t:13,m:1+t:2,m:1+t:23",
            "fields": "f1,f2,f3,f12,f14",
            "_": int(datetime.now().timestamp() * 1000)
        }
        
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            text = resp.text
            # 简单解析
            return {}
        return {}
    except Exception as e:
        print(f"[WARN] 东方财富API错误: {e}")
        return {}


def calculate_market_sentiment(zt_count, dt_count, zt_strong=0):
    """计算市场情绪和仓位建议"""
    
    # 情绪评分 (0-100)
    sentiment_score = 50
    
    # 涨停数量评分
    if zt_count >= 100:
        sentiment_score += 25
    elif zt_count >= 80:
        sentiment_score += 20
    elif zt_count >= 60:
        sentiment_score += 15
    elif zt_count >= 40:
        sentiment_score += 10
    elif zt_count >= 20:
        sentiment_score += 5
    elif zt_count < 10:
        sentiment_score -= 15
    elif zt_count < 20:
        sentiment_score -= 10
    
    # 跌停数量评分（负向）
    if dt_count >= 30:
        sentiment_score -= 20
    elif dt_count >= 20:
        sentiment_score -= 15
    elif dt_count >= 10:
        sentiment_score -= 10
    elif dt_count >= 5:
        sentiment_score -= 5
    
    # 连板强势股加分
    if zt_strong > 5:
        sentiment_score += 10
    elif zt_strong > 3:
        sentiment_score += 5
    
    # 限制范围
    sentiment_score = max(0, min(100, sentiment_score))
    
    # 判断市场状态
    if sentiment_score >= 75:
        market_status = "强势"
        position_ratio = 0.70
        single_limit = 0.15
        description = "市场情绪亢奋，赚钱效应强"
    elif sentiment_score >= 55:
        market_status = "偏强"
        position_ratio = 0.60
        single_limit = 0.12
        description = "市场情绪较好，结构性机会"
    elif sentiment_score >= 40:
        market_status = "震荡"
        position_ratio = 0.45
        single_limit = 0.10
        description = "市场情绪分化，谨慎操作"
    elif sentiment_score >= 25:
        market_status = "偏弱"
        position_ratio = 0.30
        single_limit = 0.08
        description = "市场情绪低迷，控制仓位"
    else:
        market_status = "冰点"
        position_ratio = 0.15
        single_limit = 0.05
        description = "市场情绪冰点，观望为主"
    
    return {
        "sentiment_score": sentiment_score,
        "market_status": market_status,
        "position_ratio": position_ratio,
        "single_limit": single_limit,
        "description": description
    }


def get_market_sentiment_text():
    """获取市场情绪文字描述"""
    data = get_jsq_data()
    
    zt_count = data.get('zt_count', 0)
    dt_count = data.get('dt_count', 0)
    zt_strong = data.get('zt_strong_count', 0)
    
    sentiment = calculate_market_sentiment(zt_count, dt_count, zt_strong)
    
    result = {
        "source": "jisilu",
        "zt_count": zt_count,
        "zt_strong_count": zt_strong,
        "dt_count": dt_count,
        **sentiment,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%M')
    }
    
    return result


def check_ice_point():
    """检查是否冰点"""
    data = get_jsq_data()
    zt_count = data.get('zt_count', 0)
    dt_count = data.get('dt_count', 0)
    
    is_ice = zt_count < 20
    is_super_ice = zt_count < 10
    
    sentiment = calculate_market_sentiment(zt_count, dt_count)
    
    return {
        "is_ice": is_ice,
        "is_super_ice": is_super_ice,
        "zt_count": zt_count,
        "dt_count": dt_count,
        "sentiment": sentiment,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%M')
    }


def get_position_suggestion():
    """获取仓位建议"""
    data = get_jsq_data()
    zt_count = data.get('zt_count', 0)
    dt_count = data.get('dt_count', 0)
    zt_strong = data.get('zt_strong_count', 0)
    
    sentiment = calculate_market_sentiment(zt_count, dt_count, zt_strong)
    
    return {
        "market_status": sentiment['market_status'],
        "position_ratio": sentiment['position_ratio'],
        "position_pct": int(sentiment['position_ratio'] * 100),
        "single_limit_pct": int(sentiment['single_limit'] * 100),
        "description": sentiment['description'],
        "zt_count": zt_count,
        "zt_strong_count": zt_strong,
        "dt_count": dt_count,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%M')
    }


def format_report(data):
    """格式化报告"""
    status = data.get('market_status', '未知')
    
    status_emoji = {
        "强势": "🟢",
        "偏强": "🟢",
        "震荡": "🟡",
        "偏弱": "🟠",
        "冰点": "🔴"
    }.get(status, "⚪")
    
    report = f"""
📊 **A股市场情绪报告**

{status_emoji} 市场状态: **{status}**
📈 情绪评分: {data.get('sentiment_score', 0)}/100
📝 市场描述: {data.get('description', '')}

---

📌 **涨停数据**
• 涨停家数: {data.get('zt_count', 0)}家
• 强势涨停: {data.get('zt_strong_count', 0)}家
• 跌停家数: {data.get('dt_count', 0)}家

---

💼 **仓位建议**
• 建议仓位: {data.get('position_pct', 0)}%
• 单票上限: {data.get('single_limit_pct', 0)}%

---

⏰ 更新时间: {data.get('timestamp', '')}
"""
    return report


def main():
    if len(sys.argv) < 2:
        # 默认输出完整报告
        data = get_position_suggestion()
        data.update(get_market_sentiment_text())
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(format_report(data))
        return
    
    action = sys.argv[1].lower()
    
    if action == 'sentiment' or action == '情绪':
        data = get_market_sentiment_text()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    elif action == 'ice' or action == '冰点':
        data = check_ice_point()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        if data['is_super_ice']:
            print(f"\n🚨 **极度冰点！** 涨停仅 {data['zt_count']} 家")
        elif data['is_ice']:
            print(f"\n🔴 **市场冰点** 涨停 {data['zt_count']} 家，建议仓位 ≤15%")
        else:
            print(f"\n🟡 市场未冰点（涨停 {data['zt_count']} 家）")
    
    elif action == 'position' or action == '仓位':
        data = get_position_suggestion()
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(format_report(data))
    
    elif action == 'zt' or action == '涨停':
        data = get_jsq_data()
        print(f"📈 涨停: {data.get('zt_count', 'N/A')}家")
        print(f"📈 强势涨停: {data.get('zt_strong_count', 'N/A')}家")
        print(f"📉 跌停: {data.get('dt_count', 'N/A')}家")
    
    elif action == 'all':
        data = get_position_suggestion()
        data.update(get_market_sentiment_text())
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print(format_report(data))
    
    else:
        print(f"[ERROR] 未知操作: {action}")
        print("Usage: python3 astock.py [sentiment|ice|position|zt|all]")


if __name__ == "__main__":
    main()
