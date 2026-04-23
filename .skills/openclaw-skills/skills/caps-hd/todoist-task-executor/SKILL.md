---
name: todoist-task-executor
description: Todoist automated task executor. Automatically executes tasks marked with 【执行中】 in your project, supports fetching comment attachments, downloading files, analyzing content, and logging execution reports. Use when you need to: automatically execute Todoist tasks on a schedule, process task attachments, or track task status.
---

# Todoist Task Executor

An automated task executor that polls a Todoist project for tasks marked with 【执行中】, downloads and analyzes attachments, and logs execution reports.

## ⚠️ First-Time Setup

### 1. Configure Todoist Token

```bash
# Get your token: https://todoist.com/app/settings/integrations/developer
todoist auth <your_api_token>
```

Token is stored at `~/.config/todoist-cli/config.json`

### 2. Verify Your Project

```bash
todoist projects   # Confirm your project exists
```

## Cron Configuration

- **Cron Job ID**: `a6fb7d10-e5c5-410a-9ab7-58077bea16dc`
- **Interval**: Every 30 minutes
- **Status**: ✅ Enabled

## Cron Management

```bash
# Manual trigger
openclaw cron run a6fb7d10-e5c5-410a-9ab7-58077bea16dc

# View execution history
openclaw cron runs --id a6fb7d10-e5c5-410a-9ab7-58077bea16dc --limit 3

# List all cron jobs
openclaw cron list
```

## Execution Flow

```
1. Fetch tasks from project: todoist tasks -p "<project_name>" --json
2. Filter tasks with 【执行中】 in title
3. Fetch comment attachments for the task
4. Download image to /tmp/openclaw/report.jpg
5. Analyze content and execute
6. On completion:
   - Success: restore title + todoist done + add report comment
   - Failure: update title to 【执行失败】 + add failure comment
```

## Task Title Status Convention

| Status | Title Format | Description |
|--------|--------------|-------------|
| Pending | `Task Name` | Waiting for cron execution |
| Running | `Task Name【执行中】` | Cron has picked up, executing |
| Failed | `Task Name【执行失败】` | Execution failed, needs review |
| Done | `Task Name` + Completed | Successfully completed |

## Creating a New Cron Job

```bash
openclaw cron add \
  --name "todoist-task-executor" \
  --every 30m \
  --message "Execute Todoist task automation:
1. Fetch tasks: todoist tasks -p \"<project_name>\" --json
2. Filter tasks with 【执行中】 in title
3. Execute task content
4. Mark as done or failed on completion" \
  --no-deliver
```

## Fetching Task Comment Attachments

```javascript
// Attachments are stored in comments, not task description
const https = require('https');
const fs = require('fs');
const home = process.env.USERPROFILE || process.env.HOME;
const cfg = JSON.parse(fs.readFileSync(home + '/.config/todoist-cli/config.json', 'utf8'));
const token = cfg.token;
const taskId = '<task_id>';

const req = https.request({
  hostname: 'api.todoist.com', port: 443,
  path: '/api/v2/comments?task_id=' + taskId,
  headers: { 'Authorization': 'Bearer ' + token }
}, (res) => {
  let d = '';
  res.on('data', c => d += c);
  res.on('end', () => {
    const r = JSON.parse(d);
    r.results.forEach(c => {
      if (c.file_attachment) {
        console.log('File:', c.file_attachment.file_name);
        console.log('Image URL:', c.file_attachment.image);
      }
    });
  });
});
req.end();
```

## Common Commands

```bash
# List tasks
todoist tasks -p "<project_name>"

# Update title
todoist update <task_id> --content "<new_title>"

# Mark complete
todoist done <task_id>

# Add comment
todoist comment <task_id> "<report_content>"
```

## Known Limitations

- **Attachment Downloads**: Todoist files are hosted on CloudFront CDN, which may be inaccessible in some network environments. If download fails, note in the comment that the user should send the attachment directly.
