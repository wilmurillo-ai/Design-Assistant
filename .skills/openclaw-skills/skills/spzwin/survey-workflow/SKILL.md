---
name: survey-workflow
description: 组织健康度与员工敬业度调研全流程管理 Agent。功能包括：①员工名单批量导入问卷系统；②追加人员（增量导入）；③发送调研通知（支持自定义通知模板）；④追踪填答状态；⑤截止前自动催办；⑥拉取答卷数据（API直连）；⑦计算本批次基准均值；⑧按模板生成部门/集团诊断报告。问卷包含麦肯锡组织健康度37题（10维度）+ 北森敬业度29题（核心敬业度+驱动满意度+开放问题）。
skillcode: survey-workflow
version: 1.2.0
---

# survey-workflow Agent

## 概述

本 Agent 负责**组织健康度与员工敬业度联合调研**的全流程管理，从发送调研通知、追踪填答状态、自动催办，到数据分析与报告生成。

---

## 📋 问卷结构

### 麦肯锡组织健康度 (OHI) — 37题，10个维度

| 维度 | 题数 | 题目代码 |
|------|------|----------|
| 发展方向 | 3题 | Q_OHI_001~003 |
| 领导力 | 4题 | Q_OHI_004~007 |
| 工作氛围 | 4题 | Q_OHI_008~011 |
| 责任制度 | 3题 | Q_OHI_012~014 |
| 运营体系 | 5题 | Q_OHI_015~019 |
| 组织能力 | 4题 | Q_OHI_020~023 |
| 员工激励 | 4题 | Q_OHI_024~027 |
| 外部导向 | 4题 | Q_OHI_028~031 |
| 创新和学习 | 4题 | Q_OHI_032~035 |
| 赋能和心理安全 | 2题 | Q_OHI_036~037 |

### 北森敬业度及满意度 — 29题

**核心指标（敬业度8题）**
| 维度 | 题数 | 题目代码 |
|------|------|----------|
| 留任 | 2题 | Q_ENG_001~002 |
| 努力 | 2题 | Q_ENG_003~004 |
| 挑战 | 2题 | Q_ENG_005~006 |
| 组织赋能感 | 2题 | Q_ENG_007~008 |

**关键驱动因素（满意度19题）**
| 序号 | 维度 | 题目代码 | 题目内容 |
|------|------|----------|----------|
| 1 | 自主性 | Q_ENG_009 | 在工作中，我有充分的机会展现自己的能力所长 |
| 2 | 重视员工 | Q_ENG_010 | 公司在制定政策和制度的过程中，重视员工的意见和建议 |
| 3 | 职业发展 | Q_ENG_011 | 我相信我能在公司实现自己的职业目标 |
| 4 | 直接上级_沟通期望 | Q_ENG_012 | 我的直接上级能与我清晰沟通工作期望 |
| 5 | 直接上级_工作支持 | Q_ENG_013 | 我的直接上级能为我提供必要的工作支持 |
| 6 | 赞扬认可 | Q_ENG_014 | 当表现出色时，我能得到上级或同事们的肯定 |
| 7 | 薪酬福利 | Q_ENG_015 | 相对于我的付出，公司的薪酬福利水平是合理的 |
| 8 | 同事关系 | Q_ENG_016 | 同事间的沟通是坦诚的 |
| 9 | 挑战性 | Q_ENG_017 | 我的工作内容要求我不断提高自己的知识和技能 |
| 10 | 企业愿景 | Q_ENG_018 | 我清楚我的工作与公司发展目标间的关联 |
| 11 | 培训学习 | Q_ENG_019 | 公司鼓励员工进行持续性学习 |
| 12 | 绩效管理 | Q_ENG_020 | 我能定期收到清晰的工作反馈 |
| 13 | 沟通协作_团队合作 | Q_ENG_021 | 团队各成员能为了共同目标而紧密合作 |
| 14 | 工作资源 | Q_ENG_022 | 我能及时获取到工作所需的必要资源 |
| 15 | 工作生活平衡 | Q_ENG_023 | 在非工作时间也会积极参加各项工作，以保证工作的及时性 |
| 16 | 工作环境 | Q_ENG_024 | 公司提供了舒适的办公环境 |
| 17 | 创新 | Q_ENG_025 | 公司支持员工将新想法、新技能运用到工作中 |
| 18 | 推荐意愿 | Q_ENG_026 | 我愿意介绍正在求职的朋友加入公司 |
| 19 | 沟通协作_跨部门 | Q_ENG_027 | 公司鼓励跨部门间协作事务、共享信息与资源 |

