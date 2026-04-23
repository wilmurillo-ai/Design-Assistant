-- agent-memory SQLite Schema
-- 所有结构化维度 + 关联关系存储

-- 主表：记忆记录
CREATE TABLE IF NOT EXISTS memories (
    memory_id       TEXT PRIMARY KEY,           -- 唯一编码 T20260411.213742_P01_rag_D04
    time_id         TEXT NOT NULL,              -- T20260411.213742
    time_ts         INTEGER NOT NULL,           -- Unix 时间戳（秒），用于范围查询
    person_id       TEXT NOT NULL,              -- P01
    nature_id       TEXT NOT NULL,              -- D04
    content         TEXT NOT NULL,              -- 对话内容/摘要
    content_hash    TEXT NOT NULL,              -- 内容 SHA256，防重复
    importance      TEXT DEFAULT 'medium',      -- high / medium / low
    is_aggregated   INTEGER DEFAULT 0,          -- 是否为聚合记录
    source_count    INTEGER DEFAULT 1,          -- 聚合了多少条原始记录
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

-- 主题关联（一条记录可有多个主题）
CREATE TABLE IF NOT EXISTS memory_topics (
    memory_id       TEXT NOT NULL,
    topic_code      TEXT NOT NULL,              -- ai.rag.vdb
    is_primary      INTEGER DEFAULT 1,          -- 主主题 vs 次主题
    FOREIGN KEY (memory_id) REFERENCES memories(memory_id),
    PRIMARY KEY (memory_id, topic_code)
);

-- 知识类型关联（一条记录可有多个知识类型）
CREATE TABLE IF NOT EXISTS memory_knowledge (
    memory_id       TEXT NOT NULL,
    knowledge_id    TEXT NOT NULL,              -- K01
    FOREIGN KEY (memory_id) REFERENCES memories(memory_id),
    PRIMARY KEY (memory_id, knowledge_id)
);

-- 工具关联（一条记录可涉及多个工具）
CREATE TABLE IF NOT EXISTS memory_tools (
    memory_id       TEXT NOT NULL,
    tool_id         TEXT NOT NULL,              -- t_lc
    FOREIGN KEY (memory_id) REFERENCES memories(memory_id),
    PRIMARY KEY (memory_id, tool_id)
);

-- 关联关系（跨记录连接）
CREATE TABLE IF NOT EXISTS memory_links (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id       TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    link_type       TEXT NOT NULL,              -- temporal(时间相邻) | topic(主题相同) | cross_port(跨端口) | explicit(显式引用) | compressed_from(压缩来源) | compressed_to(压缩目标)
    weight          REAL DEFAULT 1.0,           -- 关联权重，用于衰减
    reason          TEXT,                       -- 关联原因
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    FOREIGN KEY (source_id) REFERENCES memories(memory_id),
    FOREIGN KEY (target_id) REFERENCES memories(memory_id)
);

-- 对话窗口（连续对话分组）
CREATE TABLE IF NOT EXISTS windows (
    window_id       TEXT PRIMARY KEY,
    start_time      INTEGER NOT NULL,
    end_time        INTEGER,
    person_id       TEXT NOT NULL,
    message_count   INTEGER DEFAULT 0,
    topic_dominant  TEXT                        -- 该窗口的主要主题
);

-- 窗口-记录映射
CREATE TABLE IF NOT EXISTS window_memories (
    window_id       TEXT NOT NULL,
    memory_id       TEXT NOT NULL,
    seq_order       INTEGER NOT NULL,          -- 在窗口中的顺序
    FOREIGN KEY (window_id) REFERENCES windows(window_id),
    FOREIGN KEY (memory_id) REFERENCES memories(memory_id),
    PRIMARY KEY (window_id, memory_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_mem_time ON memories(time_ts);
CREATE INDEX IF NOT EXISTS idx_mem_person ON memories(person_id);
CREATE INDEX IF NOT EXISTS idx_mem_nature ON memories(nature_id);
CREATE INDEX IF NOT EXISTS idx_mem_importance ON memories(importance);
CREATE INDEX IF NOT EXISTS idx_mem_time_person ON memories(time_ts, person_id);
CREATE INDEX IF NOT EXISTS idx_mem_time_importance ON memories(time_ts, importance);
CREATE INDEX IF NOT EXISTS idx_mem_hash ON memories(content_hash);
CREATE INDEX IF NOT EXISTS idx_mem_aggregated ON memories(is_aggregated);
CREATE INDEX IF NOT EXISTS idx_link_source ON memory_links(source_id);
CREATE INDEX IF NOT EXISTS idx_link_target ON memory_links(target_id);
CREATE INDEX IF NOT EXISTS idx_link_type ON memory_links(link_type);
CREATE INDEX IF NOT EXISTS idx_link_source_type ON memory_links(source_id, link_type);
CREATE INDEX IF NOT EXISTS idx_topic_code ON memory_topics(topic_code);
CREATE INDEX IF NOT EXISTS idx_topic_memory ON memory_topics(memory_id, is_primary);

-- 待办任务状态（从 D07/todo 记忆中提取的任务）
CREATE TABLE IF NOT EXISTS tasks (
    task_id         TEXT PRIMARY KEY,           -- 自动生成: task_<memory_id>_<seq>
    memory_id       TEXT NOT NULL,              -- 来源记忆 ID
    title           TEXT NOT NULL,              -- 任务标题
    status          TEXT DEFAULT 'pending',     -- pending / in_progress / done / overdue
    assignee        TEXT DEFAULT 'ai',          -- ai / user
    deadline        INTEGER,                    -- 截止时间戳，可空
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    completed_at    INTEGER,                    -- 完成时间
    topic_code      TEXT,                       -- 关联主题
    FOREIGN KEY (memory_id) REFERENCES memories(memory_id)
);

CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_task_memory ON tasks(memory_id);
CREATE INDEX IF NOT EXISTS idx_task_deadline ON tasks(deadline);
