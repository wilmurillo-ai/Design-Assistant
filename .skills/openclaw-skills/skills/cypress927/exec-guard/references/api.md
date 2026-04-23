# cmd_exec API Reference

## CLI Mode

Read JSON from stdin, output JSON response.

### Basic Usage

```bash
echo '{"command": "echo hello"}' | ./cmd_exec_linux
```

### All Parameters

```bash
echo '{
  "command": "node app.js",
  "working_dir": "/path/to/project",
  "timeout_seconds": 60,
  "run_in_background": true,
  "watch_duration_seconds": 5,
  "env": {
    "NODE_ENV": "production",
    "API_KEY": "secret"
  }
}' | ./cmd_exec_linux
```

## HTTP Server Mode

### Start Server

```bash
# Default port 8080
./cmd_exec_linux -server

# Custom port
./cmd_exec_linux -server -port 9000

# Limit max processes
./cmd_exec_linux -server -port 8080 -max-processes 50
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/exec` | Execute command |
| GET | `/process/{pid}` | Query status |
| GET | `/process/{pid}/logs` | Get logs |
| DELETE | `/process/{pid}` | Kill process |
| GET | `/health` | Health check |

### POST /exec

**Request:**

```json
{
  "command": "string (required)",
  "working_dir": "string (optional)",
  "timeout_seconds": "number (optional, default 30)",
  "run_in_background": "boolean (optional, default false)",
  "watch_duration_seconds": "number (optional, background only)",
  "env": "object (optional)"
}
```

**Response:**

```json
{
  "status": "success|failed|timeout|killed|running",
  "exit_code": "number",
  "stdout": "string",
  "stderr": "string",
  "system_message": "string"
}
```

### GET /process/{pid}

**Response:**

```json
{
  "pid": 12345,
  "status": "running|completed|failed",
  "exit_code": 0,
  "command": "python train.py",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "",
  "watch_duration_seconds": 0,
  "watch_completed": false
}
```

### GET /process/{pid}/logs

**Response:**

```json
{
  "pid": 12345,
  "status": "running",
  "exit_code": -1,
  "command": "python train.py",
  "start_time": "2024-01-15T10:30:00Z",
  "stdout": "Training started...",
  "stderr": ""
}
```

### DELETE /process/{pid}

**Response:**

```json
{
  "status": "success",
  "message": "process 12345 terminated"
}
```

### GET /health

**Response:**

```json
{
  "status": "healthy"
}
```

## Error Responses

| HTTP Code | Error |
|-----------|-------|
| 400 | Invalid request parameters |
| 404 | Process not found |
| 405 | Method not allowed |
| 500 | Internal error |

```json
{
  "error": "process not found"
}
```