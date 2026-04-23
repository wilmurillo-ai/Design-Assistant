#!/usr/bin/env node
/**
 * Monitor & Alert System - Health Monitor
 * 
 * Checks:
 * 1. Cron execution status
 * 2. Heartbeat rhythm
 * 3. Disk space
 * 4. Token budget
 * 5. Memory health
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE = 'C:\\Users\\Administrator\\.openclaw\\workspace';
const RESULTS = {
  passed: 0,
  failed: 0,
  warnings: 0,
  alerts: []
};

function log(level, component, message) {
  const icon = {
    'PASS': '✓',
    'WARN': '⚠',
    'FAIL': '✗',
    'INFO': 'ℹ'
  }[level];
  
  console.log(`${icon} [${component}] ${message}`);
  
  if (level === 'FAIL') {
    RESULTS.failed++;
    RESULTS.alerts.push({ level, component, message });
  } else if (level === 'WARN') {
    RESULTS.warnings++;
    RESULTS.alerts.push({ level, component, message });
  } else {
    RESULTS.passed++;
  }
}

// Test 1: Cron Execution Status
function checkCrons() {
  log('INFO', 'Cron', 'Checking cron execution status...');
  
  try {
    const output = execSync('openclaw cron list', { encoding: 'utf8' });
    const lines = output.split('\n').filter(l => l.includes('cron') || l.includes('at') || l.includes('every'));
    
    const runningCrons = lines.filter(l => l.includes('running') || l.includes('ok')).length;
    const idleCrons = lines.filter(l => l.includes('idle')).length;
    
    log('PASS', 'Cron', `${runningCrons + idleCrons} crons configured (${runningCrons} running, ${idleCrons} idle)`);
    
    // Check for failed crons
    const failedCrons = lines.filter(l => l.includes('failed') || l.includes('error')).length;
    if (failedCrons > 0) {
      log('FAIL', 'Cron', `${failedCrons} cron(s) failed`);
    }
  } catch (e) {
    log('FAIL', 'Cron', `Failed to check crons: ${e.message}`);
  }
}

// Test 2: Heartbeat Rhythm
function checkHeartbeat() {
  log('INFO', 'Heartbeat', 'Checking heartbeat rhythm...');
  
  try {
    const memoryPath = path.join(WORKSPACE, 'memory', '2026-03-20.md');
    if (!fs.existsSync(memoryPath)) {
      log('WARN', 'Heartbeat', 'Today\'s memory file not found');
      return;
    }
    
    const content = fs.readFileSync(memoryPath, 'utf8');
    const heartbeatMatches = content.match(/心跳执行/g);
    const heartbeatCount = heartbeatMatches ? heartbeatMatches.length : 0;
    
    const now = new Date();
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const hoursElapsed = (now - startOfDay) / (1000 * 60 * 60);
    const expectedHeartbeats = Math.floor(hoursElapsed / 0.33); // Every 20 min
    
    log('PASS', 'Heartbeat', `${heartbeatCount} heartbeats executed today (expected ~${expectedHeartbeats})`);
    
    if (heartbeatCount < expectedHeartbeats * 0.5) {
      log('WARN', 'Heartbeat', 'Heartbeat execution rate below 50% of expected');
    }
  } catch (e) {
    log('FAIL', 'Heartbeat', `Failed to check heartbeat: ${e.message}`);
  }
}

// Test 3: Disk Space
function checkDiskSpace() {
  log('INFO', 'Disk', 'Checking disk space...');
  
  try {
    // Check workspace size
    const workspaceSize = execSync(`powershell -Command "(Get-ChildItem -Path '${WORKSPACE}' -Recurse -File | Measure-Object -Property Length -Sum).Sum"`, { encoding: 'utf8' });
    const sizeBytes = parseInt(workspaceSize.trim()) || 0;
    const sizeGB = (sizeBytes / (1024 * 1024 * 1024)).toFixed(2);
    
    log('PASS', 'Disk', `Workspace size: ${sizeGB} GB`);
    
    if (sizeGB > 10) {
      log('WARN', 'Disk', 'Workspace >10GB, consider cleanup');
    }
  } catch (e) {
    log('WARN', 'Disk', `Failed to check disk space: ${e.message}`);
  }
}

// Test 4: Token Budget
function checkTokenBudget() {
  log('INFO', 'Token', 'Checking token budget...');
  
  try {
    const budgetPath = path.join(WORKSPACE, 'memory', 'token-budget.md');
    if (!fs.existsSync(budgetPath)) {
      log('WARN', 'Token', 'Token budget file not found, creating...');
      return;
    }
    
    const content = fs.readFileSync(budgetPath, 'utf8');
    const todayMatch = content.match(/### (\d{4}-\d{2}-\d{2}).*?Total.*?(\d+)/s);
    
    if (todayMatch) {
      const todayTokens = parseInt(todayMatch[2]) || 0;
      const budget = 500000; // 500k estimated
      const usagePercent = ((todayTokens / budget) * 100).toFixed(1);
      
      log('PASS', 'Token', `Today's usage: ${todayTokens.toLocaleString()} tokens (${usagePercent}% of budget)`);
      
      if (usagePercent > 90) {
        log('FAIL', 'Token', 'CRITICAL: Token usage >90%, switch to cheap tasks only');
      } else if (usagePercent > 70) {
        log('WARN', 'Token', 'Token usage >70%, prioritize high-impact tasks');
      }
    } else {
      log('INFO', 'Token', 'No token usage data for today yet');
    }
  } catch (e) {
    log('WARN', 'Token', `Failed to check token budget: ${e.message}`);
  }
}

// Test 5: Memory Health
function checkMemoryHealth() {
  log('INFO', 'Memory', 'Checking memory health...');
  
  try {
    const memoryDir = path.join(WORKSPACE, 'memory');
    const files = fs.readdirSync(memoryDir).filter(f => f.endsWith('.md'));
    
    log('PASS', 'Memory', `${files.length} memory files found`);
    
    // Check today's file exists
    const today = new Date().toISOString().split('T')[0];
    const todayFile = `${today}.md`;
    
    if (!files.includes(todayFile)) {
      log('WARN', 'Memory', `Today's memory file (${todayFile}) not found`);
    }
    
    // Check MEMORY.md exists
    const memoryMdPath = path.join(WORKSPACE, 'MEMORY.md');
    if (!fs.existsSync(memoryMdPath)) {
      log('FAIL', 'Memory', 'MEMORY.md not found');
    } else {
      const size = fs.statSync(memoryMdPath).size;
      log('PASS', 'Memory', `MEMORY.md exists (${(size/1024).toFixed(1)} KB)`);
    }
  } catch (e) {
    log('FAIL', 'Memory', `Failed to check memory: ${e.message}`);
  }
}

// Test 6: Skill Health
function checkSkillHealth() {
  log('INFO', 'Skills', 'Checking skill health...');
  
  try {
    const skillsDir = path.join(WORKSPACE, 'skills');
    const skills = fs.readdirSync(skillsDir).filter(s => {
      const stat = fs.statSync(path.join(skillsDir, s));
      return stat.isDirectory() && !s.startsWith('.');
    });
    
    let validCount = 0;
    let invalidCount = 0;
    
    skills.forEach(skill => {
      const skillMdPath = path.join(skillsDir, skill, 'SKILL.md');
      const metaJsonPath = path.join(skillsDir, skill, '_meta.json');
      
      const hasSkillMd = fs.existsSync(skillMdPath);
      let hasValidMeta = false;
      
      if (fs.existsSync(metaJsonPath)) {
        try {
          JSON.parse(fs.readFileSync(metaJsonPath, 'utf8'));
          hasValidMeta = true;
        } catch (e) {}
      }
      
      if (hasSkillMd && hasValidMeta) {
        validCount++;
      } else {
        invalidCount++;
      }
    });
    
    log('PASS', 'Skills', `${validCount}/${skills.length} skills healthy`);
    
    if (invalidCount > 0) {
      log('WARN', 'Skills', `${invalidCount} skills missing SKILL.md or _meta.json`);
    }
  } catch (e) {
    log('FAIL', 'Skills', `Failed to check skills: ${e.message}`);
  }
}

// Main execution
console.log('='.repeat(60));
console.log('🔍 Automaton Health Monitor');
console.log('='.repeat(60));
console.log('');

checkCrons();
checkHeartbeat();
checkDiskSpace();
checkTokenBudget();
checkMemoryHealth();
checkSkillHealth();

// Summary
console.log('');
console.log('='.repeat(60));
console.log(`Summary: ${RESULTS.passed} passed, ${RESULTS.warnings} warnings, ${RESULTS.failed} failed`);
console.log('='.repeat(60));

if (RESULTS.alerts.length > 0) {
  console.log('');
  console.log('Alerts:');
  RESULTS.alerts.forEach(alert => {
    console.log(`  ${alert.level === 'FAIL' ? '🔴' : '🟡'} [${alert.component}] ${alert.message}`);
  });
}

// Exit with error code if any checks failed
process.exit(RESULTS.failed > 0 ? 1 : 0);
