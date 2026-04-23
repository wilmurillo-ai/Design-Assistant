# Kata Method Writer Skill

## Skill Metadata

```yaml
name: kata-method-writer
version: 1.0.0
description: Write ES5-compliant JavaScript methods for Kata Platform
author: Kata.ai Engineering
platforms: [kata.ai]
```

## When to Use This Skill

Use this skill when the user needs to:

- **Write custom business logic** - Data validation, calculations, transformations
- **Parse API responses** - Extract and process external data
- **Validate user input** - Phone numbers, emails, IDs, custom formats
- **Transform data** - Format currency, dates, strings
- **Implement complex conditions** - Logic too complex for YAML expressions
- **Debug existing methods** - Fix errors or improve performance

## ⚠️ CRITICAL CONSTRAINT: ES5 ONLY

**Kata Platform JavaScript engine supports ONLY ECMAScript 5.**

### ❌ NOT ALLOWED (ES6+)

```javascript
// Arrow functions
const add = (a, b) => a + b;

// Let/const
let name = 'John';
const PI = 3.14;

// Template literals
const msg = `Hello ${name}`;

// Destructuring
const {id, name} = user;

// Spread operator
const merged = {...obj1, ...obj2};

// For...of loops
for (const item of items) {}

// Default parameters
function greet(name = 'Guest') {}

// Class syntax
class User {
    constructor(name) {}
}

// Object shorthand
const obj = {name, age};

// Array methods (some)
array.find(x => x > 5);
array.findIndex(x => x > 5);
```

### ✅ REQUIRED (ES5)

```javascript
// Regular functions
function add(a, b) {
    return a + b;
}

// Var only
var name = 'John';
var PI = 3.14;

// String concatenation
var msg = 'Hello ' + name;

// Manual property access
var id = user.id;
var name = user.name;

// Manual object merge
var merged = {};
for (var key in obj1) {
    if (obj1.hasOwnProperty(key)) {
        merged[key] = obj1[key];
    }
}

// For loops
for (var i = 0; i < items.length; i++) {
    var item = items[i];
}

// Default parameters (manual)
function greet(name) {
    name = name || 'Guest';
}

// Constructor functions
function User(name) {
    this.name = name;
}

// Explicit object properties
var obj = {
    name: name,
    age: age
};

// Polyfills or loops
function findItem(array, predicate) {
    for (var i = 0; i < array.length; i++) {
        if (predicate(array[i])) {
            return array[i];
        }
    }
}
```

## Core Capabilities

### 1. Data Validation

Write validators for:
- Phone numbers (Indonesian: 08xxx or 628xxx)
- Email addresses
- Customer IDs
- OTP codes
- Custom formats

### 2. API Response Parsing

Extract data from:
- Nested JSON responses
- Array results
- Error responses
- Null/undefined handling

### 3. Data Transformation

Transform data for:
- Currency formatting (Rupiah)
- Date formatting (Indonesian/English)
- String manipulation
- Number calculations

### 4. Business Logic

Implement:
- Eligibility checks
- Calculation formulas
- Conditional routing
- State management

## Technical Context

### Method Signature

**Every Kata method must use this signature:**

```javascript
methodName(msg, ctx, dat, opts, cfg, result)
```

**Parameters:**

| Param | Type | Description | Access |
|-------|------|-------------|--------|
| `msg` | Object | Current message | Read |
| `ctx` | Object | Context (session-level data) | Read/Write |
| `dat` | Object | Data (flow-level data) | Read |
| `opts` | Object | Method options from YAML | Read |
| `cfg` | Object | Bot config from bot.yml | Read |
| `result` | Object | Previous API/method result | Read |

### Return Types

#### 1. Modified Context (Most Common)

```javascript
function myMethod(msg, ctx, dat, opts, cfg, result) {
    // Modify context
    ctx.data.processedValue = 'some value';
    ctx.context.sessionData = 'session value';

    // MUST return context
    return ctx;
}
```

#### 2. Command/Payload

```javascript
function myMethod(msg, ctx, dat, opts, cfg, result) {
    // Return command to trigger intent
    return {
        type: 'command',
        content: 'commandName',
        payload: {
            key: 'value'
        }
    };
}
```

### Accessing Data

