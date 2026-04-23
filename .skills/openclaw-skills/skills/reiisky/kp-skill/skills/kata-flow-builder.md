# Kata Flow Builder Skill

## Skill Metadata

```yaml
name: kata-flow-builder
version: 1.0.0
description: Build and modify Kata Platform conversation flows
author: Kata.ai Engineering
platforms: [kata.ai]
```

## When to Use This Skill

Use this skill when the user needs to:

- **Create new flows** - Design conversation flows from scratch
- **Modify existing flows** - Update states, transitions, or flow logic
- **Fix flow issues** - Resolve transition loops, dead ends, or logic errors
- **Add error handling** - Implement fallback paths and error recovery
- **Design state machines** - Structure complex multi-step conversations

## Prerequisites

Before using this skill:

1. ✅ **Read existing flows** - Always use Read tool first to understand current structure
2. ✅ **Understand requirements** - Clarify what the flow should accomplish
3. ✅ **Check related flows** - Review how other flows handle similar logic
4. ✅ **Identify entry/exit points** - Know where flow starts and how it ends

## Core Capabilities

### 1. Flow Structure Design

Design complete conversation flows with proper state machine architecture:

- **Intents** - Define how user input is recognized
- **States** - Create dialogue states with proper initial/end markers
- **Transitions** - Connect states with conditions and data mapping
- **Actions** - Define bot responses and API calls
- **Float conditions** - Implement global interrupts (bye, reset, etc.)

### 2. Transition Logic

Build robust transition systems:

- **Conditional transitions** - Based on intent, data, context
- **Fallback handling** - Always provide default paths
- **Data mapping** - Transform data during transitions
- **Priority management** - Handle multiple possible transitions

### 3. Error Handling

Implement comprehensive error handling:

- **Validation paths** - Handle invalid input
- **Retry logic** - Allow users to correct mistakes
- **Fallback flows** - Graceful degradation
- **Exit strategies** - Clear ways to leave flow

## Technical Context

### Kata Platform Flow Structure

```yaml
# Flow file structure
intents:           # Input recognition
    intentName:
        type: text | data | command
        priority: number
        classifier: { nlu: name }
        condition: "boolean expression"

states:            # Dialogue states
    stateName:
        initial: true | false
        enter: methodName
        action:
            - name: actionName
              condition: "..."
        transitions:
            nextState:
                condition: "..."
                mapping:
                    target: source
            fallback: true
        float:
            condition: "..."
        end: true | false

actions:           # Bot outputs
    actionName:
        type: text | template | api | method | command | schedule
        options:
            # Type-specific options

methods:           # ES5 JavaScript
    methodName(ctx): "
        // ES5 code only!
        return ctx;
    "
```

### State Machine Execution Flow

```
User Input
  ↓
Intent Classification (priority order)
  ↓
Float Evaluation (global interrupts)
  ↓
State Matching
  ↓
Enter Method (if defined)
  ↓
Actions Execution (in order)
  ↓
Data Mapping
  ↓
Transition to Next State
```

### Critical Rules

1. **Every flow must have exactly ONE initial state**
   ```yaml
   states:
       start:
           initial: true  # Entry point
           # ...
   ```

2. **Always provide fallback transitions**
   ```yaml
   transitions:
       specificCase:
           condition: "intent == 'yes'"
       defaultCase:
           fallback: true  # REQUIRED
   ```

3. **Terminal states must be marked end: true**
   ```yaml
   states:
       completed:
           action:
               - name: successMessage
           end: true  # Flow ends here
   ```

4. **Float conditions for global interrupts**
   ```yaml
   states:
       bye:
           priority: 100
           float:
               condition: "intent == 'byeIntent'"
           action:
               - name: goodbyeMessage
           end: true
   ```

## Usage Patterns

### Pattern 1: Create Simple Linear Flow

**User Request:** "Create a flow for collecting user email"

**Approach:**
```yaml
intents:
    startEmail:
        initial: true
        type: command
        condition: "content == 'collectEmail'"

    freeText:
        type: text
        priority: -1

states:
    askEmail:
        initial: true
        action:
            - name: emailQuestion
        transitions:
            validateEmail:
                fallback: true
                mapping:
                    data.email: "content"

    validateEmail:
        action:
            - name: validateEmailMethod
        transitions:
            success:
                condition: "data.isValidEmail == 'true'"
            retry:
                condition: "data.isValidEmail == 'false'"

    success:
        action:
            - name: successMessage
        end: true

    retry:
        action:
            - name: invalidEmailMessage
        transitions:
            askEmail:
                fallback: true

actions:
    emailQuestion:
        type: text
        options:
            text: "Please enter your email address:"

    successMessage:
        type: text
        options:
            text: "Thank you! Your email $(data.email) has been saved."

    invalidEmailMessage:
        type: text
        options:
            text: "Invalid email format. Please try again."
```

