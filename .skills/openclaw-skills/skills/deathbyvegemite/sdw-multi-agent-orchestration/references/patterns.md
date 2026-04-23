# Orchestration Patterns: Deep Dive

This document provides detailed implementation guidance for each orchestration pattern, including code examples, failure modes, and optimization strategies.

## Sequential Pattern

### Architecture

```
Input → Agent 1 → Agent 2 → ... → Agent N → Result
         ↓         ↓               ↓
      (state)   (state)         (state)
```

### Implementation Example

```python
class SequentialOrchestrator:
    def __init__(self, agents: list):
        self.agents = agents
        self.state = {}
    
    async def execute(self, initial_input):
        result = initial_input
        
        for agent in self.agents:
            try:
                result = await agent.process(result, self.state)
                self.state[agent.name] = result
            except Exception as e:
                # Failure handling
                if agent.can_skip:
                    continue
                else:
                    raise PipelineFailure(f"Agent {agent.name} failed", e)
        
        return result
```

### Failure Modes & Mitigation

**Early stage failure cascades:**
- Validation checks before expensive downstream processing
- Cost gates: assess confidence/quality before proceeding
- Fallback chains: try alternate agents for failed stages

**Accumulated error amplification:**
- Quality checkpoints between stages
- Intermediate result validation
- Error budgets: abort if error rate exceeds threshold

**Performance bottleneck at sequential stages:**
- Parallelize independent sub-tasks within stages
- Asynchronous processing where possible
- Caching for expensive intermediate results

### Optimization Patterns

**Conditional skipping:**
```python
if agent.should_skip(result, state):
    continue
```

**Early termination:**
```python
if satisfactory_result(result):
    return result
```

**Parallel sub-pipelines:**
```
Stage 1 → [Stage 2a, Stage 2b] (parallel) → Merge → Stage 3
```

## Concurrent Pattern

### Architecture

```
        ┌─→ Agent 1 ─┐
Input ──┼─→ Agent 2 ─┼─→ Aggregator → Result
        └─→ Agent 3 ─┘
```

### Implementation Example

```python
class ConcurrentOrchestrator:
    def __init__(self, agents: list, aggregator):
        self.agents = agents
        self.aggregator = aggregator
    
    async def execute(self, input_data):
        # Spawn all agents concurrently
        tasks = [agent.process(input_data) for agent in self.agents]
        
        # Wait for all with timeout
        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )
        
        # Filter failures, aggregate successes
        successful = [r for r in results if not isinstance(r, Exception)]
        failed = [r for r in results if isinstance(r, Exception)]
        
        if len(successful) < self.min_required:
            raise InsufficientResults(f"Only {len(successful)}/{len(self.agents)} succeeded")
        
        return self.aggregator.merge(successful, failed)
```

### Aggregation Strategies

**Voting (consensus):**
```python
def vote_aggregator(results):
    from collections import Counter
    votes = Counter([r.classification for r in results])
    return votes.most_common(1)[0][0]
```

**Averaging (numeric):**
```python
def average_aggregator(results):
    return sum(r.score for r in results) / len(results)
```

**Weighted ensemble:**
```python
def weighted_aggregator(results, weights):
    return sum(r.score * w for r, w in zip(results, weights)) / sum(weights)
```

**Best-of-N:**
```python
def best_of_n(results):
    return max(results, key=lambda r: r.confidence)
```

**Merge (combine all):**
```python
def merge_aggregator(results):
    # Combine unique insights from all agents
    combined = set()
    for r in results:
        combined.update(r.findings)
    return list(combined)
```

### Failure Handling

**Partial failure tolerance:**
```python
# Degrade gracefully with min_required threshold
if len(successful) >= self.min_required:
    return aggregator.merge(successful)
```

**Timeout management:**
```python
# Don't wait indefinitely
results = await asyncio.wait_for(
    asyncio.gather(*tasks, return_exceptions=True),
    timeout=30.0
)
```

**Retry stragglers:**
```python
# Fast path: return if all succeed quickly
# Slow path: retry failures while fast ones complete
```

## Hierarchical Pattern

### Architecture

```
          Manager Agent
         /      |      \
        /       |       \
   Worker 1  Worker 2  Worker 3
                |
           Sub-workers
```

### Implementation Example

```python
class HierarchicalOrchestrator:
    def __init__(self, manager_agent, worker_registry):
        self.manager = manager_agent
        self.registry = worker_registry
    
    async def execute(self, objective):
        # Manager decomposes task
        plan = await self.manager.plan(objective, self.registry.capabilities)
        
        # Execute sub-tasks
        results = {}
        for task in plan.tasks:
            worker = self.registry.get_agent(task.required_capability)
            results[task.id] = await worker.execute(task)
        
        # Manager synthesizes results
        return await self.manager.synthesize(objective, plan, results)
```

