---
name: multi-agent-orchestration
description: Design and implement production-ready multi-agent systems with proven orchestration patterns (sequential, concurrent, hierarchical, group chat, handoff, event-driven). Use when building coordinated AI systems, choosing between centralized/decentralized coordination, implementing agent communication protocols, managing agent lifecycles, or scaling beyond single-agent architectures. Covers role specialization, state management, failure recovery, and observability.
---

# Multi-Agent Orchestration

Design coordinated multi-agent systems using battle-tested orchestration patterns. This skill provides architectural guidance for moving from single-agent to multi-agent systems, choosing coordination patterns, and implementing production-grade orchestration layers.

## When NOT to Use Multi-Agent

Start with the simplest approach that reliably meets requirements:

| Level | When to Use | Example |
|-------|-------------|---------|
| **Direct model call** | Single-step tasks (classification, translation, summarization) | "Summarize this article" |
| **Single agent + tools** | Varied queries within one domain requiring dynamic tool use | Order lookup with API calls |
| **Multi-agent** | Cross-domain problems, security boundaries, or parallel specialization | Financial underwriting (data extraction, scoring, compliance, risk) |

**Rule: Only add multi-agent complexity when a single agent can't reliably handle the task due to:**
- Prompt complexity or tool overload
- Security/permission isolation requirements
- Parallelization benefits that outweigh coordination overhead

## Core Orchestration Patterns

### 1. Sequential (Pipeline)

Chain agents in predefined linear order. Each agent processes the previous agent's output.

**When to use:**
- Clear linear dependencies between stages
- Progressive refinement workflows (draft → review → polish)
- Data transformation pipelines

**When to avoid:**
- Stages can run in parallel
- Workflow requires backtracking or iteration
- Dynamic routing based on intermediate results

**Example:** Contract generation pipeline
```
Template Selection → Clause Customization → Regulatory Compliance → Risk Assessment
```

**Implementation pattern:**
```python
# Each agent receives prior agent's output
result = template_agent(requirements)
result = customization_agent(result, client_specs)
result = compliance_agent(result, jurisdiction)
final = risk_agent(result)
```

### 2. Concurrent (Parallel)

Run independent agents simultaneously, aggregate results.

**When to use:**
- Tasks are embarrassingly parallel
- No shared state dependencies
- Latency reduction is critical

**When to avoid:**
- Agents need to collaborate or share context
- Tasks have sequential dependencies
- Cost of spawning multiple agents outweighs speed gains

**Example:** Multi-source research aggregation
```
Web Search ⎤
News API    ⎥─→ Aggregator → Summary
Academic DB ⎦
```

### 3. Hierarchical (Supervisor)

Manager agent decomposes tasks, assigns to worker agents, aggregates results.

**When to use:**
- Complex problems requiring task decomposition
- Dynamic work distribution
- Clear separation between planning and execution

**When to avoid:**
- Single point of failure is unacceptable
- Manager becomes bottleneck
- Coordination overhead exceeds value

**Example:** DevOps incident response
```
Incident Manager
├─→ Log Analyzer
├─→ Metrics Analyzer
├─→ Dependency Checker
└─→ Remediation Planner
```

**Implementation notes:**
- Manager agent must handle task decomposition
- Workers report back with structured results
- Manager synthesizes final response

### 4. Group Chat (Collaborative)

Multiple agents collaborate in shared conversation thread.

**When to use:**
- Problem requires diverse perspectives
- Agents validate/critique each other's work
- Emergent solutions from discussion

**When to avoid:**
- Conversation becomes circular (implement turn limits)
- Clear workflow exists (use sequential instead)
- Deterministic output required

**Example:** Code review committee
```
Developer Agent ←→ Security Reviewer ←→ Performance Analyst ←→ Test Engineer
```

**Implementation pattern:**
- Selector agent determines who speaks next
- Shared message history
- Termination condition (consensus or turn limit)

### 5. Handoff (Delegation)

Agent decides dynamically when to delegate to specialized agents.

**When to use:**
- Routing logic is complex or contextual
- Different expertise domains
- Escalation workflows

**When to avoid:**
- Routing is deterministic (use sequential)
- Single agent can handle all cases

**Example:** Customer support
```
Triage Agent → [Technical Support | Billing | Cancellation] → Escalation Agent
```

