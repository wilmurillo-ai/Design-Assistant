# Database Schema

## Tables

### `todo_lists`

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(255) | NOT NULL | List name (e.g., "Job Search", "Home") |
| owner_agent | VARCHAR(100) | NOT NULL | Agent that owns this list (e.g., "researcher") |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |

Unique constraint on `(name, owner_agent)`.

### `todo_categories`

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| list_id | INTEGER | NOT NULL, FK → todo_lists(id) ON DELETE CASCADE | Parent list |
| name | VARCHAR(255) | NOT NULL | Category name |
| color | VARCHAR(7) | NULL | Optional hex color (e.g., #FF5733) |

Unique constraint on `(list_id, name)`.

### `todos`

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| list_id | INTEGER | NOT NULL, FK → todo_lists(id) ON DELETE CASCADE | Parent list |
| category_id | INTEGER | NULL, FK → todo_categories(id) ON DELETE SET NULL | Optional category |
| title | VARCHAR(500) | NOT NULL | Todo title |
| description | TEXT | NULL | Optional description |
| priority | VARCHAR(10) | DEFAULT 'medium' | low / medium / high |
| due_date | DATE | NULL | Optional due date |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| archived | BOOLEAN | DEFAULT FALSE | Archive status |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation time |
| completed_at | TIMESTAMP | NULL | When marked complete |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update time |

## Indexes

- `idx_todos_list_id` ON `todos(list_id)`
- `idx_todos_completed` ON `todos(completed)`
- `idx_todos_due_date` ON `todos(due_date)`
- `idx_todos_priority` ON `todos(priority)`

## Cross-Agent Access

Cross-agent queries require explicit `--request-from` flag. The CLI logs these
accesses to an audit table:

### `todo_access_log`

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| requesting_agent | VARCHAR(100) | NOT NULL | Agent making the request |
| target_agent | VARCHAR(100) | NOT NULL | Agent whose list is being accessed |
| list_id | INTEGER | NOT NULL, FK → todo_lists(id) | List accessed |
| accessed_at | TIMESTAMP | DEFAULT NOW() | When access occurred |
