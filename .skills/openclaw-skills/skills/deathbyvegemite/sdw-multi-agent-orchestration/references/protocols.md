# Communication Protocols for Multi-Agent Systems

This document covers standardized protocols for agent-to-agent communication, tool access, and context management.

## Model Context Protocol (MCP)

**Purpose:** Standardizes how agents access external tools, data sources, and contextual information.

**Status (2026):** Production-ready, supported by major frameworks (LangChain, Semantic Kernel, AutoGen).

### Core Concepts

**Resources:**
- Files, databases, APIs, knowledge bases
- Agents request access via standardized interface
- Resource server handles permissions and data retrieval

**Tools:**
- External capabilities agents can invoke (web search, calculations, API calls)
- Declared with input/output schemas
- Agents discover tools dynamically

**Prompts:**
- Reusable prompt templates
- Context-aware (adapt to current state)
- Reduce redundant prompt engineering

### MCP Message Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "multi-agent orchestration patterns",
      "max_results": 10
    }
  },
  "id": "req-123"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Search results: ..."
      }
    ]
  },
  "id": "req-123"
}
```

### Resource Discovery

**List available tools:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": "req-124"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "web_search",
        "description": "Search the web using Brave API",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer"}
          },
          "required": ["query"]
        }
      }
    ]
  },
  "id": "req-124"
}
```

### Security Model

**Capability-based access:**
- Agents request specific capabilities
- MCP server grants/denies based on policy
- Audit trail of all tool invocations

**Permission scopes:**
- `read`: Read-only access to resources
- `write`: Modify resources
- `execute`: Run tools/actions
- `admin`: Full control

**Example permission grant:**
```json
{
  "agent_id": "underwriting_agent",
  "capabilities": [
    {"resource": "loan_documents", "scope": "read"},
    {"resource": "credit_api", "scope": "execute"},
    {"resource": "decision_db", "scope": "write"}
  ]
}
```

### Context Management

**Context objects:**
- Represent current state (user session, workflow state, conversation history)
- Agents can read/write context
- Versioned for consistency

**Context example:**
```json
{
  "context_id": "ctx-456",
  "version": 3,
  "data": {
    "user_id": "user-789",
    "workflow": "loan_underwriting",
    "stage": "risk_assessment",
    "prior_results": {
      "credit_score": 720,
      "debt_to_income": 0.35
    }
  }
}
```

**Context updates (optimistic locking):**
```json
{
  "jsonrpc": "2.0",
  "method": "context/update",
  "params": {
    "context_id": "ctx-456",
    "expected_version": 3,
    "updates": {
      "stage": "final_decision",
      "risk_assessment": {"probability_of_default": 0.05}
    }
  },
  "id": "req-125"
}
```

If `expected_version` doesn't match, update fails (another agent modified context).

### MCP Server Implementation

**Python example (simplified):**
```python
from mcp import MCPServer, Tool, Resource

server = MCPServer()

@server.tool(
    name="web_search",
    description="Search the web",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
)
async def web_search(query: str):
    # Implementation
    results = await brave_search_api(query)
    return {"results": results}

@server.resource(
    uri="file:///data/loans/{id}",
    description="Loan document",
    permissions=["read"]
)
async def get_loan_doc(id: str):
    return await load_loan_document(id)

server.run()
```

### MCP Client Usage

**Agent requesting tool:**
```python
async def agent_task():
    # Discover tools
    tools = await mcp_client.list_tools()
    
    # Call web_search tool
    result = await mcp_client.call_tool(
        "web_search",
        {"query": "multi-agent systems"}
    )
    
    # Process result
    return result["results"]
```

### Benefits of MCP

✅ **Dynamic tool discovery:** Agents don't need hard-coded tool integrations  
✅ **Permission isolation:** Fine-grained access control  
✅ **Standardization:** Works across frameworks and platforms  
✅ **Audit trails:** All tool calls logged for compliance  
✅ **Versioning:** Tools can evolve without breaking agents  

## Agent-to-Agent Protocol (A2A)

**Purpose:** Governs peer coordination, negotiation, task delegation, and collaborative workflows.

**Status (2026):** Emerging standard, adopted by enterprise platforms (Salesforce Agentforce, Google Agent Dev Kit).

### Core Concepts

