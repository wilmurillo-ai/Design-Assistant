/**
 * data_validator.js — Universal Data Validation Engine
 * 
 * Validates JSON, objects, arrays against schemas or rules.
 * Supports type checking, required fields, patterns, ranges.
 * 
 * Usage: node data_validator.js <command> [args...]
 * Commands:
 *   validate <file> [schema]  Validate file against schema
 *   check <json> <rules>       Check JSON against rules
 *   schema <file>             Infer schema from file
 *   rules                     List available rules
 */

const fs = require('fs');
const path = require('path');

// ── Built-in Validators ─────────────────────────────────────────────────────
const VALIDATORS = {
  required: (v) => v !== undefined && v !== null && v !== '',
  type: (v, expected) => {
    if (Array.isArray(v)) return expected === 'array';
    return typeof v === expected;
  },
  min: (v, n) => typeof v === 'number' && v >= n,
  max: (v, n) => typeof v === 'number' && v <= n,
  minLength: (v, n) => typeof v === 'string' && v.length >= n,
  maxLength: (v, n) => typeof v === 'string' && v.length <= n,
  pattern: (v, regex) => new RegExp(regex).test(String(v)),
  email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v)),
  url: (v) => /^https?:\/\/[^\s]+$/.test(String(v)),
  uuid: (v) => /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(String(v)),
  enum: (v, values) => values.includes(v),
  integer: (v) => Number.isInteger(v),
  positive: (v) => v > 0,
  nonnegative: (v) => v >= 0,
  date: (v) => !isNaN(Date.parse(v)),
  isoDate: (v) => /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?/.test(String(v)),
  json: (v) => { try { JSON.parse(v); return true; } catch { return false; } },
};

// ── Validation Engine ───────────────────────────────────────────────────────
function validateValue(value, rules) {
  const errors = [];
  for (const [rule, param] of Object.entries(rules)) {
    const validator = VALIDATORS[rule];
    if (!validator) continue;
    if (!validator(value, param)) {
      errors.push({ rule, expected: param, actual: value });
    }
  }
  return { valid: errors.length === 0, errors };
}

function validateObject(obj, schema) {
  const errors = [];
  for (const [field, rules] of Object.entries(schema)) {
    const value = obj[field];
    const result = validateValue(value, rules);
    if (!result.valid) {
      errors.push({ field, ...result.errors[0] });
    }
  }
  return { valid: errors.length === 0, errors };
}

function inferSchema(data) {
  if (Array.isArray(data)) {
    if (data.length === 0) return { type: 'array' };
    const itemSchema = inferSchema(data[0]);
    return { type: 'array', items: itemSchema };
  }
  if (typeof data === 'object' && data !== null) {
    const schema = { type: 'object', properties: {} };
    for (const [key, value] of Object.entries(data)) {
      if (typeof value === 'object' && value !== null) {
        schema.properties[key] = inferSchema(value);
      } else {
        schema.properties[key] = { type: typeof value };
      }
    }
    return schema;
  }
  return { type: typeof data };
}

// ── Commands ─────────────────────────────────────────────────────────────────
function cmdValidate(file, schemaFile) {
  if (!file) { console.error('Usage: data_validator.js validate <file> [schema]'); process.exit(1); }
  if (!fs.existsSync(file)) { console.error(`File not found: ${file}`); process.exit(1); }
  
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const schema = schemaFile && fs.existsSync(schemaFile)
    ? JSON.parse(fs.readFileSync(schemaFile, 'utf8'))
    : null;
  
  if (!schema) {
    console.log('\nNo schema provided. Inferred schema:');
    console.log(JSON.stringify(inferSchema(data), null, 2));
    return;
  }
  
  const result = Array.isArray(data)
    ? { valid: data.every(item => validateObject(item, schema).valid) }
    : validateObject(data, schema);
  
  console.log(`\n## Validation Result\n`);
  console.log(`Valid: ${result.valid ? 'YES ✓' : 'NO ✗'}`);
  if (!result.valid && result.errors) {
    console.log(`\nErrors:`);
    for (const e of result.errors.slice(0, 10)) {
      console.log(`  - ${e.field}: ${e.rule} failed (expected: ${e.expected})`);
    }
    if (result.errors.length > 10) console.log(`  ... and ${result.errors.length - 10} more`);
  }
  console.log();
}

function cmdCheck(jsonStr, rulesStr) {
  if (!jsonStr || !rulesStr) {
    console.error('Usage: data_validator.js check <json> <rules>');
    process.exit(1);
  }
  try {
    const value = JSON.parse(jsonStr);
    const rules = JSON.parse(rulesStr);
    const result = validateValue(value, rules);
    console.log(`\n${result.valid ? '✅ Valid' : '❌ Invalid'}`);
    if (!result.valid) {
      for (const e of result.errors) {
        console.log(`  ${e.rule}: expected ${e.expected}, got ${e.actual}`);
      }
    }
    console.log();
  } catch (e) {
    console.error('Parse error:', e.message);
  }
}

function cmdSchema(file) {
  if (!file || !fs.existsSync(file)) {
    console.error('Usage: data_validator.js schema <file>');
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const schema = inferSchema(data);
  console.log('\n## Inferred Schema\n');
  console.log(JSON.stringify(schema, null, 2));
  console.log();
}

function cmdRules() {
  console.log(`\n## Available Validation Rules\n`);
  console.log('Rule          Description');
  console.log('────────────────────────────────────────────');
  console.log('required      Value must be present');
  console.log('type          Must be: string|number|boolean|object|array');
  console.log('min           Number >= n');
  console.log('max           Number <= n');
  console.log('minLength     String length >= n');
  console.log('maxLength     String length <= n');
  console.log('pattern       Must match regex');
  console.log('email         Valid email format');
  console.log('url           Valid HTTP(S) URL');
  console.log('uuid          Valid UUID format');
  console.log('enum          Must be in list');
  console.log('integer       Must be integer');
  console.log('positive      Number > 0');
  console.log('nonnegative   Number >= 0');
  console.log('date          Valid date');
  console.log('isoDate       ISO 8601 date format');
  console.log('json          Valid JSON string');
  console.log();
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  validate: cmdValidate,
  check: cmdCheck,
  schema: cmdSchema,
  rules: cmdRules,
};

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`data_validator.js — Universal Data Validation Engine

Usage: node data_validator.js <command> [args...]

Commands:
  validate <file> [schema]  Validate JSON file
  check <json> <rules>      Check value against rules
  schema <file>             Infer schema from file
  rules                     List available rules

Examples:
  node data_validator.js validate data.json schema.json
  node data_validator.js check '"test@example.com"' '{"email":true}'
  node data_validator.js schema users.json
`);
  process.exit(0);
}

COMMANDS[cmd](...args);