### Manager Agent Responsibilities

**Task decomposition:**
- Analyze objective and break into sub-goals
- Identify dependencies between sub-tasks
- Determine execution order (sequential, parallel, or mixed)

**Worker selection:**
- Query agent registry for capabilities
- Match capabilities to task requirements
- Consider load balancing and availability

**Result synthesis:**
- Aggregate worker outputs
- Resolve conflicts or inconsistencies
- Validate completeness against original objective

### Worker Agent Best Practices

**Clear capability declaration:**
```json
{
  "agent_id": "data_extractor",
  "capabilities": ["pdf_parsing", "table_extraction"],
  "input_schema": {...},
  "output_schema": {...}
}
```

**Bounded execution:**
- Clear start/end conditions
- Timeout enforcement
- Progress reporting back to manager

**Failure signaling:**
```python
class TaskResult:
    success: bool
    output: Any
    error: Optional[str]
    retry_suggestion: Optional[str]
```

## Group Chat Pattern

### Architecture

```
    ┌─────────────────────┐
    │  Shared History     │
    │  [msg1, msg2, ...]  │
    └─────────────────────┘
         ↑ ↓   ↑ ↓   ↑ ↓
      Agent1 Agent2 Agent3
```

### Implementation Example

```python
class GroupChatOrchestrator:
    def __init__(self, agents: list, selector, termination_fn):
        self.agents = agents
        self.selector = selector  # Determines next speaker
        self.termination_fn = termination_fn
        self.history = []
    
    async def execute(self, initial_prompt):
        self.history.append({"role": "user", "content": initial_prompt})
        
        turn = 0
        max_turns = 20  # Prevent infinite loops
        
        while not self.termination_fn(self.history) and turn < max_turns:
            # Select next speaker
            next_agent = await self.selector.choose(self.history, self.agents)
            
            # Agent responds based on full history
            response = await next_agent.respond(self.history)
            self.history.append({
                "role": next_agent.name,
                "content": response
            })
            
            turn += 1
        
        return self.history
```

### Selector Strategies

**Round-robin:**
```python
def round_robin_selector(history, agents):
    last_speaker = history[-1]["role"]
    last_idx = [a.name for a in agents].index(last_speaker)
    return agents[(last_idx + 1) % len(agents)]
```

**LLM-based routing:**
```python
async def llm_selector(history, agents):
    prompt = f"""Given conversation history, who should speak next?
    Agents: {[a.name + ': ' + a.description for a in agents]}
    History: {history[-3:]}  # Last 3 messages
    """
    selection = await llm_call(prompt)
    return find_agent_by_name(selection, agents)
```

**Capability-based:**
```python
def capability_selector(history, agents):
    last_msg = history[-1]["content"]
    required_capability = infer_capability(last_msg)
    return max(agents, key=lambda a: a.capability_match(required_capability))
```

### Termination Conditions

**Consensus reached:**
```python
def consensus_termination(history):
    recent = history[-3:]
    return all("agree" in msg["content"].lower() for msg in recent)
```

**Solution proposed:**
```python
def solution_termination(history):
    return "final answer:" in history[-1]["content"].lower()
```

**Turn limit:**
```python
def turn_limit_termination(history, max_turns=20):
    return len(history) > max_turns
```

**Quality threshold:**
```python
def quality_termination(history, validator):
    if len(history) < 5:
        return False
    latest = history[-1]
    return validator.score(latest) > 0.9
```

## Handoff Pattern

### Architecture

```
Entry Agent → [Specialist A | Specialist B | Specialist C] → Escalation
     ↑                                                            ↓
     └────────────────────── (optional loop back) ───────────────┘
```

### Implementation Example

```python
class HandoffOrchestrator:
    def __init__(self, entry_agent, specialists, escalation_agent):
        self.entry = entry_agent
        self.specialists = {s.domain: s for s in specialists}
        self.escalation = escalation_agent
    
    async def execute(self, request):
        # Triage
        routing = await self.entry.analyze(request)
        
        if routing.domain in self.specialists:
            specialist = self.specialists[routing.domain]
            result = await specialist.handle(request, routing.context)
            
            if result.needs_escalation:
                return await self.escalation.handle(request, result)
            else:
                return result
        else:
            # No specialist found, escalate directly
            return await self.escalation.handle(request, {"reason": "no_specialist"})
```

### Routing Logic

