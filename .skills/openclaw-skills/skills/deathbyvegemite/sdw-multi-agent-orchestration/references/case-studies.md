# Production Case Studies

Real-world multi-agent deployments with measured impact, lessons learned, and architectural insights.

## 1. DevOps Incident Response (100% vs 1.7% Actionable Rate)

**Company:** Enterprise SaaS provider (5000+ servers)  
**Challenge:** Manual incident response taking 2-4 hours, high MTTR, engineer burnout  
**Solution:** Multi-agent orchestration for automated diagnosis and remediation  

### Architecture

**Pattern:** Hierarchical + Concurrent

```
Incident Manager (Supervisor)
├─→ Log Aggregator (Worker)
├─→ Metrics Analyzer (Worker)
├─→ Dependency Mapper (Worker)
└─→ Remediation Planner (Worker)
     ↓
[Rollback Agent | Config Agent | Scale Agent] (Concurrent)
     ↓
Verification Agent
```

### Agent Specializations

**Incident Manager:**
- Receives alert, classifies severity
- Decomposes investigation into parallel sub-tasks
- Synthesizes findings into root cause analysis

**Log Aggregator:**
- Queries centralized logging (Elasticsearch)
- Filters by service, time window, error patterns
- Identifies anomalous log patterns

**Metrics Analyzer:**
- Pulls Prometheus/Grafana metrics
- Detects anomalies (latency spikes, error rate changes)
- Correlates metrics with deployment timeline

**Dependency Mapper:**
- Builds service dependency graph
- Identifies upstream/downstream impact
- Traces cascading failures

**Remediation Planner:**
- Suggests fixes based on root cause
- Estimates risk/impact of each option
- Prioritizes actions

**Execution Agents (Rollback/Config/Scale):**
- Apply fixes with safety checks
- Execute in dry-run mode first
- Require human approval for high-risk changes

**Verification Agent:**
- Monitors metrics post-fix
- Validates incident resolution
- Triggers rollback if metrics degrade

### Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| MTTR (Mean Time to Resolution) | 2-4 hours | 15-30 minutes | 80% reduction |
| Actionable recommendations | 1.7% (single agent) | 100% (multi-agent) | 58× improvement |
| Engineer on-call burden | High (3am pages) | Low (agent handles routine) | 70% fewer escalations |
| Cost per incident | $800 (engineer hours) | $50 (agent + review) | 94% reduction |

### Key Learnings

**Success factors:**
- Hierarchical decomposition avoided context overload
- Concurrent sub-task execution reduced latency
- Safety checks (dry-run, approval gates) built trust
- Observability (agent traces) enabled debugging

**Failure modes addressed:**
- False positives: Agent proposes fix → human reviews before apply
- Incomplete data: Graceful degradation to partial analysis
- Agent disagreement: Manager synthesizes conflicting findings

**Architectural insights:**
- Manager agent needed domain-specific prompting (incident response playbooks)
- Worker agents benefited from narrow, well-defined scopes
- Verification agent prevented "fix that breaks something else"

## 2. Automated QA Test Generation (380 → 700+ Tests)

**Company:** SaaS platform (150k users)  
**Challenge:** Manual QA couldn't keep up with rapid feature releases, flaky tests  
**Solution:** Multi-agent QA council with self-healing pipeline  

### Architecture

**Pattern:** Sequential (Council Phases) + Event-Driven (Self-Healing)

```
Analyst → Architect → Engineer → Sentinel → Healer → Scribe
                                    ↓ (reject)
                                  Healer
```

### Agent Roles (Council of Sub-Agents)

**Analyst Agent:**
- Reviews PRs, identifies testable changes
- Extracts features, edge cases, user flows
- Generates test scenarios (happy path + error cases)

**Architect Agent:**
- Designs test structure and organization
- Determines test dependencies and setup/teardown
- Chooses test framework patterns (unit, integration, e2e)

**Engineer Agent:**
- Writes actual test code (Playwright, Jest, Cypress)
- Implements mocks and fixtures
- Handles async behavior and waits

**Sentinel Agent (Quality Gate):**
- Reviews generated tests for quality
- Checks for anti-patterns (hard-coded waits, brittle selectors)
- Validates coverage against requirements
- **Rejects poor tests** → sends back to Healer

