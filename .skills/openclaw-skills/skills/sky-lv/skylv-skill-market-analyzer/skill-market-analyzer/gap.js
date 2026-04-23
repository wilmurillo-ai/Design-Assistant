/**
 * skill-market-analyzer / gap.js  v2
 * Find underserved niches: quality gaps, not just quantity gaps.
 * Key insight: clawhub search caps at 10 results per term.
 * A "gap" = weak top performers (avg top-3 score < 3.5) OR no dominant incumbent.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE = __dirname;
const CACHE = path.join(BASE, 'cache');

// Load survey
const files = fs.readdirSync(CACHE).filter(f => f.startsWith('survey_') && f.endsWith('.json')).sort();
const survey = JSON.parse(fs.readFileSync(path.join(CACHE, files[files.length - 1]), 'utf8'));

const QUALITY_THRESHOLD = 3.5;   // below this = weak incumbents
const CROWDED_THRESHOLD = 45;    // above this = oversaturated

function sleep(ms) { const end = Date.now() + ms; while (Date.now() < end) {} }
function search(term) {
  process.chdir('C:/');
  try {
    const out = execSync(`clawhub search "${term.replace(/"/g, '\\"')}"`, {
      encoding: 'utf8', timeout: 15000, shell: 'cmd',
    });
    const lines = out.trim().split('\n').filter(l => l.trim());
    const results = [];
    for (const line of lines) {
      const m = line.match(/^(.+?)\s{2,}(.+?)\s{2,}\((\d+\.\d+)\)$/);
      if (m) results.push({ slug: m[1].trim(), title: m[2].trim(), score: parseFloat(m[3]) });
    }
    return results;
  } catch { return []; }
}

// ─── 1. Category-level quality gaps ─────────────────────────────────────────
const categoryGaps = survey.categories
  .map(cat => {
    const top3Avg = cat.scores.slice(0, 3).reduce((a, b) => a + b, 0) / Math.min(3, cat.scores.length);
    const qualityGap = top3Avg < QUALITY_THRESHOLD;
    return {
      category: cat.category,
      totalFound: cat.totalFound,
      top3Avg: +top3Avg.toFixed(3),
      saturation: (cat.totalFound / CROWDED_THRESHOLD).toFixed(2),
      qualityGap,
      oversaturated: cat.totalFound >= CROWDED_THRESHOLD,
      verdict: qualityGap && !cat.totalFound >= CROWDED_THRESHOLD
        ? '🎯 OPPORTUNITY' : cat.totalFound >= CROWDED_THRESHOLD ? '🔴 OVERSATURATED' : '🟡 COMPETITIVE',
    };
  })
  .sort((a, b) => a.top3Avg - b.top3Avg);

console.log('\n=== Category Quality Gap Analysis ===\n');
console.log('  Category         | Found | Top3 Avg | Sat   | Verdict');
console.log('  ------------------|-------|----------|-------|----------------');
for (const c of categoryGaps) {
  const bar = c.oversaturated ? '🔴' : c.qualityGap ? '🟢' : '🟡';
  console.log(`  ${c.category.padEnd(17)} | ${c.totalFound.toString().padStart(5)} | ${c.top3Avg.toFixed(3).padStart(8)} | ${c.saturation.padEnd(5)} | ${bar} ${c.qualityGap ? 'WEAK TOP' : 'OK'} ${c.oversaturated ? '(crowded)' : ''}`);
}

// ─── 2. Deep-dive: find specific weak spots ──────────────────────────────────
// Probe more specific terms to find where the market ISN'T covered
const deepTerms = [
  // Self-improvement / learning
  'self-learning-agent', 'evolution-agent', 'capability-growth', 'skill-acquisition',
  // Cross-platform messaging
  'whatsapp-bot', 'signal-bot', 'wechat-bot', 'multi-platform-bot',
  // EvoMap / GEP related
  'evo-agent', 'genome-agent', 'self-evolving-agent', 'gep-protocol',
  // Productivity & workflow
  'cron-scheduler', 'auto-reminder', 'smart-reminder', 'context-aware-scheduler',
  // GitHub integration
  'github-star-manager', 'repo-analyzer', 'github-trending-watcher', 'star-exchange',
  // Developer tools
  'api-test-generator', 'openapi-generator', 'swagger-to-code',
  // Data
  'csv-transform', 'data-pipeline', 'etl-agent',
  // File intelligence
  'file-versioning', 'knowledge-graph', 'note-linking',
  // Browser / web
  'multi-tab-manager', 'webpage-compare', 'diff-viewer',
];

const deepResults = [];
for (const term of deepTerms) {
  const skills = search(term);
  deepResults.push({
    term,
    found: skills.length,
    topScore: skills.length > 0 ? skills[0].score : 0,
    topSlug: skills.length > 0 ? skills[0].slug : null,
    qualityGap: skills.length > 0 && skills[0].score < QUALITY_THRESHOLD,
  });
  sleep(400);
}

deepResults.sort((a, b) => {
  // Sort by: not crowded (found < 5) first, then by topScore (lower = more opportunity)
  if (a.found < 5 && b.found >= 5) return -1;
  if (b.found < 5 && a.found >= 5) return 1;
  return a.topScore - b.topScore;
});

console.log('\n=== Deep Niche Scan (specific terms) ===\n');
console.log('  Term                      | Found | Top Score | Top Slug');
console.log('  --------------------------|-------|-----------|---------------------');
for (const r of deepResults) {
  const gap = r.found > 0 && r.topScore < QUALITY_THRESHOLD ? '⭐' : r.found === 0 ? '🎯' : '  ';
  console.log(`  ${gap} ${r.term.padEnd(25)} | ${String(r.found).padStart(5)} | ${r.topScore.toFixed(3).padStart(9)} | ${r.topSlug || '—'}`);
}

// ─── 3. Recommendations ────────────────────────────────────────────────────────
const ourSlugs = new Set([
  'skylv-skill-creator','skylv-clawhub-search','skylv-openclaw-config-optimizer',
  'skylv-hermes-agent-integration','skylv-agency-agents','skylv-mcp-server-builder',
  'skylv-multi-agent-orchestrator','skylv-git-helper','skylv-agent-builder',
  'skylv-seo-agent','skylv-system-design','skylv-openclaw-quick-deploy',
  'skylv-skill-market-analyzer','skylv-agent-performance-profiler',
  'skylv-cross-platform-bot-builder','skylv-ai-prompt-optimizer',
]);

const recommendations = deepResults
  .filter(r => r.found < 5 || r.topScore < QUALITY_THRESHOLD)
  .filter(r => !ourSlugs.has(`skylv-${r.term.replace(/[^a-z0-9-]/gi, '-')}`))
  .slice(0, 6)
  .map(r => ({
    skillSlug: `skylv-${r.term.replace(/[^a-z0-9-]/gi, '-')}`,
    searchTerm: r.term,
    found: r.found,
    topScore: r.topScore,
    reason: r.found === 0 ? 'ZERO existing skills — create and dominate'
               : r.topScore < QUALITY_THRESHOLD ? `Weak incumbent (${r.topSlug}) — beat them`
               : `Few skills (${r.found}) — easy to rank`,
  }));

console.log('\n=== 🎯 Top Opportunities for Us ===\n');
for (let i = 0; i < recommendations.length; i++) {
  const r = recommendations[i];
  console.log(`  ${i + 1}. ${r.skillSlug}`);
  console.log(`     Search: "${r.searchTerm}" | found: ${r.found} | top: ${r.topScore}`);
  console.log(`     Why: ${r.reason}\n`);
}

// Save
const report = { generated: new Date().toISOString(), categoryGaps, deepResults, recommendations };
const date = new Date().toISOString().slice(0, 10);
fs.writeFileSync(path.join(CACHE, `gaps_${date}.json`), JSON.stringify(report, null, 2));
