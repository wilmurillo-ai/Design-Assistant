/**
 * consensus_persona_engine.js — 多 Agent 人格共识引擎
 * 
 * 当多个 Agent 协作时，如何确保它们的行为一致？
 * 通过投票、权重、规则来达成共识人格。
 * 
 * Usage: node consensus_persona_engine.js <command> [args...]
 */

const fs = require('fs');

// ── 人格维度 ──────────────────────────────────────────────────────────────────
const DIMENSIONS = {
  tone: {
    description: '沟通语调',
    options: ['formal', 'casual', 'friendly', 'professional', 'neutral'],
    weight: 0.15
  },
  verbosity: {
    description: '回复详细程度',
    options: ['concise', 'moderate', 'detailed', 'exhaustive'],
    weight: 0.10
  },
  risk_tolerance: {
    description: '风险容忍度',
    options: ['conservative', 'balanced', 'aggressive'],
    weight: 0.20
  },
  autonomy: {
    description: '自主决策程度',
    options: ['passive', 'suggestive', 'proactive', 'autonomous'],
    weight: 0.25
  },
  safety_level: {
    description: '安全检查严格程度',
    options: ['minimal', 'standard', 'strict', 'paranoid'],
    weight: 0.20
  },
  creativity: {
    description: '创造性程度',
    options: ['factual', 'balanced', 'creative', 'experimental'],
    weight: 0.10
  }
};

// ── 共识算法 ─────────────────────────────────────────────────────────────────
function calculateConsensus(votes, weights = {}) {
  const result = {};
  
  for (const [dim, data] of Object.entries(DIMENSIONS)) {
    const dimVotes = votes[dim] || {};
    let totalWeight = 0;
    const scores = {};
    
    for (const [option, count] of Object.entries(dimVotes)) {
      const voterWeight = weights[option] || 1;
      scores[option] = count * voterWeight;
      totalWeight += count * voterWeight;
    }
    
    // 找出最高票选项
    let maxScore = 0;
    let consensus = null;
    for (const [option, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        consensus = option;
      }
    }
    
    result[dim] = {
      consensus: consensus || data.options[0],
      confidence: totalWeight > 0 ? maxScore / totalWeight : 0,
      votes: dimVotes
    };
  }
  
  return result;
}

function generatePersonaConfig(consensus) {
  const config = {
    version: '1.0.0',
    generated: new Date().toISOString(),
    personality: {},
    rules: []
  };
  
  for (const [dim, data] of Object.entries(consensus)) {
    config.personality[dim] = data.consensus;
    
    // 根据共识生成规则
    if (dim === 'safety_level' && data.consensus === 'strict') {
      config.rules.push('ALWAYS ask for confirmation before destructive actions');
      config.rules.push('ALWAYS show warnings for potentially harmful operations');
    }
    if (dim === 'autonomy' && data.consensus === 'autonomous') {
      config.rules.push('CAN execute without confirmation if confidence > 0.8');
      config.rules.push('MUST report all actions taken');
    }
    if (dim === 'verbosity' && data.consensus === 'concise') {
      config.rules.push('KEEP responses under 100 words unless detail requested');
    }
  }
  
  return config;
}

// ── 命令处理 ───────────────────────────────────────────────────────────────────
function cmdVote(dimension, option, voter = 'default') {
  if (!DIMENSIONS[dimension]) {
    console.error(`Unknown dimension: ${dimension}`);
    console.log('Available:', Object.keys(DIMENSIONS).join(', '));
    process.exit(1);
  }
  if (!DIMENSIONS[dimension].options.includes(option)) {
    console.error(`Invalid option: ${option}`);
    console.log('Valid options:', DIMENSIONS[dimension].options.join(', '));
    process.exit(1);
  }
  
  // 存储投票（简化版，实际应用中应该持久化）
  const voteFile = '.consensus_votes.json';
  let votes = {};
  if (fs.existsSync(voteFile)) {
    votes = JSON.parse(fs.readFileSync(voteFile, 'utf8'));
  }
  if (!votes[dimension]) votes[dimension] = {};
  if (!votes[dimension][option]) votes[dimension][option] = 0;
  votes[dimension][option]++;
  
  fs.writeFileSync(voteFile, JSON.stringify(votes, null, 2));
  console.log(`✓ Vote recorded: ${dimension} = ${option}`);
}

function cmdConsensus() {
  const voteFile = '.consensus_votes.json';
  if (!fs.existsSync(voteFile)) {
    console.log('No votes recorded yet.');
    return;
  }
  
  const votes = JSON.parse(fs.readFileSync(voteFile, 'utf8'));
  const consensus = calculateConsensus(votes);
  const config = generatePersonaConfig(consensus);
  
  console.log('\n## Consensus Persona\n');
  console.log('Dimension'.padEnd(20) + 'Consensus'.padEnd(15) + 'Confidence');
  console.log('─'.repeat(50));
  for (const [dim, data] of Object.entries(consensus)) {
    console.log(dim.padEnd(20) + data.consensus.padEnd(15) + `${Math.round(data.confidence * 100)}%`);
  }
  
  console.log('\n## Generated Rules\n');
  for (const rule of config.rules) {
    console.log(`- ${rule}`);
  }
  
  console.log('\n## Persona Config\n');
  console.log('```json');
  console.log(JSON.stringify(config, null, 2));
  console.log('```');
}

function cmdDimensions() {
  console.log('\n## Personality Dimensions\n');
  console.log('Dimension'.padEnd(20) + 'Weight'.padEnd(10) + 'Description');
  console.log('─'.repeat(60));
  for (const [name, data] of Object.entries(DIMENSIONS)) {
    console.log(name.padEnd(20) + `${(data.weight * 100)}%`.padEnd(10) + data.description);
    console.log('  Options: ' + data.options.join(', '));
  }
}

function cmdReset() {
  const voteFile = '.consensus_votes.json';
  if (fs.existsSync(voteFile)) {
    fs.unlinkSync(voteFile);
    console.log('✓ All votes cleared');
  }
}

// ── Main ───────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  vote: () => cmdVote(args[0], args[1], args[2]),
  consensus: cmdConsensus,
  dimensions: cmdDimensions,
  reset: cmdReset,
  help: () => {
    console.log(`consensus_persona_engine.js — Multi-Agent Persona Consensus Engine

Usage: node consensus_persona_engine.js <command> [args...]

Commands:
  vote <dimension> <option>  Cast a vote for a personality dimension
  consensus                  Calculate and show current consensus
  dimensions                 List all personality dimensions
  reset                      Clear all votes

Examples:
  node consensus_persona_engine.js vote tone friendly
  node consensus_persona_engine.js vote autonomy proactive
  node consensus_persona_engine.js consensus
`);
  }
};

if (!cmd || !COMMANDS[cmd]) {
  COMMANDS.help();
  process.exit(0);
}

COMMANDS[cmd]();