### Pattern 2: Create Menu-Based Flow

**User Request:** "Create a main menu with payment, support, and settings options"

**Approach:**
```yaml
intents:
    menuStart:
        initial: true
        type: command
        condition: "content == 'showMenu'"

    paymentIntent:
        type: data
        condition: "payload.cmd == 'payment'"

    supportIntent:
        type: data
        condition: "payload.cmd == 'support'"

    settingsIntent:
        type: data
        condition: "payload.cmd == 'settings'"

states:
    mainMenu:
        initial: true
        action:
            - name: showMenuButtons
        transitions:
            toPayment:
                condition: "intent == 'paymentIntent'"
            toSupport:
                condition: "intent == 'supportIntent'"
            toSettings:
                condition: "intent == 'settingsIntent'"
            mainMenu:
                fallback: true  # Stay in menu

    toPayment:
        action:
            - name: goToPaymentFlow
        end: true

    toSupport:
        action:
            - name: goToSupportFlow
        end: true

    toSettings:
        action:
            - name: goToSettingsFlow
        end: true

actions:
    showMenuButtons:
        type: template
        options:
            type: button
            items:
                text: "Main Menu - Select an option:"
                actions:
                    - type: postback
                      label: "💳 Payment"
                      payload:
                          cmd: payment
                    - type: postback
                      label: "🆘 Support"
                      payload:
                          cmd: support
                    - type: postback
                      label: "⚙️ Settings"
                      payload:
                          cmd: settings

    goToPaymentFlow:
        type: command
        options:
            command: "toPaymentFlow"

    goToSupportFlow:
        type: command
        options:
            command: "toSupportFlow"

    goToSettingsFlow:
        type: command
        options:
            command: "toSettingsFlow"
```

### Pattern 3: Add Error Handling

**User Request:** "Add retry logic for failed API calls"

**Approach:**
```yaml
states:
    callAPI:
        action:
            - name: fetchUserData
        transitions:
            success:
                condition: "payload.status == 'success'"
                mapping:
                    data.userData: "payload.data"
                    data.retryCount: "'0'"  # Reset counter

            retryAPI:
                condition: "payload.status == 'error' && parseInt(data.retryCount || 0) < 3"
                mapping:
                    data.retryCount: "String(parseInt(data.retryCount || 0) + 1)"

            failed:
                fallback: true

    retryAPI:
        action:
            - name: retryMessage
            - name: waitBeforeRetry
        transitions:
            callAPI:
                fallback: true

    failed:
        action:
            - name: apiErrorMessage
            - name: offerSupport
        transitions:
            contactSupport:
                condition: "intent == 'yesIntent'"
            mainMenu:
                condition: "intent == 'noIntent'"
            failed:
                fallback: true

actions:
    retryMessage:
        type: text
        options:
            text: "Connection error. Retrying... (Attempt $(data.retryCount) of 3)"

    waitBeforeRetry:
        type: method
        method: sleep2Seconds

    apiErrorMessage:
        type: text
        options:
            text: "We're having trouble connecting. Would you like to contact support?"

    offerSupport:
        type: template
        options:
            type: button
            items:
                text: "Get help?"
                actions:
                    - type: postback
                      label: "Yes, contact support"
                      payload:
                          cmd: support
                    - type: postback
                      label: "No, go to main menu"
                      payload:
                          cmd: menu

methods:
    sleep2Seconds(ctx): "
        // Note: This is symbolic - actual delay handled by platform
        ctx.data.delayApplied = 'true';
        return ctx;
    "
```

### Pattern 4: Implement Float (Global Interrupt)

**User Request:** "Add a bye command that works from any state"

