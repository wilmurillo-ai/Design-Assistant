# Configuration Reference

Complete guide to configuration file options.

## Table of Contents

- [Service Configuration](#service-configuration)
- [Authentication](#authentication)
- [Test Account](#test-account)
- [Features](#features)
- [Response Handling](#response-handling)
- [Examples](#examples)

---

## Service Configuration

```json
{
  "service": {
    "name": "My Service",
    "api_base": "https://api.example.com",
    "timeout": 30,
    "retry": 3
  }
}
```

**Fields:**
- `name` (string, required): Service display name
- `api_base` (string, required): Base URL for all API calls
- `timeout` (integer, optional): Request timeout in seconds (default: 10)
- `retry` (integer, optional): Number of retries on failure (default: 0)

---

## Authentication

### Header-Based (Default)

```json
{
  "auth": {
    "method": "header",
    "token_key": "Authorization",
    "token_prefix": "Bearer",
    "user_id_key": "x-user-id"
  }
}
```

**Fields:**
- `method`: "header"
- `token_key`: Header key for token (default: "Authorization")
- `token_prefix`: Prefix for token value (default: "Bearer")
- `user_id_key`: Optional header for user ID

### Cookie-Based

```json
{
  "auth": {
    "method": "cookie",
    "cookie_name": "session"
  }
}
```

### Custom Headers

```json
{
  "auth": {
    "method": "custom",
    "headers": {
      "x-access-token": "{token}",
      "x-access-id": "{user_id}"
    }
  }
}
```

Use `{token}` and `{user_id}` placeholders.

### No Authentication

```json
{
  "auth": {
    "method": "none"
  }
}
```

---

## Test Account

```json
{
  "test_account": {
    "email": "test@example.com",
    "password": "password123",
    "login_endpoint": "/auth/login",
    "token_path": "data.token",
    "user_id_path": "data.user.id"
  }
}
```

**Fields:**
- `email` (string, required): Test account email
- `password` (string, required): Test account password
- `login_endpoint` (string, optional): Login API endpoint (default: "/login")
- `token_path` (string, optional): JSON path to extract token (default: "token")
- `user_id_path` (string, optional): JSON path to extract user ID (default: "user_id")

**JSON Path Examples:**
- `"token"` → `response['token']`
- `"data.token"` → `response['data']['token']`
- `"auth.access_token"` → `response['auth']['access_token']`

---

## Features

Each feature represents a resource type (e.g., posts, users, products).

```json
{
  "features": {
    "posts": {
      "name": "Blog Posts",
      "create": { ... },
      "read": { ... },
      "update": { ... },
      "delete": { ... }
    }
  }
}
```

### CREATE Operation

```json
{
  "create": {
    "endpoint": "/posts",
    "method": "POST",
    "params": {
      "required": ["title", "content"],
      "optional": ["tags", "published"]
    },
    "id_field": "id",
    "test_data": {
      "title": "[AutoTest] Test Post",
      "content": "This is a test post"
    }
  }
}
```

**Fields:**
- `endpoint` (string, required): API endpoint
- `method` (string, optional): HTTP method (default: "POST")
- `params.required` (array, required): Required parameters
- `params.optional` (array, optional): Optional parameters
- `id_field` (string, required): JSON path to extract resource ID
- `test_data` (object, optional): Default test data

### READ Operation

```json
{
  "read": {
    "endpoint": "/posts",
    "method": "GET",
    "detail_endpoint": "/posts/{id}",
    "list_path": "data.items"
  }
}
```

**Fields:**
- `endpoint` (string, required): List endpoint
- `method` (string, optional): HTTP method (default: "GET")
- `detail_endpoint` (string, optional): Single resource endpoint (use `{id}`)
- `list_path` (string, optional): JSON path to extract list (default: root array)

### UPDATE Operation

```json
{
  "update": {
    "endpoint": "/posts/{id}",
    "method": "PUT",
    "params": {
      "required": ["title"],
      "optional": ["content", "tags"]
    }
  }
}
```

**Fields:**
- `endpoint` (string, required): Update endpoint (use `{id}`)
- `method` (string, optional): HTTP method (default: "PUT")
- `params`: Same as CREATE

### DELETE Operation

```json
{
  "delete": {
    "endpoint": "/posts/{id}",
    "method": "DELETE"
  }
}
```

**Fields:**
- `endpoint` (string, required): Delete endpoint (use `{id}`)
- `method` (string, optional): HTTP method (default: "DELETE")

---

## Response Handling

```json
{
  "response": {
    "format": "json",
    "success_codes": [200, 201],
    "success_field": "ok",
    "error_field": "error"
  }
}
```

**Fields:**
- `format` (string, optional): Response format (default: "json")
- `success_codes` (array, optional): HTTP codes for success (default: [200, 201])
- `success_field` (string, optional): Field to check for success (e.g., "ok")
- `error_field` (string, optional): Field containing error message

---

## Complete Example

```json
{
  "service": {
    "name": "Greenlight Golf",
    "api_base": "http://3.34.82.231:3560",
    "timeout": 15
  },
  
  "auth": {
    "method": "custom",
    "headers": {
      "x-access-token": "{token}",
      "x-access-id": "{user_id}"
    }
  },
  
  "test_account": {
    "email": "test@example.com",
    "password": "test1234",
    "login_endpoint": "/login",
    "token_path": "auth_token",
    "user_id_path": "id"
  },
  
  "features": {
    "community": {
      "name": "Community Posts",
      "create": {
        "endpoint": "/auth/community/post/basic",
        "params": {
          "required": ["userId", "content", "category"],
          "optional": ["media"]
        },
        "id_field": "data",
        "test_data": {
          "content": "[AutoTest] Test post",
          "category": "free"
        }
      },
      "read": {
        "endpoint": "/auth/community/list",
        "detail_endpoint": "/auth/community/detail",
        "list_path": "data.list"
      },
      "update": {
        "endpoint": "/auth/community/post/update",
        "params": {
          "required": ["userId", "community_id", "content"]
        }
      },
      "delete": {
        "endpoint": "/auth/community/post/delete",
        "method": "POST"
      }
    }
  },
  
  "response": {
    "success_field": "ok",
    "error_field": "message"
  }
}
```
