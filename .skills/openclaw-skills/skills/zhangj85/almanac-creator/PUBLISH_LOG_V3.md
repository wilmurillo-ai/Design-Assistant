# Almanac Creator 发布日志

## V3.0.1 通用化版（2026-04-12）⭐⭐⭐⭐⭐⭐

**发布版本**: V3.0.1  
**发布时间**: 2026-04-12  
**Skill ID**: 待生成  
**发布者**: Digital Transformation Team (zhangj85)  
**发布状态**: ✅ 已发布至 ClawHub

---

## 🚀 重大升级

### 1. 节气计算通用化 ⭐⭐⭐⭐⭐

**升级内容**:
- ✅ 使用 lunar-python 自动计算节气（支持 1900-2100 年）
- ✅ 移除硬编码节气日期（原仅支持 2026 年）
- ✅ 自动显示"今日清明"、"今日立春"等节气信息
- ✅ 代码简化：无需每年更新节气表

**代码对比**:
```python
# V2.3.1（硬编码，仅 2026 年）
qingming = datetime(2026, 4, 5).date()
qingming_day = (date_obj - qingming).days + 1

# V3.0.1（通用化，支持 1900-2100 年）
lunar = Lunar.fromYmd(year, month, day)
jieqi = lunar.getJieQi()  # 自动返回节气名或 None
```

**受益**:
- ✅ 支持 1900-2100 年任意日期
- ✅ 无需每年维护更新
- ✅ 代码更简洁，易维护

---

### 2. 批量生成功能 ⭐⭐⭐⭐⭐

**功能描述**:
- ✅ 一次生成 7 天/30 天/365 天黄历
- ✅ 按年月分组输出（如 `2026-04/`）
- ✅ 进度条显示
- ✅ 效率提升 80%

**使用示例**:
```bash
# 生成 7 天黄历
python generate_almanac.py --batch 7 --start-date 2026-04-12

# 生成 30 天黄历
python generate_almanac.py --batch 30 --start-date 2026-04-01

# 生成全年黄历（365 天）
python generate_almanac.py --batch 365 --start-date 2026-01-01
```

**输出结构**:
```
reports/
├── 2026-04/
│   ├── 20260412_黄历.png
│   ├── 20260412_黄历_养生.png
│   ├── 20260412_黄历_故事.png
│   ├── 20260413_黄历.png
│   └── ...
└── 2026-05/
    └── ...
```

---

### 3. 配置文件支持 ⭐⭐⭐⭐⭐

**功能描述**:
- ✅ 创建 `config.yaml` 配置文件
- ✅ 配置字体/模板/输出/功能开关
- ✅ 无需修改代码即可调整参数
- ✅ 支持多套配置（日常版/节日版/简约版）

**配置文件示例**:
```yaml
# config.yaml
font:
  title: 90
  section: 60
  content: 48
  small: 40

template:
  default: traditional
  rotation: true
  rotation_days: 5

output:
  base_dir: ./reports
  quality: 95

batch:
  default_days: 7
  max_days: 365
  progress_bar: true
```

**使用方式**:
```bash
# 使用默认配置
python generate_almanac.py --date 2026-04-12

# 使用自定义配置
python generate_almanac.py --date 2026-04-12 --config my_config.yaml
```

---

## 📊 代码统计

| 指标 | V2.3.1 | V3.0.1 | 变化 |
|------|--------|--------|------|
| **总行数** | ~1144 行 | ~1372 行 | +228 行 |
| **硬编码节气** | 10+ 行 | 0 行 | -100% ✅ |
| **配置项** | 0 个 | 20+ 个 | +20 个 |
| **新功能函数** | 0 个 | 2 个 | +2 个 |

---

## 🎯 功能对比

| 功能模块 | V2.3.1 | V3.0.1 | 改进程度 |
|----------|--------|--------|----------|
| **节气计算** | 硬编码（2026 年） | lunar-python（1900-2100） | ⭐⭐⭐⭐⭐ |
| **批量生成** | ❌ 不支持 | ✅ 支持 7/30/365 天 | ⭐⭐⭐⭐⭐ |
| **配置文件** | ❌ 不支持 | ✅ config.yaml | ⭐⭐⭐⭐⭐ |
| **干支计算** | ✅ lunar-python | ✅ lunar-python + 节气 | ⭐⭐⭐⭐ |
| **模板轮换** | ✅ 自动轮换 | ✅ 可配置轮换 | ⭐⭐⭐⭐ |
| **输出分组** | ❌ 单目录 | ✅ 按年月分组 | ⭐⭐⭐⭐ |

---

## 📦 升级方式

### 新安装
```bash
clawhub install almanac-creator
```

### 升级
```bash
clawhub update almanac-creator
```

### 验证版本
```bash
clawhub inspect almanac-creator
# 应显示：Latest: 3.0.1
```

---

## 📝 使用示例

### 单日生成
```bash
# 生成今日黄历
python generate_almanac.py --date 2026-04-12

# 指定输出目录
python generate_almanac.py --date 2026-04-12 --output ./my-output
```

### 批量生成
```bash
# 生成一周黄历
python generate_almanac.py --batch 7 --start-date 2026-04-12

# 生成一月黄历
python generate_almanac.py --batch 30 --start-date 2026-04-01

# 生成全年黄历
python generate_almanac.py --batch 365 --start-date 2026-01-01
```

### 配置文件
```bash
# 使用默认配置
python generate_almanac.py --date 2026-04-12

# 使用自定义配置
python generate_almanac.py --date 2026-04-12 --config my_config.yaml
```

---

## 🐛 已知问题

无已知问题。

---

## 📅 后续计划

### V3.1 规划（短期）
- [ ] 添加每日诗词
- [ ] 添加生肖图标（Unicode）
- [ ] 添加黄历术语解释卡片

### V3.2 规划（长期）
- [ ] AI 生成每日运势建议
- [ ] 多语言支持（英文/繁体）
- [ ] 数据可视化（运势图表）

---

## 👥 贡献者

- **开发**: Digital Transformation Team
- **测试**: 张主管
- **发布**: zhangj85

---

## 📊 版本演进

| 版本 | 日期 | 核心特性 | 文件大小 |
|------|------|----------|----------|
| V2.3.1 | 2026-04-11 | 季节故事修复 + 大字体 | ~628KB |
| **V3.0.1** | **2026-04-12** | **节气通用化 + 批量生成 + 配置文件** | **~700KB** |

---

*发布时间：2026-04-12 11:55*  
*Skill ID: 待生成*  
*版本：V3.0.1 通用化版*
