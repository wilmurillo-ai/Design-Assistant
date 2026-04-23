# open-stocki-internal Service Design

## 1. Overview

There is no separate "internal" HTTP service. OpenStocki Gateway directly calls the LangGraph remote agent services via `langgraph_sdk`, the same way `stocki-instant.py` does today. Quant output files (reports, images) are stored in Tencent Cloud COS. Task/run metadata is stored in MongoDB (shared between Gateway and LangGraph agents).

**Architecture**:
```
+---------------------+   langgraph_sdk   +------------------------+
| OpenStocki Gateway  |----------------->| LangGraph Agent Service |
| (FastAPI)           |                  | - Instant agent         |
|                     |                  | - Quant agent           |
| - Auth, quota       |                  +---+--+-----------------+
| - Task CRUD (PG)    |                     |  |
| - User management   |   COS SDK           |  | COS SDK
| - File serving      |<-----------+   +----+  |
| - Quant scheduling  |            |   |       |
+--------+------------+            v   v       |
         |                  +----------------+ |
         |   MongoDB SDK    | Tencent COS    | |
         |                  | /threads/      | |
         |                  +----------------+ |
         v                                     v
+------------------------------------------------+
| MongoDB                                        |
| thread_status collection (run metadata)        |
+------------------------------------------------+
```

**Key design**: Gateway is the only backend service. It calls LangGraph for analysis. Both Gateway and LangGraph agents read/write COS for quant files (reports, images) and MongoDB for run metadata. Each thread_id maps to a COS directory and a MongoDB document.

## 2. Instant Mode

Gateway calls LangGraph directly, same pattern as `stocki-instant.py`:

```python
client = get_client(url=INSTANT_AGENT_URL)
graph = RemoteGraph("InstantModeAgent", client=client)

thread = await client.threads.create()
response = await graph.ainvoke(
    input={"query": query, "messages": [], "time_prompt": time_prompt, "user_context": {}},
    config={"configurable": {"user_id": user_id, "thread_id": thread["thread_id"], "model_name": MODEL_NAME}},
)
answer = response.get("answer", "")
```

**Tools available to agent**:
- `search` - web search for financial information
- `quotes` - realtime stock/index/fx/commodity prices
- `news` - financial news aggregation (v2, can launch later)

**Output**: Natural language with markdown. Format conversion is the OpenClaw skill's responsibility.

## 3. Quant Mode

Gateway calls LangGraph quant agent asynchronously. The quant agent writes output files to COS and updates run metadata in MongoDB.

### 3.1 Submission

Gateway creates a thread_id, stores task in PostgreSQL, then calls LangGraph:

```python
client = get_client(url=QUANT_AGENT_URL)
graph = RemoteGraph("QuantAgent", client=client)

thread = await client.threads.create()
# Non-blocking: use runs API to submit async
run = await client.runs.create(
    thread_id=thread["thread_id"],
    assistant_id="QuantAgent",
    input={"query": query, "timezone": timezone, "user_context": {}},
    config={"configurable": {"user_id": user_id, "model_name": MODEL_NAME}},
)
```

### 3.2 Output Files (COS)

LangGraph quant agent writes report and image files to COS. Gateway reads COS to serve result files to users:

```
cos://bucket/threads/{thread_id}/
  runs/
    run_001/
      report.md                    # final report (images as ![](images/xxx.png))
      images/
        chart_001.png
        chart_002.png
    run_002/
      report.md
      images/
        chart_001.png
        strategy_comparison.png
```

### 3.3 Run Metadata (MongoDB)

Stored in MongoDB `thread_status` collection. Written and updated by the LangGraph quant agent. Gateway reads it to determine task state and available files. Replaces the previous file-based `status.json`.

**Document schema** (one document per thread_id):

```json
{
  "_id": "th_def456",
  "current_run": "run_002",
  "runs": [
    {
      "run_id": "run_001",
      "query": "backtest momentum strategy on CSI 300",
      "status": "success",
      "summary": "CSI 300 momentum strategy yields 18.3% annualized return, Sharpe 1.2, max drawdown -15%",
      "started_at": "2026-03-24T10:00:00+08:00",
      "completed_at": "2026-03-24T10:30:00+08:00",
      "error_message": null,
      "report": "runs/run_001/report.md",
      "files": [
        "runs/run_001/report.md",
        "runs/run_001/images/chart_001.png",
        "runs/run_001/images/chart_002.png"
      ]
    },
    {
      "run_id": "run_002",
      "query": "refine with small-cap filter, lookback 60 days",
      "status": "running",
      "summary": null,
      "started_at": "2026-03-24T11:00:00+08:00",
      "completed_at": null,
      "error_message": null,
      "report": null,
      "files": []
    }
  ]
}
```

Gateway reads this document to know:
- Is any run active?
- Each run's query, status, summary, and result files
- Path to the final report for each completed run

### 3.4 Multi-Run (Iterations)

A task (thread) can have multiple quant runs. Each run creates a new subdir under `runs/` in COS and appends to the `runs` array in MongoDB. Previous results remain accessible. Gateway sends each new iteration to the same thread_id so the quant agent has conversation context from prior runs.

### 3.5 Serial Execution

Quant only supports one run at a time globally. Gateway enforces this: if a quant run is already active (check own PostgreSQL), reject new submissions with HTTP 429.

## 4. Gateway Responsibilities

| Concern | How |
|---------|-----|
| Instant query | Call LangGraph instant agent directly via `langgraph_sdk` |
| Quant submission | Call LangGraph quant agent via `langgraph_sdk` runs API |
| Task CRUD | PostgreSQL (task name, thread_id, user_id, created_at) |
| Task status | Read MongoDB thread_status document (written by LangGraph agent) |
| Result files | Read from COS (written by LangGraph agent), serve to user |
| Quant concurrency | Serial queue in PostgreSQL, reject if busy |
| Auth | API Key / session token |
| Quota | Check + deduct before calling LangGraph |
| Format conversion | None (OpenClaw skill's job) |

## 5. Status Flow

```
User submits quant query
  |
  v
Gateway: check quota, check no active run
  -> Create task in PostgreSQL (task_id, thread_id, user_id)
  -> Call LangGraph quant agent (thread_id)
  -> Return task_id to user
  |
  v
User (or cron) polls task status
  -> Gateway reads MongoDB thread_status[thread_id]
  -> "running"  : tell user still working
  -> "success"  : return summary + report path, user can fetch files from COS
  -> "error"    : show error_message

User requests iteration
  -> Gateway: same thread_id, new LangGraph run
  -> Quant agent appends run_002 to MongoDB runs array
  -> Previous run_001 results stay in COS + MongoDB
```