**开放式问答（2题）**
- Q_OPEN_001: 您认为公司在未来发展中，最需要保持或加强的一项能力是什么？
- Q_OPEN_002: 您对公司的组织氛围或管理方式，还有哪些具体的改进建议？

---

## 核心能力

### 1. 导入活动名单（前置动作）
通过 `importSurveyTargets` 接口将员工名单批量导入问卷系统。

**API 信息**：
- 路径：`POST /questionnaire/admin/surveys/targets/import`
- 生产环境：`https://sg-al-cwork-web.mediportal.com.cn/open-api/questionnaire/admin/surveys/targets/import`
- 测试环境：`https://cwork-api-test.xgjktech.com.cn/open-api/questionnaire/admin/surveys/targets/import`

**请求参数**：
```json
{
  "surveyId": "问卷ID",
  "employeeIdList": ["员工ID列表"],
  "replace": false,
  "sourceType": "来源类型"
}
```

| 参数 | 说明 |
|------|------|
| `replace=true` | 全量覆盖（替换已有名单） |
| `replace=false` | 增量导入（追加到已有名单）**← 追加人员时使用此参数** |
| `employeeIdList` | 不可为空 |

**⚠️** 需要有效员工身份；导入完成后可衔接 `sendNotify` 发送通知。

---

### 1.1 追加人员流程（增量导入）

当发现调研名单有遗漏，需要追加人员时，按以下流程操作：

**步骤1：导入追加人员**
- 调用 `importSurveyTargets` 接口
- 设置 `replace=false`（关键参数，表示增量追加）
- 传入需要追加的员工ID列表

**步骤2：向追加人员发送通知**
- 调用 `sendNotify` 接口
- 传入新追加的员工ID列表
- 使用与初始通知相同或略作调整的通知文案

**完整示例**：
```python
import requests

BASE_URL = "https://cwork-api-test.xgjktech.com.cn/open-api"
HEADERS = {"access-token": "your_token"}

survey_id = "200003"
new_employees = [1512393075401125890, 1512393196394213378]  # 新追加的员工

# Step 1：导入追加人员（增量）
import_url = f"{BASE_URL}/questionnaire/admin/surveys/targets/import"
import_resp = requests.post(import_url, json={
    "surveyId": survey_id,
    "employeeIdList": new_employees,
    "replace": False,  # ← 关键：设置为 False 表示追加
    "sourceType": "手动追加"
}, headers=HEADERS)

if import_resp.json()["resultCode"] == 1:
    print("✅ 追加人员导入成功")

    # Step 2：向追加人员发送通知
    notify_url = f"{BASE_URL}/questionnaire/notify/send"
    notify_resp = requests.post(notify_url, json={
        "surveyId": survey_id,
        "employeeIds": new_employees,
        "notifyTitle": "关于开展集团总部2026年度组织健康度与员工敬业度联合调研的通知",
        "notifyMarkdown": "【追加通知】\n\n您已加入本次调研名单，请点击以下链接完成填答：\n\nhttps://cwork-web-test.xgjktech.com.cn/questionnaire-web/web/dist/#/survey?surveyId=200003"
    }, headers=HEADERS)

    if notify_resp.json()["resultCode"] == 1:
        print("✅ 追加人员通知发送成功")
        print(f"批次号：{notify_resp.json()['data']['batchNo']}")
        print(f"成功：{notify_resp.json()['data']['successCount']} 人")
```

**注意事项**：
- ⚠️ `replace=false` 是追加人员的关键参数，不能遗漏
- ⚠️ 追加后建议单独发送通知，并在文案中标注"追加通知"或"补发"
- ⚠️ 追加人员的填答截止时间与初始调研保持一致
- 💡 建议将追加记录归档到对应批次的 `input/notification_records.json` 中

---

### 2. 发送调研通知（发汇报）
通过 `sendNotify` 接口发送调研通知，支持自定义 Markdown 通知文案。

**API 信息**：
- 路径：`POST /questionnaire/notify/send`
- 生产环境：`https://sg-al-cwork-web.mediportal.com.cn/open-api/questionnaire/notify/send`
- 测试环境：`https://cwork-api-test.xgjktech.com.cn/open-api/questionnaire/notify/send`

**请求参数**：
```json
{
  "surveyId": "问卷ID",
  "employeeIds": ["员工ID列表"],
  "notifyMarkdown": "通知文案（支持 Markdown，不传则用系统默认文案）"
}
```

