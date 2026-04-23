# Kata Debugger Skill

Expert skill for debugging and troubleshooting Kata Platform YAML bots - tracing flows, identifying issues, and resolving common problems.

## When to Use This Skill

Use this skill when you need to:
- Debug why a bot isn't responding correctly
- Trace conversation flow execution
- Identify intent matching issues
- Find transition logic errors
- Debug scheduler leaks and orphaned timers
- Resolve context/data mapping problems
- Fix API integration issues
- Identify infinite loops or circular flows
- Troubleshoot fallback triggers
- Optimize bot performance

## Debugging Philosophy

**Kata Platform Flow:** User Input → Intent Classification → State Entry → Actions → Transitions → Next State

Debug by tracing this flow step-by-step to identify where things break.

## Common Issues and Solutions

### Issue 1: Bot Not Responding

**Symptoms:**
- User sends message, no response
- Bot shows "thinking" but no output
- Random timeouts

**Debug Steps:**

1. **Check Intent Classification**
   ```yaml
   # Verify intent exists and conditions are correct
   intents:
     myIntent:
       priority: 10
       type: text
       condition: 'content.toLowerCase() == "test"'
       # Is the condition returning boolean?
       # Is priority conflicting with other intents?
   ```

2. **Check State Has Intent**
   ```yaml
   states:
     myState:
       intents:
         - myIntent  # Make sure intent is listed here
   ```

3. **Check Transition Logic**
   ```yaml
   states:
     myState:
       action:
         - name: someAction
       transitions:
         nextState:
           condition: 'true'  # Does a transition exist?
   ```

4. **Check Action Existence**
   ```yaml
   actions:
     someAction:  # Make sure action is defined
       type: text
       options:
         text: "Response"
   ```

**Common Causes:**
- Intent not in state's intent list
- Intent condition always returns false
- No matching transition
- Action not defined
- YAML syntax error (indentation)

### Issue 2: Wrong Intent Triggered

**Symptoms:**
- Bot responds with unexpected message
- Fallback triggered instead of specific intent
- Wrong flow entered

**Debug Steps:**

1. **Check Intent Priority**
   ```yaml
   # Lower number = higher priority
   intents:
     specificIntent:
       priority: 5  # Evaluated BEFORE priority 10
     generalIntent:
       priority: 10
   ```

2. **Check Overlapping Conditions**
   ```yaml
   # BAD: Both can match "help me"
   intents:
     helpIntent:
       priority: 10
       condition: 'content.indexOf("help") >= 0'
     helpMeIntent:
       priority: 12
       condition: 'content == "help me"'

   # GOOD: More specific intent has higher priority
   intents:
     helpMeIntent:
       priority: 10
       condition: 'content == "help me"'
     helpIntent:
       priority: 12
       condition: 'content.indexOf("help") >= 0'
   ```

3. **Check Float Conditions**
   ```yaml
   # Float states can intercept from anywhere
   states:
     cancel:
       float: true
       intents:
         - cancelIntent
       # This might be catching input unexpectedly
   ```

**Common Causes:**
- Priority conflict (specific intent has lower priority)
- Overlapping regex/keyword conditions
- Float state intercepting
- Fallback too aggressive

### Issue 3: Scheduler Keeps Firing

**Symptoms:**
- Timeout messages appear after conversation ended
- Multiple scheduler triggers
- "Bye" message followed by fallback

**Debug Steps:**

1. **Audit Scheduler Lifecycle**
   ```bash
   # Search for all scheduleRun* actions
   grep -r "scheduleRun" flows/

   # For each scheduler, find corresponding scheduleOff*
   # Example: scheduleRunTimeout needs scheduleOffTimeout
   ```

2. **Check Bye State Has Cleanup**
   ```yaml
   states:
     bye:
       end: true
       float: true
       intents:
         - scheduleRunTimeout  # Intent to catch scheduler
       action:
         - name: byeText
         - name: scheduleOffTimeout  # MUST cancel scheduler
   ```

