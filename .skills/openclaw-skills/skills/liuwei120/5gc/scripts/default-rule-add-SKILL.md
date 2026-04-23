# default-rule-add Skill

## 功能

为指定工程一键配置完整的 **PCF 默认规则**链路，包括：
QoS模板 → Traffic Control → PCC规则 → sm_policy_default → PCF default_smpolicy

## 触发条件

用户说"添加默认规则"、"配置PCF默认规则"、"创建默认规则"、"添加PCF规则"，
或任何包含"默认规则"+"工程"的请求。

## 脚本

`skills/5gc/scripts/default-rule-add-skill.js`

## 核心参数

所有参数均可省略，使用默认值。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--project` | 工程名 | `XW_S5GC_1` |
| `--qos-id` | QoS模板ID | `qos_default_{时间戳}` |
| `--5qi` | 5QI值 | 自动选择未使用的值（优先8/9/6/5...） |
| `--maxbr-ul` | 上行最大比特率 | `10000000` |
| `--maxbr-dl` | 下行最大比特率 | `20000000` |
| `--gbr-ul` | 上行保证比特率 | `5000000` |
| `--gbr-dl` | 下行保证比特率 | `5000000` |
| `--tc-id` | TC规则ID | `tc_default_{时间戳}` |
| `--flow-status` | TC流状态 | `ENABLED` |
| `--pcc-id` | PCC规则ID | `pcc_default` |
| `--precedence` | PCC优先级 | `63` |
| `--headed` | 显示浏览器窗口（调试用） | off |

## 使用示例

```bash
# 最简用法（自动生成所有ID）
node skills/5gc/scripts/default-rule-add-skill.js --project XW_SUPF_5_1_2_4

# 指定 QoS 和 TC
node skills/5gc/scripts/default-rule-add-skill.js --project XW_SUPF_5_1_2_4 --qos-id qos1 --tc-id tc1 --pcc-id pcc_default

# 完整参数
node skills/5gc/scripts/default-rule-add-skill.js --project XW_SUPF_5_1_2_4 --qos-id qos_new --5qi 8 --maxbr-ul 20000000 --maxbr-dl 50000000 --pcc-id pcc_new --precedence 50
```

## 自然语言调用示例

模型应将以下用户表述转换为对应的脚本调用：

| 用户表述 | 转换为 |
|----------|--------|
| "为XW_SUPF_5_1_2_4添加默认规则" | `--project XW_SUPF_5_1_2_4` |
| "用qos1和tc1创建默认规则" | `--qos-id qos1 --tc-id tc1` |
| "创建5qi=9的默认规则" | `--5qi 9` |
| "优先级设为50" | `--precedence 50` |
| "调测模式运行" | `--headed` |

## 完整链路

```
Step 1: 创建 QoS 模板
         → 5GC仪表: /sim_5gc/predfPolicy/qos/index
Step 2: 创建 Traffic Control
         → 5GC仪表: /sim_5gc/predfPolicy/trafficCtl/index
Step 3: 创建 PCC 规则（绑定 qos + tc）
         → 5GC仪表: /sim_5gc/predfPolicy/pcc/index
Step 4: 更新 sm_policy_default（pccRules 添加新PCC）
         → 5GC仪表: /sim_5gc/smpolicy/default/index
Step 5: PCF default_smpolicy → sm_policy_default
         → 5GC仪表: /sim_5gc/pcf/index
```

## 注意事项

- 同一工程可多次调用，每次创建不同的 PCC/QoS/TC
- sm_policy_default 如已存在会自动编辑追加，不会覆盖原有 pccRules
- 所有 xm-select 下拉使用 Playwright locator 点击 `.xm-option.show-icon`
- 提交前按 Escape 关闭下拉遮罩层
- 5qi 自动选择逻辑：优先从 [8,9,6,5,7,4,3,2,1] 中选未使用的值
