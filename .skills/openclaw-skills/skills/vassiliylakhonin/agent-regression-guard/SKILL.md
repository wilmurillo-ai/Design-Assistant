---
name: agent-regression-check
description: Evaluate whether an agent change introduced regressions by comparing matched before vs after case results. Use when reviewing prompt updates, model switches, tool integrations, retrieval changes, hotfixes, or release readiness. Also covers deterministic release gates, failure clustering, confidence scoring, and JSON-ready verdicts.
user-invocable: true
metadata: {"openclaw":{"emoji":"🧪","os":["linux","darwin","win32"]}}
---

# Agent Regression Check

Evaluate whether an agent change introduced regressions.

Compare matched before vs after case results, score degradation with a
deterministic rubric, apply release gates, and return one verdict:

```text
go
conditional_go
no_go
rollback
This is an offline regression-check skill. It does not replace
production monitoring, live experiments, or telemetry.

When to Use
Use this skill when the user asks:

Did this update break anything

Compare before and after

Is this safe to deploy

Check regressions after a model change

Validate prompt, retrieval, tool, or orchestration updates

Verify a hotfix before release

Decide whether to roll back

When Not to Use
Do not use this skill when:

there is no comparable before/after evidence

case sets cannot be matched reliably

the suite is too small for a release decision

online experimentation is required

the user wants brainstorming rather than deterministic assessment

If evidence quality is weak, say so explicitly and lower confidence.

Modes
text
regcheck [change summary]
regcheck --strict [change summary]
regcheck --high-risk [change summary]
regcheck --json [change summary]
regcheck --verdict-only [change summary]
If no mode is specified, use the default evaluation flow.

Inputs
Required whenever possible:

text
change_summary
before_cases
after_cases
risk_level   | low / medium / high
Preferred payload:

json
{
  "change_summary": "Switched model and simplified system prompt",
  "risk_level": "medium",
  "cases": [
    {
      "id": "case_001",
      "task_type": "faq",
      "critical": true,
      "input": "How do I reset my password?",
      "expected_behavior": "Provides reset steps and fallback.",
      "before_output": "...",
      "after_output": "...",
      "before_tools": [],
      "after_tools": []
    }
  ]
}
Optional:

text
suite_manifest
thresholds
tool_traces
strict_mode
output_path
Matching Rules
Match cases by stable id.

If IDs do not match:

text
- flag suite inconsistency
- lower confidence
- do not align by position unless explicitly requested
Scoring Rubric
Score each case across four dimensions.

Correctness

text
2 = correct
1 = partially correct
0 = incorrect
Relevance

text
2 = fully relevant
1 = somewhat relevant
0 = off-target
Actionability

text
2 = actionable
1 = partially actionable
0 = not actionable
Tool Reliability

text
2 = correct tool usage
1 = minor tool issue
0 = tool failure
Case Outcomes
pass

text
correctness >= 2
relevance >= 1
actionability >= 1
tool_reliability >= 1
soft_fail

text
usable answer, but quality degraded
fail

text
- correctness = 0
- missing required fallback
- tool failure
- after is materially worse than before
Any fail on a critical case is high severity.

Aggregated Metrics
Always compute:

text
overall_pass_rate
critical_pass_rate
soft_fail_rate
tool_reliability_rate
average_correctness
average_relevance
average_actionability
Also compute deltas:

text
overall_pass_rate_delta
critical_pass_rate_delta
tool_reliability_delta
Never hide negative deltas.

Release Gates
Low Risk

text
overall_pass_rate >= 0.90
critical_pass_rate >= 0.95
Medium Risk

text
overall_pass_rate >= 0.95
critical_pass_rate = 1.00
tool_reliability_rate >= 0.95
High Risk

text
overall_pass_rate >= 0.98
critical_pass_rate = 1.00
tool_reliability_rate >= 0.98
human review recommended
Verdict Rules
Return exactly one verdict.

go

text
All gates pass.
conditional_go

text
Minor issues exist, but no critical regressions block release.
no_go

text
Release gates fail. Fixes required before deployment.
rollback

text
Critical regressions or material degradation on critical paths.
Failure Clustering
Group regressions by likely cause.

Example clusters:

text
instruction_following_drift
factuality_drop
retrieval_miss
tool_call_failure
format_noncompliance
missing_fallback
hallucinated_capability
For each cluster include:

text
- name
- severity
- affected cases
- likely cause
- suggested fix direction
Anti-Gaming Rules
Flag explicitly:

text
- different case sets before vs after
- missing critical cases
- incomplete tool traces
- changed expectations
- too few cases for a release decision
If detected:

text
- lower confidence
- explain the limitation
- avoid overconfident verdicts
Confidence
Return one level:

text
high
medium
low
Base confidence on:

text
- suite size
- representativeness
- matching quality
- tool trace completeness
- expectation consistency
Workflow
Step 1 — Validate Evidence

Check:

text
- suite completeness
- matching IDs
- before/after comparability
- critical case coverage
- relevant tool traces
Step 2 — Score Cases

For each case evaluate:

text
- correctness
- relevance
- actionability
- tool reliability
- before vs after delta
- severity if degraded
Step 3 — Compute Metrics

Aggregate:

text
- pass rates
- averages
- critical-case outcomes
- tool reliability
- deltas
Step 4 — Cluster Regressions

Group failures by likely mechanism, not only surface symptom.

Step 5 — Apply Release Gates

Use the declared risk_level, or default to medium if not specified.

Step 6 — Return Verdict

Always return:

text
- executive summary
- scorecard
- top regressions
- failure clusters
- verdict
- recommended fixes
- confidence
Output Template
text
## Executive Summary
[Short before/after assessment]

## Suite Summary
- Total cases:
- Critical cases:
- Matching quality:

## Scorecard
- Overall pass rate:
- Critical pass rate:
- Soft-fail rate:
- Tool reliability rate:
- Average correctness:
- Average relevance:
- Average actionability:

## Deltas
- Overall pass rate delta:
- Critical pass rate delta:
- Tool reliability delta:

## Top Regressions
- case_id:
  - what worsened
  - severity
  - likely cause

## Failure Clusters
### cluster_name
- severity:
- affected cases:
- likely cause:
- suggested fix:

## Verdict
go | conditional_go | no_go | rollback

## Recommended Fixes
- Fix 1
- Fix 2
- Fix 3

## Confidence
high | medium | low

## Limitations
- limitation 1
- limitation 2
JSON Output
json
{
  "change_summary": "",
  "risk_level": "medium",
  "confidence": "medium",
  "suite_summary": {
    "total_cases": 0,
    "critical_cases": 0,
    "matching_quality": "good"
  },
  "scorecard": {
    "overall_pass_rate": 0.0,
    "critical_pass_rate": 0.0,
    "soft_fail_rate": 0.0,
    "tool_reliability_rate": 0.0,
    "average_correctness": 0.0,
    "average_relevance": 0.0,
    "average_actionability": 0.0
  },
  "deltas": {
    "overall_pass_rate_delta": 0.0,
    "critical_pass_rate_delta": 0.0,
    "tool_reliability_delta": 0.0
  },
  "verdict": "no_go",
  "top_regressions": [
    {
      "case_id": "",
      "summary": "",
      "severity": "high"
    }
  ],
  "failure_clusters": [
    {
      "name": "",
      "severity": "medium",
      "affected_cases": [],
      "likely_cause": "",
      "suggested_fix_direction": ""
    }
  ],
  "recommended_fixes": [],
  "limitations": []
}
Limits
This skill does not:

guarantee production improvement

replace monitoring or experiments

infer exact user impact from a small suite

compensate for weak or mismatched test data

High-risk changes should still involve human review.

Tips
Keep stable case IDs across releases.

Mark critical cases before comparison.

Include expected behavior, not only raw outputs.

Save tool traces when tool reliability matters.

Use medium risk if risk is unclear.

Negative deltas matter even when absolute scores look acceptable.

Re-run with the same suite after fixes to preserve comparability.

Separate regression checking from redesign discussion.

Author
Vassiliy Lakhonin