```javascript
function example(msg, ctx, dat, opts, cfg, result) {
    // Read from context
    var userId = ctx.context.userId;
    var sessionId = ctx.context.$sessionId;

    // Read from data
    var firstName = ctx.data.firstName;
    var amount = ctx.data.amount;

    // Read from message
    var content = msg.content;
    var type = msg.type;

    // Read from config
    var apiUrl = cfg.apiUrl;
    var apiKey = cfg.apiKey;

    // Read from previous result (API response)
    var apiData = result.data;
    var apiStatus = result.status;

    // Write to context
    ctx.data.newField = 'value';
    ctx.context.sessionField = 'value';

    return ctx;
}
```

## Usage Patterns

### Pattern 1: Simple Validation

**User Request:** "Write a method to validate Indonesian phone numbers"

**Approach:**

```javascript
function validatePhone(msg, ctx, dat, opts, cfg, result) {
    var phone = ctx.data.phoneNumber || '';

    // Remove spaces and dashes
    phone = phone.replace(/[\s-]/g, '');

    // Indonesian phone pattern:
    // - Starts with 08 (mobile) or 628 (international)
    // - Total length 10-13 digits
    var pattern = /^(08|628)[0-9]{8,11}$/;

    var isValid = pattern.test(phone);

    // Store result
    ctx.data.isValidPhone = isValid;

    // Store cleaned phone
    if (isValid) {
        ctx.data.cleanedPhone = phone;
    }

    return ctx;
}
```

### Pattern 2: API Response Parsing

**User Request:** "Parse billing API response and extract invoice data"

**Approach:**

```javascript
function parseBillingResponse(msg, ctx, dat, opts, cfg, result) {
    var status = 'failed';
    var invoiceNo = '';
    var amount = 0;
    var dueDate = '';

    try {
        // Validate response exists
        if (!result || !result.data) {
            ctx.data.parseError = 'No response data';
            ctx.data.parseStatus = 'failed';
            return ctx;
        }

        // Check success code
        if (result.result === 1) {
            // Extract nested data
            var billingData = result.data.billing;

            if (billingData) {
                // Handle both array and single object
                if (Array.isArray(billingData)) {
                    if (billingData.length > 0) {
                        invoiceNo = billingData[0].invoiceNumber;
                        amount = parseFloat(billingData[0].amount) || 0;
                        dueDate = billingData[0].dueDate;
                    }
                } else {
                    invoiceNo = billingData.invoiceNumber;
                    amount = parseFloat(billingData.amount) || 0;
                    dueDate = billingData.dueDate;
                }

                status = 'success';
            }
        }
    } catch (e) {
        ctx.data.parseError = e.message;
        status = 'failed';
    }

    // Store extracted data
    ctx.data.invoiceNumber = invoiceNo;
    ctx.data.billingAmount = amount;
    ctx.data.dueDate = dueDate;
    ctx.data.parseStatus = status;

    return ctx;
}
```

### Pattern 3: Data Transformation

**User Request:** "Format amount as Rupiah currency"

**Approach:**

```javascript
function formatRupiah(msg, ctx, dat, opts, cfg, result) {
    var amount = parseFloat(ctx.data.amount) || 0;

    // Round to integer
    var rounded = Math.round(amount);

    // Convert to string
    var str = String(rounded);

    // Add thousand separators (dots)
    var formatted = '';
    var count = 0;

    // Iterate from right to left
    for (var i = str.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) {
            formatted = '.' + formatted;
        }
        formatted = str[i] + formatted;
        count++;
    }

    // Add Rp prefix
    formatted = 'Rp ' + formatted;

    ctx.data.formattedAmount = formatted;

    return ctx;
}
```

### Pattern 4: Date Formatting

**User Request:** "Format date in Indonesian (DD Nama_Bulan YYYY)"

**Approach:**

