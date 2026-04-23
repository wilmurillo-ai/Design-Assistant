---
name: test-skill
description: A specialized framework for performance benchmarking, context continuity, and edge-case validation.
author: test-skill
---

# SKILL.md: Testing & Validation Framework

## 1. Load & Stress Testing (`load-test`)
This module evaluates the model's stability and accuracy under heavy token loads or high-complexity computational requests.

* **Massive Input Processing:** Tests "needle-in-a-haystack" retrieval by processing large datasets and extracting specific, isolated facts.
* **High-Frequency Reasoning:** Executes multi-step logical chains (e.g., 10+ sequential reasoning steps) to monitor for cumulative logic drift.
* **Concurrent Tasking:** Requests multiple divergent outputs (e.g., a code snippet, a creative story, and a data table) in a single turn to test instruction following.

## 2. Context & Memory Sharing (`shared-context-test`)
This module validates the ability to maintain state and utilize shared information across a long-form conversation.

* **State Persistence:** Establishes specific variables (e.g., `session_id`, `user_preferences`, `global_constants`) at the start and verifies their application in later turns.
* **Multi-Source Integration:** Analyzes the relationship between multiple provided documents or tool outputs to ensure cross-pollination of data.
* **Contextual Threading:** Tests if the model can resume a complex logic task after an intentional "distraction" or unrelated query.

## 3. Capability Boundary Testing (`edge-case-test`)
Designed to identify the functional limits and the "breaking points" of the skill logic.

* **Instruction Conflict Resolution:** Provides contradictory constraints to evaluate the model's prioritization logic and clarity of refusal/adjustment.
* **Formatting Rigidity:** Demands complex, nested output formats (e.g., strict JSON, multi-variable LaTeX, or deep-nested Markdown) to check for syntax integrity.
* **Adversarial Robustness:** Inputs non-sequiturs, gibberish, or ambiguous prompts to verify that the skill maintains a grounded, helpful persona without hallucinating.

## 4. Validation Matrix

| Test ID | Category | Objective | Success Criteria |
| :--- | :--- | :--- | :--- |
| **LT-01** | Load | 50-step logic chain | Zero hallucination in final result |
| **SC-01** | Sharing | Variable recall (>10 turns) | Precise retrieval of Turn 1 parameters |
| **EC-01** | Edge | Nested syntax rendering | 100% valid code/LaTeX/Markdown syntax |
| **EC-02** | Edge | Contradictory constraints | Logical reconciliation or proactive clarification |

---

## 5. Execution Protocol
To initiate a test sequence, use the following command structure:

> **Command:** `INIT_TEST [Test ID]`
> **Parameters:** Define any specific variables or data sets to be injected into the test environment.