### 6. Event-Driven (Reactive)

Agents respond to events via publish-subscribe or message bus.

**When to use:**
- Asynchronous workflows
- Decoupled agent communication
- Real-time reactive systems

**When to avoid:**
- Debugging asynchronous flows is prohibitive
- Synchronous coordination is simpler and sufficient

**Example:** CI/CD pipeline
```
Code Push → Build Agent → [Test Agent, Security Scanner, Docs Generator] → Deploy Agent
```

## Coordination Models

### Centralized (Supervisor Pattern)

**Pros:**
- Clear control and simplified management
- Easy to reason about workflow
- Centralized observability

**Cons:**
- Single point of failure
- Manager can become bottleneck
- Scalability limits

**Use when:** Control and visibility matter more than resilience.

### Decentralized (Peer-to-Peer)

**Pros:**
- No single point of failure
- Scales horizontally
- Robust to individual agent failures

**Cons:**
- Complex coordination logic
- Harder to debug
- Emergent behaviors may be unpredictable

**Use when:** Resilience and scale matter more than simplicity.

### Hierarchical (Tiered)

**Pros:**
- Balances control with flexibility
- Natural division of planning vs execution
- Scales better than centralized

**Cons:**
- More complex than centralized
- Still has failure points at higher tiers

**Use when:** Need both coordination and scale.

## Agent Specialization Roles

### Worker Agents
Execute well-defined tasks (RAG retrieval, data extraction, scoring).

**Stateless:** Handle each request independently.
**Stateful:** Track progress across multi-step workflows.

### Service Agents
Provide shared utilities (QA, compliance, diagnostics, healing).

**Quality Assurance:** Verify outputs, cross-check compliance.
**Diagnostic:** Trace issues, generate error reports.
**Healing:** Retry failures, reset workflow states.
**Upgrade Scheduler:** Manage version transitions seamlessly.

### Support Agents
Meta-level oversight (monitoring, analytics, data management).

**Monitoring:** Track latency, detect drift, visualize health.
**Analytics:** Evaluate patterns, identify anomalies.
**Data Agents:** Refresh datasets, maintain currency.

## State Management

**Short-term (scratchpad):** Shared workspace for agent collaboration within a session.
**Long-term (persistent):** Operational status, configuration, history across sessions.
**Checkpointing:** Save state at key points for recovery and resume.

**Conflict resolution strategies:**
- Last-write-wins (simple, risks data loss)
- Optimistic locking (version checks before write)
- Consensus protocols (multiple agents agree on state)

## Communication Protocols

### Standardized Message Formats

**FIPA-ACL / KQML:** Structured agent communication languages.
**Model Context Protocol (MCP):** Standardizes tool/context access.
**Agent-to-Agent (A2A):** Governs peer coordination, negotiation, delegation.

### Communication Patterns

**Direct (message passing):** Agent → Agent explicit messages.
**Indirect (shared environment):** Agents modify/read shared state.
**Broadcast (pub-sub):** Event bus for decoupled async communication.

**Avoid communication overload:** Excessive messaging inflates latency and saturates channels. Use batching, filtering, and rate limiting.

## Orchestration Layer Components

### Planning Unit
- Decomposes high-level objectives into tasks
- Assigns tasks to specialized agents
- Defines execution order

### Policy Unit
- Embeds domain and governance constraints
- Defines "how" tasks are performed
- Coordinates with control unit for enforcement

### Execution Unit
- Manages agent lifecycle (init, execute, validate, complete)
- Collects telemetry via support agents
- Ensures smooth operation of worker agents

### Control Unit
- Receives telemetry from execution unit
- Delegates remediation to service agents
- Manages context switches and fallbacks
- Enforces policies throughout execution

## Operational Resilience

### Failure Handling

**Automatic retries:** Transient failure recovery with exponential backoff.
**Fallback agents:** Backup agents when primary fails.
**Circuit breakers:** Stop cascading failures by halting calls to failing services.
**Graceful degradation:** Partial results when full completion impossible.

### Observability

**Distributed tracing (OpenTelemetry):** Track agent interactions, message passing, tool execution.
**State transition logs:** Visualize agent connections, identify stalls/hallucinations.
**Cost tracking:** Monitor per-agent token usage and API costs.
**Latency monitoring:** Detect bottlenecks in orchestration layer.

