# Kata Platform Technical Reference

**Internal Engineering Documentation**

This document provides a complete technical reference for the Kata.ai conversational AI platform. It is written for developers building YAML-based chatbots and assumes familiarity with state machines, APIs, and JavaScript.

---

## Table of Contents

1. [Platform Architecture](#platform-architecture)
2. [Project Structure](#project-structure)
3. [Core Concepts](#core-concepts)
4. [Intents](#intents)
5. [States](#states)
6. [Actions](#actions)
7. [Transitions](#transitions)
8. [Methods](#methods)
9. [NLU System](#nlu-system)
10. [Schedulers](#schedulers)
11. [Context & Data](#context--data)
12. [Multi-Channel Support](#multi-channel-support)
13. [API Integration](#api-integration)
14. [Flow Control Patterns](#flow-control-patterns)
15. [Best Practices](#best-practices)
16. [Debugging](#debugging)
17. [Common Pitfalls](#common-pitfalls)

---

## Platform Architecture

### Overview

Kata Platform is a **YAML-based conversational AI framework** that uses a **state machine pattern** to manage dialogue flow. It processes user messages through intent classification, state evaluation, action execution, and transition logic.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kata Platform                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   NLU        │  │   State      │  │   Action     │ │
│  │   Engine     │─▶│   Machine    │─▶│   Executor   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ▲                 │                   │         │
│         │                 │                   │         │
│         │                 ▼                   ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   User       │  │   Context    │  │   External   │ │
│  │   Input      │  │   Manager    │  │   APIs       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Multi-Channel       │
              │  Output (WA/Web/etc) │
              └──────────────────────┘
```

### Execution Pipeline

Every user message flows through this pipeline:

```
1. INPUT RECEPTION
   ├─ Receive message from channel (WhatsApp, Web, etc.)
   ├─ Extract: content, payload, metadata
   └─ Load: current context, data, state

2. INTENT CLASSIFICATION
   ├─ Match intents by priority
   ├─ Evaluate: type (text/data/command)
   ├─ Check: classifiers (NLU/keyword/regex/method)
   └─ Condition: additional boolean checks

3. FLOAT EVALUATION (GLOBAL STATES)
   ├─ Check: float conditions (highest priority)
   ├─ Can interrupt: from any state
   └─ Common: bye, reset, error handlers

4. STATE RESOLUTION
   ├─ Current state: context.$state
   ├─ Evaluate: transitions (in order)
   ├─ Check: condition expressions
   └─ Select: first matching transition

5. ENTER METHOD EXECUTION
   ├─ Run: inline method (if defined)
   ├─ Execute: before actions
   └─ Purpose: setup, calculations

6. ACTIONS EXECUTION
   ├─ Process: action list (in order)
   ├─ Types: text, template, api, method, command, schedule
   ├─ Conditional: check action conditions
   └─ Output: messages, API calls, commands

7. DATA MAPPING
   ├─ Transform: context/data fields
   ├─ Syntax: target_path: source_expression
   └─ Execute: JavaScript expressions

8. TRANSITION
   ├─ Move: to next state (or end)
   ├─ Update: context.$state
   └─ Loop: back to step 2 (for next message)

9. PERSISTENCE
   ├─ Save: context (session data)
   ├─ Save: data (conversation state)
   └─ Track: state history
```

---

## Project Structure

### Standard Directory Layout

```
kata-bot-project/
├── bot.yml                     # Main entry point
├── nlus.yml                    # NLU definitions (optional)
├── flows/                      # Flow definitions
│   ├── greetings.yml          # Main entry flow
│   ├── payment.yml            # Payment flow
│   ├── support.yml            # Support flow
│   ├── fallback.yml           # Error handling
│   └── [feature].yml          # Feature-specific flows
├── method/                     # Custom JavaScript
│   ├── function.js            # Business logic (ES5!)
│   └── helper.js              # Helper functions
└── README.md                   # Documentation
```

### bot.yml Structure

The `bot.yml` file is the **main configuration file** that ties everything together:

```yaml
schema: kata.ai/schema/kata-ml/1.0
name: MyBot
desc: Bot description
version: 1.0.0

# Maximum recursion depth for flow transitions
# Prevents infinite loops
maxRecursion: 20

# Flow definitions (can be inline or $include)
flows:
    # Main entry flow (always starts here)
    greetings: $include(./flows/greetings.yml)

    # Feature flows
    payment: $include(./flows/payment.yml)
    support: $include(./flows/support.yml)

    # Error handling
    fallback: $include(./flows/fallback.yml)

# Custom methods (ES5 JavaScript)
methods:
    # Method name: function signature
    validatePhone: $include(./method/function.js:validatePhone)
    formatCurrency: $include(./method/function.js:formatCurrency)

# NLU definitions (intent classifiers)
nlus: $include(./nlus.yml)

# Global configuration
config:
    botName: "MyBot Assistant"
    apiUrl: "https://api.example.com"
    apiKey: "secret_key_here"
    maxRetries: 3
```

### Flow File Structure

Each flow file defines a complete dialogue flow:

```yaml
# Intent definitions (how user input is recognized)
intents:
    intentName:
        type: text|data|command
        priority: 1-100
        classifier:
            nlu: nluName
        condition: "boolean expression"

# State definitions (dialogue states)
states:
    stateName:
        initial: true|false        # Entry point
        enter: methodName          # Pre-action method
        action:                    # Actions to execute
            - name: actionName
              condition: "..."     # Optional condition
        transitions:               # Where to go next
            nextState:
                condition: "..."
                mapping:
                    target: source
        float:                     # Global interrupt
            condition: "..."
        end: true|false            # Terminal state

# Action definitions (bot outputs)
actions:
    actionName:
        type: text|template|api|method|command|schedule
        options:
            # Type-specific options

# Method definitions (inline JavaScript)
methods:
    methodName(ctx): "
        // ES5 JavaScript code
        return ctx;
    "
```

---

## Core Concepts

### State Machine Model

Kata Platform implements a **finite state machine (FSM)**:

- **States**: Nodes in the conversation graph
- **Intents**: User input triggers
- **Transitions**: Edges between states
- **Actions**: Side effects (output, API calls)
- **Context/Data**: State variables

### Three-Layer Architecture

#### 1. **Intent Layer** (Input Recognition)
Classifies user input into actionable intents using:
- NLU models (ML-based)
- Keyword matching (exact/fuzzy)
- Regex patterns
- Custom validation methods
- Payload conditions (button clicks)

#### 2. **State Layer** (Flow Logic)
Manages conversation state:
- Evaluates conditions
- Executes business logic
- Controls flow transitions
- Handles errors

#### 3. **Action Layer** (Output Generation)
Produces bot responses:
- Text messages
- UI templates (buttons, carousels)
- API calls
- Commands (flow transitions, schedules)

---

## Intents

Intents classify user input and determine which transition to follow.

### Intent Structure

```yaml
intents:
    intentName:
        # Intent type
        type: text | data | command

        # Processing priority (higher = earlier)
        # Range: -100 to 100
        priority: 10

        # Can this intent start a flow?
        initial: true | false

        # Classifier definition
        classifier:
            nlu: nluName               # NLU model
            # OR
            method: methodName         # Custom validator
            # OR (keyword/regex defined in nlus.yml)

        # Additional condition
        condition: "boolean expression"

        # Fallback intent (catch-all)
        fallback: true | false

        # Extract attributes
        attributes:
            attrName:
                nlu: nluName
```

### Intent Types

#### text
For natural language input:

```yaml
greetingIntent:
    type: text
    priority: 20
    classifier:
        nlu: greetingNLU
```

#### data
For structured payloads (button clicks, menu selections):

```yaml
paymentIntent:
    type: data
    priority: 10
    condition: "payload.cmd == 'payment'"
```

#### command
For system-generated events:

```yaml
scheduleIntent:
    type: command
    priority: 1
    condition: "content == 'scheduleReminder'"
```

### Intent Priority

Intents are evaluated **in priority order** (highest first):

```yaml
intents:
    # Checked first
    resetIntent:
        priority: 100
        # ...

    # Checked second
    paymentIntent:
        priority: 50
        # ...

    # Checked third
    generalIntent:
        priority: 10
        # ...

    # Checked last (catch-all)
    fallbackIntent:
        priority: -10
        fallback: true
```

### Intent Conditions

Additional boolean checks:

```yaml
intents:
    paymentIntent:
        type: data
        # Only match if:
        # 1. Type is 'data' AND
        # 2. Condition is true
        condition: "payload.cmd == 'payment' && data.status == 'active'"
```

**Available variables:**
- `intent` - Matched intent name
- `content` - Message content
- `payload` - Structured data payload
- `context.*` - Session variables
- `data.*` - Conversation variables
- `metadata.*` - Channel metadata

---

## States

States represent dialogue positions in the conversation flow.

### State Structure

```yaml
states:
    stateName:
        # Is this the entry point?
        initial: true

        # Execute method before actions
        enter: methodName

        # Actions to execute
        action:
            - name: actionName
              condition: "optional condition"
            - name: anotherAction

        # Transition definitions
        transitions:
            targetState:
                condition: "boolean expression"
                mapping:
                    target_field: "source expression"
            fallback: true  # Default transition

        # Float condition (global interrupt)
        float:
            condition: "intent == 'bye'"
            mapping:
                # ...

        # Mark as terminal state
        end: true
```

### Initial State

Every flow must have **exactly one** initial state:

```yaml
states:
    start:
        initial: true
        action:
            - name: welcomeMessage
        transitions:
            menu:
                fallback: true
```

### Enter Method

Execute logic **before** actions run:

```yaml
states:
    calculateTotal:
        enter: computeTotalAmount
        action:
            - name: showTotal
        transitions:
            # ...

methods:
    computeTotalAmount(ctx): "
        var total = 0;
        for (var i = 0; i < ctx.data.items.length; i++) {
            total += ctx.data.items[i].price;
        }
        ctx.data.totalAmount = total;
        return ctx;
    "
```

### Float Conditions

**Global interrupts** that can trigger from **any state**:

```yaml
states:
    bye:
        priority: 100  # Higher priority
        float:
            condition: "intent == 'byeIntent'"
            mapping:
                data.conversationEnded: "'true'"
        action:
            - name: goodbyeMessage
        end: true
```

Float states are checked **before** regular transitions and can interrupt the normal flow from anywhere.

### End States

Terminal states that conclude the flow:

```yaml
states:
    completed:
        action:
            - name: successMessage
        end: true  # Flow ends here
```

---

## Actions

Actions define what the bot **outputs** or **does**.

### Action Types

#### text
Simple text message:

```yaml
actions:
    welcomeMessage:
        type: text
        options:
            text: "Hello! How can I help you today?"
```

**Variable interpolation:**

```yaml
actions:
    greetUser:
        type: text
        options:
            text: "Hi $(data.firstName), your balance is Rp $(data.balance)"
```

#### template
UI elements (buttons, carousels):

```yaml
actions:
    paymentOptions:
        type: template
        options:
            type: button
            items:
                text: "Select payment method:"
                actions:
                    - type: postback
                      label: "Credit Card"
                      payload:
                          cmd: "payment"
                          method: "card"
                    - type: postback
                      label: "Bank Transfer"
                      payload:
                          cmd: "payment"
                          method: "transfer"
```

#### api
HTTP request to external service:

```yaml
actions:
    fetchUserData:
        type: api
        options:
            method: POST
            uri: "$(config.apiUrl)/users"
            headers:
                Authorization: "Bearer $(config.apiToken)"
                Content-Type: "application/json"
            body:
                userId: "$(data.userId)"
                action: "getUserInfo"
```

#### method
Execute custom JavaScript function:

```yaml
actions:
    validateInput:
        type: method
        method: validateUserInput
```

#### command
Trigger internal command (flow transition):

```yaml
actions:
    goToPayment:
        type: command
        options:
            command: "toPaymentFlow"
            payload:
                amount: "$(data.amount)"
```

#### schedule
Set up timed message:

```yaml
actions:
    setReminder:
        type: schedule
        options:
            id: "reminder_123"
            command: add
            message:
                type: command
                content: "sendReminder"
            start: "$(context.reminderTime)"
            end: "$(context.reminderTime)"
            freqType: minute
            freqInterval: 5
```

### Conditional Actions

Execute actions only when conditions match:

```yaml
states:
    processPayment:
        action:
            # Always execute
            - name: validatePayment

            # Only for premium users
            - name: applyDiscount
              condition: "data.isPremium == 'true'"

            # Only for WhatsApp channel
            - name: sendWhatsAppReceipt
              condition: "data.channelType == 'whatsapp'"
```

---

## Transitions

Transitions define **state changes** in the conversation flow.

### Transition Structure

```yaml
states:
    currentState:
        transitions:
            # Named transition (explicit)
            targetState:
                condition: "intent == 'continueIntent'"
                mapping:
                    data.nextStep: "'payment'"
                    context.amount: "payload.amount"

            # Fallback (default)
            anotherState:
                fallback: true
```

### Transition Evaluation Order

Transitions are checked **in definition order**:

```yaml
states:
    menu:
        transitions:
            # Checked FIRST
            payment:
                condition: "intent == 'paymentIntent'"

            # Checked SECOND
            support:
                condition: "intent == 'supportIntent'"

            # Checked LAST (if nothing else matches)
            menu:
                fallback: true
```

⚠️ **Order matters!** First matching transition wins.

### Condition Expressions

Boolean JavaScript expressions:

```yaml
transitions:
    nextState:
        # Simple equality
        condition: "intent == 'confirmIntent'"

    anotherState:
        # Multiple conditions (AND)
        condition: "intent == 'paymentIntent' && data.balance > 0"

    thirdState:
        # Multiple conditions (OR)
        condition: "intent == 'exitIntent' || intent == 'cancelIntent'"

    fourthState:
        # Complex expression
        condition: "intent == 'checkoutIntent' && data.cart.length > 0 && data.loggedIn == 'true'"
```

**Available variables:**
- `intent` - Current matched intent
- `content` - Message content
- `payload.*` - Data payload fields
- `context.*` - Session variables
- `data.*` - Conversation variables
- `metadata.*` - Channel metadata

### Data Mapping

Transform data during transitions:

```yaml
transitions:
    checkout:
        condition: "intent == 'proceedIntent'"
        mapping:
            # Copy from payload to data
            data.selectedMethod: "payload.paymentMethod"

            # Execute JavaScript expression
            data.totalAmount: "parseInt(payload.amount) + parseInt(data.tax)"

            # Set literal value
            data.status: "'processing'"

            # Copy to context (session-level)
            context.lastAction: "'checkout'"

            # Access nested objects
            data.user.id: "payload.userId"
```

**Mapping syntax:**
```
target_path: "source_expression"
```

- **Left side** (target): Where to store
- **Right side** (source): JavaScript expression to evaluate

### Fallback Transitions

Default path when no conditions match:

```yaml
transitions:
    specificCase:
        condition: "intent == 'specificIntent'"

    # If no other transition matches, go here
    defaultState:
        fallback: true
```

⚠️ **Always provide a fallback** to prevent undefined behavior.

---

## Methods

Methods are **ES5 JavaScript functions** for custom logic.

### Method Signature

```javascript
methodName(msg, ctx, dat, opts, cfg, result)
```

**Parameters:**
- `msg` - Current message object
- `ctx` - Context object (read/write session data)
- `dat` - Data object (read/write conversation data)
- `opts` - Method options (from YAML)
- `cfg` - Bot configuration (from bot.yml config)
- `result` - Previous API/method result (if chained)

### Return Types

#### 1. Modify Context (most common)

```javascript
validatePhone(msg, ctx, dat, opts, cfg, result) {
    var phone = ctx.data.phoneNumber;

    // Validate Indonesian phone number
    var isValid = /^(08|628)[0-9]{8,11}$/.test(phone);

    // Store result in context
    ctx.data.isValidPhone = isValid;

    // Must return context
    return ctx;
}
```

#### 2. Return Command/Payload

```javascript
checkBalance(msg, ctx, dat, opts, cfg, result) {
    var balance = parseFloat(result.balance);

    if (balance > 0) {
        return {
            type: 'command',
            content: 'hasBalance',
            payload: {
                amount: balance
            }
        };
    } else {
        return {
            type: 'command',
            content: 'noBalance',
            payload: {
                amount: 0
            }
        };
    }
}
```

### ES5 Constraints

⚠️ **CRITICAL**: Kata Platform only supports **ECMAScript 5**.

#### NOT ALLOWED (ES6+)

```javascript
// ❌ Arrow functions
const add = (a, b) => a + b;

// ❌ Let/const
let name = 'John';
const MAX = 100;

// ❌ Template literals
var msg = `Hello ${name}`;

// ❌ Destructuring
const {id, name} = user;

// ❌ Spread operator
const merged = {...obj1, ...obj2};

// ❌ Class syntax
class User {
    constructor(name) {
        this.name = name;
    }
}

// ❌ For...of loops
for (const item of items) { }

// ❌ Default parameters
function greet(name = 'Guest') { }

// ❌ Object shorthand
const obj = {name, age};
```

#### REQUIRED (ES5)

```javascript
// ✅ Regular functions
function add(a, b) {
    return a + b;
}

// ✅ Var only
var name = 'John';
var MAX = 100;

// ✅ String concatenation
var msg = 'Hello ' + name;

// ✅ Manual property access
var id = user.id;
var name = user.name;

// ✅ Manual object merge
var merged = {};
for (var key in obj1) {
    if (obj1.hasOwnProperty(key)) {
        merged[key] = obj1[key];
    }
}
for (var key in obj2) {
    if (obj2.hasOwnProperty(key)) {
        merged[key] = obj2[key];
    }
}

// ✅ Constructor functions
function User(name) {
    this.name = name;
}

// ✅ For loops
for (var i = 0; i < items.length; i++) {
    var item = items[i];
}

// ✅ Default parameters (manual)
function greet(name) {
    name = name || 'Guest';
}

// ✅ Explicit object properties
var obj = {
    name: name,
    age: age
};
```

### Common Method Patterns

#### Pattern 1: Data Validation

```javascript
validateEmail(msg, ctx, dat, opts, cfg, result) {
    var email = ctx.data.email || '';
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    ctx.data.isValidEmail = emailRegex.test(email);

    return ctx;
}
```

#### Pattern 2: API Response Parsing

```javascript
parseUserData(msg, ctx, dat, opts, cfg, result) {
    try {
        if (result && result.data) {
            ctx.data.userId = result.data.id;
            ctx.data.userName = result.data.name;
            ctx.data.userEmail = result.data.email;
            ctx.data.parseSuccess = 'true';
        } else {
            ctx.data.parseSuccess = 'false';
        }
    } catch (e) {
        ctx.data.parseSuccess = 'false';
        ctx.data.errorMsg = e.message;
    }

    return ctx;
}
```

#### Pattern 3: Data Transformation

```javascript
formatCurrency(msg, ctx, dat, opts, cfg, result) {
    var amount = parseFloat(ctx.data.amount) || 0;

    // Format as Rupiah
    var formatted = 'Rp ' + amount.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    ctx.data.formattedAmount = formatted;

    return ctx;
}
```

#### Pattern 4: Conditional Logic

```javascript
checkEligibility(msg, ctx, dat, opts, cfg, result) {
    var age = parseInt(ctx.data.age) || 0;
    var balance = parseFloat(ctx.data.balance) || 0;

    var isEligible = age >= 18 && balance >= 100000;

    return {
        type: 'command',
        content: isEligible ? 'eligible' : 'notEligible',
        payload: {
            age: age,
            balance: balance,
            eligible: isEligible
        }
    };
}
```

---

## NLU System

Natural Language Understanding classifies user input.

### NLU Types

#### keyword
Exact or fuzzy keyword matching:

```yaml
nlus:
    paymentKeyword:
        type: keyword
        options:
            keywords:
                payment:
                    - bayar
                    - pembayaran
                    - pay
                    - tagihan
            exact: false  # Fuzzy matching
```

#### regex
Regular expression matching:

```yaml
nlus:
    phoneNumber:
        type: regex
        options:
            regex: "^(08|628)[0-9]{8,11}$"
```

#### method
Custom validation function:

```yaml
nlus:
    customValidator:
        type: method
        method: validateInput
```

```javascript
// In function.js
validateInput(text, ctx) {
    // Custom logic
    return text.length > 5 && text.length < 100;
}
```

#### nl
External NLU service (ML-based):

```yaml
nlus:
    intentClassifier:
        type: nl
        options:
            nluId: "YourProject:intent-model"
            threshold: 0.75
```

### NLU in Intents

```yaml
intents:
    paymentIntent:
        type: text
        classifier:
            nlu: paymentKeyword
        condition: "context.$state == 'menu'"
```

---

## Schedulers

Schedulers send **delayed or recurring messages**.

### Scheduler Actions

#### scheduleRun (Create)

```yaml
actions:
    setReminder:
        type: schedule
        options:
            id: uniqueSchedulerId        # Unique identifier
            command: add                 # Create scheduler
            message:
                type: command
                content: reminderCommand # Command to send
            start: "2026-01-30 14:00:00" # Start time (UTC+7)
            end: "2026-01-30 14:00:00"   # End time
            freqType: minute             # minute|hour|day
            freqInterval: 5              # Every 5 minutes
```

#### scheduleOff (Delete)

```yaml
actions:
    cancelReminder:
        type: schedule
        options:
            id: uniqueSchedulerId        # Same ID as above
            command: remove              # Delete scheduler
```

### Scheduler Pattern

**CRITICAL**: Every scheduler **must** have a cleanup action.

```yaml
states:
    waitingForResponse:
        enter: timeSchedule
        action:
            # Turn off old scheduler (if exists)
            - name: scheduleOffReminder

            # Create new scheduler
            - name: scheduleRunReminder

            # Send message
            - name: askQuestion
        transitions:
            # ...

methods:
    timeSchedule(ctx): "
        var now = new Date(ctx.context.$now);
        now.setMinutes(now.getMinutes() + 3);

        var dateISO = now.toISOString();
        var parts = dateISO.split('T');
        var timeParts = parts[1].split('.');

        ctx.context.reminderTime = parts[0] + ' ' + timeParts[0];

        return ctx;
    "

actions:
    scheduleRunReminder:
        type: schedule
        options:
            id: reminder_user_response
            command: add
            message:
                type: command
                content: timeoutReminder
            start: $(context.reminderTime)
            end: $(context.reminderTime)
            freqType: minute
            freqInterval: 3

    scheduleOffReminder:
        type: schedule
        options:
            id: reminder_user_response
            command: remove
```

### Scheduler Cleanup Pattern

**Always clean up schedulers in:**
1. **Bye states** (when user exits)
2. **State transitions** (before creating new ones)
3. **Error handlers** (to prevent orphans)

```yaml
states:
    bye:
        float:
            condition: "intent == 'timeoutIntent'"
        action:
            # CRITICAL: Clean up schedulers
            - name: scheduleOffReminder
            - name: scheduleOffFollowup
            - name: scheduleOffNotification
            - name: byeMessage
        end: true
```

---

## Context & Data

### Context (Session-Level)

**Persists across flows** within a session:

```yaml
mapping:
    context.userId: "payload.userId"
    context.sessionId: "payload.sessionId"
    context.lastFlow: "'payment'"
```

**Special context variables:**
- `context.$state` - Current state name
- `context.$lastFlow` - Previous flow name
- `context.$now` - Current timestamp

### Data (Conversation-Level)

**Flow-specific variables**:

```yaml
mapping:
    data.firstName: "payload.name"
    data.amount: "payload.amount"
    data.status: "'pending'"
```

### Metadata (Channel Info)

**Read-only channel information**:

- `metadata.channelType` - 'whatsapp', 'qiscus', 'generic'
- `metadata.whatsappSenderId` - WhatsApp phone number
- `metadata.qiscusSenderId` - Qiscus user ID

### Variable Interpolation

Use `$()` syntax to interpolate variables:

```yaml
actions:
    greeting:
        type: text
        options:
            text: "Hi $(data.firstName), your balance is $(data.balance)"
```

In API calls:

```yaml
actions:
    callAPI:
        type: api
        options:
            uri: "$(config.apiUrl)/users/$(data.userId)"
            body:
                amount: "$(data.amount)"
```

---

## Multi-Channel Support

Kata Platform supports multiple messaging channels.

### Channel Detection

```yaml
actions:
    sendMessage:
        type: text
        condition: "data.channelType == 'qiscus'"
        options:
            text: "Message for Qiscus"

    sendWhatsApp:
        type: api
        condition: "data.channelType == 'generic'"
        options:
            uri: "https://api-whatsapp.kata.ai/v1/messages"
            # ...
```

### WhatsApp-Specific Features

#### Interactive Messages

```yaml
actions:
    whatsappButton:
        type: api
        options:
            method: POST
            uri: "https://api-whatsapp.kata.ai/v1/messages"
            headers:
                Authorization: "Bearer $(config.waToken)"
            body:
                to: "$(data.waSenderId)"
                type: interactive
                interactive:
                    type: button
                    body:
                        text: "Choose an option:"
                    action:
                        buttons:
                            - type: reply
                              reply:
                                  id: btn_1
                                  title: "Option 1"
```

#### CTA (Call-to-Action) URLs

```yaml
actions:
    whatsappCTA:
        type: api
        options:
            method: POST
            uri: "https://api-whatsapp.kata.ai/v1/messages"
            headers:
                Authorization: "Bearer $(config.waToken)"
            body:
                to: "$(data.waSenderId)"
                type: interactive
                interactive:
                    type: cta_url
                    body:
                        text: "Download your invoice"
                    action:
                        name: cta_url
                        parameters:
                            display_text: "Download PDF"
                            url: "$(context.invoiceUrl)"
```

---

## API Integration

### API Action Structure

```yaml
actions:
    callExternalAPI:
        type: api
        options:
            method: POST | GET | PUT | DELETE
            uri: "https://api.example.com/endpoint"
            headers:
                Authorization: "Bearer $(config.apiToken)"
                Content-Type: "application/json"
            body:
                field1: "$(data.value1)"
                field2: "value2"
                nested:
                    field3: "$(data.value3)"
```

### Response Handling

API responses are available in the `payload` variable:

```yaml
states:
    fetchData:
        action:
            - name: callAPI
            - name: parseResponse
        transitions:
            success:
                condition: "payload.status == 'success'"
                mapping:
                    data.userId: "payload.data.id"
                    data.userName: "payload.data.name"

            error:
                condition: "payload.status == 'error'"
                mapping:
                    data.errorMsg: "payload.message"
```

### Error Handling Pattern

```yaml
states:
    callAPI:
        action:
            - name: apiRequest
        transitions:
            # Check for successful response
            success:
                condition: "payload.result == 1"
                mapping:
                    data.apiData: "payload.data"

            # API returned error code
            apiError:
                condition: "payload.result != 1"
                mapping:
                    data.errorCode: "payload.errorCode"

            # API call failed (timeout, network, etc.)
            networkError:
                fallback: true
```

---

## Flow Control Patterns

### Pattern 1: Menu Navigation

```yaml
states:
    mainMenu:
        action:
            - name: showMenu
        transitions:
            payment:
                condition: "intent == 'paymentIntent'"

            support:
                condition: "intent == 'supportIntent'"

            settings:
                condition: "intent == 'settingsIntent'"

            # Stay in menu if invalid input
            mainMenu:
                fallback: true
```

### Pattern 2: Multi-Step Form

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
                    data.errorMsg: "'Invalid email format'"

    askPhone:
        # ... continue form
```

### Pattern 3: Confirmation Flow

```yaml
states:
    showSummary:
        action:
            - name: displaySummary
            - name: askConfirmation
        transitions:
            confirmed:
                condition: "intent == 'yesIntent'"

            cancelled:
                condition: "intent == 'noIntent'"

            # Re-ask if unclear
            showSummary:
                fallback: true

    confirmed:
        action:
            - name: processOrder
            - name: sendConfirmation
        end: true

    cancelled:
        action:
            - name: sendCancellation
        transitions:
            mainMenu:
                fallback: true
```

### Pattern 4: Error Recovery

```yaml
states:
    processPayment:
        action:
            - name: callPaymentAPI
        transitions:
            paymentSuccess:
                condition: "payload.status == 'success'"
                mapping:
                    data.transactionId: "payload.transactionId"

            paymentRetry:
                condition: "payload.status == 'retry'"
                mapping:
                    data.retryCount: "parseInt(data.retryCount || 0) + 1"

            paymentFailed:
                fallback: true

    paymentRetry:
        action:
            - name: retryMessage
        transitions:
            processPayment:
                condition: "parseInt(data.retryCount) < 3"

            paymentFailed:
                condition: "parseInt(data.retryCount) >= 3"
```

### Pattern 5: Flow Handover

```yaml
# In flow A
states:
    transferToFlowB:
        action:
            - name: transferCommand
        end: true

actions:
    transferCommand:
        type: command
        options:
            command: "toFlowB"
            payload:
                transferData: "$(data.someValue)"

# In flow B
intents:
    startFlowB:
        type: command
        condition: "content == 'toFlowB'"

states:
    initFlowB:
        initial: true
        action:
            - name: receiveData
        transitions:
            # ...
        mapping:
            data.receivedData: "payload.transferData"
```

---

## Best Practices

### 1. Flow Design

✅ **DO:**
- Keep flows focused on single features
- Provide clear exit paths (back, cancel, main menu)
- Use meaningful state/intent names
- Document complex logic with comments
- Always include fallback transitions

❌ **DON'T:**
- Create circular transitions without exit conditions
- Mix multiple features in one flow
- Use generic names (state1, state2, etc.)
- Forget to handle edge cases

### 2. State Management

✅ **DO:**
- Initialize data fields early
- Clear sensitive data after use
- Use context for session-wide data
- Use data for flow-specific variables
- Reset data on flow exit

❌ **DON'T:**
- Assume fields are set
- Leave credentials in context
- Use global variables (not supported)
- Forget to clean up data

### 3. Intent Design

✅ **DO:**
- Use descriptive intent names
- Set appropriate priorities
- Add conditions for disambiguation
- Test NLU with real user input
- Provide clear fallback handling

❌ **DON'T:**
- Create overlapping intents
- Use too broad keyword matching
- Forget to prioritize critical intents
- Skip intent condition checks

### 4. Method Writing

✅ **DO:**
- Use ES5 syntax only
- Add try-catch for error handling
- Return context object
- Validate input data
- Keep functions focused and small

❌ **DON'T:**
- Use ES6+ features
- Modify global state
- Assume data exists
- Write complex nested logic
- Forget to return

### 5. API Integration

✅ **DO:**
- Handle timeout scenarios
- Parse response data carefully
- Use environment-specific configs
- Log errors for debugging
- Implement retry logic

❌ **DON'T:**
- Hardcode URLs/tokens
- Assume API always succeeds
- Ignore error responses
- Make blocking synchronous calls (N/A in Kata)

### 6. Scheduler Management

✅ **DO:**
- Clean up schedulers in bye states
- Use unique scheduler IDs
- Turn off before creating new ones
- Document scheduler purpose
- Test scheduler cleanup

❌ **DON'T:**
- Create schedulers without cleanup
- Reuse scheduler IDs across flows
- Forget to handle scheduler intents
- Leave orphaned schedulers

### 7. Testing

✅ **DO:**
- Test happy paths
- Test error scenarios
- Test edge cases (empty input, wrong format)
- Test across channels (WhatsApp, Web)
- Test scheduler timing

❌ **DON'T:**
- Test only once
- Skip error path testing
- Assume conditions work
- Forget to test transitions

---

## Debugging

### Common Issues & Solutions

#### Issue: Transition Not Firing

**Symptoms:**
- Bot doesn't move to expected state
- Stays in same state or goes to fallback

**Causes:**
1. Condition syntax error
2. Variable not set
3. Wrong intent matched
4. Priority conflict

**Debug steps:**
```yaml
# Add debug action to see current state
states:
    problematicState:
        action:
            # Add this temporarily
            - name: debugAction
        transitions:
            # ...

actions:
    debugAction:
        type: text
        options:
            text: |
                DEBUG:
                Intent: $(intent)
                Data.field: $(data.field)
                Context.field: $(context.field)
```

#### Issue: Method Not Executing

**Symptoms:**
- Method action runs but no effect
- Data not updated

**Causes:**
1. ES6 syntax used (fails silently!)
2. Method doesn't return context
3. Wrong parameter access

**Debug steps:**
```javascript
// Add logging at start
methodName(msg, ctx, dat, opts, cfg, result) {
    // Log to verify execution
    ctx.data.debugMethodRan = 'true';

    try {
        // Your logic here
        ctx.data.result = 'success';
    } catch (e) {
        // Catch errors
        ctx.data.error = e.message;
    }

    // MUST return context
    return ctx;
}
```

#### Issue: Scheduler Keeps Firing

**Symptoms:**
- Bye message appears unexpectedly
- Scheduler triggers after flow end

**Causes:**
1. Missing scheduleOff action
2. Scheduler not cleaned in bye state
3. Wrong scheduler ID

**Debug steps:**
```yaml
# Check all states that set schedulers
states:
    stateWithScheduler:
        action:
            # MUST have corresponding Off
            - name: scheduleOffReminder  # Turn off first
            - name: scheduleRunReminder  # Then create new
        transitions:
            # ...

# Ensure bye state cleans up
states:
    bye:
        float:
            condition: "intent == 'scheduleRunReminder'"
        action:
            - name: scheduleOffReminder  # Clean up
            - name: byeMessage
        end: true
```

#### Issue: API Not Returning Data

**Symptoms:**
- payload.* variables are undefined
- Transitions fail after API call

**Causes:**
1. API timeout
2. Wrong response format
3. Method not parsing correctly

**Debug steps:**
```yaml
states:
    afterAPI:
        action:
            # Add debug to see raw response
            - name: debugAPIResponse
        transitions:
            # ...

actions:
    debugAPIResponse:
        type: text
        options:
            text: |
                API Response:
                Status: $(payload.status)
                Result: $(payload.result)
                Data: $(payload.data)
```

### Debug Action Pattern

```yaml
actions:
    debugState:
        type: text
        options:
            text: |
                === DEBUG INFO ===
                State: $(context.$state)
                Intent: $(intent)
                Content: $(content)
                Data.field1: $(data.field1)
                Data.field2: $(data.field2)
                Channel: $(metadata.channelType)
                ==================
```

---

## Common Pitfalls

### 1. ES6 Syntax in Methods

**Problem:**
```javascript
// ❌ This will FAIL SILENTLY
const validatePhone = (phone) => {
    return /^08[0-9]{8,11}$/.test(phone);
};
```

**Solution:**
```javascript
// ✅ Use ES5
function validatePhone(phone) {
    var pattern = /^08[0-9]{8,11}$/;
    return pattern.test(phone);
}
```

### 2. Forgotten Fallback

**Problem:**
```yaml
transitions:
    success:
        condition: "intent == 'yesIntent'"

    error:
        condition: "intent == 'noIntent'"

    # ❌ Missing fallback - what if neither matches?
```

**Solution:**
```yaml
transitions:
    success:
        condition: "intent == 'yesIntent'"

    error:
        condition: "intent == 'noIntent'"

    # ✅ Always provide fallback
    askAgain:
        fallback: true
```

### 3. Circular Transitions

**Problem:**
```yaml
states:
    stateA:
        transitions:
            stateB:
                fallback: true

    stateB:
        transitions:
            stateA:
                fallback: true

    # ❌ Infinite loop!
```

**Solution:**
```yaml
states:
    stateA:
        transitions:
            stateB:
                condition: "intent == 'continueIntent'"

            # ✅ Provide exit
            exit:
                fallback: true

    stateB:
        transitions:
            stateA:
                condition: "intent == 'backIntent'"

            # ✅ Provide exit
            exit:
                fallback: true
```

### 4. Scheduler Leak

**Problem:**
```yaml
states:
    askQuestion:
        action:
            # ❌ Create scheduler but never clean up
            - name: scheduleRunReminder
        transitions:
            # ... user exits flow
            # Scheduler keeps running!
```

**Solution:**
```yaml
states:
    askQuestion:
        action:
            - name: scheduleOffReminder  # ✅ Clean up first
            - name: scheduleRunReminder
        transitions:
            # ...

    bye:
        float:
            condition: "intent == 'timeoutIntent'"
        action:
            - name: scheduleOffReminder  # ✅ Clean up in bye
            - name: byeMessage
        end: true
```

### 5. Undefined Variable Access

**Problem:**
```yaml
mapping:
    # ❌ What if payload.user doesn't exist?
    data.userName: "payload.user.name"
```

**Solution:**
```yaml
# ✅ Use method to safely access
states:
    processUser:
        action:
            - name: extractUserName
        transitions:
            # ...

methods:
    extractUserName(msg, ctx, dat, opts, cfg, result): "
        var userName = 'Unknown';

        if (result && result.user && result.user.name) {
            userName = result.user.name;
        }

        ctx.data.userName = userName;
        return ctx;
    "
```

---

## Appendix: Quick Reference

### Intent Evaluation Order

1. **Float conditions** (highest priority)
2. **Regular intents** (by priority value)
3. **Fallback intent** (lowest priority)

### Transition Evaluation Order

1. **Float condition** (if defined)
2. **Named transitions** (in definition order)
3. **Fallback transition** (last resort)

### Variable Scopes

| Scope | Lifetime | Use Case |
|-------|----------|----------|
| `context.*` | Session | User ID, session data |
| `data.*` | Flow | Form fields, temp data |
| `metadata.*` | Message | Channel, sender info |
| `payload.*` | Action | API response, button data |

### Action Types

| Type | Purpose | Example |
|------|---------|---------|
| `text` | Simple message | Welcome text |
| `template` | UI elements | Buttons, carousels |
| `api` | HTTP request | Fetch user data |
| `method` | Custom logic | Validate input |
| `command` | Internal command | Flow transition |
| `schedule` | Timed message | Reminders |

### ES5 vs ES6 Comparison

| Feature | ES5 ✅ | ES6 ❌ |
|---------|--------|--------|
| Functions | `function f() {}` | `() => {}` |
| Variables | `var x` | `let x`, `const x` |
| Strings | `'a' + b` | `` `a${b}` `` |
| Objects | `{a: a}` | `{a}` |
| Loops | `for (var i...)` | `for (const x of...)` |

---

**End of Technical Reference**

*This document is maintained by the Kata.ai engineering team. Last updated: January 2026*
