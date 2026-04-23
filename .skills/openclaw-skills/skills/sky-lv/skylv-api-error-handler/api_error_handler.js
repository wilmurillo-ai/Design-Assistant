/**
 * api_error_handler.js — Comprehensive API Error Handling
 * 
 * Categorizes errors, suggests fixes, implements retry strategies.
 * Integrates with self-healing-agent ecosystem.
 * 
 * Usage: node api_error_handler.js <command> [args...]
 * Commands:
 *   analyze <error>        Analyze error and suggest fix
 *   retry <strategy>       Get retry strategy details
 *   log <error> [context]  Log an error for analysis
 *   stats                  Show error statistics
 *   categories             List error categories
 */

const fs = require('fs');
const LOG_FILE = '.api-errors.json';

// ── Error Categories ─────────────────────────────────────────────────────────
const CATEGORIES = {
  'rate-limit': {
    patterns: [/rate.?limit|429|too.?many|quota|limit.*exceeded/i],
    http: [429],
    severity: 'warning',
    retryable: true,
    fix: 'Implement exponential backoff. Wait for Retry-After header value.',
    example: 'await sleep(retryAfterMs * Math.pow(2, attempt))',
  },
  'timeout': {
    patterns: [/timeout|timed?.?out|etimedout|econnreset/i],
    http: [408, 504],
    severity: 'warning',
    retryable: true,
    fix: 'Increase timeout or implement request chunking.',
    example: 'timeoutMs: 30000 -> 60000',
  },
  'auth': {
    patterns: [/unauthorized|invalid.?key|api.?key|auth|401|forbidden|403/i],
    http: [401, 403],
    severity: 'critical',
    retryable: false,
    fix: 'Check API key validity, regenerate if compromised, verify scopes.',
    example: 'Verify: openclaw config get api.key',
  },
  'validation': {
    patterns: [/invalid|bad.?request|required|missing|validation|400/i],
    http: [400, 422],
    severity: 'error',
    retryable: false,
    fix: 'Review request payload. Check required fields, types, and constraints.',
    example: 'Validate payload before API call',
  },
  'server': {
    patterns: [/server.?error|internal.?error|500|502|503|504|upstream/i],
    http: [500, 502, 503, 504],
    severity: 'warning',
    retryable: true,
    fix: 'Server-side issue. Retry with exponential backoff. Check status page.',
    example: 'Check: status.anthropic.com or status.openai.com',
  },
  'network': {
    patterns: [/econnrefused|enotfound|network|dns|offline/i],
    http: [],
    severity: 'critical',
    retryable: true,
    fix: 'Check network connectivity. Verify DNS resolution. Check firewall rules.',
    example: 'ping api.openai.com',
  },
  'not-found': {
    patterns: [/not.?found|404|does.?not.?exist/i],
    http: [404],
    severity: 'error',
    retryable: false,
    fix: 'Verify resource ID/URL. Resource may have been deleted or moved.',
    example: 'GET /repos/{owner}/{repo} - verify both exist',
  },
  'conflict': {
    patterns: [/conflict|already.?exists|duplicate|409/i],
    http: [409],
    severity: 'warning',
    retryable: false,
    fix: 'Resource already exists. Use update (PUT/PATCH) instead of create (POST).',
    example: 'Use PUT instead of POST for existing resources',
  },
};

// ── Retry Strategies ─────────────────────────────────────────────────────────
const RETRY_STRATEGIES = {
  'exponential': {
    description: 'Double wait time after each failure',
    calculate: (attempt, baseMs = 1000) => baseMs * Math.pow(2, attempt),
    maxAttempts: 5,
    suitable: ['rate-limit', 'server', 'timeout'],
  },
  'linear': {
    description: 'Fixed wait time between retries',
    calculate: (attempt, baseMs = 1000) => baseMs,
    maxAttempts: 3,
    suitable: ['network'],
  },
  'fibonacci': {
    description: 'Fibonacci sequence for wait times',
    calculate: (attempt) => {
      const fib = [0, 1000, 1000, 2000, 3000, 5000, 8000];
      return fib[Math.min(attempt, fib.length - 1)];
    },
    maxAttempts: 6,
    suitable: ['rate-limit', 'server'],
  },
  'immediate': {
    description: 'Retry immediately (for idempotent operations)',
    calculate: () => 0,
    maxAttempts: 1,
    suitable: ['timeout'],
  },
};

// ── Error Storage ────────────────────────────────────────────────────────────
function loadErrors() {
  if (!fs.existsSync(LOG_FILE)) return [];
  try { return JSON.parse(fs.readFileSync(LOG_FILE, 'utf8')); }
  catch { return []; }
}

function saveErrors(errors) {
  fs.writeFileSync(LOG_FILE, JSON.stringify(errors.slice(-100), null, 2));
}

// ── Analysis ─────────────────────────────────────────────────────────────────
function categorizeError(errorText, httpStatus) {
  const text = String(errorText || '').toLowerCase();
  const status = parseInt(httpStatus) || 0;
  
  for (const [category, config] of Object.entries(CATEGORIES)) {
    if (config.http.includes(status)) return category;
    for (const pattern of config.patterns) {
      if (pattern.test(text)) return category;
    }
  }
  return 'unknown';
}