**Healer Agent:**
- Receives rejected tests with feedback
- Fixes issues (better selectors, proper waits, error handling)
- Re-submits to Sentinel

**Scribe Agent:**
- Documents tests (purpose, coverage, maintenance notes)
- Updates test inventory and coverage reports
- Generates human-readable test plans

### Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Test count | 380 | 700+ | 84% increase |
| Coverage | 60% | 87% | +27pp |
| Flaky test rate | 15% | <2% | 87% reduction |
| Time to generate suite | 45-60 min (manual) | 5-10 min (agent) | 85% faster |
| Cost per test | Human: $25 | Agent: $0.06 | 99.8% cheaper |

### Key Learnings

**Sequential council pattern advantages:**
- Each agent specialized deeply in one phase
- Progressive refinement improved quality
- Sentinel quality gate prevented bad tests from merging

**Self-healing via Healer agent:**
- Rejected tests fixed automatically (85% success rate)
- Only 15% escalated to humans
- Iterative fix loop avoided infinite rewrites (max 3 attempts)

**Anti-patterns avoided:**
- Single "super-agent" tried everything at once → poor quality
- Parallel generation without review → inconsistent patterns
- No feedback loop → same mistakes repeated

## 3. Financial Underwriting (Multi-Model Specialization)

**Company:** Fintech lender ($500M originations/year)  
**Challenge:** Manual underwriting slow, inconsistent decisions, compliance risk  
**Solution:** Hierarchical agent system with domain specialists  

### Architecture

**Pattern:** Hierarchical + Sequential

```
Underwriting Manager
├─→ Data Extraction Agent (docx/pdf parsing)
├─→ Credit Scoring Agent (fine-tuned model)
├─→ Compliance Agent (regulation knowledge base)
└─→ Risk Assessment Agent (historical default data)
     ↓
Final Decision Agent (Manager synthesis)
```

### Specialization Strategy

**Data Extraction Agent:**
- Fine-tuned on loan documents
- Extracts: income, employment, assets, debts
- Validates extracted data against schemas

**Credit Scoring Agent:**
- Custom model trained on company's historical data
- Incorporates industry-specific risk factors
- Outputs score + explanation

**Compliance Agent:**
- Checks against lending regulations (TILA, ECOA, Fair Lending)
- Flags prohibited criteria (race, religion, etc.)
- Verifies required disclosures

**Risk Assessment Agent:**
- Analyzes debt-to-income ratio, payment history
- Models default probability
- Suggests loan terms (rate, amount, duration)

**Final Decision Agent (Manager):**
- Synthesizes all sub-agent outputs
- Resolves conflicts (e.g., good score but high risk)
- Generates decision with reasoning

### Results

| Metric | Before (Manual) | After (Multi-Agent) | Improvement |
|--------|-----------------|---------------------|-------------|
| Processing time | 2-3 days | 30 minutes | 95% faster |
| Decision consistency | 65% (inter-rater agreement) | 92% | +27pp |
| Compliance violations | 3-5 per month | <1 per quarter | 95% reduction |
| Throughput | 50 apps/day | 500 apps/day | 10× increase |
| Cost per decision | $120 (labor) | $8 (compute) | 93% cheaper |

### Key Learnings

**Domain-specific fine-tuning critical:**
- Generic models struggled with financial jargon
- Fine-tuned extraction agent 3× more accurate

**Compliance as separate agent:**
- Isolated regulatory logic from scoring logic
- Easier to update for new regulations
- Audit trail per agent for explainability

**Manager synthesis prevented conflicts:**
- Sub-agents sometimes contradicted (e.g., high score but high debt ratio)
- Manager agent weighed trade-offs with business rules

## 4. Customer Support Routing (Hierarchical Handoff)

**Company:** E-commerce platform (10M users)  
**Challenge:** Generic support bot poor quality, high escalation rate  
**Solution:** Triage agent + specialist agents for billing/tech/account issues  

### Architecture

**Pattern:** Handoff + Hierarchical