3. **Check Cross-Flow Schedulers**
   ```yaml
   # Flow A creates scheduler
   flows:
     flowA:
       actions:
         scheduleTimeout:
           # Creates scheduleRunTimeout

   # Flow B must handle cleanup
   flows:
     flowB:
       states:
         bye:
           intents:
             - scheduleRunTimeout  # Catch from flowA
           action:
             - name: scheduleOffTimeout  # Clean up
   ```

4. **Check Intent Matches Command**
   ```yaml
   # Scheduler creates command "scheduleRunTimeout"
   actions:
     scheduleTimeout:
       body:
         command: scheduleRunTimeout

   # Intent MUST match exactly
   intents:
     scheduleRunTimeout:
       type: command
       condition: 'content == "scheduleRunTimeout"'
   ```

**Common Causes:**
- Missing scheduleOff* action
- Bye state doesn't have scheduler intent
- Cross-flow scheduler not handled
- Intent name doesn't match command

**Fix Pattern:**
```yaml
# 1. Add scheduler intent
intents:
  scheduleRunMyScheduler:
    priority: 1
    type: command
    condition: 'content == "scheduleRunMyScheduler"'

# 2. Add to bye float condition
states:
  bye:
    float: true
    condition: 'intent == "scheduleRunPart1" || intent == "scheduleRunMyScheduler"'
    intents:
      - scheduleRunMyScheduler

# 3. Add cleanup action
actions:
  scheduleOffMyScheduler:
    type: api
    options:
      method: DELETE
      uri: $(config.schedulerUrl)/myScheduler_$(metadata.sessionId)

# 4. Call cleanup in bye state
states:
  bye:
    action:
      - name: byeText
      - name: scheduleOffMyScheduler
```

### Issue 4: Infinite Loop / Circular Flow

**Symptoms:**
- Bot keeps repeating same message
- Flow never ends
- Stack overflow errors

**Debug Steps:**

1. **Trace Transition Chain**
   ```yaml
   # Check for circular transitions
   states:
     stateA:
       transitions:
         stateB:
           condition: 'true'

     stateB:
       transitions:
         stateA:
           condition: 'true'  # Circular!
   ```

2. **Check End States**
   ```yaml
   # Make sure flows have proper end states
   states:
     bye:
       end: true  # MUST have end: true
       action:
         - name: byeText
       # No transitions from end state!
   ```

3. **Check Transition Conditions**
   ```yaml
   # Make sure transitions are mutually exclusive
   states:
     myState:
       transitions:
         stateA:
           condition: 'data.choice == "A"'
         stateB:
           condition: 'data.choice == "B"'
         fallback:
           condition: 'true'  # Catch-all
   ```

**Common Causes:**
- Circular transition (A → B → A)
- Missing end: true on terminal states
- All transitions have false conditions
- Float state transitioning back to itself

**Prevention:**
- Always have end states with `end: true`
- Use flowcharts to visualize transitions
- Ensure at least one transition condition is true
- Avoid self-transitions unless intentional

### Issue 5: Context/Data Not Persisting

**Symptoms:**
- Variables reset unexpectedly
- User data lost between states
- Context empty when expected

**Debug Steps:**

1. **Check Scope Usage**
   ```yaml
   # CONTEXT: Persists across entire conversation
   mapping:
     context:
       userId: $(result.response.body.id)  # Stays forever

   # DATA: Scoped to current flow
   mapping:
     data:
       tempValue: $(result.response.body.temp)  # Lost on flow change

   # PAYLOAD: One-time intent data
   attributes:
     data:
       selection: $(payload.value)  # Only from this intent
   ```

2. **Check Mapping Syntax**
   ```yaml
   # BAD: Wrong variable reference
   text: "$(context.userName)"  # Works

   # BAD: Typo
   text: "$(contxt.userName)"  # Fails silently!

   # BAD: Undefined check
   condition: 'context.userName == "John"'  # Error if undefined
   condition: 'typeof context.userName != "undefined" && context.userName == "John"'  # Safe
   ```