**典型调用流程**：
1. 调 `listUnsubmittedParticipants`（5.9）获取未通知人员
2. 调 `sendNotify`（5.5）发送通知
3. 记录发送结果

**响应结构**：
```json
{
  "resultCode": 1,
  "resultMsg": null,
  "data": {
    "batchNo": "批次号",
    "successCount": 3,
    "failCount": 0
  }
}
```

---

### 3. 追踪填答状态
通过 API 实时查询员工的提交状态，支持按部门/名单维度查看填答率。

**相关 API**：
| 操作 | 路径 | 说明 |
|------|------|------|
| 查已提交名单 | `GET /questionnaire/surveys/participants/submitted/list?surveyId={id}` | 活动名单口径-已提交 |
| 查未提交名单 | `GET /questionnaire/surveys/participants/unsubmitted/list?surveyId={id}` | 活动名单口径-未提交 |
| 查单个提交状态 | `GET /questionnaire/submission/status?surveyId={id}&employeeId={empId}` | 查询某员工是否已提交 |
| 分页提交列表 | `POST /questionnaire/submission/list` | 按部门筛选分页查看 |

---

### 4. 自动催办提醒
截止前定时检查未提交人员，向未提交对象发送催办通知。

**API 信息**：
- 路径：`GET /questionnaire/notify/pressure`
- 生产环境：`https://sg-al-cwork-web.mediportal.com.cn/open-api/questionnaire/notify/pressure`
- 测试环境：`https://cwork-api-test.xgjktech.com.cn/open-api/questionnaire/notify/pressure`

**请求参数**：
```
GET /questionnaire/notify/pressure?surveyId={surveyId}&employeeIds={id1,id2,...}
```

**典型催办闭环流程**：
1. 调 `listUnsubmittedParticipants`（5.9）→ 获取未提交人员名单
2. 调 `pressureNotify`（5.6）→ 对未提交人员发起催办
3. 调 `listSubmittedParticipants`（5.8）/ `listUnsubmittedParticipants`（5.9）→ 复盘本次催办效果

**⚠️** 催办接口虽为 GET，业务语义为写操作，请控制调用频率。

---

### 5. 拉取答卷数据
通过 `getSubmissionDetail` 接口拉取每位提交者的完整答卷数据。

**API 信息**：
- 路径：`GET /questionnaire/submission/detail`
- 生产环境：`https://sg-al-cwork-web.mediportal.com.cn/open-api/questionnaire/submission/detail`
- 测试环境：`https://cwork-api-test.xgjktech.com.cn/open-api/questionnaire/submission/detail`

**请求参数**：
```
GET /questionnaire/submission/detail?surveyId={surveyId}&submissionId={submissionId}
```

**返回字段**：
- `answers[]`：每题答题记录，含 `questionId`、`dimension`、`scoreValue`、`textAnswer`、`supplementaryText`
- `durationSec`：填答时长
- `submitTimeMillis`：提交时间

---

### 6. 统计分析
通过 `getStatistics` 接口获取整卷或分维度的评分统计。

**API 信息**：
- 路径：`GET /questionnaire/statistics`
- 生产环境：`https://sg-al-cwork-web.mediportal.com.cn/open-api/questionnaire/statistics`
- 测试环境：`https://cwork-api-test.xgjktech.com.cn/open-api/questionnaire/statistics`

**请求参数**：
```
GET /questionnaire/statistics?surveyId={surveyId}&groupBy={survey|dimension}
```

**`groupBy` 取值**：
- `survey`：获取整卷分值分布
- `dimension`：获取分维度分值分布

---

### 7. 生成分析报告
- 按模板输出结构化分析报告
- 包含数据概览、维度得分、问题诊断、改进建议

#### ⚠️ 报告模板强制要求（必须严格遵守）

报告分两类：**部门报告（7章）** 和 **集团报告（8章）**，两者章节结构不同，生成前必须确认报告类型并严格按对应模板输出。

---

##### 部门报告（7章）— 必须完整包含：

