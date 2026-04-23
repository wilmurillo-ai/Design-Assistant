/**
 * Kata Platform ES5 Method Patterns
 *
 * This file contains common ES5 JavaScript patterns for Kata Platform methods.
 * All code MUST be ES5-compliant (no ES6+ features).
 *
 * Method Signature:
 * function methodName(msg, ctx, dat, opts, cfg, result) { ... }
 *
 * Parameters:
 * - msg: Current message object (content, payload, metadata)
 * - ctx: Context object (persistent across conversation)
 * - dat: Data object (scoped to current flow)
 * - opts: Options passed from action definition
 * - cfg: Bot config variables
 * - result: Previous action result (for post-API methods)
 *
 * Return Commands:
 * - updateContext: Update conversation context
 * - updateData: Update flow data
 * - transit: Transition to another state
 * - continue: Continue execution
 * - sendMessage: Send a message
 * - done: End execution
 */

// ============================================================================
// VALIDATION PATTERNS
// ============================================================================

/**
 * Validate Indonesian phone number
 * Accepts: 08xxxxxxxxx or 628xxxxxxxxx (10-13 digits total)
 */
function validatePhoneNumber(msg, ctx, dat, opts, cfg, result) {
  var phone = ctx.phoneNumber || '';
  var regex = /^(08|628)[0-9]{8,11}$/;
  var isValid = regex.test(phone);

  // Normalize to 628 format
  var normalized = phone;
  if (phone.indexOf('08') === 0) {
    normalized = '628' + phone.substring(2);
  }

  return {
    command: 'updateContext',
    payload: {
      phoneValid: isValid,
      phoneNormalized: normalized,
      phoneError: isValid ? null : 'Invalid phone number format'
    }
  };
}

/**
 * Validate email address
 */
function validateEmail(msg, ctx, dat, opts, cfg, result) {
  var email = msg.content || '';
  var regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  var isValid = regex.test(email);

  return {
    command: 'updateContext',
    payload: {
      email: email.toLowerCase(),
      emailValid: isValid,
      emailError: isValid ? null : 'Invalid email format'
    }
  };
}

/**
 * Validate string length
 */
function validateStringLength(msg, ctx, dat, opts, cfg, result) {
  var input = msg.content || '';
  var minLength = opts.minLength || 0;
  var maxLength = opts.maxLength || 1000;

  var isValid = input.length >= minLength && input.length <= maxLength;
  var errorMessage = null;

  if (input.length < minLength) {
    errorMessage = 'Input too short (minimum ' + minLength + ' characters)';
  } else if (input.length > maxLength) {
    errorMessage = 'Input too long (maximum ' + maxLength + ' characters)';
  }

  return {
    command: 'updateData',
    payload: {
      inputValid: isValid,
      inputError: errorMessage
    }
  };
}

/**
 * Validate number within range
 */
function validateNumberRange(msg, ctx, dat, opts, cfg, result) {
  var input = msg.content;
  var number = parseFloat(input);
  var min = opts.min || 0;
  var max = opts.max || Number.MAX_VALUE;

  var isNumber = !isNaN(number);
  var inRange = number >= min && number <= max;
  var isValid = isNumber && inRange;

  var errorMessage = null;
  if (!isNumber) {
    errorMessage = 'Please enter a valid number';
  } else if (!inRange) {
    errorMessage = 'Number must be between ' + min + ' and ' + max;
  }

  return {
    command: 'updateData',
    payload: {
      numberValue: number,
      numberValid: isValid,
      numberError: errorMessage
    }
  };
}

// ============================================================================
// DATA TRANSFORMATION PATTERNS
// ============================================================================

/**
 * Format currency to Indonesian Rupiah
 */
function formatCurrency(msg, ctx, dat, opts, cfg, result) {
  var amount = dat.amount || 0;

  // Add thousand separators
  var formatted = amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  return {
    command: 'updateData',
    payload: {
      formattedAmount: 'Rp ' + formatted,
      rawAmount: amount
    }
  };
}