3. **Check Method Return**
   ```javascript
   // BAD: Doesn't update context
   function myMethod(msg, ctx, dat, opts, cfg, result) {
     var name = "John";
     // Forgot to return!
   }

   // GOOD: Returns context update
   function myMethod(msg, ctx, dat, opts, cfg, result) {
     return {
       command: 'updateContext',
       payload: {
         userName: "John"
       }
     };
   }
   ```

**Common Causes:**
- Using `data` scope instead of `context`
- Typo in variable name
- Method not returning context update
- Flow transition clears data scope

### Issue 6: API Call Failing

**Symptoms:**
- API action not executing
- Empty response
- Error messages

**Debug Steps:**

1. **Log Full Response**
   ```yaml
   actions:
     debugApi:
       type: api
       options:
         method: GET
         uri: $(config.apiUrl)/test
         mapping:
           data:
             fullResponse: $(result)
             status: $(result.response.status)
             body: $(result.response.body)
             error: $(result.error)
   ```

2. **Check HTTP Status**
   ```yaml
   mapping:
     data:
       success: $(result.response.status == 200)
       unauthorized: $(result.response.status == 401)
       notFound: $(result.response.status == 404)
       serverError: $(result.response.status >= 500)
   ```

3. **Verify Headers**
   ```yaml
   headers:
     # Check authentication
     Authorization: "Bearer $(config.apiToken)"
     # Check content type
     Content-Type: "application/json"
     # Check required headers
     X-API-Key: $(config.apiKey)
   ```

4. **Verify Body Structure**
   ```yaml
   body:
     # Make sure structure matches API spec
     field1: $(context.value1)
     nested:
       field2: $(data.value2)
   ```

**Common Causes:**
- Wrong HTTP method (GET vs POST)
- Missing authentication headers
- Incorrect body structure
- Network timeout
- API endpoint changed
- Config variables undefined

### Issue 7: Fallback Always Triggered

**Symptoms:**
- Every input goes to fallback
- Specific intents never match

**Debug Steps:**

1. **Check Intent Conditions Return Boolean**
   ```yaml
   # BAD: Returns string, not boolean
   intents:
     badIntent:
       condition: 'content.toLowerCase()'  # Returns string!

   # GOOD: Returns boolean
   intents:
       condition: 'content.toLowerCase() == "test"'
   ```

2. **Check Regex Syntax**
   ```yaml
   # BAD: Wrong regex syntax
   condition: 'content.match(/test/)'  # match() not supported

   # GOOD: Use test()
   condition: '/test/.test(content)'
   ```

3. **Check Case Sensitivity**
   ```yaml
   # BAD: Case sensitive
   condition: 'content == "Test"'  # Won't match "test"

   # GOOD: Case insensitive
   condition: 'content.toLowerCase() == "test"'
   ```

4. **Check Intent Priority**
   ```yaml
   # BAD: Fallback evaluated before specific intent
   intents:
     fallback:
       priority: 5
       fallback: true
     specific:
       priority: 10  # Never reached!

   # GOOD: Fallback has lowest priority
   intents:
     specific:
       priority: 10
     fallback:
       priority: 99
       fallback: true
   ```

**Common Causes:**
- Condition returns non-boolean
- Regex syntax error
- Case sensitivity mismatch
- Fallback priority too high
- Intent not in state's intent list

### Issue 8: ES6 Code Breaking Methods

**Symptoms:**
- Method not executing
- Silent failures
- Unexpected behavior

**Debug Examples:**