```
Triage Agent
├─→ Billing Specialist
│   ├─→ Refund Sub-Agent
│   └─→ Invoice Sub-Agent
├─→ Technical Support
│   ├─→ Login Issues Sub-Agent
│   └─→ Bug Report Sub-Agent
├─→ Account Management
│   ├─→ Subscription Changes
│   └─→ Cancellation Retention
└─→ Escalation Agent (Human Handoff)
```

### Routing Logic

**Triage Agent:**
- Classifies intent (billing, technical, account, general)
- Extracts key entities (order ID, product, error message)
- Routes to specialist with context

**Specialists:**
- Access domain-specific knowledge bases
- Use tools (billing API, order lookup, account management)
- Escalate when confidence < 70% or user requests human

**Sub-Agents:**
- Handle narrow sub-tasks within specialist domain
- E.g., Refund Sub-Agent checks eligibility, processes refund, sends confirmation

### Results

| Metric | Before (Generic Bot) | After (Specialist Agents) | Improvement |
|--------|---------------------|---------------------------|-------------|
| Resolution rate | 35% | 72% | +37pp |
| Customer satisfaction | 3.2/5 | 4.5/5 | +41% |
| Escalation rate | 65% | 28% | 57% reduction |
| Average handle time | 8 min | 4 min | 50% faster |
| Cost per interaction | $5 | $1.20 | 76% cheaper |

### Key Learnings

**Specialist agents vs monolithic bot:**
- Specialists had focused knowledge → higher accuracy
- Easier to improve one specialist than entire system

**Hierarchical routing prevented tool overload:**
- Triage agent didn't need access to all tools
- Specialists loaded only relevant tools/knowledge

**Escalation agent preserved context:**
- When human needed, full conversation + agent findings passed along
- Human didn't start from scratch

## 5. Legal Document Generation (Sequential Pipeline)

**Company:** Law firm (50 attorneys)  
**Challenge:** Contract drafting time-consuming, inconsistent quality  
**Solution:** Sequential pipeline for template → customization → compliance → risk  

### Architecture

**Pattern:** Sequential

```
Template Selection → Clause Customization → Compliance Review → Risk Assessment → Final Polish
```

### Pipeline Stages

**Template Selection Agent:**
- Analyzes client requirements (contract type, jurisdiction, parties)
- Selects appropriate base template from library
- Identifies required clauses

**Clause Customization Agent:**
- Fine-tuned on firm's past contracts
- Adapts clauses for client specifics
- Maintains legal precision while customizing

**Compliance Review Agent:**
- Checks against jurisdictional regulations
- Validates required disclosures
- Flags potentially unenforceable clauses

**Risk Assessment Agent:**
- Reviews liability exposure
- Identifies client-unfavorable terms
- Suggests protective clauses

**Final Polish Agent:**
- Formatting consistency
- Grammar/style cleanup
- Citation validation

### Results

| Metric | Before (Manual) | After (Pipeline) | Improvement |
|--------|----------------|------------------|-------------|
| Drafting time | 6-8 hours | 1-2 hours | 75% faster |
| Revision cycles | 4-5 | 1-2 | 60% fewer |
| Compliance issues | 2-3 per contract | <1 per 5 contracts | 90% reduction |
| Attorney satisfaction | 6/10 | 9/10 | +50% |
| Cost per contract | $2,400 | $600 | 75% cheaper |

### Key Learnings

**Sequential appropriate for document generation:**
- Each stage built on previous stage's output
- Progressive refinement improved quality

**Domain expertise via fine-tuning:**
- Customization agent trained on firm's style
- Compliance agent needed regulatory knowledge base

**Human-in-the-loop at final stage:**
- Attorney reviewed final output before sending to client
- Agents produced 90% complete draft → attorney added 10% judgment

## 6. News Pipeline (Concurrent + Event-Driven)

**Company:** News aggregation platform  
**Challenge:** Manual curation slow, missed breaking stories  
**Solution:** Event-driven agents for aggregation, fact-checking, synthesis  

### Architecture

**Pattern:** Event-Driven + Concurrent

```
RSS Feeds / APIs → Event Bus
                      ↓
      [Aggregator | Fact-Checker | Trend Analyzer] (Concurrent)
                      ↓
                  Synthesizer
                      ↓
                   Publisher
```

### Agent Roles

**Aggregator Agent:**
- Subscribes to: `news.article.published` events
- Clusters related stories
- Deduplicates identical articles