**Agents as peers:**
- No central orchestrator required (though one can exist)
- Agents negotiate, delegate, and collaborate directly
- Supports both hierarchical and decentralized patterns

**Message types:**
- `request`: Ask another agent to perform a task
- `inform`: Share information
- `agree` / `refuse`: Accept or decline requests
- `query-ref`: Ask another agent for information
- `subscribe`: Register for event notifications

### A2A Message Format

**Request delegation:**
```json
{
  "protocol": "A2A/1.0",
  "type": "request",
  "sender": "agent-incident-manager",
  "receiver": "agent-log-analyzer",
  "content": {
    "action": "analyze_logs",
    "params": {
      "service": "api-gateway",
      "time_window": "last_1h",
      "error_filter": "5xx"
    }
  },
  "conversation_id": "conv-789",
  "reply_with": "req-abc"
}
```

**Inform response:**
```json
{
  "protocol": "A2A/1.0",
  "type": "inform",
  "sender": "agent-log-analyzer",
  "receiver": "agent-incident-manager",
  "content": {
    "analysis": {
      "error_count": 342,
      "most_common": "timeout connecting to database",
      "suspected_root_cause": "db connection pool exhausted"
    }
  },
  "conversation_id": "conv-789",
  "in_reply_to": "req-abc"
}
```

**Refuse (agent cannot handle request):**
```json
{
  "protocol": "A2A/1.0",
  "type": "refuse",
  "sender": "agent-log-analyzer",
  "receiver": "agent-incident-manager",
  "content": {
    "reason": "Elasticsearch unavailable",
    "suggestion": "Try agent-backup-log-analyzer"
  },
  "conversation_id": "conv-789",
  "in_reply_to": "req-abc"
}
```

### Conversation Management

**Conversation IDs:**
- Track related messages
- Enable multi-turn exchanges
- Support forking conversations (one agent spawns multiple sub-tasks)

**Example conversation flow:**
```
Manager → [request] → Worker A (conv-1)
Worker A → [query-ref] → Worker B (conv-1-fork-1)
Worker B → [inform] → Worker A (conv-1-fork-1)
Worker A → [inform] → Manager (conv-1)
```

### Negotiation Protocol

**Task negotiation (auction-style):**
```json
// Manager broadcasts task
{
  "type": "cfp",  // Call For Proposals
  "content": {
    "task": "analyze_metrics",
    "deadline": "2026-03-20T17:00:00Z"
  }
}

// Agents bid
{
  "type": "propose",
  "content": {
    "cost": 100,  // tokens
    "time": 30,   // seconds
    "confidence": 0.9
  }
}

// Manager accepts best bid
{
  "type": "accept-proposal",
  "content": {
    "selected_agent": "agent-metrics-analyzer-2"
  }
}
```

### Coordination Patterns

**Peer collaboration (group chat):**
```json
{
  "type": "inform",
  "sender": "agent-code-reviewer",
  "receiver": "all",  // Broadcast
  "content": {
    "observation": "Security vulnerability in login function"
  }
}
```

**Hierarchical delegation:**
```json
{
  "type": "request",
  "sender": "manager",
  "receiver": "worker-1",
  "content": {
    "action": "extract_data",
    "delegation_authority": "can_sub_delegate"  // Worker can delegate further
  }
}
```

### Event Subscription

**Subscribe to events:**
```json
{
  "type": "subscribe",
  "sender": "agent-monitor",
  "receiver": "agent-deployment",
  "content": {
    "event_type": "deployment_completed"
  }
}
```

**Event notification:**
```json
{
  "type": "inform",
  "sender": "agent-deployment",
  "receiver": "agent-monitor",
  "content": {
    "event": "deployment_completed",
    "details": {
      "service": "api-v2",
      "version": "1.5.0",
      "timestamp": "2026-03-20T16:30:00Z"
    }
  }
}
```

### Error Handling

**Agent failure:**
```json
{
  "type": "failure",
  "sender": "agent-worker",
  "receiver": "agent-manager",
  "content": {
    "error": "OutOfMemoryError",
    "partial_result": {...},  // Best effort
    "retry_possible": false
  }
}
```

### A2A Security

**Authentication:**
- Agents use signed messages (JWT or similar)
- Receiver verifies sender identity