| 章节 | 必须包含的内容 |
|------|--------------|
| 第1章 | 核心结论速览：含 OHI 总分/敬业度总分/满意度总分 + 与总部平均分对比表；Top3 优势维度 + Top3 改进维度；与总部差距最大的维度 |
| 第2章 | 10维度得分概览表（含本部门得分/总部平均/差距/评级）+ Mermaid 雷达图（用 `mermaid` 格式，dept vs 总部平均两条曲线） |
| 第3章 | 核心敬业度4子维度（含总部对比）+ 驱动满意度全部20项维度（含总部对比），缺一不可 |
| 第4章 | 优势保持（详细说明）+ 改进方向（根因 + 措施 + 时间三要素必须齐全） |
| 第5章 | 情感分析表（负面/中性/正面数量和占比）+ 高频主题与典型原话表 |
| 第6章 | 部门负责人行动清单（行动项/负责人/完成时间/成功标准，四列必须完整） |
| 第7章 | HRBP支持资源 + 人力资源中心资源 + 建议下一步动作 |

---

##### 集团报告（8章）— 必须完整包含：

| 章节 | 必须包含的内容 |
|------|--------------|
| 第1章 | 核心结论速览：含 OHI 总分/敬业度总分；Top3 优势维度 + Top3 改进维度；员工最关注的3个问题；核心建议 |
| 第2章 | 调研概况与样本结构：填答概况表（发放数/回收数/填答率/平均时长）+ 样本分布（按部门/司龄/职级） |
| 第3章 | OHI分析：Mermaid雷达图（集团 vs 行业基准）+ 10维度得分详表（排名 + 评价）+ 题目级详细分析 |
| 第4章 | 敬业度分析：核心敬业度4子维度得分 + 驱动满意度全部维度 + 与敬业度相关性标注 + 结论 |
| 第5章 | 交叉分析：各部门得分对比表 + 管理者vs员工对比（如有数据）+ 不同司龄群体对比（如数据支持） |
| 第6章 | 开放式反馈分析：情感分析（正面/中性/负面占比）+ 高频主题词Top10 + 各主题提及频次与情感倾向表 |
| 第7章 | 核心发现与改进建议：优势领域 + 主要短板 + 根因 + 改进优先级排序表（P0/P1/P2，含责任主体/措施/预期效果/建议时间） |
| 第8章 | 后续行动计划：调研结果沟通会 + 部门级反馈工作坊 + 专项改进小组 + 季度脉冲调研计划 + 下一次年度调研计划 |

---

##### 常见错误（禁止再犯）：

- ❌ **部门报告**不写总部平均分对比 → 每表必须有"总部平均"列
- ❌ **部门报告**缺 Mermaid 雷达图 → 第2章必须包含
- ❌ **部门报告**满意度只写部分维度 → 20项全部列出
- ❌ **部门报告**改进建议缺时间/根因 → 根因+措施+时间三要素必须齐全
- ❌ **部门报告**缺行动清单第6章 → 行动项/负责人/时间/成功标准四列必须完整
- ❌ **集团报告**第5章缺各部门对比表 → 至少包含各部门 OHI + 敬业度得分对比
- ❌ **集团报告**第7章缺优先级排序 → P0/P1/P2 + 责任主体/措施/效果/时间缺一不可
- ❌ 生成前不确认报告类型 → 先确认是"部门报告"还是"集团报告"再开始写

#### 报告生成脚本（使用 Jinja2 模板）

报告生成采用「**模板 + 数据分离**」架构，确保报告结构不会在代码修改中丢失。

```
workspace-survey/
├── templates/
│   ├── dept_report.md.j2     ← 部门报告模板（Jinja2）
│   └── group_report.md.j2    ← 集团报告模板（Jinja2）
└── scripts/
    ├── generate_dept_reports_v4.py  ← 部门报告生成
    └── generate_group_report.py       ← 集团报告生成
```

**运行命令**：
```bash
# 部门报告（3份，每个部门一份）
python3 scripts/generate_dept_reports_v4.py --analysis-file data/分析结果.json

# 集团报告（1份）
python3 scripts/generate_group_report.py --analysis-file data/分析结果.json
```

**⚠️ 关键词提取规则（必须遵守）**：

开放式反馈的高频关键词必须是**「动词+名词」的完整搭配**，拒绝单独的形容词/动词。

✅ 合格关键词示例：`提高薪酬`、`减少加班`、`加强团队建设`、`改善工作环境`、`明确职业发展`

❌ 不合格关键词（会被过滤）：`改善`、`加强`、`提高`、`减少`（必须搭配名词才有意义）

实现逻辑见 `generate_group_report.py` 中 `_extract_keywords` 函数，核心约束：
1. 动作词列表 + 名词列表，通过子串匹配提取完整搭配
2. 按频次排序，长词覆盖短词
3. 单独的语气词/形容词不进入结果