```javascript
function formatDateIndonesian(msg, ctx, dat, opts, cfg, result) {
    var dateString = ctx.data.dateISO || '';

    // Parse date: "2026-01-29"
    var parts = dateString.split('-');

    if (parts.length !== 3) {
        ctx.data.formattedDate = dateString; // Return as-is
        return ctx;
    }

    var year = parts[0];
    var month = parseInt(parts[1], 10);
    var day = parseInt(parts[2], 10);

    // Indonesian month names
    var monthNames = [
        'Januari', 'Februari', 'Maret', 'April',
        'Mei', 'Juni', 'Juli', 'Agustus',
        'September', 'Oktober', 'November', 'Desember'
    ];

    var monthName = monthNames[month - 1] || '';

    // Format: "29 Januari 2026"
    var formatted = day + ' ' + monthName + ' ' + year;

    ctx.data.formattedDate = formatted;

    return ctx;
}
```

### Pattern 5: Conditional Logic with Return

**User Request:** "Check if user is eligible for discount (age >= 18, balance >= 100000)"

**Approach:**

```javascript
function checkDiscountEligibility(msg, ctx, dat, opts, cfg, result) {
    var age = parseInt(ctx.data.age) || 0;
    var balance = parseFloat(ctx.data.balance) || 0;

    var isEligible = age >= 18 && balance >= 100000;

    var reason = '';
    if (!isEligible) {
        if (age < 18) {
            reason = 'Age below 18';
        } else if (balance < 100000) {
            reason = 'Insufficient balance';
        }
    }

    // Return command to trigger different intents
    return {
        type: 'command',
        content: isEligible ? 'eligible' : 'notEligible',
        payload: {
            age: age,
            balance: balance,
            eligible: isEligible,
            reason: reason
        }
    };
}
```

### Pattern 6: Array Processing

**User Request:** "Calculate total from array of items"

**Approach:**

```javascript
function calculateTotal(msg, ctx, dat, opts, cfg, result) {
    var items = ctx.data.cartItems || [];
    var total = 0;
    var itemCount = 0;

    // ES5: Use for loop (not for...of)
    for (var i = 0; i < items.length; i++) {
        var item = items[i];

        if (item && item.price) {
            var price = parseFloat(item.price) || 0;
            var quantity = parseInt(item.quantity) || 1;

            total += price * quantity;
            itemCount += quantity;
        }
    }

    // Apply tax (10%)
    var tax = total * 0.1;
    var grandTotal = total + tax;

    ctx.data.subtotal = total;
    ctx.data.tax = tax;
    ctx.data.grandTotal = grandTotal;
    ctx.data.totalItems = itemCount;

    return ctx;
}
```

### Pattern 7: String Manipulation

**User Request:** "Extract first name from full name"

**Approach:**

```javascript
function extractFirstName(msg, ctx, dat, opts, cfg, result) {
    var fullName = ctx.data.fullName || '';

    // Trim whitespace
    fullName = fullName.replace(/^\s+|\s+$/g, '');

    var firstName = fullName;

    // Split by space
    var parts = fullName.split(' ');

    if (parts.length > 0) {
        firstName = parts[0];
    }

    // Capitalize first letter
    if (firstName.length > 0) {
        firstName = firstName.charAt(0).toUpperCase() +
                    firstName.slice(1).toLowerCase();
    }

    ctx.data.firstName = firstName;

    return ctx;
}
```

### Pattern 8: Null Safety

**User Request:** "Safely access nested API response properties"

**Approach:**

```javascript
function safeExtractUserData(msg, ctx, dat, opts, cfg, result) {
    // Default values
    var userId = '';
    var userName = 'Unknown';
    var userEmail = '';
    var userPhone = '';

    try {
        // Check each level before accessing
        if (result) {
            if (result.data) {
                if (result.data.user) {
                    var user = result.data.user;

                    if (user.id) {
                        userId = String(user.id);
                    }

                    if (user.name) {
                        userName = user.name;
                    }

                    if (user.contact) {
                        if (user.contact.email) {
                            userEmail = user.contact.email;
                        }
                        if (user.contact.phone) {
                            userPhone = user.contact.phone;
                        }
                    }
                }
            }
        }
    } catch (e) {
        // Log error but continue
        ctx.data.extractError = e.message;
    }

    // Store extracted values
    ctx.data.userId = userId;
    ctx.data.userName = userName;
    ctx.data.userEmail = userEmail;
    ctx.data.userPhone = userPhone;

    return ctx;
}
```

## Common ES5 Patterns

### Safe Property Access