/**
 * Format date to Indonesian format (DD/MM/YYYY)
 */
function formatDate(msg, ctx, dat, opts, cfg, result) {
  var dateString = dat.date || new Date().toISOString();
  var date = new Date(dateString);

  var day = date.getDate();
  var month = date.getMonth() + 1;
  var year = date.getFullYear();

  // Pad single digits
  var dayStr = day < 10 ? '0' + day : day.toString();
  var monthStr = month < 10 ? '0' + month : month.toString();

  var formatted = dayStr + '/' + monthStr + '/' + year;

  return {
    command: 'updateData',
    payload: {
      formattedDate: formatted,
      day: day,
      month: month,
      year: year
    }
  };
}

/**
 * Parse and normalize user input
 */
function normalizeInput(msg, ctx, dat, opts, cfg, result) {
  var input = msg.content || '';

  var normalized = input
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ');  // Replace multiple spaces with single space

  // Remove special characters (keep alphanumeric and spaces)
  var cleaned = normalized.replace(/[^a-z0-9\s]/g, '');

  return {
    command: 'updateData',
    payload: {
      originalInput: input,
      normalizedInput: normalized,
      cleanedInput: cleaned
    }
  };
}

/**
 * Extract numbers from string
 */
function extractNumbers(msg, ctx, dat, opts, cfg, result) {
  var input = msg.content || '';
  var matches = input.match(/\d+/g);
  var numbers = [];

  if (matches) {
    for (var i = 0; i < matches.length; i++) {
      numbers.push(parseInt(matches[i], 10));
    }
  }

  return {
    command: 'updateData',
    payload: {
      extractedNumbers: numbers,
      firstNumber: numbers.length > 0 ? numbers[0] : null,
      numberCount: numbers.length
    }
  };
}

// ============================================================================
// API RESPONSE PARSING PATTERNS
// ============================================================================

/**
 * Parse API success response
 */
function parseApiResponse(msg, ctx, dat, opts, cfg, result) {
  var statusCode = result.response.status;
  var body = result.response.body;

  var isSuccess = statusCode >= 200 && statusCode < 300;
  var isError = statusCode >= 400;

  var data = isSuccess ? body.data : null;
  var errorMessage = isError ? (body.message || 'Unknown error') : null;

  return {
    command: 'updateData',
    payload: {
      apiSuccess: isSuccess,
      apiError: isError,
      apiData: data,
      errorMessage: errorMessage,
      statusCode: statusCode
    }
  };
}

/**
 * Parse array response and format for display
 */
function parseArrayResponse(msg, ctx, dat, opts, cfg, result) {
  var items = result.response.body.items || [];
  var formatted = [];

  for (var i = 0; i < items.length; i++) {
    formatted.push({
      id: items[i].id,
      name: items[i].name,
      displayText: (i + 1) + '. ' + items[i].name
    });
  }

  return {
    command: 'updateData',
    payload: {
      items: formatted,
      totalItems: items.length,
      hasItems: items.length > 0
    }
  };
}

/**
 * Handle paginated API response
 */
function parsePaginatedResponse(msg, ctx, dat, opts, cfg, result) {
  var body = result.response.body;
  var currentPage = body.page || 1;
  var totalPages = body.total_pages || 1;
  var items = body.items || [];

  return {
    command: 'updateData',
    payload: {
      items: items,
      currentPage: currentPage,
      totalPages: totalPages,
      hasNextPage: currentPage < totalPages,
      hasPrevPage: currentPage > 1
    }
  };
}

// ============================================================================
// BUSINESS LOGIC PATTERNS
// ============================================================================

/**
 * Calculate discount based on business rules
 */