**Approach:**
```yaml
intents:
    byeIntent:
        type: text
        priority: 100  # High priority
        classifier:
            nlu: byeKeyword

states:
    # This state can trigger from ANYWHERE
    bye:
        priority: 100
        float:
            condition: "intent == 'byeIntent'"
            mapping:
                # Clean up sensitive data
                data.tempData: "'null'"
                data.sessionData: "'null'"
        action:
            # Clean up schedulers
            - name: scheduleOffAll
            # Send goodbye
            - name: goodbyeMessage
        end: true

    # ... other states continue normally ...

actions:
    goodbyeMessage:
        type: text
        options:
            text: "Goodbye! Thanks for chatting. Type 'Hi' anytime to start again."

    scheduleOffAll:
        type: schedule
        options:
            id: reminderScheduler
            command: remove
```

### Pattern 5: Multi-Step Form Flow

**User Request:** "Create a registration flow: name → email → phone → confirm"

**Approach:**
```yaml
states:
    askName:
        initial: true
        action:
            - name: askNameQuestion
        transitions:
            askEmail:
                fallback: true
                mapping:
                    data.name: "content"

    askEmail:
        action:
            - name: askEmailQuestion
        transitions:
            validateEmail:
                fallback: true
                mapping:
                    data.email: "content"

    validateEmail:
        action:
            - name: validateEmailMethod
        transitions:
            askPhone:
                condition: "data.isValidEmail == 'true'"
            askEmail:
                condition: "data.isValidEmail == 'false'"
                mapping:
                    data.errorMessage: "'Please enter a valid email'"

    askPhone:
        action:
            - name: askPhoneQuestion
        transitions:
            validatePhone:
                fallback: true
                mapping:
                    data.phone: "content"

    validatePhone:
        action:
            - name: validatePhoneMethod
        transitions:
            showSummary:
                condition: "data.isValidPhone == 'true'"
            askPhone:
                condition: "data.isValidPhone == 'false'"
                mapping:
                    data.errorMessage: "'Please enter a valid phone number'"

    showSummary:
        action:
            - name: displaySummary
            - name: askConfirmation
        transitions:
            submit:
                condition: "intent == 'yesIntent'"
            askName:
                condition: "intent == 'noIntent'"
                mapping:
                    data.name: "'null'"
                    data.email: "'null'"
                    data.phone: "'null'"
            showSummary:
                fallback: true

    submit:
        action:
            - name: submitRegistration
            - name: successMessage
        end: true

actions:
    displaySummary:
        type: text
        options:
            text: |
                Please confirm your details:
                Name: $(data.name)
                Email: $(data.email)
                Phone: $(data.phone)

    askConfirmation:
        type: template
        options:
            type: button
            items:
                text: "Is this correct?"
                actions:
                    - type: postback
                      label: "✅ Yes, submit"
                      payload:
                          cmd: confirm
                    - type: postback
                      label: "❌ No, start over"
                      payload:
                          cmd: restart
```

## Best Practices

### DO ✅

1. **Read before writing** - Always examine existing flows first
   ```bash
   # First understand the current structure
   Read flows/payment.yml
   # Then make changes
   Edit flows/payment.yml
   ```

2. **Provide clear fallbacks** - Every state needs a default path
   ```yaml
   transitions:
       specificCase:
           condition: "..."
       fallback: true  # Always provide
   ```

3. **Use meaningful names** - Self-documenting code
   ```yaml
   # Good
   states:
       validateCustomerID:
           # ...

   # Bad
   states:
       state1:
           # ...
   ```

4. **Test all paths** - Consider happy path AND error cases
   ```yaml
   transitions:
       success:
           condition: "payload.status == 'success'"
       retry:
           condition: "payload.status == 'retry'"
       error:
           fallback: true  # Catch all other cases
   ```

5. **Document complex logic** - Add comments
   ```yaml
   states:
       processPayment:
           # Check if user has sufficient balance
           # Retry up to 3 times on network errors
           # Fallback to manual payment if API fails
           action:
               - name: checkBalance
               # ...
   ```

### DON'T ❌

1. **Create circular loops** - Without exit conditions
   ```yaml
   # BAD - Infinite loop
   states:
       stateA:
           transitions:
               stateB:
                   fallback: true

       stateB:
           transitions:
               stateA:
                   fallback: true  # No way out!

   # GOOD - Provide exit
   states:
       stateA:
           transitions:
               stateB:
                   condition: "intent == 'continue'"
               exit:
                   fallback: true  # Exit path

       stateB:
           transitions:
               stateA:
                   condition: "intent == 'back'"
               exit:
                   fallback: true  # Exit path
   ```

