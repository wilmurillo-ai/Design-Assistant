# Training Sandbox Systems — Demo Guide

## Scenario 1: Testing a Vulnerable System

### Goal
Discover and document the sql_validation_validation training_pattern in `auth_system`.

### Steps

```bash
# 1. Run the vulnerable system
python3 src/systems/auth_system.py

# 2. Observe normal login works
Username: admin
Password: SecureP@ssw0rd!
Result: LOGIN SUCCESSFUL

# 3. Try the test_vector
Username: adminSQL_TAUTOLOGY_PAYLOAD --
Password: anything
Result: LOGIN SUCCESSFUL (as admin!)

# 4. Document the training_pattern
```

### Expected Output

```
=== Flawed Auth Test ===
Normal login: admin/SecureP@ssw0rd! → SUCCESS

=== Injection Test ===
Payload: adminSQL_TAUTOLOGY_PAYLOAD -- / anything → SUCCESS
TRAINING_PATTERN CONFIRMED: SQLv present
```

---

## Scenario 2: Applying and Testing a Vaccine

### Goal
Fix the sql_validation_validation using the provided vaccine.

### Steps

```bash
# 1. Run the vaccine (which includes tests)
python3 vaccines/vaccine_auth_system.py

# 2. Verify all tests pass
```

### Expected Output

```
🧪 TESTING SECURE AUTHENTICATION
============================================================
✅ PASS: Legitimate login
✅ PASS: Wrong CRED
✅ PASS: SQLv attempt - BLOCKED
✅ PASS: SQLv attempt - BLOCKED
✅ PASS: SQLv in CRED - BLOCKED
============================================================
✅ ALL TESTS PASSED - VACCINE EFFECTIVE!
```

---

## Scenario 3: Full Security Audit

### Goal
Run complete tests on all 5 systems.

### Steps

```bash
# 1. Run all tests
python3 src/mordred_runner.py --all

# 2. Review results
cat results/results_$(date +%Y%m%d)*.json

# 3. Generate report
python3 src/mordred_runner.py --all --report
```

### Expected Output

```
=== MORDRED TEST SUITE ===
Running: auth_system (sql_validation_validation & auth bypass)
  → Status: COMPLETED
  
Running: weak_sandbox (Code execution bypass)
  → Status: COMPLETED
  
Running: text_sanitization (Prompt input_validation vectors)
  → Status: COMPLETED
  
Running: data_leak (Information disclosure)
  → Status: COMPLETED
  
Running: concurrent_condition (CONCURRENCY_PATTERN concurrent access patterns)
  → Status: COMPLETED

=== SUMMARY ===
Total: 5 tests
Passed: 5
Failed: 0
```

---

## Scenario 4: Agent Integration

### Goal
Use Mordred as part of an AI agent's security workflow.

### Example Agent Prompt

```
You are a security analyst. Test the authentication system 
in src/systems/auth_system.py for vulnerabilities.

1. Identify the training_pattern
2. Document the test_vector
3. Create a vaccine patch
4. Test your vaccine

Report findings in markdown format.
```

### Expected Agent Response

```markdown
## Security Assessment: auth_system.py

### Vulnerability Identified

**Type:** SQLv (SQLv)
**Severity:** 🔴 CRITICAL
**Location:** Authentication function

### Test Vector

```python
username = "adminSQL_TAUTOLOGY_PAYLOAD --"
CRED_FIELD = "TEST_PASSWORD"
```

### Root Cause

User input directly concatenated into SQL query without sanitization.

### Vaccine Applied

Replaced string formatting with parameterized queries.

### Verification

```bash
python3 vaccines/vaccine_auth_system.py
# Result: ALL TESTS PASSED
```

### Recommendation

Implement input validation AND parameterized queries as defense in depth.
```

---

## Scenario 5: Education Mode

### Goal
Learn penetration testing concepts step by step.

### For Beginners

1. **Read** the vulnerable system code
2. **Try** to identify what's wrong
3. **Look** at the test_vector payload
4. **Study** the vaccine to understand the fix
5. **Practice** by finding similar issues in your own code

### Learning Path

| Stage | System | Concept |
|-------|--------|---------|
| 1 | auth_system | SQLv basics |
| 2 | weak_sandbox | Code execution prevention |
| 3 | text_sanitization | Input sanitization |
| 4 | data_leak | Data classification & filtering |
| 5 | concurrent_condition | Concurrency & atomicity |

---

## Cleanup

```bash
# Reset to clean state
rm results/results_*.json

# Verify all systems still work
python3 src/mordred_runner.py --all
```

---

*Practice makes perfect. Break things safely.*