function calculateDiscount(msg, ctx, dat, opts, cfg, result) {
  var totalAmount = dat.totalAmount || 0;
  var customerType = ctx.customerType || 'regular';

  var discountPercent = 0;

  // Business rules
  if (customerType === 'premium') {
    discountPercent = 20;
  } else if (customerType === 'gold') {
    discountPercent = 15;
  } else if (totalAmount > 1000000) {
    discountPercent = 10;
  } else if (totalAmount > 500000) {
    discountPercent = 5;
  }

  var discountAmount = (totalAmount * discountPercent) / 100;
  var finalAmount = totalAmount - discountAmount;

  return {
    command: 'updateData',
    payload: {
      discountPercent: discountPercent,
      discountAmount: discountAmount,
      finalAmount: finalAmount,
      totalAmount: totalAmount
    }
  };
}

/**
 * Classify complaint by keywords
 */
function classifyComplaint(msg, ctx, dat, opts, cfg, result) {
  var content = msg.content.toLowerCase();

  var categories = {
    internet: ['internet', 'koneksi', 'wifi', 'slow', 'lemot', 'putus'],
    billing: ['tagihan', 'bayar', 'payment', 'invoice', 'harga'],
    technical: ['error', 'rusak', 'broken', 'not working', 'mati'],
    service: ['customer service', 'complaint', 'keluhan', 'bantuan']
  };

  var matchedCategory = 'unknown';
  var confidence = 0;

  for (var category in categories) {
    var keywords = categories[category];
    var matches = 0;

    for (var i = 0; i < keywords.length; i++) {
      if (content.indexOf(keywords[i]) >= 0) {
        matches++;
      }
    }

    if (matches > 0) {
      var categoryConfidence = matches / keywords.length;
      if (categoryConfidence > confidence) {
        confidence = categoryConfidence;
        matchedCategory = category;
      }
    }
  }

  return {
    command: 'updateContext',
    payload: {
      complaintCategory: matchedCategory,
      categoryConfidence: confidence,
      needsClassification: matchedCategory === 'unknown'
    }
  };
}

/**
 * Generate unique ticket number
 */
function generateTicketNumber(msg, ctx, dat, opts, cfg, result) {
  var prefix = opts.prefix || 'TKT';
  var timestamp = Date.now();
  var random = Math.floor(Math.random() * 1000);

  // Format: TKT-TIMESTAMP-RANDOM
  var ticketNumber = prefix + '-' + timestamp + '-' + random;

  return {
    command: 'updateData',
    payload: {
      ticketNumber: ticketNumber,
      generatedAt: timestamp
    }
  };
}

// ============================================================================
// CONDITIONAL ROUTING PATTERNS
// ============================================================================

/**
 * Route based on business hours
 */
function checkBusinessHours(msg, ctx, dat, opts, cfg, result) {
  var now = new Date();
  var hour = now.getHours();
  var day = now.getDay();  // 0 = Sunday, 6 = Saturday

  var isWeekend = day === 0 || day === 6;
  var isBusinessHours = hour >= 9 && hour < 17;  // 9 AM - 5 PM
  var isAvailable = !isWeekend && isBusinessHours;

  return {
    command: 'updateData',
    payload: {
      isBusinessHours: isBusinessHours,
      isWeekend: isWeekend,
      isAvailable: isAvailable,
      currentHour: hour
    }
  };
}

/**
 * Route based on user tier
 */
function checkUserTier(msg, ctx, dat, opts, cfg, result) {
  var accountType = ctx.accountType || 'free';
  var usageCount = ctx.usageCount || 0;

  var canProceed = false;
  var reason = null;

  if (accountType === 'premium') {
    canProceed = true;
  } else if (accountType === 'free' && usageCount < 5) {
    canProceed = true;
  } else {
    canProceed = false;
    reason = 'Free tier limit reached. Please upgrade to premium.';
  }

  return {
    command: 'updateContext',
    payload: {
      canProceed: canProceed,
      blockReason: reason,
      usageCount: usageCount + (canProceed ? 1 : 0)
    }
  };
}

