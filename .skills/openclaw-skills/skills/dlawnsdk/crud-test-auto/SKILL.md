---
name: crud-test-auto
description: Automated CRUD test generation for simple REST APIs (JSON only, synchronous operations). Use when you need quick smoke tests for Create/Read/Update/Delete operations with basic rollback. Generates Python test scripts from config file. Supports header/cookie auth, simple CRUD flows. NOT for: GraphQL, WebSocket, OAuth flows, batch operations, complex nested resources, or production environments. Best for: dev/staging smoke tests, regression checks, rapid prototyping. See LIMITATIONS.md for full scope.
---

# CRUD Test Automation

Automatically generate basic CRUD smoke tests for simple REST APIs.

**⚠️ Beta Software (v1.0.0)** - See [README.md](README.md) for maturity assessment and [LIMITATIONS.md](references/LIMITATIONS.md) for full constraints.

## Overview

This skill generates automated CRUD smoke tests from a configuration file. Users define API endpoints and parameters, and the skill creates Python test scripts with basic rollback.

**What it does well:**
- Quick CRUD smoke tests for simple REST APIs
- Config-driven test generation
- Basic resource cleanup (DELETE-based)
- Fast iteration for new endpoints

**What it does NOT do:**
- Complex test scenarios (use manual testing)
- Production-safe operations (dev/staging only)
- Side-effect rollback (notifications, points, webhooks remain)
- Comprehensive validation (only status + ID checks)

**⚠️ Read [LIMITATIONS.md](references/LIMITATIONS.md) before use!**

## Quick Start

### 1. Create Configuration File

Create `my-service-config.json`:

```json
{
  "service": {
    "name": "My Service",
    "api_base": "https://api.example.com",
    "auth": {
      "method": "header",
      "token_key": "Authorization",
      "token_prefix": "Bearer"
    }
  },
  "test_account": {
    "email": "test@example.com",
    "password": "password123"
  },
  "features": {
    "posts": {
      "name": "Blog Posts",
      "create": {
        "endpoint": "/posts",
        "method": "POST",
        "params": {
          "required": ["title", "content"],
          "optional": ["tags", "published"]
        },
        "id_field": "id"
      },
      "read": {
        "endpoint": "/posts",
        "method": "GET"
      },
      "update": {
        "endpoint": "/posts/{id}",
        "method": "PUT",
        "params": {
          "required": ["title", "content"]
        }
      },
      "delete": {
        "endpoint": "/posts/{id}",
        "method": "DELETE"
      }
    }
  }
}
```

### 2. Generate Tests

```bash
python3 scripts/generate_tests.py --config my-service-config.json
```

This creates:
- `test_posts_crud.py` - Full CRUD test suite
- `test_posts_create_delete.py` - Minimal Create→Delete transaction test

### 3. Run Tests

```bash
python3 test_posts_crud.py
```

Output:
```
======================================================================
🧪 CRUD Test: Blog Posts
======================================================================

[CREATE] Creating resource...
  ✅ CREATE success (ID: 123)

[READ] Reading resource...
  ✅ READ success (title: Test Post)

[UPDATE] Updating resource...
  ✅ UPDATE success

[DELETE] Deleting resource (rollback)...
  ✅ DELETE success

======================================================================
🎉 Test Complete: 4/4 passed (100%)
======================================================================
```

## Configuration Guide

See [CONFIG.md](references/CONFIG.md) for complete configuration options.

### Minimal Configuration

```json
{
  "service": {
    "api_base": "https://api.example.com"
  },
  "features": {
    "users": {
      "create": {"endpoint": "/users"},
      "delete": {"endpoint": "/users/{id}"}
    }
  }
}
```

### Authentication Methods

**Header-based (default):**
```json
{
  "auth": {
    "method": "header",
    "token_key": "Authorization",
    "token_prefix": "Bearer"
  }
}
```

**Cookie-based:**
```json
{
  "auth": {
    "method": "cookie",
    "cookie_name": "session"
  }
}
```

**Custom headers:**
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

## Test Patterns

### Pattern 1: Create → Delete (Minimal)

Tests only resource creation and cleanup:

```python
def test_create_delete():
    resource_id = None
    try:
        # CREATE
        resource_id = create_resource()
        assert resource_id is not None
    finally:
        # ROLLBACK
        if resource_id:
            delete_resource(resource_id)
```