```javascript
// ES6+ (NOT ALLOWED)
const value = obj?.prop?.nested;

// ES5 (REQUIRED)
var value = obj && obj.prop && obj.prop.nested;
```

### Array Iteration

```javascript
// ES6+ (NOT ALLOWED)
arr.forEach(item => console.log(item));
arr.map(x => x * 2);
arr.filter(x => x > 5);

// ES5 (REQUIRED)
for (var i = 0; i < arr.length; i++) {
    var item = arr[i];
    // Process item
}

// Or use available ES5 methods
var doubled = arr.map(function(x) {
    return x * 2;
});

var filtered = arr.filter(function(x) {
    return x > 5;
});
```

### Object Creation

```javascript
// ES6+ (NOT ALLOWED)
const obj = {name, age};

// ES5 (REQUIRED)
var obj = {
    name: name,
    age: age
};
```

### Default Parameters

```javascript
// ES6+ (NOT ALLOWED)
function greet(name = 'Guest') {}

// ES5 (REQUIRED)
function greet(name) {
    name = name || 'Guest';
}
```

### String Building

```javascript
// ES6+ (NOT ALLOWED)
const msg = `Hello ${name}, you have ${count} items`;

// ES5 (REQUIRED)
var msg = 'Hello ' + name + ', you have ' + count + ' items';
```

### Object Merging

```javascript
// ES6+ (NOT ALLOWED)
const merged = {...obj1, ...obj2};

// ES5 (REQUIRED)
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
```

## Best Practices

### DO ✅

1. **Always validate input**
   ```javascript
   function process(msg, ctx, dat, opts, cfg, result) {
       var input = ctx.data.input || '';

       if (input.length === 0) {
           ctx.data.error = 'Input required';
           return ctx;
       }

       // Process...
   }
   ```

2. **Use try-catch for error handling**
   ```javascript
   function parseJSON(msg, ctx, dat, opts, cfg, result) {
       try {
           var data = JSON.parse(result.body);
           ctx.data.parsedData = data;
           ctx.data.parseSuccess = 'true';
       } catch (e) {
           ctx.data.parseSuccess = 'false';
           ctx.data.parseError = e.message;
       }

       return ctx;
   }
   ```

3. **Provide default values**
   ```javascript
   function calculate(msg, ctx, dat, opts, cfg, result) {
       var amount = parseFloat(ctx.data.amount) || 0;
       var quantity = parseInt(ctx.data.quantity) || 1;
       var discount = parseFloat(ctx.data.discount) || 0;

       // Calculate with safe defaults
   }
   ```

4. **Return consistent types**
   ```javascript
   function validate(msg, ctx, dat, opts, cfg, result) {
       // Always return ctx for consistency
       ctx.data.isValid = someCondition;
       return ctx;
   }
   ```

5. **Keep functions focused**
   ```javascript
   // Good - Single responsibility
   function validateEmail(msg, ctx, dat, opts, cfg, result) {
       var email = ctx.data.email || '';
       var pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
       ctx.data.isValidEmail = pattern.test(email);
       return ctx;
   }

   // Bad - Too many responsibilities
   function validateAndSendEmail(msg, ctx, dat, opts, cfg, result) {
       // Validate
       // Format
       // Send API request
       // Parse response
       // Update multiple fields
       // Too complex!
   }
   ```

### DON'T ❌

1. **Use ES6+ syntax** - Will fail silently
   ```javascript
   // BAD
   const validate = (phone) => /^08/.test(phone);

   // GOOD
   function validate(phone) {
       return /^08/.test(phone);
   }
   ```

2. **Forget to return** - Method will have no effect
   ```javascript
   // BAD
   function update(msg, ctx, dat, opts, cfg, result) {
       ctx.data.value = 'new';
       // Missing return!
   }

   // GOOD
   function update(msg, ctx, dat, opts, cfg, result) {
       ctx.data.value = 'new';
       return ctx;  // Must return
   }
   ```

3. **Modify parameters directly** - Can cause issues
   ```javascript
   // BAD
   function process(msg, ctx, dat, opts, cfg, result) {
       msg.content = 'modified';  // Don't modify msg
       return ctx;
   }

   // GOOD
   function process(msg, ctx, dat, opts, cfg, result) {
       var content = msg.content;
       // Work with copy
       ctx.data.processedContent = content;
       return ctx;
   }
   ```