2. **Forget initial states** - Every flow needs exactly one
   ```yaml
   # BAD - No initial state
   states:
       someState:
           # ...

   # GOOD
   states:
       start:
           initial: true  # Entry point
           # ...
   ```

3. **Miss end markers** - Terminal states need end: true
   ```yaml
   # BAD
   states:
       completed:
           action:
               - name: successMessage
           # Missing end: true

   # GOOD
   states:
       completed:
           action:
               - name: successMessage
           end: true  # Flow terminates
   ```

4. **Assume data exists** - Always validate
   ```yaml
   # BAD
   mapping:
       data.name: "payload.user.name"  # What if null?

   # GOOD - Use method to safely extract
   states:
       extractName:
           action:
               - name: safeExtractName
           # ...

   methods:
       safeExtractName(msg, ctx, dat, opts, cfg, result): "
           var name = 'Unknown';
           if (result && result.user && result.user.name) {
               name = result.user.name;
           }
           ctx.data.name = name;
           return ctx;
       "
   ```

## Debugging Flows

### Issue: Transition Not Working

**Symptoms:** Flow stays in same state or goes to unexpected state

**Debug Approach:**
```yaml
# Add temporary debug action
states:
    problematicState:
        action:
            - name: debugInfo
            # ... other actions
        transitions:
            # ...

actions:
    debugInfo:
        type: text
        options:
            text: |
                DEBUG:
                Current Intent: $(intent)
                Data.field: $(data.field)
                Payload.value: $(payload.value)
```

**Common Causes:**
1. Condition syntax error
2. Wrong intent matched (check priority)
3. Missing fallback
4. Data not set

### Issue: Flow Not Starting

**Symptoms:** Flow never enters initial state

**Checklist:**
- [ ] Is there exactly ONE `initial: true` state?
- [ ] Is the flow properly included in bot.yml?
- [ ] Is the start intent defined correctly?
- [ ] Is the intent command/condition correct?

### Issue: Dead End State

**Symptoms:** Flow gets stuck with no way forward

**Fix:**
```yaml
# BAD - No transitions
states:
    stuckState:
        action:
            - name: someAction
        # Missing transitions!

# GOOD - Always provide path forward
states:
    properState:
        action:
            - name: someAction
        transitions:
            nextState:
                fallback: true  # Or end: true
```

## Integration with Other Skills

### With kata-method-writer

When flows need custom logic:
```yaml
states:
    processData:
        enter: calculateTotal  # Use kata-method-writer skill
        action:
            - name: showTotal
        transitions:
            # ...
```

### With kata-scheduler-manager

When flows need timed events:
```yaml
states:
    waitForResponse:
        action:
            - name: scheduleReminder  # Use kata-scheduler-manager skill
            - name: askQuestion
        transitions:
            # ...
```

### With kata-api-integrator

When flows need external data:
```yaml
states:
    fetchData:
        action:
            - name: callExternalAPI  # Use kata-api-integrator skill
            - name: parseResponse
        transitions:
            # ...
```

## Examples

See `examples/` directory for complete flow examples:
- `examples/basic-flow.yml` - Simple linear flow
- `examples/menu-flow.yml` - Menu-based navigation
- `examples/form-flow.yml` - Multi-step form
- `examples/error-handling-flow.yml` - Retry and error recovery

## Quick Reference

### Flow Structure Checklist

- [ ] Intents defined with priorities
- [ ] Exactly ONE initial state
- [ ] All states have transitions
- [ ] All transitions have conditions or fallback
- [ ] Float states for global interrupts
- [ ] Terminal states marked with end: true
- [ ] Actions defined for all names referenced
- [ ] Methods in ES5 syntax only

### Common Intent Patterns

```yaml
# Text input
intentName:
    type: text
    classifier:
        nlu: nluName

# Button click
buttonIntent:
    type: data
    condition: "payload.cmd == 'command'"

# System command
systemIntent:
    type: command
    condition: "content == 'eventName'"

# Fallback (catch-all)
fallbackIntent:
    fallback: true
    priority: -10
```

### Common Transition Patterns

```yaml
# Conditional
nextState:
    condition: "intent == 'yesIntent'"

# With mapping
anotherState:
    condition: "intent == 'continueIntent'"
    mapping:
        data.field: "payload.value"

# Fallback
defaultState:
    fallback: true
```

---

**End of Kata Flow Builder Skill**

*For complete Kata Platform reference, see KATA_PLATFORM_GUIDE.md*