**Authorization:**
- Agents declare capabilities
- Receivers check if sender is authorized for requested action

**Example signed message:**
```json
{
  "protocol": "A2A/1.0",
  "type": "request",
  "sender": "agent-xyz",
  "signature": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "content": {...}
}
```

### Benefits of A2A

✅ **Decentralized coordination:** No single point of failure  
✅ **Negotiation support:** Agents can bid, agree, refuse  
✅ **Event-driven workflows:** Subscribe/publish patterns  
✅ **Conversation tracking:** Multi-turn exchanges maintained  
✅ **Interoperability:** Agents from different vendors can communicate  

## FIPA-ACL (Foundation for Intelligent Physical Agents - Agent Communication Language)

**Purpose:** Mature standard for agent communication (predates LLM era but still relevant).

**Status:** Widely used in academic/research systems, less common in LLM-based production systems.

### Message Structure

```
(inform
  :sender agent1
  :receiver agent2
  :content "database connection restored"
  :language English
  :ontology incident-response
)
```

### Performatives (Message Types)

| Performative | Purpose | Example |
|-------------|---------|---------|
| `inform` | Share information | "Error rate is 5%" |
| `request` | Ask for action | "Restart service X" |
| `query-if` | Ask yes/no question | "Is service healthy?" |
| `query-ref` | Ask for information | "What is current latency?" |
| `agree` | Accept request | "I will restart service X" |
| `refuse` | Decline request | "I cannot restart service X (no permission)" |
| `propose` | Suggest action | "I propose rolling back to v1.4" |
| `accept-proposal` | Agree to proposal | "Proceed with rollback" |
| `reject-proposal` | Decline proposal | "Rollback too risky" |
| `cfp` | Call for proposals | "Who can analyze logs?" |

### Comparison: FIPA-ACL vs A2A

| Feature | FIPA-ACL | A2A |
|---------|----------|-----|
| Format | S-expressions | JSON |
| Maturity | 20+ years | 2-3 years |
| LLM integration | Not designed for LLMs | LLM-native |
| Adoption (2026) | Academic | Enterprise |
| Flexibility | Formal, rigid | Flexible, extensible |

**When to use FIPA-ACL:**
- Academic research
- Formal verification required
- Legacy system integration

**When to use A2A:**
- LLM-based agents
- Enterprise production systems
- Interoperability with modern frameworks

## KQML (Knowledge Query and Manipulation Language)

**Purpose:** Another mature standard for agent communication, focuses on knowledge exchange.

**Status:** Similar to FIPA-ACL, mostly academic/research use.

### Example

```
(ask-one
  :sender agent-underwriting
  :receiver agent-credit-bureau
  :content (credit-score customer-12345)
  :reply-with id-789
)
```

**Response:**
```
(tell
  :sender agent-credit-bureau
  :receiver agent-underwriting
  :content (credit-score customer-12345 720)
  :in-reply-to id-789
)
```

## Choosing a Protocol

### Decision Matrix

| Scenario | Recommended Protocol | Rationale |
|----------|---------------------|-----------|
| LLM-based agents, production | **MCP + A2A** | Modern, LLM-native, enterprise support |
| Tool/resource access | **MCP** | Standardized, secure, dynamic discovery |
| Peer coordination | **A2A** | Negotiation, event-driven, flexible |
| Formal verification needed | **FIPA-ACL** | Mature, well-defined semantics |
| Academic research | **FIPA-ACL or KQML** | Established in literature |
| Custom enterprise system | **Custom JSON-RPC** | Full control, tailored to needs |

### Hybrid Approach

Many production systems use:
- **MCP** for tool/resource access
- **A2A** for agent coordination
- **Custom protocols** for domain-specific needs

**Example:**
```
Incident Manager (A2A) ← coordinate → Log Analyzer
                ↓                            ↓
              (MCP)                        (MCP)
                ↓                            ↓
        Slack API Tool              Elasticsearch Resource
```

## Protocol Implementation Patterns

### Request-Response Pattern

```python
async def agent_request(sender, receiver, action, params):
    msg = {
        "protocol": "A2A/1.0",
        "type": "request",
        "sender": sender,
        "receiver": receiver,
        "content": {"action": action, "params": params},
        "conversation_id": generate_conversation_id(),
        "reply_with": generate_message_id()
    }
    
    response = await send_and_wait(msg)
    
    if response["type"] == "inform":
        return response["content"]
    elif response["type"] == "refuse":
        raise AgentRefusedError(response["content"]["reason"])
    else:
        raise UnexpectedResponseError(response)
```

