# 训练计划框架（Training Framework）

定义各级别训练天数、时长、技能顺序和休息规则。

## 单板训练计划

```yaml
training_framework_snowboard:
  level_0:
    total_days: 1
    daily_hours: 2.5
    skill_sequence:
      - skill_ids: [L0-SB-02, L0-SB-03]
        duration_minutes: 45
        weight: 0.30
      - skill_ids: [L0-SB-03]
        duration_minutes: 30
        weight: 0.20
      - skill_ids: [L0-SB-04, L0-SB-05]
        duration_minutes: 35
        weight: 0.23
    rest_rule: 第一天不要超过 3 小时肌肉会疲劳
    day1_focus: [L0-SB-02, L0-SB-03, L0-SB-04, L0-SB-05]

  level_1:
    total_days: 3
    daily_hours: 2.2
    skill_sequence:
      - skill_ids: [L1-SB-01, L1-SB-02]
        duration_hours: 2
        weight: 0.30
        day: 1
      - skill_ids: [L1-SB-03]
        duration_hours: 2
        weight: 0.30
        day: 2
      - skill_ids: [L1-SB-04, L1-SB-05]
        duration_hours: 2.5
        weight: 0.38
        day: 3
    rest_rule: 每天练习 2-3 小时不要超过肌肉疲劳会影响学习
    day1_focus: [L1-SB-01, L1-SB-02]

  level_2:
    total_days: 5
    daily_hours: 2.7
    skill_sequence:
      - skill_ids: [L2-SB-01, L2-SB-02]
        duration_hours: 2.5
        weight: 0.18
        day: 1
      - skill_ids: [L2-SB-03, L2-SB-06]
        duration_hours: 2.5
        weight: 0.18
        day: 2
      - skill_ids: [L2-SB-04, L2-SB-05]
        duration_hours: 2.5
        weight: 0.18
        day: 3
      - skill_ids: [L2-SB-07]
        duration_hours: 3
        weight: 0.22
        day: 4
      - skill_ids: [L2-SB-08, L2-SB-09]
        duration_hours: 3
        weight: 0.22
        day: 5
    rest_rule: 每天 2.5-3 小时第 4-5 天可适当延长到 3 小时
    day1_focus: [L2-SB-01, L2-SB-02]

  level_3:
    is_continuous: true
    style_tracks:
      carving:
        skills: [L3-SB-04, L3-SB-05, L3-SB-06]
        description: 刻滑路线：高立刃刻滑、动态刻滑、短弯刻滑
      freestyle:
        skills: [L3-SB-07, L3-SB-08, L3-SB-09]
        description: 公园路线：中跳、360 度旋转、道具进阶
      powder:
        skills: [L3-SB-10, L3-SB-11, L3-SB-12]
        description: 野雪路线：粉雪进阶、陡坡滑行、道外安全
    rest_rule: 持续精进级别建议每年雪季设定一个技术目标雪季前 1-2 天回顾 Level 2 核心技能
```

## 双板训练计划

```yaml
training_framework_ski:
  level_0:
    total_days: 1
    daily_hours: 2.5
    skill_sequence:
      - skill_id: L0-SK-01
        weight: 0.15
      - skill_id: L0-SK-02
        weight: 0.15
      - skill_id: L0-SK-03
        weight: 0.20
      - skill_id: L0-SK-04
        weight: 0.15
      - skill_id: L0-SK-05
        weight: 0.15
    rest_rule: 第一天不要超过 3 小时肌肉会疲劳
    day1_focus: [L0-SK-01, L0-SK-02, L0-SK-03, L0-SK-04, L0-SK-05]

  level_1:
    total_days: 3
    daily_hours: 2.0
    skill_sequence:
      - skill_id: L1-SK-01
        weight: 0.18
      - skill_id: L1-SK-02
        weight: 0.18
      - skill_id: L1-SK-03
        weight: 0.18
      - skill_id: L1-SK-04
        weight: 0.18
      - skill_id: L1-SK-05
        weight: 0.14
      - skill_id: L1-SK-06
        weight: 0.14
    rest_rule: 每天练习 2-3 小时不要超过肌肉疲劳会影响学习
    day1_focus: [L1-SK-01, L1-SK-02]

  level_2:
    total_days: 5
    daily_hours: 2.5
    skill_sequence:
      - skill_id: L2-SK-01
        weight: 0.15
      - skill_id: L2-SK-02
        weight: 0.12
      - skill_id: L2-SK-03
        weight: 0.10
      - skill_id: L2-SK-04
        weight: 0.10
      - skill_id: L2-SK-05
        weight: 0.12
      - skill_id: L2-SK-06
        weight: 0.10
      - skill_id: L2-SK-07
        weight: 0.12
      - skill_id: L2-SK-08
        weight: 0.08
      - skill_id: L2-SK-09
        weight: 0.06
      - skill_id: L2-SK-10
        weight: 0.05
    rest_rule: 每天 2.5-3 小时避免肌肉疲劳
    day1_focus: [L2-SK-01, L2-SK-02]

  level_3:
    is_continuous: true
    style_tracks:
      carving:
        skills: [L3-SK-05, L3-SK-06, L3-SK-07]
        description: 卡宾路线：高立刃卡宾、动态卡宾、短弯卡宾
      mogul:
        skills: [L3-SK-08, L3-SK-09, L3-SK-10]
        description: 蘑菇路线：蘑菇节奏、吸收技术进阶、连续蘑菇道
      powder:
        skills: [L3-SK-11, L3-SK-12, L3-SK-13]
        description: 野雪路线：粉雪进阶、陡坡滑行、道外安全
    rest_rule: 持续精进每雪季 10 天以上每年雪季前 1-2 天回顾 Level 2 核心技能
```
