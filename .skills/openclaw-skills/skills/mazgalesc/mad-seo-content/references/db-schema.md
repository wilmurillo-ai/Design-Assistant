# SQLite Content Calendar Schema

This document outlines the expected schema for the SQLite database used by Mad SEO Manager to track the content lifecycle (`/root/.openclaw/shared/mad_seo.db`).

## Table: `content_calendar`

The `content_calendar` table stores all planned, drafted, and published content across the entire pipeline.

### Schema Definition
```sql
CREATE TABLE IF NOT EXISTS content_calendar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    pillar TEXT NOT NULL,
    funnel_stage TEXT NOT NULL CHECK (funnel_stage IN ('TOFU', 'MOFU', 'BOFU')),
    status TEXT NOT NULL CHECK (status IN ('Idea', 'Draft', 'Review', 'Scheduled', 'Published', 'Repurposed')),
    scheduled_date DATE,
    published_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Required Agent Operations

#### 1. Inserting New Ideas (Via `mad_seo:plan_content`)
When planning content, the agent should insert records with status `Idea`.
```sql
INSERT INTO content_calendar (title, pillar, funnel_stage, status, scheduled_date)
VALUES ('Title', 'Core Pillar', 'TOFU', 'Idea', '2026-05-01');
```

#### 2. Updating Status (Via Content Generation or Repurposing)
When drafts are completed or repurposed, update the status and `updated_at` timestamp.
```sql
UPDATE content_calendar 
SET status = 'Repurposed', updated_at = CURRENT_TIMESTAMP 
WHERE id = [ID] OR title = '[Exact Title]';
```

#### 3. Reviewing the Calendar
The agent can query this database at any time to review what needs to be drafted next or what gaps exist in the funnel (e.g., finding out there is no BOFU content scheduled this month).
