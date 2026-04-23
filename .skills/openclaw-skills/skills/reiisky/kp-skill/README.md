# Kata Platform Claude Code Skills

A comprehensive Claude Code skills repository for developing chatbots on the Kata.ai platform.

## What is This?

This repository provides specialized Claude Code skills and comprehensive documentation for building, maintaining, and debugging YAML-based conversational AI bots on the Kata.ai platform. These skills enable Claude to understand Kata Platform's architecture and assist with bot development.

## Directory Structure

```
kp-claude-skills/
├── README.md                       # This file
├── KATA_PLATFORM_GUIDE.md          # Complete technical reference
├── skills/
│   ├── kata-flow-builder.md        # Flow design & transitions
│   ├── kata-method-writer.md       # ES5 JavaScript methods
│   ├── kata-intent-designer.md     # Intent & NLU design
│   ├── kata-action-builder.md      # Action definitions
│   ├── kata-scheduler-manager.md   # Scheduler management
│   ├── kata-api-integrator.md      # API integration
│   └── kata-debugger.md            # Debugging & troubleshooting
└── examples/
    ├── basic-flow.yml              # Example flow structure
    ├── method-patterns.js          # ES5 method examples
    └── common-patterns.yml         # Reusable patterns

```

## Installation

### For Claude Desktop App

1. Copy this entire directory to your Claude Code skills location:
   ```bash
   # On Windows
   cp -r kp-claude-skills "$HOME/AppData/Roaming/Claude/skills/"

   # On macOS
   cp -r kp-claude-skills "$HOME/Library/Application Support/Claude/skills/"

   # On Linux
   cp -r kp-claude-skills "$HOME/.config/Claude/skills/"
   ```

2. Restart Claude Desktop

3. Skills will be available automatically when working in Kata bot projects

### For Claude Code CLI

1. Create a `.claudeconfig` file in your Kata bot project root:
   ```json
   {
     "skillDirectories": [
       "/path/to/kp-claude-skills/skills"
     ]
   }
   ```

2. Skills will activate when Claude detects Kata YAML files

## Quick Start

### Working with Flows

```bash
# Claude will auto-detect Kata projects and offer assistance
claude "Create a new payment flow with OVO, GoPay, and DANA options"
claude "Add error handling to the createcase.yml flow"
claude "Fix the transition loop in subscriber.yml"
```

### Writing Methods

```bash
claude "Write an ES5 method to validate Indonesian phone numbers"
claude "Create a method to format currency in Rupiah"
claude "Debug the getBilling method - it's returning null"
```

### Managing Schedulers

```bash
claude "Add a 3-minute reminder scheduler to the payment flow"
claude "Check for orphaned schedulers that aren't cleaned up"
```

## Key Concepts (TL;DR)

### Kata Platform Basics

- **YAML-based**: Everything is defined in YAML files
- **State Machine**: Flows use intents → states → actions → transitions
- **ES5 Only**: JavaScript methods must be ECMAScript 5 (no arrow functions, let/const, etc.)
- **Modular**: Flows, methods, NLUs are split into separate files via `$include()`

### Common File Types

| File | Purpose | Example |
|------|---------|---------|
| `bot.yml` | Main config, includes all flows/methods | Entry point |
| `flows/*.yml` | Flow definitions (states, transitions) | `payment.yml` |
| `method/*.js` | Custom business logic (ES5) | `function.js` |
| `nlus.yml` | Intent classifiers (NLU definitions) | `nlus.yml` |

### Flow Execution Order

```
User Input
  ↓
Intent Classification (NLU)
  ↓
State Evaluation (check conditions)
  ↓
Enter Method (if defined)
  ↓
Execute Actions (API calls, text, etc.)
  ↓
Data Mapping (transform context/data)
  ↓
Transition to Next State
```

## Skills Overview

### 🚀 triva-add-kbr
**Use when:** Adding a new Keyword-Based Routing (KBR) shortcut to initiate a conversation with a specific product or campaign flow.

**Capabilities:**
- Define shortcut triggers in NLU
- Wire shortcut routing logic in greeting flows
- Implement floating shortcuts for active conversations
- Ensure all dependencies (NLU, Intent, Destination State) are defined first

### 🎯 kata-flow-builder
**Use when:** Creating or modifying conversation flows, states, and transitions

**Capabilities:**
- Design state machines with proper intent routing
- Create fallback and error handling paths
- Implement float conditions for global interrupts
- Validate transition logic

### 🔧 kata-method-writer
**Use when:** Writing custom JavaScript business logic

**Capabilities:**
- Write ES5-compliant methods (critical!)
- Access Kata method parameters: `msg, ctx, dat, opts, cfg, result`
- Return proper command/payload structures
- Handle API response parsing

### 🧠 kata-intent-designer
**Use when:** Defining how user input is recognized

