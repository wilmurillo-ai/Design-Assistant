#!/usr/bin/env node
/**
 * Token Budget Monitor
 * 
 * Proactively tracks token usage and alerts before hitting limits.
 * Prevents the API credit crisis we experienced today (~28 tokens remaining).
 * 
 * Usage: node token-monitor.js [--check] [--alert-threshold 70]
 */

const fs = require('fs');
const path = require('path');

const TOKEN_BUDGET_FILE = path.join(__dirname, '../../memory/token-budget.md');
const SESSION_STATE_FILE = path.join(__dirname, '../../SESSION-STATE.md');
const ALERT_THRESHOLD = parseInt(process.argv[3]) || 70; // Default 70%

// Estimated daily limit for aliyun/qwen3.5-plus
const DAILY_TOKEN_LIMIT = 500000;

function parseTokenUsage() {
  try {
    const content = fs.readFileSync(TOKEN_BUDGET_FILE, 'utf-8');
    
    // Extract today's total from the markdown table
    const todayMatch = content.match(/\*\*Total\*\*\s*\|\s*\*\d+\*\s*\|\s*\*\~?(\d+)k\*\*/);
    if (todayMatch) {
      return parseInt(todayMatch[1]) * 1000; // Convert k to actual number
    }
    
    // Fallback: estimate from heartbeat count
    const heartbeatMatch = content.match(/Heartbeats:\s*(\d+)\s*executed/);
    if (heartbeatMatch) {
      return parseInt(heartbeatMatch[1]) * 4000; // Avg 4k per heartbeat
    }
    
    return 0;
  } catch (err) {
    console.error('Error reading token budget file:', err.message);
    return 0;
  }
}

function calculateUsagePercent(used) {
  return Math.round((used / DAILY_TOKEN_LIMIT) * 100);
}

function getAlertLevel(percent) {
  if (percent >= 100) return 'CRITICAL';
  if (percent >= 90) return 'SEVERE';
  if (percent >= 70) return 'WARNING';
  if (percent >= 50) return 'NOTICE';
  return 'OK';
}

function generateAlert(used, percent, level) {
  const timestamp = new Date().toISOString();
  
  const alerts = {
    CRITICAL: {
      action: 'IMMEDIATE_SLEEP',
      message: `🚨 TOKEN LIMIT REACHED (${percent}%) - Stop all non-essential tasks`,
      tasks: ['Log handoff notes', 'Save state', 'Sleep until reset']
    },
    SEVERE: {
      action: 'MINIMAL_MODE',
      message: `⚠️ CRITICAL TOKEN USAGE (${percent}%) - Switch to essential tasks only`,
      tasks: ['No research', 'No content generation', 'Only critical maintenance']
    },
    WARNING: {
      action: 'PRIORITIZE',
      message: `⚠️ HIGH TOKEN USAGE (${percent}%) - Prioritize high-impact tasks`,
      tasks: ['Skip low-value heartbeats', 'Batch related tasks', 'Warn user']
    },
    NOTICE: {
      action: 'MONITOR',
      message: `📊 MODERATE TOKEN USAGE (${percent}%) - Normal operation with awareness`,
      tasks: ['Track trends', 'Optimize where possible']
    },
    OK: {
      action: 'NORMAL',
      message: `✅ TOKEN USAGE HEALTHY (${percent}%)`,
      tasks: ['Continue normal operation']
    }
  };
  
  return {
    timestamp,
    level,
    percent,
    used,
    remaining: DAILY_TOKEN_LIMIT - used,
    ...alerts[level]
  };
}

function updateSessionState(alert) {
  try {
    let content = fs.readFileSync(SESSION_STATE_FILE, 'utf-8');
    
    // Update or add token status section
    const tokenStatusSection = `
### Token Budget (${new Date().toISOString().split('T')[0]})
- **Used**: ${Math.round(alert.used / 1000)}k / ${DAILY_TOKEN_LIMIT / 1000}k (${alert.percent}%)
- **Remaining**: ${Math.round(alert.remaining / 1000)}k
- **Status**: ${alert.level}
- **Action**: ${alert.action}
`;
    
    // Check if token budget section exists
    const tokenRegex = /### Token Budget.*?(?=\n###|\n---|$)/s;
    if (content.match(tokenRegex)) {
      content = content.replace(tokenRegex, tokenStatusSection.trim());
    } else {
      // Insert before "Health Check" or after "System Status"
      const insertMarker = '### Health Check';
      const insertIndex = content.indexOf(insertMarker);
      if (insertIndex !== -1) {
        content = content.slice(0, insertIndex) + tokenStatusSection + '\n' + content.slice(insertIndex);
      }
    }
    
    fs.writeFileSync(SESSION_STATE_FILE, content);
    console.log('✅ SESSION-STATE.md updated with token status');
  } catch (err) {
    console.error('Error updating SESSION-STATE.md:', err.message);
  }
}

function check() {
  const used = parseTokenUsage();
  const percent = calculateUsagePercent(used);
  const level = getAlertLevel(percent);
  const alert = generateAlert(used, percent, level);
  
  console.log('\n=== Token Budget Monitor ===');
  console.log(`Timestamp: ${alert.timestamp}`);
  console.log(`Used: ${Math.round(used / 1000)}k / ${DAILY_TOKEN_LIMIT / 1000}k (${percent}%)`);
  console.log(`Remaining: ${Math.round(alert.remaining / 1000)}k`);
  console.log(`Status: ${alert.level}`);
  console.log(`Action: ${alert.action}`);
  console.log(`Message: ${alert.message}`);
  
  if (alert.tasks.length > 0) {
    console.log('\nRecommended Tasks:');
    alert.tasks.forEach(task => console.log(`  - ${task}`));
  }
  
  // Update SESSION-STATE.md
  updateSessionState(alert);
  
  // Return exit code based on severity
  if (level === 'CRITICAL' || level === 'SEVERE') {
    process.exit(1); // Signal that action is needed
  }
  
  process.exit(0);
}

// Main execution
if (process.argv.includes('--check') || process.argv.length === 2) {
  check();
} else {
  console.log('Token Budget Monitor');
  console.log('Usage: node token-monitor.js [--check] [--alert-threshold 70]');
  console.log('');
  console.log('Options:');
  console.log('  --check              Run a token usage check');
  console.log('  --alert-threshold X  Set custom alert threshold (default: 70)');
  console.log('');
  console.log('Exit codes:');
  console.log('  0 - Normal operation');
  console.log('  1 - Action required (CRITICAL/SEVERE)');
}
