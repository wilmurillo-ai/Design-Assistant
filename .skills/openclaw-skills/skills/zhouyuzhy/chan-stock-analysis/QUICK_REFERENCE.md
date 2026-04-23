# 缠论分析快速参考

## 执行命令

```bash
# 使用新脚本 v6（推荐）
D:\Tools\CoPaw\venv\Scripts\python.exe "D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v6.py" --code "代码"

# 示例
D:\Tools\CoPaw\venv\Scripts\python.exe "D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v6.py" --code 159890
```

---

## 核心概念速记

### 笔（Bi）
- 极值点 → 极值点
- 最小5根K线
- 方向：上升或下降

### 中枢（Zhongshu）
- 三笔同向笔 → 中枢
- 范围 = max(低点) 到 min(高点)
- 中枢内=盘整，离开=趋势

### 背驰（Beichi）
- 同向笔的动能衰竭
- 三个条件：同号对比、MACD面积、DIF高度
- 强背驰（<50%）vs 弱背驰（50%-100%）

---

## 分析流程

```
1. 获取四级数据（日K、30分钟、5分钟、1分钟）
   ↓
2. 识别分型 → 笔 → 中枢
   ↓
3. 判断趋势（考虑中枢位置）
   ↓
4. 识别背驰（同号对比 + MACD面积 + DIF高度）
   ↓
5. 多级别联立判断
   ↓
6. 生成分析报告
```

---

## 常见错误

| 错误 | 原因 | 正确做法 |
|------|------|--------|
| 中枢判断错误 | 任意两个高低点 | 三笔同向笔 |
| 趋势判断错误 | 仅看最后一笔 | 考虑中枢位置 |
| 背驰判断错误 | 正数和负数对比 | 同号对比 |
| 均线信号错误 | 仅看最近5根K线 | 结合中枢和背驰 |

---

## 输出格式

```
一、日线级别分析
  - 当前价
  - 趋势
  - 中枢
  - MACD
  - 背驰

二、30分钟级别分析
  - 同上

三、5分钟级别分析
  - 同上

四、1分钟级别分析
  - 同上

五、多级别联立状态总结
  - 各级别趋势
  - 背驰汇总

六、走势完全分类与推演
  - 分类一（>70%）
  - 分类二（~25%）
  - 分类三（<5%）

七、终极操作策略
  - 基于多级别联立的建议

八、风险提示
  - 免责声明
```

---

## 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 笔最小周期 | 5根K线 | 极值点间隔 |
| 中枢最小笔数 | 3笔 | 同向笔数量 |
| 强背驰阈值 | <50% | 离开段/进入段 |
| 弱背驰阈值 | 50%-100% | 离开段/进入段 |
| 缓存有效期 | 24小时 | K线数据缓存 |

---

## 数据源优先级

1. 缓存（24小时有效）
2. akshare
3. futu（富途）
4. tushare

---

## 文件位置

| 文件 | 路径 |
|------|------|
| 脚本 v6 | `D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v6.py` |
| 脚本 v5 | `D:\QClawData\workspace\skills\chan-stock-analysis\scripts\chan_v5.py` |
| 技能文档 | `D:\QClawData\workspace\skills\chan-stock-analysis\SKILL.md` |
| 缓存目录 | `D:\QClawData\workspace\skills\chan-stock-analysis\scripts\cache\` |

---

## 触发词

- "缠论分析"
- "分析下股票"
- "使用缠论分析下"
- "帮我分析下"