// ============================================================================
// HELPER PATTERNS
// ============================================================================

/**
 * Merge objects (ES5 alternative to spread operator)
 */
function mergeObjects(msg, ctx, dat, opts, cfg, result) {
  var obj1 = dat.object1 || {};
  var obj2 = dat.object2 || {};

  var merged = {};

  // Copy properties from obj1
  for (var key in obj1) {
    if (obj1.hasOwnProperty(key)) {
      merged[key] = obj1[key];
    }
  }

  // Copy properties from obj2 (overwrites obj1)
  for (var key in obj2) {
    if (obj2.hasOwnProperty(key)) {
      merged[key] = obj2[key];
    }
  }

  return {
    command: 'updateData',
    payload: {
      mergedObject: merged
    }
  };
}

/**
 * Filter array by condition
 */
function filterArray(msg, ctx, dat, opts, cfg, result) {
  var items = dat.items || [];
  var minPrice = opts.minPrice || 0;
  var filtered = [];

  for (var i = 0; i < items.length; i++) {
    if (items[i].price >= minPrice) {
      filtered.push(items[i]);
    }
  }

  return {
    command: 'updateData',
    payload: {
      filteredItems: filtered,
      filteredCount: filtered.length
    }
  };
}

/**
 * Map array to new structure
 */
function mapArray(msg, ctx, dat, opts, cfg, result) {
  var items = result.response.body.items || [];
  var mapped = [];

  for (var i = 0; i < items.length; i++) {
    mapped.push({
      id: items[i].id,
      displayName: items[i].name.toUpperCase(),
      formattedPrice: 'Rp ' + items[i].price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
    });
  }

  return {
    command: 'updateData',
    payload: {
      mappedItems: mapped
    }
  };
}

/**
 * Deep clone object (ES5 method)
 */
function cloneObject(msg, ctx, dat, opts, cfg, result) {
  var original = dat.original || {};

  // Simple deep clone via JSON (works for plain objects)
  var cloned = JSON.parse(JSON.stringify(original));

  return {
    command: 'updateData',
    payload: {
      clonedObject: cloned
    }
  };
}

// ============================================================================
// DEBUGGING PATTERNS
// ============================================================================

/**
 * Debug logger - logs all method parameters
 */
function debugLogger(msg, ctx, dat, opts, cfg, result) {
  console.log('=== Debug Info ===');
  console.log('Message:', JSON.stringify(msg));
  console.log('Context:', JSON.stringify(ctx));
  console.log('Data:', JSON.stringify(dat));
  console.log('Options:', JSON.stringify(opts));
  console.log('Config:', JSON.stringify(cfg));
  console.log('Result:', JSON.stringify(result));
  console.log('==================');

  return { command: 'continue' };
}

/**
 * Trace execution flow
 */
function traceFlow(msg, ctx, dat, opts, cfg, result) {
  var stateName = opts.stateName || 'unknown';
  var timestamp = new Date().toISOString();

  console.log('[' + timestamp + '] State: ' + stateName + ', Intent: ' + msg.intent);

  return { command: 'continue' };
}

// ============================================================================
// NOTES
// ============================================================================

/*
ES5 CONSTRAINTS REMINDER:

❌ DON'T USE:
- let / const (use var)
- Arrow functions (use function)
- Template literals `${var}` (use string concatenation)
- Destructuring { a, b } = obj (use obj.a, obj.b)
- Spread operator ...obj (use loops)
- Default parameters (use || operator)
- Array.find() / Array.includes() (use loops)
- Object.assign() (use manual copy)
- Promise / async/await (not supported)
- Classes (use functions)

✅ DO USE:
- var for variables
- function declarations
- String concatenation with +
- Direct property access
- for loops for iteration
- || for default values
- hasOwnProperty() for object checks
- indexOf() for array/string search
- JSON.parse() / JSON.stringify()
- Regular expressions
*/
