# Stocki System Architecture

```
                          External Users
            ______________________|______________________
           |                      |                      |
     [stocki.ai]          [OpenClaw/ClawBot]      [Broker API]
      Web Frontend          WeChat users           B2B clients
           |                      |                      |
           v                      v                      v
    +-------------+     +------------------+    +------------------+
    | llm-orch    |     | open-stocki      |    | open-stocki      |
    | (streaming  |     | skill            |    | gateway          |
    |  display)   |     | (OpenClaw plugin)|    | (API Key auth)   |
    +------+------+     +--------+---------+    +--------+---------+
           |                     |                       |
           |                     v                       |
           |            +------------------+             |
           |            | open-stocki      |             |
           |            | gateway          |<------------+
           |            | (FastAPI)        |
           |            | - Auth + Quota   |
           |            | - Task mgmt      |
           |            | - PostgreSQL     |
           |            +--------+---------+
           |                     |
           |                     | langgraph_sdk
           |                     v
           |            +------------------+
           +----------->| stocki-internal  |
                        | (LangGraph)      |
                        | - Instant agent  |
                        | - Quant agent    |
                        +--------+---------+
                                 |
                        +--------+---------+
                        |   Data Layer     |
                        | - MongoDB (meta) |
                        | - COS (files)    |
                        +------------------+
```

## Three External Paths


| #   | Frontend                | Middleware                   | Notes                                |
| --- | ----------------------- | ---------------------------- | ------------------------------------ |
| 1   | stocki.ai (2C web)      | llm-orch -> stocki-internal  | Streaming display, direct connection |
| 2   | OpenClaw skill (WeChat) | open-stocki skill -> gateway | Via ClawBot, WeChat-friendly output  |
| 3   | Broker API (B2B)        | gateway directly             | API Key auth, programmatic access    |


