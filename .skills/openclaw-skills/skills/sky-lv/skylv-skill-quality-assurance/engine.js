/**
 * Skill Quality Assurance Engine
 * Analyzes and scores SKILL.md quality for OpenClaw skills
 * Used for: self-improvement, skill review, quality metrics
 */

const fs = require('fs');
const path = require('path');

// Quality dimensions with weights
const DIMENSIONS = {
  clarity: 0.20,
  completeness: 0.20,
  actionability: 0.25,
  discoverability: 0.15,
  examples: 0.20
};

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  match[1].split('\n').forEach(line => {
    const [k, ...v] = line.split(':');
    if (k && v.length) fm[k.trim()] = v.join(':').trim();
  });
  return fm;
}

function extractBody(content) {
  const idx = content.indexOf('---', 4);
  return idx > 0 ? content.slice(idx + 3).trim() : content;
}

function scoreClarity(body) {
  let score = 0;
  // No very long sentences (>100 chars without period)
  const longSentences = (body.match(/[^.!?]{100,}[.!?]/g) || []).length;
  score += Math.max(0, 10 - longSentences * 2);
  // Has clear headings
  const headings = (body.match(/^#{1,3}\s+\w/gm) || []).length;
  score += Math.min(5, headings * 1.5);
  // No filler phrases
  const fillers = ['obviously', 'basically', 'simply', 'just', 'actually'].filter(w => body.includes(w)).length;
  score += Math.max(0, 5 - fillers);
  return Math.min(10, Math.max(0, score));
}

function scoreCompleteness(body, fm) {
  let score = 0;
  const required = ['name', 'description'];
  required.forEach(k => { if (fm[k]) score += 2; });
  // Has install instructions
  if (body.match(/install|openclaw skill/i)) score += 2;
  // Has usage section
  if (body.match(/^#{1,2}\s+(usage|how to use|examples?)/im)) score += 2;
  // Has triggers or keywords
  if (fm.triggers || fm.keywords || fm.usage) score += 2;
  return Math.min(10, score);
}

function scoreActionability(body) {
  let score = 0;
  // Has step-by-step instructions
  const numbered = (body.match(/^\d+\.\s+\w/gm) || []).length;
  score += Math.min(5, numbered * 1.5);
  // Has code blocks
  const codeBlocks = (body.match(/```[\s\S]*?```/g) || []).length;
  score += Math.min(3, codeBlocks * 1);
  // Has commands to run
  const commands = (body.match(/\$\s+\w|openclaw\s+\w/i) || []).length;
  score += Math.min(2, commands);
  return Math.min(10, score);
}

function scoreDiscoverability(fm, body) {
  let score = 0;
  // Has good description (50+ chars)
  if (fm.description && fm.description.length > 50) score += 3;
  // Has keywords
  if (fm.keywords) {
    const kw = fm.keywords.split(',').length;
    score += Math.min(4, kw * 0.8);
  }
  // Has category
  if (fm.category || fm.tags) score += 3;
  return Math.min(10, score);
}

function scoreExamples(body) {
  let score = 0;
  // Has code examples
  const codeEx = (body.match(/```\w[\s\S]*?```/g) || []).length;
  score += Math.min(5, codeEx * 1.5);
  // Has before/after or use case examples
  if (body.match(/before|after|example|case study/i)) score += 3;
  // Has output examples
  if (body.match(/output|result|sample|example/i)) score += 2;
  return Math.min(10, score);
}

function analyzeSkill(skillPath) {
  const files = fs.readdirSync(skillPath);
  const skillMdPath = path.join(skillPath, 'SKILL.md');
  const readmeMdPath = path.join(skillPath, 'README.md');
  
  let content = '';
  let source = 'none';
  
  if (files.includes('SKILL.md')) {
    content = fs.readFileSync(skillMdPath, 'utf8');
    source = 'SKILL.md';
  } else if (files.includes('README.md')) {
    content = fs.readFileSync(readmeMdPath, 'utf8');
    source = 'README.md';
  } else {
    return null; // No documentation
  }
  
  const fm = parseFrontmatter(content);
  const body = extractBody(content);
  
  const scores = {
    clarity: scoreClarity(body),
    completeness: scoreCompleteness(body, fm),
    actionability: scoreActionability(body),
    discoverability: scoreDiscoverability(fm, body),
    examples: scoreExamples(body)
  };
  
  const overall = Math.round(
    Object.entries(scores).reduce((sum, [k, v]) => sum + v * DIMENSIONS[k], 0) * 10
  ) / 10;
  
  const issues = [];
  if (scores.clarity < 5) issues.push('Low clarity - consider more headings');
  if (scores.completeness < 5) issues.push('Missing required sections');
  if (scores.actionability < 5) issues.push('Not actionable - add step-by-step guides');
  if (scores.discoverability < 5) issues.push('Poor discoverability - add keywords/tags');
  if (scores.examples < 3) issues.push('Needs more examples');
  
  return {
    name: path.basename(skillPath),
    source,
    overall,
    scores,
    issues,
    recommendations: generateRecommendations(scores, fm, body)
  };
}

function generateRecommendations(scores, fm, body) {
  const recs = [];
  
  if (scores.discoverability < 6) {
    recs.push({
      priority: 'high',
      area: 'discoverability',
      suggestion: 'Add frontmatter keywords: `keywords: skill, tool, automation` and a clear description (50+ chars)'
    });
  }
  
  if (scores.examples < 5) {
    recs.push({
      priority: 'medium',
      area: 'examples',
      suggestion: 'Add a ## Usage section with at least 2 code examples showing input → output'
    });
  }
  
  if (scores.actionability < 6) {
    recs.push({
      priority: 'high',
      area: 'actionability',
      suggestion: 'Add numbered step-by-step instructions for the main workflow'
    });
  }
  
  if (!fm.description) {
    recs.push({
      priority: 'high',
      area: 'completeness',
      suggestion: 'Add description in frontmatter: `description: What this skill does in one sentence`'
    });
  }
  
  if (!fm.triggers && !fm.keywords) {
    recs.push({
      priority: 'medium',
      area: 'discoverability',
      suggestion: 'Add triggers keyword in frontmatter for ClawHub search'
    });
  }
  
  return recs;
}

function generateReport(skillDir) {
  const results = [];
  const dirs = fs.readdirSync(skillDir).filter(f => 
    fs.statSync(path.join(skillDir, f)).isDirectory()
  );
  
  for (const d of dirs) {
    const r = analyzeSkill(path.join(skillDir, d));
    if (r) results.push(r);
  }
  
  results.sort((a, b) => b.overall - a.overall);
  
  console.log('# Skill Quality Report\n');
  console.log(`Analyzed: ${results.length} skills\n`);
  
  console.log('## Overall Rankings\n');
  results.forEach((r, i) => {
    const grade = r.overall >= 7 ? '✅' : r.overall >= 5 ? '⚠️' : '❌';
    console.log(`${i+1}. ${grade} skylv-${r.name.padEnd(35)} ${r.overall.toFixed(1)}/10`);
  });
  
  console.log('\n## Dimension Breakdown\n');
  results.slice(0, 10).forEach(r => {
    console.log(`\n### skylv-${r.name} (${r.overall}/10)`);
    console.log(`  Clarity:        ${'█'.repeat(Math.round(r.scores.clarity))}${'░'.repeat(10-Math.round(r.scores.clarity))} ${r.scores.clarity}/10`);
    console.log(`  Completeness:   ${'█'.repeat(Math.round(r.scores.completeness))}${'░'.repeat(10-Math.round(r.scores.completeness))} ${r.scores.completeness}/10`);
    console.log(`  Actionability:  ${'█'.repeat(Math.round(r.scores.actionability))}${'░'.repeat(10-Math.round(r.scores.actionability))} ${r.scores.actionability}/10`);
    console.log(`  Discoverability:${'█'.repeat(Math.round(r.scores.discoverability))}${'░'.repeat(10-Math.round(r.scores.discoverability))} ${r.scores.discoverability}/10`);
    console.log(`  Examples:       ${'█'.repeat(Math.round(r.scores.examples))}${'░'.repeat(10-Math.round(r.scores.examples))} ${r.scores.examples}/10`);
    if (r.issues.length) console.log(`  Issues: ${r.issues.join(' | ')}`);
  });
  
  const avgOverall = results.reduce((s, r) => s + r.overall, 0) / results.length;
  console.log(`\n## Summary`);
  console.log(`Average score: ${avgOverall.toFixed(1)}/10`);
  console.log(`Grade A (7+): ${results.filter(r => r.overall >= 7).length}`);
  console.log(`Grade B (5-6): ${results.filter(r => r.overall >= 5 && r.overall < 7).length}`);
  console.log(`Grade C (<5): ${results.filter(r => r.overall < 5).length}`);
  
  // Top recommendations across all skills
  const allRecs = results.flatMap(r => r.recommendations);
  const byPriority = {
    high: allRecs.filter(r => r.priority === 'high'),
    medium: allRecs.filter(r => r.priority === 'medium')
  };
  
  console.log('\n## Top Improvements Needed\n');
  [...byPriority.high, ...byPriority.medium].slice(0, 10).forEach(r => {
    console.log(`[${r.priority.toUpperCase()}] ${r.area}: ${r.suggestion}`);
  });
  
  return results;
}

// CLI mode
if (require.main === module) {
  const targetDir = process.argv[2] || 'C:/Users/Administrator/workspace/skills';
  generateReport(targetDir);
}

module.exports = { analyzeSkill, scoreDimensions: DIMENSIONS, generateReport };
