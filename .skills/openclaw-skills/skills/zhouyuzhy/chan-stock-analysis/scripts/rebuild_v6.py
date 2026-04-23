import os, stat

src = r'D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v5.py'
dst = r'D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v6_new.py'

if os.path.exists(dst):
    os.chmod(dst, stat.S_IWRITE)
    os.remove(dst)

with open(src, encoding='utf-8') as f:
    lines = f.readlines()

head = lines[:511]

tail = '''

def format_level_analysis(level_data, level_name):
    out = []
    if not level_data:
        out.append(f"  ❌ {level_name}数据不足")
        return '\\n'.join(out)
    ma = level_data.get('ma_analysis')
    m = level_data.get('macd') or {}
    beichi = level_data.get('beichi')
    bsp = level_data.get('buy_sell_points')
    fib = level_data.get('fib')
    current = level_data['current']
    direction = level_data['direction']
    dir_emoji = '📈 上涨' if direction == 'up' else '📉 下跌' if direction == 'down' else '➡️ 未知'
    out.append(f"\\n  当前价：{current:.3f}  趋势：{dir_emoji}")
    if level_data['zhongshus']:
        zs = level_data['zhongshus'][-1]
        out.append(f"  中枢区间：{zs['range'][0]:.3f} - {zs['range'][1]:.3f}")
    if ma:
        if ma.get('resistance_ma'):
            diff_pct = (ma['resistance_price'] - current) / current * 100
            out.append(f"  📍 压力：MA{ma['resistance_ma']}={ma['resistance_price']:.3f}（{diff_pct:+.2f}%）")
        if ma.get('support_ma'):
            diff_pct = (current - ma['support_price']) / ma['support_price'] * 100
            out.append(f"  📍 支撑：MA{ma['support_ma']}={ma['support_price']:.3f}（{diff_pct:+.2f}%）")
        if ma.get('strong_support'):
            p, c = ma['strong_support']
            mv = ma['ma_values'].get(p, 0)
            out.append(f"  💪 历史多次支撑：MA{p}={mv:.3f}（{c}次）")
        if ma.get('strong_resistance'):
            p, c = ma['strong_resistance']
            mv = ma['ma_values'].get(p, 0)
            out.append(f"  💪 历史多次压力：MA{p}={mv:.3f}（{c}次）")
        if ma.get('signal') == 'bullish_breakout':
            out.append(f"  🚀 均线看多：有效突破多次承压均线，回踩不破")
        elif ma.get('signal') == 'bearish_breakdown':
            out.append(f"  🔻 均线看空：有效跌破多次支撑均线，回升未突破")
    if m:
        macd_val = m.get('macd', 0)
        color = "红柱" if macd_val > 0 else "绿柱"
        dyn = "动能增强" if abs(macd_val) > 0.01 else "动能减弱"
        out.append(f"  MACD：DIF={m['dif']:.3f} DEA={m['dea']:.3f} {color}{abs(macd_val):.3f}（{dyn}）")
    if beichi:
        bc_type_str = "底背驰 🟢" if beichi['type'] == 'bottom' else "顶背驰 🔴"
        strength_str = "强" if beichi['strength'] == 'strong' else "弱"
        out.append(f"  ⚡ 背驰：{bc_type_str}（{strength_str}，进入段{beichi['enter_pct']:.1f}% → 离开段{beichi['leave_pct']:.1f}%，比值{beichi['ratio']:.0%}）")
    else:
        out.append(f"  ⚡ 背驰：未发现")
    if bsp:
        emoji_map = {'1buy': '🟢 一买', '2buy': '🟢 二买', '3buy': '🟢 三买', '1sell': '🔴 一卖', '2sell': '🔴 二卖', '3sell': '🔴 三卖'}
        for pt in bsp:
            confirmed = "✅ 已确认" if pt['confirmed'] else "⚠️ 待确认"
            pt_label = emoji_map.get(pt['type'], pt['type'])
            out.append(f"  🎯 {pt_label}：{pt['desc']} [{confirmed}]")
    if fib:
        out.append(f"  斐波那契（{fib['trend']}趋势，区间{fib['low']:.3f}-{fib['high']:.3f}，当前位置{fib['position']*100:.1f}%）：")
        for lv in ['0.618', '0.500', '0.382']:
            price = fib['levels'][lv]
            marker = ""
            if fib['support'] and fib['support'][0] == lv: marker = " ←支撑"
            elif fib['resistance'] and fib['resistance'][0] == lv: marker = " ←阻力"
            out.append(f"    {lv}: {price:.3f}{marker}")
    return '\\n'.join(out)


def generate_report(name, code, daily, m30, m5, m1):
    today = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    daily_a = analyze_level(daily, '日线') if daily else None
    m30_a = analyze_level(m30, '30分钟') if m30 else None
    m5_a = analyze_level(m5, '5分钟') if m5 else None
    m1_a = analyze_level(m1, '1分钟') if m1 else None
    trends = {}
    if daily_a: trends['日线'] = daily_a['direction']
    if m30_a: trends['30分钟'] = m30_a['direction']
    if m5_a: trends['5分钟'] = m5_a['direction']
    if m1_a: trends['1分钟'] = m1_a['direction']
    up_count = sum(1 for t in trends.values() if t == 'up')
    down_count = sum(1 for t in trends.values() if t == 'down')
    resonance = 'up' if up_count >= 3 else 'down' if down_count >= 3 else 'mixed'
    resonance_level = '强' if (up_count if resonance == 'up' else down_count) == 4 else '中'
    all_bsp = {}
    for lv_name, lv_data in [('日线', daily_a), ('30分钟', m30_a), ('5分钟', m5_a), ('1分钟', m1_a)]:
        if lv_data and lv_data.get('buy_sell_points'):
            all_bsp[lv_name] = lv_data['buy_sell_points']
    all_beichi = {}
    for lv_name, lv_data in [('日线', daily_a), ('30分钟', m30_a), ('5分钟', m5_a), ('1分钟', m1_a)]:
        if lv_data and lv_data.get('beichi'):
            all_beichi[lv_name] = lv_data['beichi']
    report = [f"{'━'*60}", f"  缠论多级别联立分析报告 v6", f"  标的：{name}（{code}）", f"  时间：{today}", f"{'━'*60}"]
    for i, (lv_name, lv_data) in enumerate([('日线', daily_a), ('30分钟', m30_a), ('5分钟', m5_a), ('1分钟', m1_a)], 1):
        cn = ['一', '二', '三', '四'][i-1]
        report.append(f"\\n{cn}、{lv_name}级别分析")
        report.append("─" * 50)
        report.append(format_level_analysis(lv_data, lv_name))
    report.append(f"\\n五、多级别联立状态总结")
    report.append("━" * 60)
    report.append(f"\\n  【各级别趋势】")
    for level, trend in trends.items():
        emoji = '📈' if trend == 'up' else '📉' if trend == 'down' else '➡️'
        report.append(f"    {level}：{emoji} {'上涨' if trend=='up' else '下跌' if trend=='down' else '未知'}")
    if all_beichi:
        report.append(f"\\n  【背驰汇总】")
        for level, bc in all_beichi.items():
            bc_str = "底背驰🟢" if bc['type'] == 'bottom' else "顶背驰🔴"
            report.append(f"    {level}：{bc_str}（{'强' if bc['strength']=='strong' else '弱'}，比值{bc['ratio']:.0%}）")
    report.append(f"\\n  【买卖点联立判断】")
    buy_types = ['1buy', '2buy', '3buy']
    sell_types = ['1sell', '2sell', '3sell']
    buy_label = {'1buy': '一买', '2buy': '二买', '3buy': '三买'}
    sell_label = {'1sell': '一卖', '2sell': '二卖', '3sell': '三卖'}
    big_levels = ['日线', '30分钟']
    small_levels = ['5分钟', '1分钟']
    big_buy = None
    big_sell = None
    for lv in big_levels:
        if lv in all_bsp:
            for pt in all_bsp[lv]:
                if pt['type'] in buy_types and not big_buy: big_buy = (lv, pt)
                if pt['type'] in sell_types and not big_sell: big_sell = (lv, pt)
    small_beichi_bottom = any(all_beichi.get(lv, {}).get('type') == 'bottom' for lv in small_levels)
    small_beichi_top = any(all_beichi.get(lv, {}).get('type') == 'top' for lv in small_levels)
    if big_buy:
        lv, pt = big_buy
        status = "✅ 小级别背驰确认，可考虑入场" if small_beichi_bottom else "⚠️ 等待小级别背驰确认"
        report.append(f"    🟢 {lv}{buy_label[pt['type']]}：{pt['desc']}")
        report.append(f"       → {status}")
    elif big_sell:
        lv, pt = big_sell
        status = "✅ 小级别背驰确认，可考虑减仓/做空" if small_beichi_top else "⚠️ 等待小级别背驰确认"
        report.append(f"    🔴 {lv}{sell_label[pt['type']]}：{pt['desc']}")
        report.append(f"       → {status}")
    else:
        res_text = '🔴 共振做多' if resonance == 'up' else '🟢 共振做空' if resonance == 'down' else '⚪ 震荡分化'
        report.append(f"    暂无明确买卖点，当前联立判断：{res_text}（{resonance_level}共振）")
        if daily_a and m30_a and daily_a['direction'] != m30_a['direction']:
            report.append(f"    ⚠️ 大小级别背离，等待方向确认")
    report.append(f"\\n六、走势完全分类与推演")
    report.append("─" * 50)
    daily_fib = daily_a['fib'] if daily_a and daily_a.get('fib') else None
    m30_dir = m30_a['direction'] if m30_a else None
    if daily_fib and m30_dir:
        d_high, d_low = daily_fib['high'], daily_fib['low']
        if m30_dir == 'up':
            report.extend([f"\\n  【分类一】大概率 >70%：上涨延续", f"    路径：价格继续上涨，挑战前高 {d_high:.3f}", f"    操作：多头持有，回调至均线支撑加仓", f"\\n  【分类二】中概率 ~25%：震荡整理", f"    路径：在 {d_low:.3f} - {d_high:.3f} 区间震荡", f"    操作：高抛低吸，区间边缘注意反向", f"\\n  【分类三】小概率 <5%：趋势反转", f"    路径：出现大级别顶背驰，跌破均线支撑", f"    操作：多单止损，等待一卖信号"])
        else:
            report.extend([f"\\n  【分类一】大概率 >70%：下跌延续", f"    路径：价格继续下跌，测试前低 {d_low:.3f}", f"    操作：空头持有，反弹至均线压力位做空", f"\\n  【分类二】中概率 ~25%：反弹整理", f"    路径：反弹至 {d_high:.3f} 附近后回落", f"    操作：反弹至压力位做空，止损前高", f"\\n  【分类三】小概率 <5%：趋势反转", f"    路径：出现大级别底背驰，放量突破均线压力", f"    操作：空单止损，等待一买信号"])
    report.append(f"\\n七、终极操作策略")
    report.append("─" * 50)
    if big_buy:
        lv, pt = big_buy
        pt_name = buy_label[pt['type']]
        if small_beichi_bottom:
            report.extend([f"\\n  当前处于 {lv}{pt_name} 区域，小级别已确认背驰", f"  ✅ 建议：轻仓试多，止损设在前低", f"  目标：等待30分钟/日线级别反弹确认"])
        else:
            report.extend([f"\\n  当前处于 {lv}{pt_name} 区域，等待小级别背驰确认", f"  ⚠️ 建议：观望，等待5分钟/1分钟出现底背驰后入场"])
    elif big_sell:
        lv, pt = big_sell
        pt_name = sell_label[pt['type']]
        if small_beichi_top:
            report.extend([f"\\n  当前处于 {lv}{pt_name} 区域，小级别已确认背驰", f"  ✅ 建议：减仓/止盈，止损设在前高"])
        else:
            report.extend([f"\\n  当前处于 {lv}{pt_name} 区域，等待小级别背驰确认", f"  ⚠️ 建议：观望，等待5分钟/1分钟出现顶背驰后减仓"])
    elif resonance == 'up':
        report.extend([f"\\n  多级别共振做多，无明确卖点", f"  建议：持有多单，回调至均线支撑可加仓"])
    elif resonance == 'down':
        report.extend([f"\\n  多级别共振做空，无明确买点", f"  建议：持有空单，反弹至均线压力可加空"])
    else:
        report.extend([f"\\n  震荡分化，暂无明确方向", f"  建议：观望为主，等待大级别背驰信号出现"])
    report.extend([f"\\n八、风险提示", "─" * 50, f"  ⚠️ 本分析仅供学习参考，不构成投资建议", f"  ⚠️ 买卖点需结合实际K线形态人工确认", f"  ⚠️ 市场有风险，投资需谨慎", f"\\n{'━'*60}", f"  分析完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"{'━'*60}"])
    return '\\n'.join(report)


def main():
    parser = argparse.ArgumentParser(description='缠论多级别联立分析 v6')
    parser.add_argument('--code', '-c', type=str, required=True, help='股票/指数代码')
    args = parser.parse_args()
    code = args.code.strip()
    is_index = code in ['399001', '399006', '399300', '000001', '000016', '000688', '000852']
    index_names = {'399006': '创业板指', '399001': '深证成指', '399300': '沪深300', '000001': '上证指数', '000016': '上证50', '000688': '科创50'}
    name = index_names.get(code, code)
    print(f"\\n{'='*60}")
    print(f"  正在获取 {name}（{code}）数据...")
    print(f"  策略：akshare → futu → tushare（缓存优先）")
    print(f"{'='*60}\\n")
    print("📊 获取日K数据...")
    daily, daily_src = get_kline(code, 'daily', is_index)
    print(f"   {'✅' if daily else '❌'} {len(daily) if daily else 0}根 (来源: {daily_src})\\n")
    print("📊 获取30分钟K数据...")
    m30, m30_src = get_kline(code, '30', is_index)
    print(f"   {'✅' if m30 else '❌'} {len(m30) if m30 else 0}根 (来源: {m30_src})\\n")
    print("📊 获取5分钟K数据...")
    m5, m5_src = get_kline(code, '5', is_index)
    print(f"   {'✅' if m5 else '❌'} {len(m5) if m5 else 0}根 (来源: {m5_src})\\n")
    print("📊 获取1分钟K数据...")
    m1, m1_src = get_kline(code, '1', is_index)
    print(f"   {'✅' if m1 else '❌'} {len(m1) if m1 else 0}根 (来源: {m1_src})\\n")
    if not all([daily, m30, m5, m1]):
        missing = [n for n, d in [('日K', daily), ('30分钟K', m30), ('5分钟K', m5), ('1分钟K', m1)] if not d]
        print(f"\\n{'='*60}")
        print(f"  ❌ 分钟级数据获取失败，无法进行多级别联立分析")
        print(f"  失败数据：{', '.join(missing)}")
        print(f"{'='*60}")
        import sys; sys.exit(1)
    print("\\n📝 生成分析报告...\\n")
    print(generate_report(name, code, daily, m30, m5, m1))


if __name__ == "__main__":
    main()
'''

with open(dst, 'w', encoding='utf-8') as f:
    f.writelines(head)
    f.write(tail)

print(f"Written to {dst}")

import py_compile
try:
    py_compile.compile(dst, doraise=True)
    print("Syntax OK!")
except py_compile.PyCompileError as e:
    print(f"Syntax Error: {e}")