**复验方法**：生成报告后执行 `grep -A15 "高频主题词" output/集团报告_*.md`，确认关键词均为有效搭配。

---

## 使用方式

### 方式一：脚本式（本地数据）
```bash
# 1. 员工匹配校验
python3 scripts/match_employees.py --excel-path data/员工名单.xlsx

# 2. 发送调研通知
python3 scripts/send_notification.py --employees data/匹配结果.json \
  --survey-url "https://xxx.com/survey" --deadline 2026-04-30

# 3. 追踪填答状态
python3 scripts/track_submissions.py --employees data/匹配结果.json \
  --data-file data/问卷数据.xlsx

# 4. 发送催办提醒
python3 scripts/send_reminder.py --employees data/匹配结果.json \
  --data-file data/问卷数据.xlsx --days-before 3

# 5. 加载问卷数据
python3 scripts/load_survey_data.py --data-file data/问卷数据.xlsx

# 6. 三层分析
python3 scripts/analyze_data.py --data-file data/问卷数据.xlsx --level all

# 7. 生成报告
python3 scripts/generate_report.py --data-file data/问卷数据.xlsx --level all
```

### 方式二：API 直连（实时数据）
直接调用问卷系统 Open API，无需本地 Excel 数据。

**推荐流程（通知 → 催办 → 复盘）**：
```python
import requests

BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api"
HEADERS = {"appKey": "你的appKey"}

survey_id = "问卷ID"

# Step 1：获取未提交人员名单
unsubmitted_url = f"{BASE_URL}/questionnaire/surveys/participants/unsubmitted/list"
resp = requests.get(unsubmitted_url, params={"surveyId": survey_id}, headers=HEADERS)
unsubmitted_list = resp.json()["data"]  # 人员列表

# Step 2：发送通知（发汇报）
notify_url = f"{BASE_URL}/questionnaire/notify/send"
requests.post(notify_url, json={
    "surveyId": survey_id,
    "employeeIds": [p["employeeId"] for p in unsubmitted_list]
}, headers=HEADERS)

# Step 3：催办未提交人员
pressure_url = f"{BASE_URL}/questionnaire/notify/pressure"
requests.get(pressure_url, params={
    "surveyId": survey_id,
    "employeeIds": ",".join([p["employeeId"] for p in unsubmitted_list])
}, headers=HEADERS)

# Step 4：复盘提交情况
submitted_url = f"{BASE_URL}/questionnaire/surveys/participants/submitted/list"
resp_sub = requests.get(submitted_url, params={"surveyId": survey_id}, headers=HEADERS)
submitted_list = resp_sub.json()["data"]
print(f"已提交: {len(submitted_list)} 人，未提交: {len(unsubmitted_list)} 人")
```

**API 索引速查**：
| 功能 | 方法 | 路径 | 小节 |
|------|------|------|------|
| 查询提交状态 | GET | `/questionnaire/submission/status` | 5.1 |
| 查询提交详情 | GET | `/questionnaire/submission/detail` | 5.2 |
| 提交列表分页 | POST | `/questionnaire/submission/list` | 5.3 |
| 评分统计 | GET | `/questionnaire/statistics` | 5.4 |
| **发送通知（发汇报）** | POST | `/questionnaire/notify/send` | **5.5** |
| **催办** | GET | `/questionnaire/notify/pressure` | **5.6** |
| 条件已提交名单 | POST | `/questionnaire/surveys/submitted` | 5.7 |
| **已提交人员列表** | GET | `/questionnaire/surveys/participants/submitted/list` | **5.8** |
| **未提交人员列表** | GET | `/questionnaire/surveys/participants/unsubmitted/list` | **5.9** |
| 导入活动名单 | POST | `/questionnaire/admin/surveys/targets/import` | 5.10 |

> 详细字段结构见 `docs/问卷系统API调用说明.md`

---

## 配置文件 (config/config.json)

关键配置项：
- `survey.deadline`: 调研截止日期
- `survey.min_response_rate`: 最低填答率要求 (85%)
- `survey.survey_url`: 调研H5页面链接
- `reminder.schedule`: 催办提醒规则

---

## 数据文件格式

### 员工名单 Excel
| 工号 | 姓名 | 部门 | 中心 |
|------|------|------|------|
| 001 | 张三 | 人力资源部 | 专业责任中心 |

### 问卷数据 Excel
| 工号 | 姓名 | 部门 | 中心 | Q_OHI_001 | Q_OHI_002 | ... | Q_ENG_001 | ... | 提交时间 |
|------|------|------|------|-----------|-----------|-----|-----------|-----|----------|

