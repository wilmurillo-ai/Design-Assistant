# Limitations & Known Issues

**Important:** Understand these limitations before using this skill in production.

---

## Supported Scope

### ✅ What This Skill Supports

**API Style:**
- REST APIs with JSON responses
- Synchronous operations only
- Simple CRUD operations

**Authentication:**
- Header-based (Bearer, custom headers)
- Cookie-based
- No OAuth flow automation (tokens must be obtained manually)

**Operations:**
- Create single resource
- Read list/detail
- Update single resource
- Delete single resource

**Rollback:**
- Resource deletion via DELETE endpoint
- **Only** removes the created resource record

---

## ❌ What This Skill Does NOT Support

### Not Supported Features

1. **GraphQL APIs**
2. **WebSocket / Real-time APIs**
3. **Batch operations** (bulk create/update/delete)
4. **File uploads** (multipart/form-data)
5. **OAuth authentication flows**
6. **Nested resource creation** (e.g., create user → create profile)
7. **Async operations** (job queues, background processing)
8. **Pagination testing**
9. **Search/filtering validation**
10. **Rate limiting handling**

---

## ⚠️ Rollback Limitations

### What Rollback DOES

- Calls DELETE endpoint
- Removes the resource record from database

### What Rollback DOES NOT Do

**Side effects are NOT reverted:**
- ❌ Notifications sent
- ❌ Emails dispatched
- ❌ Points/credits awarded
- ❌ Webhooks triggered
- ❌ External integrations
- ❌ Audit logs
- ❌ File system changes
- ❌ Cache updates
- ❌ Search index updates

**Example:**
```python
# Test creates a post
create_post()  # ✅ Post created
               # ❌ Email notification sent
               # ❌ 50 points awarded
               # ❌ Webhook to Slack triggered

# Rollback deletes post
delete_post()  # ✅ Post deleted
               # ❌ Email NOT recalled
               # ❌ Points NOT reverted
               # ❌ Slack message remains
```

**Recommendation:**
- Use test accounts with disabled notifications
- Use separate test environment
- Mock external integrations in test mode

---

## 🐛 Known Edge Cases

### 1. Soft Delete

**Problem:** Some APIs use soft delete (sets `deleted=true`), not hard delete.

**Impact:** Repeated tests may fail due to unique constraints on "deleted" records.

**Workaround:**
- Use unique test data each time (e.g., timestamp suffix)
- Clean up soft-deleted records manually
- Configure hard delete endpoint if available

### 2. Eventual Consistency

**Problem:** Some systems (e.g., distributed databases) have propagation delay.

**Impact:** 
- Create → Read may not find the resource immediately
- Delete → Read may still return the resource

**Workaround:**
- Add delay after create/delete (not implemented yet)
- Use `--eventual-consistency` flag (future feature)
- Retry read with backoff

### 3. Resource Dependencies

**Problem:** Deleting a resource may fail if other resources reference it.

**Impact:** Rollback fails, leaves test data.

**Example:**
```
User → Posts → Comments
```
Deleting User fails if Posts exist.

**Workaround:**
- Delete in reverse order (Comments → Posts → User)
- Use cascade delete (if API supports)
- Manual cleanup required

### 4. ID Extraction Complexity

**Problem:** Response structure varies widely.

**Current support:**
```json
// Simple (✅ Supported)
{ "id": 123 }

// Nested (✅ Supported)
{ "data": { "id": 123 } }

// Multiple IDs (❌ NOT supported)
{ "user_id": 1, "profile_id": 2 }

// Array response (❌ NOT supported)
[{ "id": 1 }, { "id": 2 }]
```

**Workaround:**
- Ensure API returns single resource with clear ID
- Use detail endpoint if list endpoint returns array

### 5. Authentication Token Expiry

**Problem:** Long-running tests may exceed token validity.

**Impact:** Tests fail mid-execution.

**Workaround:**
- Use long-lived test tokens
- Implement token refresh (not supported yet)
- Split tests into smaller batches

---

## 🚨 Safety Concerns

### Production Environment Risk

**Risk:** Accidentally running write tests against production.

**Mitigation:**
1. **Always use test/staging environment**
2. Use `--read-only` flag (future feature)
3. Separate config files per environment
4. Add environment validation in config

**Example safety check (manual):**
```json
{
  "service": {
    "api_base": "https://api.production.com",
    "environment": "production",  // ⚠️ DANGEROUS
    "allow_write": false          // Safety flag
  }
}
```

### Data Corruption

**Risk:** Test failures leave orphaned/corrupted data.

**Impact:**
- Database pollution
- Broken relationships
- Quota consumption

**Mitigation:**
- Always use isolated test accounts
- Regular test database cleanup
- Use transaction-safe test environments
- Monitor orphaned resources

---

## 📊 Test Quality Limitations

### What Generated Tests Validate

**Currently:**
- ✅ HTTP status codes (200, 201, 404)
- ✅ Resource ID presence
- ✅ Basic CRUD flow completion

**NOT validated (yet):**
- ❌ Response schema correctness
- ❌ Field values accuracy
- ❌ Timestamp validation
- ❌ Relationship integrity
- ❌ Permission boundaries
- ❌ Error message correctness

**Example:**
```python
# Current (weak)
assert response.status_code == 200
assert response['id'] is not None

# Needed (strong)
assert response.status_code == 200
assert response['id'] is not None
assert response['title'] == expected_title
assert response['created_at'] <= now()
assert response['author']['id'] == user_id
```

---

## 🎯 Realistic Use Cases

### ✅ Good Fit

- **Smoke testing** - Verify basic CRUD works
- **Regression testing** - Ensure endpoints remain functional
- **Quick validation** - Test new API endpoints
- **Local development** - Rapid iteration testing
- **CI/CD sanity checks** - Pre-deployment verification

### ❌ Not a Good Fit

- **Comprehensive QA** - Needs manual test design
- **Performance testing** - No load/stress support
- **Security testing** - No auth/authz validation
- **Integration testing** - No cross-service orchestration
- **User acceptance testing** - Requires human judgment

---

## 🔮 Future Improvements

Planned features to address limitations:

1. **Safety Mode**
   - `--dry-run` flag
   - `--read-only` flag
   - Environment allowlist

2. **Better Assertions**
   - Schema validation
   - Field equality checks
   - Timestamp validation

3. **Resilience**
   - Retry logic
   - Eventual consistency handling
   - Token refresh

4. **Cleanup Strategies**
   - Cascade delete
   - Dependency resolution
   - Orphan detection

5. **Advanced Features**
   - Pagination testing
   - Filtering validation
   - Batch operations

---

## 📝 Summary

**Use this skill when:**
- You need quick CRUD smoke tests
- Your API is simple REST + JSON
- You have a clean test environment
- You understand rollback limitations

**Do NOT use when:**
- Production safety is critical
- Complex nested resources
- Async/eventual consistency
- Comprehensive test coverage needed

**Best practice:**
- Test → Dev → Staging → (never Production)
- Isolated test accounts
- Regular manual cleanup
- Combine with manual testing

---

**Last updated:** 2026-03-25  
**Skill version:** 1.1.0