**Fact-Checker Agent:**
- Subscribes to: `news.article.clustered` events
- Cross-references claims against trusted sources
- Flags misinformation

**Trend Analyzer Agent:**
- Subscribes to: `news.article.clustered` events
- Identifies trending topics
- Predicts virality

**Synthesizer Agent:**
- Subscribes to: `news.cluster.complete` events (after all concurrent agents finish)
- Generates summary of cluster
- Cites sources

**Publisher Agent:**
- Subscribes to: `news.summary.ready` events
- Posts to platform
- Notifies subscribers

### Results

| Metric | Before (Manual) | After (Event-Driven) | Improvement |
|--------|----------------|----------------------|-------------|
| Story latency | 30-60 min | 2-5 min | 90% faster |
| Daily stories published | 50 | 300 | 6× increase |
| Fact-check coverage | 20% | 95% | +75pp |
| Breaking news speed | Slow (human-dependent) | Fast (automated) | Near real-time |

### Key Learnings

**Event-driven pattern suited news pipeline:**
- Async processing: agents worked independently
- Scalable: added new agents without refactoring

**Fact-checker as independent agent:**
- Ran in parallel with trend analysis → no added latency
- Flagged stories before publication

**Eventual consistency acceptable:**
- Initial summary published quickly
- Fact-checks updated summary asynchronously

## Cross-Study Insights

### Pattern Selection

| Use Case | Pattern | Why |
|----------|---------|-----|
| Incident response | Hierarchical + Concurrent | Task decomposition + parallel diagnosis |
| QA generation | Sequential (council) | Progressive refinement, quality gates |
| Underwriting | Hierarchical + Sequential | Domain specialization + ordered workflow |
| Support routing | Handoff + Hierarchical | Dynamic routing + specialist depth |
| Document generation | Sequential | Linear dependencies, refinement stages |
| News pipeline | Event-Driven + Concurrent | Async, independent tasks |

### Universal Success Factors

1. **Role specialization:** Narrow, well-defined agent responsibilities
2. **Observability:** Trace agent interactions, debug failures
3. **Human oversight:** Final review or approval gates for high-stakes
4. **Graceful degradation:** Partial results better than total failure
5. **Iterative improvement:** Start simple, add complexity as needed

### Common Failure Modes

**Agent disagreement without resolution:**
- Fix: Manager agent synthesizes with conflict resolution logic

**Context overload (single agent doing too much):**
- Fix: Decompose into smaller specialist agents

**Communication storms (excessive messaging):**
- Fix: Batch updates, use indirect communication (shared state)

**Cascading failures (one agent fails → all fail):**
- Fix: Fallback agents, partial result tolerance

**Infinite loops (group chat without termination):**
- Fix: Turn limits, consensus detection, quality thresholds

### Cost Optimization

**Token usage patterns:**
- Specialist agents used 60-80% fewer tokens than generalists
- Sequential patterns more token-efficient than group chats
- Concurrent patterns increased total tokens but reduced wall-clock time

**Cost per outcome:**
- Multi-agent systems: $0.06 - $8 per task
- Human equivalents: $25 - $800 per task
- ROI: 50-500× depending on task complexity

### Production Readiness Checklist

From successful deployments:

- [ ] Observability: Distributed tracing, logs, metrics
- [ ] Error handling: Retries, fallbacks, circuit breakers
- [ ] Security: Permission isolation, audit trails
- [ ] Testing: Unit tests per agent, integration tests for orchestration
- [ ] Monitoring: Latency, success rate, cost per execution
- [ ] Documentation: Agent capabilities, input/output schemas
- [ ] Rollback: Ability to revert to manual process if agents fail
- [ ] Human escalation: Clear path when agents can't resolve

### Scaling Lessons

**When to add more agents:**
- Single agent's context window saturated
- Clear sub-domain specialization opportunities
- Parallel execution would reduce latency

**When NOT to add more agents:**
- Coordination overhead exceeds value
- Single agent already solves problem reliably
- No clear specialization boundaries

**Agent count sweet spots:**
- 2-4 agents: Most common, manageable coordination
- 5-8 agents: Hierarchical orchestration needed
- 9+ agents: Requires robust framework, careful design