### Event-Driven Pattern

```python
class EventBus:
    def __init__(self):
        self.subscriptions = defaultdict(list)
    
    def subscribe(self, event_type, agent_id, handler):
        self.subscriptions[event_type].append((agent_id, handler))
    
    async def publish(self, event):
        msg = {
            "protocol": "A2A/1.0",
            "type": "inform",
            "sender": event["source"],
            "content": {"event": event["type"], "details": event["data"]}
        }
        
        subscribers = self.subscriptions[event["type"]]
        tasks = [handler(msg) for (agent_id, handler) in subscribers]
        await asyncio.gather(*tasks, return_exceptions=True)
```

### Negotiation Pattern

```python
async def negotiate_task(manager, task, candidate_agents):
    # Broadcast CFP
    cfp = {
        "protocol": "A2A/1.0",
        "type": "cfp",
        "sender": manager,
        "content": {"task": task}
    }
    await broadcast(cfp, candidate_agents)
    
    # Collect proposals
    proposals = await wait_for_proposals(timeout=5.0)
    
    # Select best proposal
    best = min(proposals, key=lambda p: p["content"]["cost"])
    
    # Accept selected, reject others
    for proposal in proposals:
        if proposal == best:
            await send_accept(proposal["sender"])
        else:
            await send_reject(proposal["sender"])
    
    return best["sender"]
```

## Observability & Debugging

### Message Tracing

**Distributed trace with OpenTelemetry:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def send_a2a_message(msg):
    with tracer.start_as_current_span("send_a2a_message") as span:
        span.set_attribute("protocol", msg["protocol"])
        span.set_attribute("sender", msg["sender"])
        span.set_attribute("receiver", msg["receiver"])
        span.set_attribute("type", msg["type"])
        span.set_attribute("conversation_id", msg.get("conversation_id"))
        
        response = await transport.send(msg)
        
        span.set_attribute("response_type", response["type"])
        return response
```

### Message Logs

**Structured logging:**
```json
{
  "timestamp": "2026-03-20T16:45:00Z",
  "protocol": "A2A/1.0",
  "type": "request",
  "sender": "agent-manager",
  "receiver": "agent-worker-1",
  "conversation_id": "conv-123",
  "message_id": "msg-456",
  "content": {"action": "analyze", "params": {...}},
  "latency_ms": 120
}
```

### Protocol Debugging Tools

**Message replayer:**
- Capture message sequences
- Replay for debugging
- Inject faults (dropped messages, delays)

**Protocol validator:**
- Check message format
- Verify conversation flows
- Detect protocol violations

## Best Practices

### Protocol Design

✅ **Versioning:** Include protocol version in every message  
✅ **Idempotency:** Handlers should tolerate duplicate messages  
✅ **Timeouts:** Always set timeouts on request-response  
✅ **Conversation IDs:** Track related messages  
✅ **Structured content:** Use JSON schemas for message content  

### Security

✅ **Authentication:** Verify sender identity  
✅ **Authorization:** Check permissions before acting  
✅ **Audit logs:** Record all inter-agent communication  
✅ **Rate limiting:** Prevent message storms  
✅ **Encryption:** Use TLS for transport  

### Error Handling

✅ **Graceful failures:** Return `refuse` or `failure` messages, don't crash  
✅ **Partial results:** Provide best-effort output when full completion impossible  
✅ **Retry logic:** Implement exponential backoff for transient failures  
✅ **Circuit breakers:** Stop calling failing agents  

### Performance

✅ **Batching:** Group multiple messages when possible  
✅ **Async:** Non-blocking I/O for message passing  
✅ **Compression:** Compress large message payloads  
✅ **Caching:** Cache responses for idempotent queries  

## Resources

**MCP Specification:** https://modelcontextprotocol.io  
**A2A Protocol (Google):** https://github.com/google/a2a  
**FIPA-ACL Specification:** http://www.fipa.org/specs/fipa00061/  
**KQML Reference:** http://www.cs.umbc.edu/kqml/