### Self-Healing

**Anomaly detection:** Identify drift, degraded performance, or stuck agents.
**Automated recovery:** Restart failed agents, reset workflow states.
**Health checks:** Periodic validation of agent availability and correctness.

## Production Considerations

### Agent Registry
Centralized directory storing:
- Agent capabilities and endpoints
- Version metadata
- Health status
- Discovery information

Enables dynamic agent onboarding without hard-coded dependencies.

### Intelligent Routing
- Classifier component analyzes intent
- Routes requests to best-suited specialist
- Maintains routing metrics for optimization

### Security Boundaries
- Permission isolation per agent
- Audit trails for compliance
- Least-privilege access to tools/data
- Separate security contexts when agents access sensitive data

### Cost Control
- Token usage limits per agent
- Budget allocation across agent pool
- Automatic throttling when approaching limits
- Per-agent cost attribution for optimization

## Framework Selection Criteria

When evaluating multi-agent frameworks, prioritize:

1. **Lifecycle management:** Agent registry, discovery, versioning
2. **Orchestration patterns:** Native support for needed patterns (sequential, hierarchical, group chat)
3. **Observability:** OpenTelemetry integration, state visualization
4. **Resilience:** Retries, fallbacks, circuit breakers, health checks
5. **Communication:** Support for MCP, A2A, or similar standards
6. **Governance:** Policy enforcement, audit trails, permission models

**Leading frameworks (2026):**
- **LangGraph:** State visualization, cyclic workflows, strong observability
- **CrewAI:** Role-based agents, hierarchical orchestration
- **AutoGen (AG2 v0.4):** Group chat coordination, selector agents
- **Semantic Kernel:** Intent plane routing, enterprise integration

## Common Anti-Patterns

❌ **Over-generalized single agent:** One agent trying to handle all domains → domain overload, context degradation.

❌ **Excessive agent decomposition:** Too many agents → coordination overhead exceeds value.

❌ **Circular group chats:** Agents debating without convergence → implement turn limits and consensus checks.

❌ **Ignoring failure modes:** No retries, no fallbacks → cascading failures.

❌ **Communication storms:** Excessive messaging → implement throttling, batching, or indirect communication.

❌ **Tight coupling:** Agents directly reference others → use registry-based discovery and standardized protocols.

## Decision Tree

```
Is this a single-step task?
├─ Yes → Use direct model call
└─ No
   ├─ Can one agent with tools handle it?
   │  ├─ Yes → Use single agent + tools
   │  └─ No
   │     ├─ Are stages linear with clear dependencies?
   │     │  └─ Yes → Sequential pattern
   │     ├─ Are tasks independent and parallelizable?
   │     │  └─ Yes → Concurrent pattern
   │     ├─ Does it need task decomposition + work distribution?
   │     │  └─ Yes → Hierarchical pattern
   │     ├─ Does it benefit from collaborative discussion?
   │     │  └─ Yes → Group chat pattern
   │     ├─ Does routing depend on runtime context?
   │     │  └─ Yes → Handoff pattern
   │     └─ Is it asynchronous/event-driven?
   │        └─ Yes → Event-driven pattern
```

## Implementation Checklist

- [ ] Justify multi-agent complexity (single agent inadequate?)
- [ ] Choose orchestration pattern based on task characteristics
- [ ] Define agent roles and specializations
- [ ] Select coordination model (centralized, decentralized, hierarchical)
- [ ] Design state management strategy (short-term, long-term, checkpointing)
- [ ] Choose communication protocol (MCP, A2A, custom)
- [ ] Implement orchestration layer (planning, policy, execution, control)
- [ ] Add observability (tracing, logging, metrics)
- [ ] Design failure handling (retries, fallbacks, circuit breakers)
- [ ] Test coordination logic with edge cases
- [ ] Monitor costs and latency in production

## References

For detailed architectural patterns and real-world implementations, see:
- [references/patterns.md](references/patterns.md) - Deep dive into each pattern with code examples
- [references/case-studies.md](references/case-studies.md) - Production deployments and lessons learned
- [references/protocols.md](references/protocols.md) - MCP and A2A protocol specifications
