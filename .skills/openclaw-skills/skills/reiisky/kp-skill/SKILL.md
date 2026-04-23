---
name: kata-platform
description: Comprehensive skills for building chatbots on Kata.ai platform and Triva-specific KBR shortcuts - flows, methods, intents, actions, schedulers, API integration, and debugging
user_invocable: true
trigger: when working with Kata Platform YAML bot files, Triva-specific shortcuts, ES5 JavaScript methods, or Kata.ai chatbot development
match:
  - bot.yml
  - "flows/*.yml"
  - "method/*.js"
  - nlus.yml
  - "*.yml containing kata-ml schema"
---

# Kata Platform Development Skills

You are an expert Kata Platform chatbot developer. Use these skills when helping users build, modify, or debug YAML-based conversational AI bots on the Kata.ai platform.

## Quick Reference

- **Platform**: Kata.ai (kata-ml schema 1.0)
- **Configuration**: YAML-based state machines
- **JavaScript**: ES5 ONLY (no arrow functions, let/const, template literals)
- **Key Files**: bot.yml (main), flows/*.yml, method/*.js, nlus.yml

## When to Apply These Skills

Apply these skills when the user is:
- Creating or modifying conversation flows
- Writing JavaScript methods (MUST be ES5)
- Designing intents and NLU classifiers
- Building actions (text, template, API, method, schedule)
- Managing schedulers and reminders
- Integrating external APIs
- Debugging bot issues

## Critical Constraints

### ES5 JavaScript Only

**NEVER use ES6+ features in methods. They will fail silently.**

```javascript
// FORBIDDEN (ES6+)
const fn = () => {}        // Arrow functions
let x = 1; const y = 2;    // let/const
`Hello ${name}`            // Template literals
const {a, b} = obj;        // Destructuring
{...obj}                   // Spread operator

// REQUIRED (ES5)
function fn() {}           // Function keyword
var x = 1;                 // var only
'Hello ' + name            // String concatenation
var a = obj.a;             // Manual access
```

### Method Signature

Every Kata method MUST use this signature:
```javascript
function methodName(msg, ctx, dat, opts, cfg, result) {
    // Access: ctx.data.field, ctx.context.field
    // Modify: ctx.data.newField = 'value'
    return ctx; // MUST return ctx
}
```

## Flow Structure

```yaml
intents:
    intentName:
        type: text | data | command
        priority: number
        classifier: { nlu: name }
        condition: "boolean expression"

states:
    stateName:
        initial: true          # Exactly ONE per flow
        enter: methodName      # Optional ES5 method
        action:
            - name: actionName
              condition: "..."
        transitions:
            nextState:
                condition: "intent == 'someIntent'"
                mapping:
                    data.field: "value"
            fallbackState:
                fallback: true # ALWAYS provide fallback
        end: true             # Mark terminal states

actions:
    actionName:
        type: text | template | api | method | command | schedule
        options:
            # Type-specific options
```

## Execution Flow

```
User Input → Intent Classification → Float Evaluation →
State Match → Enter Method → Actions → Data Mapping → Transition
```

## Common Patterns

### 1. Validation Flow
```yaml
states:
    askInput:
        initial: true
        action:
            - name: promptUser
        transitions:
            validateInput:
                fallback: true
                mapping:
                    data.input: "content"

    validateInput:
        enter: validateMethod  # ES5 validation
        transitions:
            success:
                condition: "data.isValid == 'true'"
            retry:
                fallback: true
```

### 2. Menu with Buttons
```yaml
actions:
    showMenu:
        type: template
        options:
            type: button
            items:
                text: "Select option:"
                actions:
                    - type: postback
                      label: "Option 1"
                      payload:
                          cmd: option1
```

### 3. API Integration
```yaml
actions:
    callAPI:
        type: api
        options:
            method: POST
            uri: "$(cfg.apiUrl)/endpoint"
            headers:
                Authorization: "Bearer $(cfg.apiKey)"
            body:
                userId: "$(ctx.context.userId)"
```

### 4. Scheduler
```yaml
# Set reminder
actions:
    setReminder:
        type: schedule
        options:
            id: reminderScheduler
            command: insert
            target:
                type: relative
                value: 180000  # 3 minutes
            flow: reminderFlow

# Clear scheduler (ALWAYS clean up!)
    clearReminder:
        type: schedule
        options:
            id: reminderScheduler
            command: remove
```

### 5. Float (Global Interrupt)
```yaml
states:
    bye:
        priority: 100
        float:
            condition: "intent == 'byeIntent'"
        action:
            - name: goodbyeMessage
            - name: clearAllSchedulers  # Clean up!
        end: true
```

## Project-Specific Patterns (Triva)

### Keyword-Based Routing (KBR) Shortcut
**Purpose**: Enable direct "deep linking" to campaign or product states via specific keywords.

**Requirements**:
- **Keywords**: Define a specific keyword set in `nlu.yml`.
- **Intents**: Register the trigger intent in `greeting.yml` (initial & float).
- **Jump Target**: Identify the destination flow and specific target state.

**How to Use**:
1. Define the keyword triggers and intents.
2. Wire the routing logic in the source flow (`greeting.yml`).
3. Implement the destination jump logic in the target flow.

**Detailed Workflow**: Refer to the specialized skill: `skills/triva-add-kbr.md`.

## ES5 Method Examples

### Phone Validation
```javascript
function validatePhone(msg, ctx, dat, opts, cfg, result) {
    var phone = ctx.data.phone || '';
    phone = phone.replace(/[\s-]/g, '');
    var isValid = /^(08|628)[0-9]{8,11}$/.test(phone);
    ctx.data.isValidPhone = isValid;
    return ctx;
}
```

### Format Rupiah
```javascript
function formatRupiah(msg, ctx, dat, opts, cfg, result) {
    var amount = parseInt(ctx.data.amount) || 0;
    var str = String(amount);
    var formatted = '';
    var count = 0;
    for (var i = str.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) {
            formatted = '.' + formatted;
        }
        formatted = str[i] + formatted;
        count++;
    }
    ctx.data.formattedAmount = 'Rp ' + formatted;
    return ctx;
}
```

### Safe API Response Parsing
```javascript
function parseResponse(msg, ctx, dat, opts, cfg, result) {
    var data = null;
    try {
        if (result && result.data) {
            data = result.data;
        }
    } catch (e) {
        ctx.data.parseError = e.message;
    }
    ctx.data.apiData = data;
    ctx.data.parseSuccess = data ? 'true' : 'false';
    return ctx;
}
```

## Debugging Checklist

1. **Method not working?**
   - Check for ES6 syntax (arrow functions, let/const, template literals)
   - Verify `return ctx` at the end
   - Check syntax errors (brackets, quotes)

2. **Transition not firing?**
   - Check intent priority
   - Verify condition syntax
   - Ensure fallback exists

3. **Flow not starting?**
   - Check `initial: true` on entry state
   - Verify flow is included in bot.yml
   - Check start intent definition

4. **Scheduler keeps firing?**
   - Missing `scheduleOff*` action
   - Add cleanup to bye/end states

## File References

For detailed documentation:
- See `KATA_PLATFORM_GUIDE.md` for complete technical reference
- See `skills/` directory for detailed skill documentation
- See `examples/` directory for working code samples

## Best Practices

1. **Always read before editing** - Understand existing code first
2. **Provide fallback transitions** - Every state needs a default path
3. **Clean up schedulers** - Every scheduleRun needs scheduleOff
4. **Use meaningful names** - Self-documenting state/action names
5. **Validate input** - Check for null/undefined in methods
6. **Test all paths** - Consider happy path AND error cases
