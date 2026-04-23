#!/usr/bin/env python3
"""Position Manager - 统一仓位管理

整合币安合约持仓和A股模拟持仓，统一风控
"""

import sys
import json
import datetime
from pathlib import Path

sys.path.insert(0, __file__.rsplit('/', 2)[0])

from config import load_config, get_signature, load_positions, save_positions
from binance_api import get_position as get_binance_position, get_balance as get_binance_balance, get_current_price


# 数据目录
DATA_DIR = Path(__file__).parent.parent / 'data'
POSITIONS_FILE = DATA_DIR / 'positions.json'


def get_astock_positions():
    """获取A股模拟持仓"""
    positions = load_positions()
    return positions.get('astock', {})


def get_total_exposure():
    """计算总风险敞口"""
    config = load_config()
    
    result = {
        'binance': {
            'total_value': 0,
            'positions': []
        },
        'astock': {
            'total_value': 0,
            'positions': []
        },
        'total_value': 0,
        'total_exposure': 0
    }
    
    # Binance持仓
    try:
        btc_pos = get_binance_position('BTCUSDT')
        btc_balance = get_binance_balance()
        
        if btc_pos:
            btc_price = get_current_price('BTCUSDT') or btc_pos['entry_price']
            position_value = abs(btc_pos['quantity']) * btc_price
            
            result['binance']['positions'].append({
                'symbol': 'BTCUSDT',
                'direction': 'long' if btc_pos['quantity'] > 0 else 'short',
                'quantity': abs(btc_pos['quantity']),
                'entry_price': btc_pos['entry_price'],
                'current_price': btc_price,
                'value': position_value,
                'pnl': btc_pos.get('unrealized_pnl', 0),
                'leverage': btc_pos.get('leverage', 1)
            })
            result['binance']['total_value'] += position_value
        
        if btc_balance:
            result['binance']['available'] = btc_balance.get('available', 0)
            result['binance']['balance'] = btc_balance.get('balance', 0)
    except Exception as e:
        result['binance']['error'] = str(e)
    
    # A股持仓
    astock_positions = get_astock_positions()
    for symbol, pos in astock_positions.items():
        result['astock']['positions'].append({
            'symbol': symbol,
            'quantity': pos.get('quantity', 0),
            'cost': pos.get('cost', 0),
            'current_price': pos.get('current_price', pos.get('cost', 0)),
            'value': pos.get('quantity', 0) * pos.get('current_price', pos.get('cost', 0)),
            'pnl': pos.get('pnl', 0)
        })
        result['astock']['total_value'] += pos.get('quantity', 0) * pos.get('current_price', pos.get('cost', 0))
    
    # 总计
    result['total_value'] = result['binance']['total_value'] + result['astock']['total_value']
    result['total_exposure'] = result['binance']['total_value']  # 合约仓位为敞口
    
    return result


def calculate_position_suggestion(exposure_data):
    """根据市场情绪和持仓计算仓位建议"""
    from astock import get_position_suggestion
    
    market_data = get_position_suggestion()
    market_ratio = market_data['position_ratio']
    
    binance_value = exposure_data['binance']['total_value']
    available = exposure_data['binance'].get('available', 0)
    
    # 建议的最大持仓
    suggested_max = available * market_ratio if available > 0 else 0
    
    # 当前是否超仓
    is_overexposed = binance_value > suggested_max and suggested_max > 0
    
    return {
        'market_status': market_data['market_status'],
        'market_ratio': market_ratio,
        'current_value': binance_value,
        'available': available,
        'suggested_max': suggested_max,
        'suggested_add': max(0, suggested_max - binance_value),
        'should_reduce': is_overexposed,
        'reduce_amount': binance_value - suggested_max if is_overexposed else 0
    }


def get_risk_warnings(exposure_data):
    """获取风险警告"""
    warnings = []
    
    binance_value = exposure_data['binance']['total_value']
    available = exposure_data['binance'].get('available', 0)
    
    # 杠杆检查
    for pos in exposure_data['binance']['positions']:
        if pos.get('leverage', 1) > 10:
            warnings.append(f"⚠️ {pos['symbol']} 杠杆{pos['leverage']}x超过10x限制")
    
    # 亏损检查
    for pos in exposure_data['binance']['positions']:
        pnl_pct = (pos.get('pnl', 0) / (pos.get('value', 1))) * 100
        if pnl_pct < -5:
            warnings.append(f"🚨 {pos['symbol']} 亏损{pnl_pct:.1f}%，建议止损")
        elif pnl_pct < -3:
            warnings.append(f"⚠️ {pos['symbol']} 亏损{pnl_pct:.1f}%，关注风险")
    
    # 单币种集中度
    if binance_value > 0:
        for pos in exposure_data['binance']['positions']:
            ratio = pos.get('value', 0) / binance_value if binance_value > 0 else 0
            if ratio > 0.5:
                warnings.append(f"⚠️ {pos['symbol']} 集中度{ratio*100:.0f}%，建议分散")
    
    return warnings