4. **Assume data exists** - Always check
   ```javascript
   // BAD
   var name = result.data.user.name;  // May crash

   // GOOD
   var name = 'Unknown';
   if (result && result.data && result.data.user) {
       name = result.data.user.name || 'Unknown';
   }
   ```

## Debugging Methods

### Issue: Method Not Working

**Symptoms:** No effect, data not updated

**Debug Approach:**

```javascript
function debugMethod(msg, ctx, dat, opts, cfg, result) {
    // Add debug flag at start
    ctx.data.debugMethodStarted = 'true';

    try {
        // Your logic here
        ctx.data.processedValue = 'result';
        ctx.data.debugSuccess = 'true';

    } catch (e) {
        // Catch errors
        ctx.data.debugError = e.message;
        ctx.data.debugSuccess = 'false';
    }

    // Verify return
    ctx.data.debugReturned = 'true';
    return ctx;
}
```

**Common Causes:**
1. ES6 syntax (check for arrow functions, let/const, template literals)
2. Missing return statement
3. Syntax error (check all brackets/parentheses)
4. Wrong parameter access

### Issue: Undefined Value

**Symptoms:** ctx.data.field is undefined

**Debug:**

```javascript
function debug(msg, ctx, dat, opts, cfg, result) {
    // Log what's available
    ctx.data.debugMsg = msg ? 'has msg' : 'no msg';
    ctx.data.debugResult = result ? 'has result' : 'no result';

    // Check specific field
    if (result) {
        ctx.data.debugResultType = typeof result;
        ctx.data.debugResultKeys = Object.keys(result).join(',');
    }

    return ctx;
}
```

## Integration with Other Skills

### With kata-flow-builder

Methods are used in states:

```yaml
states:
    validateInput:
        enter: validatePhoneMethod  # Use this skill
        action:
            - name: showResult
        transitions:
            success:
                condition: "data.isValidPhone == 'true'"
            retry:
                condition: "data.isValidPhone == 'false'"
```

### With kata-api-integrator

Methods parse API responses:

```yaml
states:
    fetchData:
        action:
            - name: callAPI
            - name: parseAPIResponse  # Use this skill
        transitions:
            # ...
```

## Method Template

**Use this template for new methods:**

```javascript
function methodName(msg, ctx, dat, opts, cfg, result) {
    // 1. Declare variables with defaults
    var inputValue = ctx.data.inputField || '';
    var outputValue = '';

    // 2. Validate input
    if (!inputValue) {
        ctx.data.errorMsg = 'Input required';
        ctx.data.success = 'false';
        return ctx;
    }

    // 3. Process with error handling
    try {
        // Your logic here
        outputValue = inputValue.toUpperCase();

        ctx.data.outputField = outputValue;
        ctx.data.success = 'true';

    } catch (e) {
        ctx.data.errorMsg = e.message;
        ctx.data.success = 'false';
    }

    // 4. Always return context
    return ctx;
}
```

## Quick Reference

### ES5 Checklist

- [ ] No arrow functions (`=>`)
- [ ] No `let` or `const` (only `var`)
- [ ] No template literals (`` `${}` ``)
- [ ] No destructuring (`{a, b} = obj`)
- [ ] No spread operator (`...`)
- [ ] No `for...of` loops
- [ ] No default parameters
- [ ] No class syntax
- [ ] Use `var` for all variables
- [ ] Use `function` keyword
- [ ] Use string concatenation (`+`)
- [ ] Use `for` loops for iteration

### Method Signature

```javascript
function methodName(msg, ctx, dat, opts, cfg, result) {
    // Access data
    var value = ctx.data.field;

    // Modify data
    ctx.data.newField = 'value';

    // Return context
    return ctx;
}
```

### Common Validations

```javascript
// Email
/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

// Indonesian phone
/^(08|628)[0-9]{8,11}$/.test(phone)

// Numeric only
/^[0-9]+$/.test(str)

// 6-digit OTP
/^[0-9]{6}$/.test(otp)
```

---

**End of Kata Method Writer Skill**

*For complete ES5 reference and platform details, see KATA_PLATFORM_GUIDE.md*
