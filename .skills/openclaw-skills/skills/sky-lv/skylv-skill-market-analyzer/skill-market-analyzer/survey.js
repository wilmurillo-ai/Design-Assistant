/**
 * skill-market-analyzer / survey.js
 * Full market landscape scan across 12 categories via clawhub search API.
 */
'use strict';
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BASE = __dirname;
const CACHE = path.join(BASE, 'cache');
if (!fs.existsSync(CACHE)) fs.mkdirSync(CACHE, { recursive: true });

// 12 market segments
const CATEGORIES = [
  { category: 'agent',         terms: ['agent', 'autonomous', 'self-improving', 'memory'] },
  { category: 'web',          terms: ['browser', 'automation', 'scrape', 'crawler'] },
  { category: 'code',         terms: ['coding', 'refactor', 'debug', 'test', 'review'] },
  { category: 'file',         terms: ['file', 'organize', 'pdf', 'document', 'docx'] },
  { category: 'data',         terms: ['data', 'sql', 'database', 'csv', 'analytics'] },
  { category: 'communication', terms: ['email', 'telegram', 'discord', 'slack', 'webhook'] },
  { category: 'devops',       terms: ['docker', 'ci-cd', 'deploy', 'server', 'cloud'] },
  { category: 'ai-ml',        terms: ['llm', 'prompt', 'rag', 'embedding', 'fine-tune'] },
  { category: 'content',      terms: ['blog', 'social', 'seo', 'copywriting', 'translation'] },
  { category: 'productivity', terms: ['schedule', 'reminder', 'calendar', 'task', 'todo'] },
  { category: 'security',     terms: ['auth', 'permission', 'sandbox', 'audit'] },
  { category: 'platform',     terms: ['github', 'notion', 'notion-api', 'notion-sync'] },
];

// Global dedup: slug -> { title, score, term }
const globalSkills = new Map();

function parseSearchOutput(output) {
  const lines = output.trim().split('\n').filter(l => l.trim());
  const results = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    // Format: "slug  Title  (score)"
    const m = line.match(/^(.+?)\s{2,}(.+?)\s{2,}\((\d+\.\d+)\)$/);
    if (m) {
      results.push({
        slug: m[1].trim(),
        title: m[2].trim(),
        score: parseFloat(m[3]),
      });
    }
  }
  return results;
}

function searchClawhub(term) {
  process.chdir('C:/');
  const cmd = `clawhub search "${term.replace(/"/g, '\\"')}"`;
  try {
    const out = execSync(cmd, { encoding: 'utf8', timeout: 20000, shell: 'cmd' });
    return parseSearchOutput(out);
  } catch (e) {
    // Fallback: try via clawhub CLI directly
    const out = execSync(`clawhub search ${term}`, { encoding: 'utf8', timeout: 20000 });
    return parseSearchOutput(out);
  }
}

function sleep(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) { /* spin */ }
}

async function survey() {
  const report = {
    generated: new Date().toISOString(),
    categories: [],
    totalSkills: 0,
    totalQueries: 0,
  };

  console.log('=== ClawHub Skill Market Survey ===\n');

  for (const cat of CATEGORIES) {
    const catResult = {
      category: cat.category,
      terms: [],
      totalFound: 0,
      avgScore: 0,
      scores: [],
      top5: [],
      skillCount: 0,
    };

    console.log(`[${cat.category}] scanning ${cat.terms.length} terms...`);

    for (const term of cat.terms) {
      const skills = searchClawhub(term);
      catResult.totalQueries++;
      catResult.scores.push(...skills.map(s => s.score));

      // Track globally (dedup by slug)
      for (const s of skills) {
        if (!globalSkills.has(s.slug)) {
          globalSkills.set(s.slug, { slug: s.slug, title: s.title, score: s.score, term });
        }
      }

      catResult.terms.push({
        term,
        found: skills.length,
        top: skills.slice(0, 3).map(s => s.slug),
      });

      catResult.skillCount += skills.length;
      sleep(300); // rate limit courtesy pause
    }

    catResult.totalFound = catResult.scores.length;
    catResult.avgScore = catResult.scores.length
      ? (catResult.scores.reduce((a, b) => a + b, 0) / catResult.scores.length).toFixed(3)
      : 0;

    // Top 5 skills for this category (by score, deduped)
    const catSkills = [];
    for (const s of globalSkills.values()) {
      // Check if this skill appeared in any of this category's terms
      const appeared = catResult.terms.some(t => t.top.includes(s.slug));
      if (appeared) catSkills.push(s);
    }
    catResult.top5 = catSkills.sort((a, b) => b.score - a.score).slice(0, 5).map(s => s.slug);

    report.categories.push(catResult);
    report.totalSkills += catResult.skillCount;

    console.log(`  -> found ${catResult.skillCount} results, avg score ${catResult.avgScore}`);
    console.log(`  top: ${catResult.top5.join(', ')}\n`);
  }

  report.globalSkillCount = globalSkills.size;

  // Save
  const date = new Date().toISOString().slice(0, 10);
  const surveyFile = path.join(CACHE, `survey_${date}.json`);
  fs.writeFileSync(surveyFile, JSON.stringify(report, null, 2));
  console.log(`\nSaved: ${surveyFile}`);
  console.log(`Total unique skills found: ${report.globalSkillCount}`);
  console.log(`Total queries run: ${report.totalQueries}`);

  return report;
}

survey().catch(e => { console.error('SURVEY ERROR:', e.message); process.exit(1); });