**When to use:** Quick smoke test, rollback verification

### Pattern 2: Full CRUD

Tests all operations with rollback:

```python
def test_full_crud():
    resource_id = None
    try:
        # CREATE
        resource_id = create_resource()
        
        # READ
        data = read_resource(resource_id)
        assert data['title'] == 'Test'
        
        # UPDATE
        update_resource(resource_id, {'title': 'Updated'})
        
        # READ (verify update)
        data = read_resource(resource_id)
        assert data['title'] == 'Updated'
    finally:
        # DELETE (rollback)
        if resource_id:
            delete_resource(resource_id)
```

**When to use:** Complete feature verification

### Pattern 3: Edge Cases

Tests error conditions:

```python
def test_edge_cases():
    # Missing required field
    result = create_resource(title="", content="test")
    assert result['error'] == 'title_required'
    
    # Invalid ID
    result = read_resource("invalid-id")
    assert result['status'] == 404
```

**When to use:** Error handling validation

## Advanced Usage

### Custom Validation

Add custom validation functions to generated tests:

```python
def custom_validator(response):
    """Add your own validation logic"""
    assert response['status'] == 'published'
    assert len(response['tags']) > 0
    return True
```

### Multiple Environments

Use different configs for different environments:

```bash
# Development
python3 scripts/generate_tests.py --config dev-config.json

# Staging
python3 scripts/generate_tests.py --config staging-config.json

# Production (read-only tests)
python3 scripts/generate_tests.py --config prod-config.json --read-only
```

### Batch Testing

Test multiple features at once:

```bash
python3 scripts/run_all_tests.py --config my-config.json
```

## Generated Files

The skill generates these files:

```
test_<feature>_crud.py          # Full CRUD test
test_<feature>_create_delete.py # Minimal transaction test
test_results_<timestamp>.json   # Test results
test_report_<timestamp>.html    # Visual report
```

## Workflow

See [WORKFLOW.md](references/WORKFLOW.md) for detailed step-by-step guides:
- API analysis workflow
- Test generation workflow
- Debugging failed tests
- Report generation

## Troubleshooting

**Tests fail with authentication error:**
- Verify auth configuration in config file
- Check token/cookie validity
- Test login endpoint manually

**Rollback not working:**
- Verify delete endpoint configuration
- Check id_field extraction path
- Ensure delete endpoint accepts the correct ID format

**Generated tests don't match API:**
- Re-analyze API with [API-ANALYSIS.md](references/API-ANALYSIS.md)
- Update config file with correct parameters
- Regenerate tests

## Examples

See [EXAMPLES.md](references/EXAMPLES.md) for real-world examples:
- E-commerce API (products, orders, reviews)
- Social media API (posts, comments, likes)
- SaaS API (users, projects, tasks)
- Golf app API (joins, communities, profiles)

## Scripts Reference

- `generate_tests.py` - Generate test files from config
- `run_all_tests.py` - Execute all generated tests
- `report_generator.py` - Create visual test reports
- `validate_config.py` - Validate configuration file

## Best Practices

1. **Start small** - Test Create→Delete first, then add Read/Update
2. **Always rollback** - Never leave test data in production
3. **Use descriptive names** - Name features clearly in config
4. **Version control config** - Track changes to test configurations
5. **Separate environments** - Use different configs for dev/staging/prod

## Limitations

**Supported:**
- REST APIs with JSON responses only
- Synchronous CRUD operations
- Simple header/cookie authentication
- Single resource operations

**NOT Supported:**
- GraphQL, WebSocket, gRPC
- OAuth flows (manual token required)
- Batch operations
- File uploads
- Nested resource creation
- Async/job-based operations

**Rollback limitations:**
- Only deletes the resource record
- Does NOT revert: emails, notifications, points, webhooks, logs
- May fail on soft-delete or dependent resources

**Test quality:**
- Basic validation only (status code + ID presence)
- No schema validation
- No field equality checks
- No permission/auth boundary testing

**See [LIMITATIONS.md](references/LIMITATIONS.md) for complete details.**

## See Also

- [CONFIG.md](references/CONFIG.md) - Complete configuration reference
- [WORKFLOW.md](references/WORKFLOW.md) - Step-by-step guides
- [API-ANALYSIS.md](references/API-ANALYSIS.md) - How to analyze APIs
- [EXAMPLES.md](references/EXAMPLES.md) - Real-world examples