**Rule-based:**
```python
def rule_based_routing(request):
    if "billing" in request.lower():
        return "billing_specialist"
    elif "technical" in request.lower() or "error" in request.lower():
        return "technical_support"
    elif "cancel" in request.lower():
        return "retention_specialist"
    else:
        return "general_support"
```

**LLM-based classification:**
```python
async def llm_routing(request):
    prompt = f"""Classify this support request:
    Request: {request}
    Categories: [billing, technical, account, cancellation, general]
    Return only the category name.
    """
    return await llm_call(prompt)
```

**Confidence-based escalation:**
```python
async def confident_routing(request):
    classification = await llm_call(classify_prompt(request))
    
    if classification.confidence < 0.7:
        return "escalation"
    else:
        return classification.category
```

### Escalation Patterns

**Automatic escalation triggers:**
- Low confidence from specialist
- User explicitly requests human support
- Sensitive issue detected (legal, security)
- Repeated failures to resolve

**Escalation with context:**
```python
class EscalationContext:
    original_request: str
    attempted_specialists: list[str]
    partial_results: list[Any]
    failure_reasons: list[str]
    sentiment_score: float
```

## Event-Driven Pattern

### Architecture

```
Event Bus (Pub-Sub)
    ↓           ↓           ↓
  Agent A    Agent B    Agent C
    ↓           ↓           ↓
Publish    Publish    Publish
```

### Implementation Example

```python
class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)
    
    def subscribe(self, event_type, handler):
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event):
        handlers = self.subscribers[event.type]
        tasks = [h(event) for h in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

class EventDrivenOrchestrator:
    def __init__(self, agents: list, event_bus: EventBus):
        self.agents = agents
        self.bus = event_bus
        
        # Register agents as subscribers
        for agent in agents:
            for event_type in agent.subscribes_to:
                self.bus.subscribe(event_type, agent.handle_event)
    
    async def execute(self, initial_event):
        await self.bus.publish(initial_event)
        # Agents react autonomously, publishing new events
```

### Event Design

**Event structure:**
```python
@dataclass
class Event:
    type: str
    source: str
    timestamp: datetime
    payload: dict
    correlation_id: str  # Track related events
```

**Event types example (CI/CD):**
- `code.pushed`
- `build.started`, `build.completed`, `build.failed`
- `tests.started`, `tests.passed`, `tests.failed`
- `security.scan.completed`
- `deploy.triggered`, `deploy.completed`

### Async Coordination Challenges

**Event ordering:**
- Use sequence numbers or vector clocks
- Implement causal ordering when needed

**Duplicate events:**
- Idempotent handlers (same event processed multiple times = same result)
- Deduplication with event IDs

**Event loss:**
- Persistent event log (event sourcing)
- At-least-once delivery guarantees

**Backpressure:**
- Rate limiting per subscriber
- Queue depth monitoring
- Circuit breakers on slow consumers

## Pattern Comparison Matrix

| Pattern | Complexity | Latency | Failure Handling | Best For |
|---------|-----------|---------|------------------|----------|
| Sequential | Low | High (cumulative) | Fragile (cascade) | Linear pipelines |
| Concurrent | Medium | Low (parallel) | Robust (partial) | Independent tasks |
| Hierarchical | High | Medium | Moderate (manager SPOF) | Task decomposition |
| Group Chat | High | High (many turns) | Complex (convergence) | Collaborative reasoning |
| Handoff | Medium | Medium | Good (specialist fallback) | Routing/escalation |
| Event-Driven | High | Low (async) | Complex (eventual consistency) | Reactive systems |

## Pattern Selection Decision Tree

```
Do tasks have clear dependencies?
├─ Yes: Are they linear?
│  ├─ Yes → Sequential
│  └─ No: Do they form a hierarchy?
│     └─ Yes → Hierarchical
└─ No: Can they run in parallel?
   ├─ Yes → Concurrent
   └─ No: Is routing dynamic?
      ├─ Yes → Handoff
      └─ No: Is system reactive?
         ├─ Yes → Event-Driven
         └─ No: Does it need discussion?
            └─ Yes → Group Chat
```

## Hybrid Patterns

Real-world systems often combine patterns:

**Hierarchical + Concurrent:**
Manager decomposes task, workers execute in parallel.

**Sequential + Handoff:**
Pipeline stages hand off to specialists at each stage.

**Event-Driven + Hierarchical:**
Event triggers orchestrator, which manages hierarchical workflow.

**Example: DevOps Incident Response**
```
Event (Alert) → Incident Manager (Hierarchical)
                ├─→ Log Analyzer
                ├─→ Metrics Analyzer (triggers Event)
                └─→ Remediation Planner
                        ↓
                   [Fix A | Fix B | Fix C] (Concurrent)
                        ↓
                   Verification Agent
```