```javascript
// ❌ ES6 - WON'T WORK
const validatePhone = (phone) => {
  let isValid = /^08[0-9]{8,11}$/.test(phone);
  return { command: 'updateContext', payload: { isValid } };
};

// ✅ ES5 - CORRECT
function validatePhone(phone) {
  var isValid = /^08[0-9]{8,11}$/.test(phone);
  return {
    command: 'updateContext',
    payload: { isValid: isValid }
  };
}

// ❌ ES6 Template Literals
var message = `Hello ${name}!`;

// ✅ ES5 String Concatenation
var message = 'Hello ' + name + '!';

// ❌ ES6 Destructuring
const { id, name } = data;

// ✅ ES5 Direct Access
var id = data.id;
var name = data.name;

// ❌ ES6 Spread Operator
var merged = { ...obj1, ...obj2 };

// ✅ ES5 Manual Merge
var merged = {};
for (var k in obj1) merged[k] = obj1[k];
for (var k in obj2) merged[k] = obj2[k];
```

**Common ES6 Features to Avoid:**
- `let` / `const` → Use `var`
- Arrow functions → Use `function`
- Template literals → Use string concatenation
- Destructuring → Use direct property access
- Spread operator → Manual object/array manipulation
- Default parameters → Manual defaults
- `Array.find()` / `Array.includes()` → Use loops

## Debugging Tools and Techniques

### 1. Console Logging in Methods

```javascript
function debugMethod(msg, ctx, dat, opts, cfg, result) {
  console.log('=== Debug Info ===');
  console.log('Message:', msg);
  console.log('Context:', ctx);
  console.log('Data:', dat);
  console.log('Options:', opts);
  console.log('Config:', cfg);
  console.log('Result:', result);
  console.log('================');

  return { command: 'continue' };
}
```

### 2. Trace Intent Matching

```yaml
states:
  debugState:
    action:
      - name: debugIntent

actions:
  debugIntent:
    type: text
    options:
      text: |
        DEBUG INFO:
        Intent: $(intent)
        Content: $(content)
        Payload: $(payload)
        Context: $(context)
        Data: $(data)
```

### 3. Test State Transitions

```yaml
states:
  testState:
    action:
      - name: showState

actions:
  showState:
    type: text
    options:
      text: "Current state: testState, Intent: $(intent)"

transitions:
  nextState:
    condition: 'true'
```

### 4. Validate Data Availability

```javascript
function checkDataAvailability(msg, ctx, dat, opts, cfg, result) {
  var report = [];

  report.push('Context keys: ' + Object.keys(ctx).join(', '));
  report.push('Data keys: ' + Object.keys(dat).join(', '));

  if (ctx.userId) {
    report.push('User ID: ' + ctx.userId);
  } else {
    report.push('WARNING: userId not in context');
  }

  console.log(report.join('\n'));

  return { command: 'continue' };
}
```

### 5. API Response Inspection

```yaml
actions:
  inspectApi:
    type: api
    options:
      method: GET
      uri: $(config.apiUrl)/test
      mapping:
        data:
          responseStatus: $(result.response.status)
          responseHeaders: $(result.response.headers)
          responseBody: $(result.response.body)
          hasError: $(typeof result.error != "undefined")
          errorMessage: $(result.error ? result.error.message : null)

states:
  showApiDebug:
    action:
      - name: inspectApi
      - name: displayDebug

actions:
  displayDebug:
    type: text
    options:
      text: |
        API Debug:
        Status: $(data.responseStatus)
        Has Error: $(data.hasError)
        Error: $(data.errorMessage)
```

## Debugging Checklist

### Intent Issues
- [ ] Intent exists in `intents:` section
- [ ] Intent listed in state's `intents:` array
- [ ] Intent condition returns boolean
- [ ] Intent priority is appropriate
- [ ] No conflicting intents with higher priority
- [ ] Float conditions not blocking intent

### State Issues
- [ ] State exists in `states:` section
- [ ] State has at least one intent
- [ ] State has at least one action
- [ ] State has transitions (unless end state)
- [ ] End states have `end: true`
- [ ] Float states have `float: true`

