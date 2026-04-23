# Kata Intent Designer Skill

Expert skill for designing and managing intent classifiers in Kata Platform YAML bots.

## When to Use This Skill

Use this skill when you need to:
- Define how user input is recognized and classified
- Create keyword, regex, or NLU-based intents
- Set intent priorities and evaluation conditions
- Design data payload structures for intents
- Handle multi-channel input variations
- Debug intent classification issues
- Optimize intent matching performance

## Intent Fundamentals

Intents are the entry points to your conversation flows. They classify user input and route it to the appropriate state handler.

### Intent Types

1. **Command Intent** - Internal system commands (schedulers, transitions)
2. **Text Intent** - Keyword or regex matching on user messages
3. **Data Intent** - Button clicks, quick replies, payload-based inputs
4. **Method Intent** - Custom classification logic via ES5 methods

### Intent Structure

```yaml
intents:
  intentName:
    priority: 1                    # Lower = higher priority (1 is highest)
    type: text                     # text, command, data, method
    condition: 'true'              # Optional boolean expression
    initial: false                 # Mark as conversation starter
    fallback: false                # Mark as fallback handler
    attributes:
      # Intent-specific configuration
```

## Usage Patterns

### Pattern 1: Keyword Intent

Simple keyword matching for common phrases:

```yaml
intents:
  greet:
    priority: 5
    type: text
    condition: 'content.toLowerCase() == "hi" || content.toLowerCase() == "hello"'
    initial: true

  checkBilling:
    priority: 10
    type: text
    condition: 'content.toLowerCase().indexOf("billing") >= 0 || content.toLowerCase().indexOf("tagihan") >= 0'
```

**When to use:**
- Simple, unambiguous keyword matching
- High-confidence triggers (greetings, menu selections)
- Performance-critical paths (avoids NLU overhead)

### Pattern 2: Regex Intent

Pattern matching for structured input:

```yaml
intents:
  phoneNumber:
    priority: 8
    type: text
    condition: '/^(08|628)[0-9]{8,11}$/.test(content)'

  ticketNumber:
    priority: 7
    type: text
    condition: '/^TKT[0-9]{10}$/.test(content)'

  emailAddress:
    priority: 9
    type: text
    condition: '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(content)'
```

**When to use:**
- Validating user input format (phone numbers, emails, IDs)
- Extracting structured data
- Enforcing input patterns

### Pattern 3: NLU Intent

Natural language understanding for complex classification:

```yaml
nlus:
  nluBilling:
    type: nl
    options:
      threshold: 0.7
    nlu:
      type: keyword
      profile: billingProfile

intents:
  checkBilling:
    priority: 10
    type: text
    condition: 'nlu.billing && nlu.billing.confidence > 0.7'
```

**When to use:**
- Handling natural language variations
- Multi-word phrase understanding
- Intent classification with confidence scoring

### Pattern 4: Data/Payload Intent

Button clicks and quick reply handling:

```yaml
intents:
  selectPaymentMethod:
    priority: 5
    type: data
    condition: 'payload.action == "selectPayment"'
    attributes:
      data:
        method: $(payload.method)
        amount: $(payload.amount)

  quickReplyYes:
    priority: 3
    type: data
    condition: 'payload.type == "quickReply" && payload.value == "yes"'
```

**When to use:**
- Handling structured input from buttons/quick replies
- Capturing metadata from interactive messages
- WhatsApp list/button responses

### Pattern 5: Method Intent

Custom classification logic via ES5 method:

```yaml
methods:
  classifyComplaint:
    code: |
      function classifyComplaint(msg, ctx, dat, opts, cfg, result) {
        var content = msg.content.toLowerCase();
        var keywords = {
          internet: ['internet', 'koneksi', 'wifi', 'slow', 'lemot'],
          billing: ['tagihan', 'bayar', 'payment', 'invoice'],
          technical: ['error', 'rusak', 'broken', 'not working']
        };

        for (var category in keywords) {
          var words = keywords[category];
          for (var i = 0; i < words.length; i++) {
            if (content.indexOf(words[i]) >= 0) {
              return {
                command: 'updateContext',
                payload: {
                  complaintType: category,
                  confidence: 0.85
                }
              };
            }
          }
        }

        return {
          command: 'updateContext',
          payload: { complaintType: 'unknown', confidence: 0.0 }
        };
      }

intents:
  complaint:
    priority: 12
    type: method
    method: classifyComplaint
    condition: 'context.complaintType != "unknown"'
```

**When to use:**
- Complex classification logic
- Multi-factor intent detection
- Custom confidence scoring
- Business rule-based routing

### Pattern 6: Command Intent

Internal system triggers (schedulers, transitions):

```yaml
intents:
  scheduleRunTimeout:
    priority: 1
    type: command
    condition: 'content == "scheduleRunTimeout"'

  transitionToMenu:
    priority: 1
    type: command
    condition: 'content == "transitionToMenu"'
```

**When to use:**
- Scheduler triggers
- Programmatic state transitions
- Internal flow control

### Pattern 7: Conditional Intent

Context-aware intent activation:

```yaml
intents:
  confirmPayment:
    priority: 8
    type: text
    condition: 'context.awaitingConfirmation == true && (content.toLowerCase() == "yes" || content.toLowerCase() == "ya")'

  cancelIfActive:
    priority: 6
    type: text
    condition: 'context.sessionActive == true && content.toLowerCase().indexOf("cancel") >= 0'
```

**When to use:**
- State-dependent intent matching
- Conditional routing based on conversation context
- Session-aware handlers

## Intent Priority Strategy

Priority determines evaluation order (lower number = higher priority):

```yaml
# Priority 1-3: System/Command intents
intents:
  scheduleRunTimeout:
    priority: 1
    type: command

  # Priority 4-7: High-confidence data intents
  buttonClick:
    priority: 5
    type: data

  # Priority 8-12: Text/regex intents
  phoneValidation:
    priority: 8
    type: text

  # Priority 13-20: NLU/method intents
  naturalLanguage:
    priority: 15
    type: text

  # Priority 90+: Fallback intents
  fallback:
    priority: 99
    type: text
    fallback: true
```

**Priority Guidelines:**
- 1-3: Commands, schedulers, critical system intents
- 4-7: Structured data (buttons, quick replies)
- 8-12: Keyword/regex text matching
- 13-20: NLU and method-based classification
- 90-99: Fallback and catch-all handlers

## Data Payload Mapping

Extract data from intents using attributes:

```yaml
intents:
  selectProduct:
    priority: 5
    type: data
    condition: 'payload.action == "selectProduct"'
    attributes:
      data:
        productId: $(payload.id)
        productName: $(payload.name)
        productPrice: $(payload.price)
        selectedAt: $(metadata.timestamp)

  # Now data.productId, data.productName, etc. are available in states
```

**Variable Interpolation:**
- `$(payload.field)` - From button/quick reply payload
- `$(content)` - Raw user message
- `$(metadata.field)` - System metadata (channel, timestamp, etc.)
- `$(context.field)` - Current context data
- `$(data.field)` - Current data scope

## Multi-Channel Intent Design

Handle channel-specific input variations:

```yaml
intents:
  menuSelection:
    priority: 5
    type: text
    # WhatsApp: List response comes as text
    # Web: Button click comes as payload
    condition: |
      (metadata.channelType == "whatsapp" && (content == "1" || content == "2" || content == "3")) ||
      (metadata.channelType == "qiscus" && payload.action == "selectMenu")
    attributes:
      data:
        # Normalize selection across channels
        menuChoice: |
          $(metadata.channelType == "whatsapp" ? content : payload.menuId)
```

**Channel Types:**
- `whatsapp` - WhatsApp Business API
- `qiscus` - Qiscus Multichannel Chat
- `line` - LINE Messaging API
- `telegram` - Telegram Bot API

## Common Patterns

### Initial Intent (Conversation Starter)

```yaml
intents:
  greet:
    priority: 5
    type: text
    condition: 'content.toLowerCase() == "hi" || content.toLowerCase() == "hello"'
    initial: true
    attributes:
      context:
        sessionStarted: true
        startTime: $(metadata.timestamp)
```

### Fallback Intent

```yaml
intents:
  fallbackCounter:
    priority: 99
    type: text
    fallback: true
    condition: 'true'
    attributes:
      context:
        fallbackCount: $(context.fallbackCount ? context.fallbackCount + 1 : 1)
```

### Float Intent (Global Interrupt)

```yaml
intents:
  cancelAnytime:
    priority: 3
    type: text
    condition: 'content.toLowerCase() == "cancel" || content.toLowerCase() == "batal"'

flows:
  mainFlow:
    states:
      cancel:
        float: true  # Accessible from any state
        intents:
          - cancelAnytime
```

### Reentry Intent

```yaml
intents:
  backToMenu:
    priority: 4
    type: text
    condition: 'content.toLowerCase() == "menu" || content.toLowerCase().indexOf("main menu") >= 0'
    attributes:
      context:
        # Clear previous context
        awaitingInput: null
        previousSelection: null
      command: transit
      commandArgs:
        - mainMenu
        - start
```

## Best Practices

### DO:

1. **Use Clear Priority Strategy**
   ```yaml
   # Good: Clear priority separation
   intents:
     systemCommand:
       priority: 1
     buttonClick:
       priority: 5
     textKeyword:
       priority: 10
     fallback:
       priority: 99
   ```

2. **Validate Input Format**
   ```yaml
   # Good: Strict regex validation
   phoneNumber:
     priority: 8
     type: text
     condition: '/^(08|628)[0-9]{8,11}$/.test(content)'
   ```

3. **Normalize Across Channels**
   ```yaml
   # Good: Handle channel differences
   attributes:
     data:
       selection: $(metadata.channelType == "whatsapp" ? content : payload.value)
   ```

4. **Use Fallback for Unmatched Input**
   ```yaml
   # Good: Always provide fallback
   fallback:
     priority: 99
     type: text
     fallback: true
     condition: 'true'
   ```

### DON'T:

1. **Don't Use Same Priority**
   ```yaml
   # Bad: Unpredictable evaluation order
   intent1:
     priority: 10
   intent2:
     priority: 10  # Same priority!
   ```

2. **Don't Use Overly Broad Conditions**
   ```yaml
   # Bad: Catches too much
   complaint:
     condition: 'content.length > 10'  # Too broad!
   ```

3. **Don't Forget Initial Intent**
   ```yaml
   # Bad: No conversation starter
   flows:
     main:
       states:
         start:
           intents:
             - someIntent  # Not marked as initial!
   ```

4. **Don't Skip Fallback**
   ```yaml
   # Bad: No fallback handler
   states:
     myState:
       intents:
         - intent1
         - intent2
       # Missing: fallback transition
   ```

## Debugging Intent Issues

### Issue: Intent Not Triggering

**Check:**
1. Priority conflicts (lower intents evaluated first)
2. Condition syntax (must return boolean)
3. Intent exists in state's `intents` list
4. Float condition not blocking
5. Previous state has transition to this state

**Debug Method:**
```javascript
// Add to method to log intent evaluation
function debugIntent(msg, ctx, dat, opts, cfg, result) {
  console.log('Content:', msg.content);
  console.log('Payload:', msg.payload);
  console.log('Metadata:', msg.metadata);
  console.log('Context:', ctx);

  // Test condition manually
  var testCondition = msg.content.toLowerCase() == "test";
  console.log('Condition result:', testCondition);

  return { command: 'continue' };
}
```

### Issue: Wrong Intent Triggered

**Cause:** Priority ordering, overlapping conditions

**Fix:**
```yaml
# Before: Overlapping conditions
intents:
  general:
    priority: 10
    condition: 'content.indexOf("help") >= 0'
  specific:
    priority: 12  # Lower priority, never reached!
    condition: 'content == "help billing"'

# After: Correct priority
intents:
  specific:
    priority: 10  # Higher priority
    condition: 'content == "help billing"'
  general:
    priority: 12  # Lower priority
    condition: 'content.indexOf("help") >= 0'
```

### Issue: Fallback Always Triggered

**Cause:** No matching intent conditions, fallback catches all

**Fix:**
```yaml
# Check all intent conditions return boolean
intents:
  myIntent:
    # Bad: Returns string, not boolean
    # condition: 'content.toLowerCase()'

    # Good: Returns boolean
    condition: 'content.toLowerCase() == "yes"'
```

## Intent Condition Syntax

### String Comparison
```yaml
condition: 'content == "exact match"'
condition: 'content.toLowerCase() == "case insensitive"'
condition: 'content.indexOf("contains") >= 0'
```

### Regex Matching
```yaml
condition: '/^pattern$/.test(content)'
condition: '/[0-9]{10}/.test(content)'
```

### Logical Operators
```yaml
condition: 'content == "hi" || content == "hello"'
condition: 'content.length > 5 && content.length < 20'
condition: '!(content.indexOf("spam") >= 0)'
```

### Context Checks
```yaml
condition: 'context.authenticated == true'
condition: 'context.step == 2'
condition: 'typeof context.userId != "undefined"'
```

### Payload Checks
```yaml
condition: 'payload.action == "submit"'
condition: 'payload.type == "quickReply" && payload.value == "yes"'
```

### Combined Conditions
```yaml
condition: |
  (metadata.channelType == "whatsapp" && content == "1") ||
  (metadata.channelType == "qiscus" && payload.menuId == "option1")
```

## Intent Template

Use this template for new intents:

```yaml
intents:
  intentName:
    priority: 10                           # 1-99, lower = higher priority
    type: text                             # text, command, data, method
    condition: 'content.toLowerCase() == "trigger"'
    initial: false                         # true if conversation starter
    fallback: false                        # true if catch-all handler
    attributes:
      # Optional: Map data from intent
      data:
        fieldName: $(payload.field)
      context:
        contextField: value
    # Only for method intents:
    # method: methodName
```

## Examples from Real Bot

### From bot-ftth (greetings.yml)

```yaml
intents:
  greet:
    priority: 5
    type: text
    condition: 'content.toLowerCase() == "hi" || content.toLowerCase() == "halo"'
    initial: true

  scheduleRunPart1:
    priority: 1
    type: command
    condition: 'content == "scheduleRunPart1"'

  backToMenu:
    priority: 3
    type: data
    condition: 'payload.postback == "backToMenu"'

  selectComplaintType:
    priority: 7
    type: data
    condition: 'payload.action == "selectComplaint"'
    attributes:
      data:
        complaintType: $(payload.type)
        complaintCode: $(payload.code)
```

## Summary

When designing intents:
1. Start with clear priority strategy (system → data → text → fallback)
2. Use specific conditions before broad ones
3. Always provide initial and fallback intents
4. Test conditions return boolean values
5. Normalize multi-channel input in attributes
6. Use method intents for complex classification
7. Map payload data to context/data scopes early
8. Debug with console logs in methods
9. Keep conditions simple and readable
10. Document intent purpose and triggers

Remember: Intents are the gateway to your flows - design them carefully for reliable conversation routing.