function analyzeError(errorText, httpStatus) {
  const category = categorizeError(errorText, httpStatus);
  const config = CATEGORIES[category] || {
    severity: 'unknown',
    retryable: false,
    fix: 'Manual investigation required.',
    example: '',
  };
  
  const strategies = Object.entries(RETRY_STRATEGIES)
    .filter(([_, s]) => s.suitable.includes(category))
    .map(([name, s]) => ({ name, description: s.description }));
  
  return {
    category,
    severity: config.severity,
    retryable: config.retryable,
    fix: config.fix,
    example: config.example,
    strategies,
  };
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdAnalyze(errorText, httpStatus) {
  if (!errorText) {
    console.error('Usage: api_error_handler.js analyze <error> [httpStatus]');
    process.exit(1);
  }
  
  const result = analyzeError(errorText, httpStatus);
  
  console.log(`\n## Error Analysis\n`);
  console.log(`Category: ${result.category.toUpperCase()}`);
  console.log(`Severity: ${result.severity.toUpperCase()}`);
  console.log(`Retryable: ${result.retryable ? 'YES' : 'NO'}`);
  console.log(`\nFix: ${result.fix}`);
  if (result.example) console.log(`Example: ${result.example}`);
  
  if (result.strategies.length > 0) {
    console.log(`\nRetry strategies:`);
    for (const s of result.strategies) {
      console.log(`  - ${s.name}: ${s.description}`);
    }
  }
  console.log();
}

function cmdRetry(strategy) {
  const s = RETRY_STRATEGIES[strategy];
  if (!s) {
    console.log(`\nAvailable strategies: ${Object.keys(RETRY_STRATEGIES).join(', ')}\n`);
    return;
  }
  
  console.log(`\n## Retry Strategy: ${strategy}\n`);
  console.log(`Description: ${s.description}`);
  console.log(`Max attempts: ${s.maxAttempts}`);
  console.log(`Suitable for: ${s.suitable.join(', ')}\n`);
  
  console.log(`Wait times (first 5 attempts):`);
  for (let i = 0; i < 5; i++) {
    const ms = s.calculate(i);
    console.log(`  Attempt ${i + 1}: ${ms}ms (${(ms / 1000).toFixed(1)}s)`);
  }
  console.log();
}

function cmdLog(errorText, context) {
  if (!errorText) {
    console.error('Usage: api_error_handler.js log <error> [context]');
    process.exit(1);
  }
  
  const errors = loadErrors();
  const entry = {
    timestamp: new Date().toISOString(),
    error: errorText,
    context: context || '',
    category: categorizeError(errorText),
  };
  errors.push(entry);
  saveErrors(errors);
  
  console.log(`\n✅ Error logged`);
  console.log(`   Category: ${entry.category}`);
  console.log(`   Total logged: ${errors.length}\n`);
}

function cmdStats() {
  const errors = loadErrors();
  if (errors.length === 0) {
    console.log('\nNo errors logged yet.\n');
    return;
  }
  
  const byCategory = {};
  for (const e of errors) {
    const cat = e.category || 'unknown';
    byCategory[cat] = (byCategory[cat] || 0) + 1;
  }
  
  console.log(`\n## Error Statistics\n`);
  console.log(`Total errors: ${errors.length}`);
  console.log(`\nBy category:`);
  for (const [cat, count] of Object.entries(byCategory).sort((a, b) => b[1] - a[1])) {
    const percent = (count / errors.length * 100).toFixed(1);
    console.log(`  ${cat}: ${count} (${percent}%)`);
  }
  
  const recent = errors.slice(-5);
  if (recent.length > 0) {
    console.log(`\nRecent errors:`);
    for (const e of recent) {
      const time = e.timestamp.slice(11, 19);
      console.log(`  [${time}] ${e.category}: ${e.error.slice(0, 50)}`);
    }
  }
  console.log();
}

function cmdCategories() {
  console.log(`\n## Error Categories\n`);
  console.log('Category      HTTP    Severity   Retryable');
  console.log('─────────────────────────────────────────────');
  for (const [cat, config] of Object.entries(CATEGORIES)) {
    const http = config.http.length > 0 ? config.http.join(',') : '-';
    console.log(`${cat.padEnd(14)} ${http.padEnd(7)} ${config.severity.padEnd(10)} ${config.retryable ? 'YES' : 'NO'}`);
  }
  console.log();
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  analyze: cmdAnalyze,
  retry: cmdRetry,
  log: cmdLog,
  stats: cmdStats,
  categories: cmdCategories,
};

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`api_error_handler.js — Comprehensive API Error Handling

Usage: node api_error_handler.js <command> [args...]

Commands:
  analyze <error> [http]  Analyze error and suggest fix
  retry <strategy>        Show retry strategy details
  log <error> [context]   Log an error for analysis
  stats                   Show error statistics
  categories              List error categories

Categories:
  rate-limit  - 429, quota exceeded
  timeout     - Connection timeouts
  auth        - 401, 403, invalid keys
  validation  - 400, 422, invalid input
  server      - 500, 502, 503, 504
  network     - DNS, connection failures
  not-found   - 404
  conflict    - 409, already exists

Retry Strategies:
  exponential - Double wait time (default)
  linear      - Fixed wait time
  fibonacci   - Fibonacci sequence
  immediate   - No delay

Examples:
  node api_error_handler.js analyze "rate limit exceeded" 429
  node api_error_handler.js retry exponential
  node api_error_handler.js log "Connection timeout" "api.openai.com"
  node api_error_handler.js stats
`);
  process.exit(0);
}

COMMANDS[cmd](...args);