def add_astock_position(symbol, quantity, cost):
    """添加A股模拟持仓"""
    positions = load_positions()
    if 'astock' not in positions:
        positions['astock'] = {}
    
    positions['astock'][symbol] = {
        'quantity': quantity,
        'cost': cost,
        'current_price': cost,
        'add_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_positions(positions)
    return positions['astock']


def remove_astock_position(symbol):
    """移除A股模拟持仓"""
    positions = load_positions()
    if 'astock' in positions and symbol in positions['astock']:
        del positions['astock'][symbol]
        save_positions(positions)
        return True
    return False


def update_astock_prices():
    """更新A股持仓价格（需要行情数据源）"""
    # TODO: 接入实时行情
    pass


def format_exposure_report(exposure_data, suggestion=None, warnings=None):
    """格式化风险敞口报告"""
    report = """
📊 **统一仓位报告**

"""
    
    # Binance
    binance = exposure_data['binance']
    report += "**🟡 币安合约持仓**\n"
    if binance.get('error'):
        report += f"⚠️ 错误: {binance['error']}\n"
    elif binance['positions']:
        for pos in binance['positions']:
            emoji = "🟢" if pos['pnl'] >= 0 else "🔴"
            report += f"{emoji} {pos['symbol']}: {pos['quantity']}个, 价值${pos['value']:.2f}, PnL: ${pos['pnl']:.2f} ({pos['leverage']}x)\n"
        report += f"💰 可用: ${binance.get('available', 0):.2f}\n"
        report += f"📊 合约总价值: ${binance['total_value']:.2f}\n"
    else:
        report += "📭 无持仓\n"
        report += f"💰 可用: ${binance.get('available', 0):.2f}\n"
    
    report += "\n"
    
    # A股
    astock = exposure_data['astock']
    report += "**🟠 A股模拟持仓**\n"
    if astock['positions']:
        for pos in astock['positions']:
            emoji = "🟢" if pos['pnl'] >= 0 else "🔴"
            report += f"{emoji} {pos['symbol']}: {pos['quantity']}股, 成本${pos['cost']:.2f}, 盈亏${pos['pnl']:.2f}\n"
        report += f"📊 A股总价值: ${astock['total_value']:.2f}\n"
    else:
        report += "📭 无持仓\n"
    
    report += "\n"
    
    # 总计
    report += f"**📈 总风险敞口**: ${exposure_data['total_exposure']:.2f}\n"
    report += f"**💵 总价值**: ${exposure_data['total_value']:.2f}\n"
    
    # 仓位建议
    if suggestion:
        status_emoji = {
            "强势": "🟢",
            "偏强": "🟢",
            "震荡": "🟡",
            "偏弱": "🟠",
            "冰点": "🔴"
        }.get(suggestion['market_status'], "⚪")
        
        report += f"""
---

**📊 市场状态**: {status_emoji} {suggestion['market_status']}
**💼 建议仓位**: {int(suggestion['market_ratio']*100)}%
**📍 当前敞口**: ${suggestion['current_value']:.2f}
"""
        
        if suggestion['should_reduce']:
            report += f"\n⚠️ **超仓警告**: 建议减仓 ${suggestion['reduce_amount']:.2f}"
        elif suggestion['suggested_add'] > 100:
            report += f"\n💡 可以加仓: 最多 +${suggestion['suggested_add']:.2f}"
    
    # 风险警告
    if warnings:
        report += "\n\n---\n**🚨 风险警告**\n"
        for w in warnings:
            report += f"{w}\n"
    
    report += f"\n⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return report


def main():
    if len(sys.argv) < 2:
        # 默认输出完整报告
        exposure = get_total_exposure()
        suggestion = calculate_position_suggestion(exposure)
        warnings = get_risk_warnings(exposure)
        
        print(json.dumps({
            'exposure': exposure,
            'suggestion': suggestion,
            'warnings': warnings,
            'timestamp': datetime.datetime.now().isoformat()
        }, indent=2, ensure_ascii=False))
        
        print(format_exposure_report(exposure, suggestion, warnings))
        return
    
    action = sys.argv[1].lower()
    
    if action == 'exposure' or action == '敞口':
        exposure = get_total_exposure()
        print(json.dumps(exposure, indent=2, ensure_ascii=False))
    
    elif action == 'suggestion' or action == '建议':
        exposure = get_total_exposure()
        suggestion = calculate_position_suggestion(exposure)
        print(json.dumps(suggestion, indent=2, ensure_ascii=False))
    
    elif action == 'risk' or action == '风险':
        exposure = get_total_exposure()
        warnings = get_risk_warnings(exposure)
        print(json.dumps(warnings, indent=2, ensure_ascii=False))
        for w in warnings:
            print(w)
    
    elif action == 'add' and len(sys.argv) >= 5:
        # add ASTOCK <symbol> <quantity> <cost>
        symbol = sys.argv[2]
        quantity = float(sys.argv[3])
        cost = float(sys.argv[4])
        add_astock_position(symbol, quantity, cost)
        print(f"[OK] 添加 {symbol}: {quantity}股 @ ${cost}")
    
    elif action == 'remove' and len(sys.argv) >= 3:
        symbol = sys.argv[2]
        if remove_astock_position(symbol):
            print(f"[OK] 移除 {symbol}")
        else:
            print(f"[WARN] {symbol} 不存在")
    
    elif action == 'list':
        positions = load_positions()
        print(json.dumps(positions, indent=2, ensure_ascii=False))
    
    else:
        print("[Usage] position_manager.py [exposure|suggestion|risk|add|remove|list]")


if __name__ == "__main__":
    main()