### Action Issues
- [ ] Action defined in `actions:` section
- [ ] Action type is valid (text, template, api, method)
- [ ] Action referenced by name in state
- [ ] Conditional actions have valid conditions
- [ ] Variables used in actions are defined

### Transition Issues
- [ ] At least one transition condition is true
- [ ] Transition target states exist
- [ ] No circular transitions without exit
- [ ] Fallback transition exists
- [ ] Conditions are mutually exclusive or prioritized

### Scheduler Issues
- [ ] Every scheduleRun* has matching scheduleOff*
- [ ] Scheduler intents defined (type: command)
- [ ] Bye states catch scheduler intents
- [ ] Float condition includes scheduler intents
- [ ] Cleanup actions called in bye/end states

### API Issues
- [ ] HTTP method is correct
- [ ] URI is valid and includes protocol
- [ ] Headers include authentication
- [ ] Body structure matches API spec
- [ ] Response mapping uses safe access
- [ ] Error handling implemented
- [ ] Config variables are defined

### Method Issues
- [ ] ES5 syntax only (no ES6+)
- [ ] Method signature correct: `function name(msg, ctx, dat, opts, cfg, result)`
- [ ] Method returns valid command object
- [ ] Variables declared with `var`
- [ ] String concatenation (not template literals)
- [ ] Regular functions (not arrow functions)

## Performance Debugging

### Identify Slow States

```javascript
function measureStatePerformance(msg, ctx, dat, opts, cfg, result) {
  var startTime = Date.now();

  // Simulate work
  // ... your logic ...

  var endTime = Date.now();
  var duration = endTime - startTime;

  console.log('State execution time:', duration, 'ms');

  return { command: 'continue' };
}
```

### Optimize Heavy API Calls

```yaml
# Cache API responses in context
actions:
  getCachedData:
    type: api
    condition: 'typeof context.cachedData == "undefined"'  # Only if not cached
    options:
      method: GET
      uri: $(config.apiUrl)/expensive
      mapping:
        context:
          cachedData: $(result.response.body)
          cachedAt: $(metadata.timestamp)
```

## Common Error Messages

### "State not found"
- Check state name spelling
- Verify state exists in flow
- Check transition target

### "Intent not defined"
- Add intent to `intents:` section
- Check intent name spelling

### "Action not found"
- Define action in `actions:` section
- Check action name in state reference

### "Invalid transition"
- Check transition target state exists
- Verify condition syntax

### "Method execution failed"
- Check for ES6 syntax
- Verify method signature
- Check return object structure
- Look for runtime errors in logs

## Debugging Workflow

1. **Reproduce the Issue**
   - Get exact user input that causes problem
   - Note expected vs actual behavior

2. **Identify the Phase**
   - Intent classification?
   - State entry?
   - Action execution?
   - Transition evaluation?

3. **Add Debug Logging**
   - Log current state/intent
   - Log context/data values
   - Log API responses
   - Log method execution

4. **Isolate the Problem**
   - Test intent matching separately
   - Test actions individually
   - Test transitions in isolation
   - Test methods with sample data

5. **Fix and Verify**
   - Make minimal changes
   - Test the exact scenario
   - Check for side effects
   - Verify fix doesn't break other flows

6. **Clean Up**
   - Remove debug logs
   - Remove test states/actions
   - Document the fix

## Summary

When debugging Kata Platform bots:
1. Understand the execution flow (intent → state → action → transition)
2. Check one phase at a time
3. Use logging extensively
4. Verify ES5 compliance in methods
5. Audit scheduler lifecycle
6. Check intent priorities and conditions
7. Validate API responses
8. Test transitions exhaustively
9. Monitor context/data scopes
10. Document issues and solutions

Remember: Most bugs are in three places:
1. **Intent matching** - condition/priority issues
2. **Scheduler cleanup** - missing scheduleOff*
3. **ES6 syntax** - in methods

Start with these when debugging unknown issues.