**Capabilities:**
- Create keyword/regex/NLU classifiers
- Set intent priorities and conditions
- Design data payload structures
- Handle multi-channel inputs

### 📤 kata-action-builder
**Use when:** Defining bot outputs and API calls

**Capabilities:**
- Create text/template/API/method actions
- Build WhatsApp interactive messages
- Define conditional action execution
- Structure API request bodies

### ⏰ kata-scheduler-manager
**Use when:** Managing scheduled messages and reminders

**Capabilities:**
- Create time-based message schedulers
- Ensure proper cleanup (scheduleOff actions)
- Debug scheduler issues
- Prevent orphaned schedulers

### 🔌 kata-api-integrator
**Use when:** Integrating external APIs

**Capabilities:**
- Structure API action definitions
- Parse and map API responses
- Handle authentication/headers
- Implement error handling

### 🐛 kata-debugger
**Use when:** Troubleshooting bot issues

**Capabilities:**
- Trace intent → state → action flow
- Identify transition loops
- Find missing scheduler cleanup
- Debug context/data mapping

## Usage Examples

### Example 1: Create a New Flow

```bash
# Claude will use kata-flow-builder skill
claude "Create a billing inquiry flow with these states:
- Start: Ask for customer ID
- Validate: Check if valid customer
- Display: Show billing info
- Options: Payment, Download, or Main Menu"
```

### Example 2: Write a Validation Method

```bash
# Claude will use kata-method-writer skill
claude "Write an ES5 method to validate Indonesian mobile numbers
(must start with 08 or 628, length 10-13 digits)"
```

### Example 3: Debug Scheduler Issue

```bash
# Claude will use kata-scheduler-manager skill
claude "The payment flow is showing 'bye' message after 5 minutes
even though user is still active. Check schedulers."
```

## Best Practices

### ✅ DO

- **Always read before editing** - Use Read tool first to understand existing code
- **Maintain ES5 compatibility** - No `let`, `const`, arrow functions, or template literals
- **Clean up schedulers** - Every `scheduleRun*` needs a corresponding `scheduleOff*`
- **Use explicit conditions** - Write clear boolean expressions in transitions
- **Test float conditions** - Ensure global states don't create unintended loops
- **Add proper end states** - Mark terminal states with `end: true`

### ❌ DON'T

- **Don't use ES6+ features** - Methods will fail silently
- **Don't forget fallback transitions** - Always provide a default path
- **Don't create circular flows** - Without proper exit conditions
- **Don't skip scheduler cleanup** - Causes orphaned timers
- **Don't hardcode values** - Use config variables when possible
- **Don't create globals** - All state in context/data objects

## ES5 Quick Reference

### ❌ ES6+ (NOT ALLOWED)
```javascript
// Arrow functions
const add = (a, b) => a + b;

// Let/const
let name = 'test';
const API_URL = 'https://...';

// Template literals
var msg = `Hello ${name}`;

// Destructuring
const {id, name} = data;

// Spread operator
const merged = {...obj1, ...obj2};
```

### ✅ ES5 (REQUIRED)
```javascript
// Regular functions
function add(a, b) {
  return a + b;
}

// Var only
var name = 'test';
var API_URL = 'https://...';

// String concatenation
var msg = 'Hello ' + name;

// Manual property access
var id = data.id;
var name = data.name;

// Manual object merge
var merged = {};
for (var k in obj1) merged[k] = obj1[k];
for (var k in obj2) merged[k] = obj2[k];
```

## Troubleshooting

### Issue: Methods not executing

**Cause:** ES6+ syntax in method code
**Solution:** Convert all code to ES5 (see reference above)

### Issue: Transition not firing

**Cause:** Condition evaluation order or missing intent
**Solution:** Check intent priority, condition syntax, and transition order

### Issue: Scheduler keeps firing

**Cause:** Missing `scheduleOff*` action
**Solution:** Add cleanup action to bye/end states

### Issue: Fallback intent triggered unexpectedly

**Cause:** Intent priority conflict or missing intent definition
**Solution:** Check intent priorities and add missing intents

## Additional Resources

- **Kata Platform Docs**: [kata.ai/docs](https://kata.ai/docs) (internal only)
- **KATA_PLATFORM_GUIDE.md**: Complete technical reference (this repo)
- **example/** folder: Working examples and patterns

## Contributing

This is an internal tool. To improve:

1. Add new skills to `skills/` directory
2. Update examples with real patterns from production bots
3. Document common pitfalls and solutions
4. Keep ES5 reference updated

## Version

- **Version**: 1.0.0
- **Last Updated**: January 2026
- **Kata Platform Schema**: kata.ai/schema/kata-ml/1.0
- **Tested With**: Indosat HiFi Assistant (bot-ftth)

## License

Internal use only - Kata.ai engineering team