---

## 批次归档规范（强制执行）

每次调研视为一个独立批次，**所有操作必须归档到对应批次目录**，不得散落在 `latest/` 或其他位置。

### 目录结构规范

```
output/archive/{surveyId}/{日期}/
├── input/
│   ├── employee_list.json       # 本批次导入的员工名单
│   └── notification_records.json # 发通知/催办记录（按时间顺序）
├── data/
│   ├── submissions/             # 每位提交者的原始答卷（一人一个文件）
│   │   └── {employeeId}_{姓名}.json
│   └── benchmark.json           # 本批次全体均值（生成报告前必须先有）
└── reports/
    ├── 集团报告_{日期}.md
    └── {部门名}_诊断报告_{日期}.md
```

### 关键规则

1. **先建档，再操作**：每个新批次开始时，先创建目录结构
2. **发名单导入 → 写入 `input/employee_list.json`**
3. **发通知/催办 → 追加到 `input/notification_records.json`**
4. **拉取答卷数据 → 存入 `data/submissions/{employeeId}_{姓名}.json`**
5. **计算均值 → 生成 `data/benchmark.json`**（所有报告对比基准的唯一来源）
6. **生成报告 → 存入 `reports/`**，同时同步到 `output/latest/`
7. **报告中的对比值**：统一使用"**本批次全体均值**"，不得写"总部平均"（因为只有一批数据时这就是本批均值）

### benchmark.json 必须字段

```json
{
  "surveyId": "问卷ID",
  "surveyDate": "YYYY-MM-DD",
  "totalEmployees": 3,
  "totalSubmissions": 1,
  "responseRate": 0.333,
  "ohi_avg": 3.45,
  "engagement_avg": 3.62,
  "satisfaction_avg": 3.07,
  "ohi_dimensions": { "发展方向": 3.00, ... },
  "engagement_core": { "留任": 3.00, ... },
  "satisfaction": { "薪酬福利": 3.00, ... }
}
```

### 常见错误（禁止再犯）

- ❌ 报告对比值写"总部平均" → 统一写"本批次全体均值"
- ❌ 数据散落在 latest/ 不归档 → 操作后立即写入对应批次目录
- ❌ 不生成 benchmark.json 就出报告 → benchmark 是所有报告的对比基准
- ❌ 多人数据混在一个文件 → 一人一个 JSON 文件，方便独立引用

## 认证说明（重要，必须阅读）

**🏭 默认使用生产环境**，除非明确指定测试环境。

生产环境调用问卷系统 API 时，**必须使用 APP Key 换取 access-token**，不能直接用 token。

### 认证流程

```
XG_BIZ_API_KEY (APP Key)
        ↓  cms-auth-skills/login.py
  access-token
        ↓
  问卷系统 API 请求头
```

### 认证命令

```bash
python3 skills/cms-auth-skills/scripts/auth/login.py \
  --ensure \
  --app-key "$XG_BIZ_API_KEY"
```

### QuestionnaireClient 自动鉴权

`scripts/utils/questionnaire_client.py` 已内置自动换 token 逻辑：
- 初始化时若有 `XG_BIZ_API_KEY` 但无 `access_token`，自动调用 `login.py` 换取 token
- 脚本调用时只需指定 `base_url` 为生产地址即可，无需手动传 token

```python
from questionnaire_client import QuestionnaireClient

# 生产环境（自动用 XG_BIZ_API_KEY 换 token）
client = QuestionnaireClient(
    base_url="https://sg-al-cwork-web.mediportal.com.cn"
)

# 发送通知
client.send_notify(survey_id=200003, notify_title="...", ...)
```

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `401: 缺少访问凭证` | 直接用 app_key 当 token | 用 login.py 换成 access-token |
| `401: Token校验失败` | token 已过期或用错了 | 重新用 login.py 换取新 token |
| `活动名单为空` | 未导入名单 | 先调 `import_targets` 再发通知 |

## 依赖

- Python 3.9+ (标准库)
- CWork API (通过 cms-auth-skills 鉴权)
- 问卷系统 Open API（路径 `/questionnaire/**`，见 `docs/问卷系统API调用说明.md`）

---

## 维护说明

- 配置文件：`workspace-survey/config/config.json`（权威版本，含题目原文、催办模板、数据质量规则、AI分析规则）
- 问卷维度配置已内置到 config.json 中
- 截止日期等参数可随时修改配置文件调整
