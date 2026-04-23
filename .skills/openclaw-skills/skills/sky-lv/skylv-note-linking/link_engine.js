/**
 * link_engine.js — Note Linking & Knowledge Graph Builder
 * 
 * Pure Node.js semantic note linker. No external APIs.
 * Uses TF-IDF + Jaccard + structural signals to find connections.
 */

const fs = require('fs');
const path = require('path');

const NOTES_DIR = process.argv[2] || path.join(process.env.USERPROFILE || process.env.HOME, '.qclaw', 'workspace');
const OUTPUT_FORMAT = (process.argv[3] || 'markdown').toLowerCase();
const QUERY = process.argv.slice(4).join(' ') || null;
const DEPTH = parseInt(process.argv[5] || '2', 10);

const GRAPH_CACHE = path.join(process.env.TEMP || '/tmp', 'note-linking-graph.json');
const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const AUTO_LINK_THRESHOLD = 0.85;
const SUGGEST_THRESHOLD = 0.60;

// ── 1. File Discovery ──────────────────────────────────────────────

function discoverNotes(dir, files = []) {
  if (!fs.existsSync(dir)) return files;
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      discoverNotes(full, files);
    } else if (/\.(md|txt|org|markdown)$/i.test(entry.name)) {
      try {
        const stat = fs.statSync(full);
        if (stat.size <= MAX_FILE_SIZE) {
          files.push({ path: full, relPath: path.relative(dir, full), size: stat.size });
        }
      } catch {}
    }
  }
  return files;
}

// ── 2. Note Parsing ────────────────────────────────────────────────

function parseNote(file) {
  const raw = fs.readFileSync(file.path, 'utf8');
  const lines = raw.split('\n');

  // Frontmatter detection
  let frontmatter = {};
  let contentStart = 0;
  if (raw.startsWith('---')) {
    const endIdx = raw.indexOf('---', 3);
    if (endIdx > 0) {
      const fmText = raw.slice(3, endIdx).trim();
      contentStart = endIdx + 3;
      frontmatter = parseFrontmatter(fmText);
    }
  }

  const rawContent = raw.slice(contentStart).trim();

  // Extract wikilinks and markdown links
  const wikilinks = [...rawContent.matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)]
    .map(m => m[1].toLowerCase());
  const mdLinks = [...rawContent.matchAll(/\[([^\]]+)\]\(([^)]+)\)/g)]
    .map(m => ({ text: m[1], url: m[2] }));

  // Extract headings
  const headings = lines
    .filter(l => /^#{1,6}\s+/.test(l))
    .map(l => l.replace(/^#+\s+/, '').trim());

  // Content blocks (split by headings)
  const blocks = rawContent.split(/\n(?=#+\s)/).filter(b => b.trim());

  // Keywords & entities
  const words = rawContent.toLowerCase()
    .replace(/[#*`\[\]|()]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 3 && !STOP_WORDS.has(w));

  return {
    path: file.path,
    relPath: file.relPath,
    name: path.basename(file.path, path.extname(file.path)),
    nameLower: path.basename(file.path, path.extname(file.path)).toLowerCase(),
    frontmatter,
    rawContent,
    wikilinks,
    mdLinks,
    headings,
    blocks,
    words,
    wordSet: new Set(words),
    urlSet: new Set(mdLinks.filter(l => !l.url.startsWith('#')).map(l => l.text.toLowerCase())),
  };
}

function parseFrontmatter(text) {
  const fm = {};
  for (const line of text.split('\n')) {
    const m = line.match(/^(\w+):\s*(.*)$/);
    if (m) fm[m[1].trim()] = m[2].trim().replace(/^["']|["']$/g, '');
  }
  return fm;
}

// ── 3. TF-IDF Computation ──────────────────────────────────────────

function computeTFIDF(notes) {
  const N = notes.length;
  const df = {}; // document frequency

  for (const note of notes) {
    for (const word of note.wordSet) {
      df[word] = (df[word] || 0) + 1;
    }
  }

  for (const note of notes) {
    const tf = {};
    for (const word of note.words) {
      tf[word] = (tf[word] || 0) + 1;
    }
    const total = note.words.length;
    note.tfidf = {};
    for (const [word, count] of Object.entries(tf)) {
      note.tfidf[word] = (count / total) * Math.log(N / df[word]);
    }
    // Top keywords (top 20 by TF-IDF)
    note.topKeywords = Object.entries(note.tfidf)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 20)
      .map(([w]) => w);
    note.tfidfSet = new Set(note.topKeywords);
  }
}

// ── 4. Similarity Scoring ──────────────────────────────────────────

function cosine(a, b) {
  // Both are Map<string, number> of tfidf scores
  let dot = 0, normA = 0, normB = 0;
  for (const [k, va] of a) {
    if (b.has(k)) dot += va * b.get(k);
    normA += va * va;
  }
  for (const vb of b.values()) normB += vb * vb;
  if (normA === 0 || normB === 0) return 0;
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function jaccard(a, b) {
  let intersection = 0;
  for (const x of a) if (b.has(x)) intersection++;
  const union = a.size + b.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

function computeScore(a, b) {
  // 1. Content similarity (TF-IDF cosine on top keywords)
  const aTfidf = new Map(Object.entries(a.tfidf));
  const bTfidf = new Map(Object.entries(b.tfidf));
  const contentSim = cosine(aTfidf, bTfidf);

  // 2. Keyword overlap (Jaccard on top keywords)
  const keywordSim = jaccard(a.tfidfSet, b.tfidfSet);

  // 3. Explicit link (wikilink → high boost)
  const explicitLink = a.wikilinks.includes(b.nameLower) || b.wikilinks.includes(a.nameLower) ? 0.3 : 0;

  // 4. Heading similarity (near-duplicate headings suggest same topic)
  const commonHeadings = a.headings.filter(h =>
    b.headings.some(bh => levenshtein(h.toLowerCase(), bh.toLowerCase()) <= 3)
  ).length;
  const headingBoost = commonHeadings > 0 ? Math.min(0.2, commonHeadings * 0.1) : 0;

  // 5. YAML tag intersection
  const aTags = new Set([
    ...(a.frontmatter.tags || '').split(/[,\s]+/),
    ...(a.frontmatter.topics || '').split(/[,\s]+/),
  ].filter(t => t));
  const bTags = new Set([
    ...(b.frontmatter.tags || '').split(/[,\s]+/),
    ...(b.frontmatter.topics || '').split(/[,\s]+/),
  ].filter(t => t));
  const tagBoost = aTags.size > 0 && bTags.size > 0 ? jaccard(aTags, bTags) * 0.15 : 0;

  // 6. Name similarity
  const nameSim = 1 - levenshtein(a.nameLower, b.nameLower) / Math.max(a.nameLower.length, b.nameLower.length, 1);
  const nameBoost = nameSim > 0.7 ? (nameSim - 0.7) * 0.3 : 0;

  const score = Math.min(1, contentSim * 0.35 + keywordSim * 0.25 + explicitLink + headingBoost + tagBoost + nameBoost);
  return Math.round(score * 1000) / 1000;
}

function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, (_, i) => [i]);
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      dp[i][j] = a[i-1] === b[j-1] ? dp[i-1][j-1] : 1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]);
    }
  }
  return dp[m][n];
}

// ── 5. Graph Construction ─────────────────────────────────────────

function buildGraph(notes) {
  computeTFIDF(notes);
  const edges = [];

  for (let i = 0; i < notes.length; i++) {
    for (let j = i + 1; j < notes.length; j++) {
      const score = computeScore(notes[i], notes[j]);
      if (score >= SUGGEST_THRESHOLD) {
        edges.push({
          from: notes[i].relPath,
          to: notes[j].relPath,
          fromName: notes[i].name,
          toName: notes[j].name,
          score,
          type: score >= AUTO_LINK_THRESHOLD ? 'auto' : 'suggest',
          reasons: buildReasons(notes[i], notes[j], score),
        });
      }
    }
  }

  // Sort by score descending
  edges.sort((a, b) => b.score - a.score);

  return edges;
}

function buildReasons(a, b, score) {
  const reasons = [];
  if (a.wikilinks.includes(b.nameLower)) reasons.push('explicit wikilink');
  if (b.wikilinks.includes(a.nameLower)) reasons.push('backlink');
  const commonKw = [...a.tfidfSet].filter(k => b.tfidfSet.has(k)).slice(0, 5);
  if (commonKw.length > 0) reasons.push(`shared topics: ${commonKw.join(', ')}`);
  if (a.frontmatter.tags && b.frontmatter.tags) {
    const common = a.frontmatter.tags.split(/[,\s]+/).filter(t => t && b.frontmatter.tags.includes(t));
    if (common.length) reasons.push(`shared tags: ${common.join(', ')}`);
  }
  return reasons.length ? reasons : ['semantic similarity'];
}

// ── 6. Graph Analysis ──────────────────────────────────────────────

function analyzeGraph(notes, edges) {
  const nodeMap = new Map(notes.map(n => [n.relPath, { id: n.relPath, name: n.name, connections: 0, topics: n.topKeywords.slice(0, 5) }]));

  for (const edge of edges) {
    nodeMap.get(edge.from).connections++;
    nodeMap.get(edge.to).connections++;
  }

  const nodes = [...nodeMap.values()].sort((a, b) => b.connections - a.connections);
  const orphanCount = nodes.filter(n => n.connections === 0).length;

  // Find bridges (notes that connect separate clusters)
  const bridges = findBridges(notes, edges);

  return { nodes, edges, orphanCount, bridges };
}

function findBridges(notes, edges) {
  // Simplified bridge detection: notes with high degree that connect disparate topics
  const nodeEdges = new Map();
  for (const e of edges) {
    if (!nodeEdges.has(e.from)) nodeEdges.set(e.from, []);
    if (!nodeEdges.has(e.to)) nodeEdges.set(e.to, []);
    nodeEdges.get(e.from).push(e);
    nodeEdges.get(e.to).push(e);
  }

  return [...nodeEdges.entries()]
    .filter(([, es]) => es.length >= 3 && es.some(e => e.score >= 0.7))
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, 5)
    .map(([id, es]) => ({ id, edgeCount: es.length, strongest: Math.max(...es.map(e => e.score)) }));
}

// ── 7. Query Engine ────────────────────────────────────────────────

function answerQuery(notes, edges, query) {
  const queryWords = query.toLowerCase().replace(/[#*`\[\]|()]/g, ' ').split(/\s+/).filter(w => w.length > 2);
  const querySet = new Set(queryWords);

  // Find notes relevant to query
  const scored = notes.map(note => {
    const keywordMatch = [...querySet].filter(w => note.wordSet.has(w)).length;
    const tfidfMatch = [...querySet].filter(w => note.tfidfSet.has(w)).length;
    const headingMatch = note.headings.filter(h => queryWords.some(qw => h.toLowerCase().includes(qw))).length;
    const score = keywordMatch * 1 + tfidfMatch * 2 + headingMatch * 3;
    return { note, score };
  }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);

  if (scored.length === 0) return { answer: `No notes found matching: "${query}"`, related: [] };

  const topNote = scored[0].note;

  // Find related notes
  const relatedEdges = edges.filter(e => e.from === topNote.relPath || e.to === topNote.relPath)
    .sort((a, b) => b.score - a.score);

  return {
    topNote: topNote.relPath,
    relevance: scored[0].score,
    related: relatedEdges.map(e => ({
      note: e.from === topNote.relPath ? e.to : e.from,
      name: e.from === topNote.relPath ? e.toName : e.fromName,
      score: e.score,
      type: e.type,
      reasons: e.reasons,
    })),
  };
}

// ── 8. Output Formatters ──────────────────────────────────────────

function formatMarkdown(notes, edges, analysis, query) {
  const { nodes, edges: sortedEdges, orphanCount, bridges } = analysis;

  let output = `## 📊 Knowledge Graph — ${NOTES_DIR}\n\n`;
  output += `| Metric | Value |\n|--------|-------|\n`;
  output += `| Notes analyzed | ${notes.length} |\n`;
  output += `| Total links found | ${edges.length} |\n`;
  output += `| Auto-linkable (≥${AUTO_LINK_THRESHOLD}) | ${edges.filter(e => e.type === 'auto').length} |\n`;
  output += `| Suggested (${SUGGEST_THRESHOLD}–${AUTO_LINK_THRESHOLD}) | ${edges.filter(e => e.type === 'suggest').length} |\n`;
  output += `| Orphan notes | ${orphanCount} |\n\n`;

  // Top hubs
  output += `### 🔗 Top Hubs (most connected)\n\n`;
  for (const node of nodes.slice(0, 10)) {
    const bar = '█'.repeat(Math.min(node.connections, 20));
    output += `${bar} **${node.name}** — ${node.connections} connections\n`;
  }

  // High-confidence auto-links
  const autoLinks = sortedEdges.filter(e => e.type === 'auto');
  if (autoLinks.length > 0) {
    output += `\n### ✅ Auto-links (confidence ≥ ${AUTO_LINK_THRESHOLD})\n\n`;
    output += `| From | To | Score | Reason |\n`;
    output += `|------|----|-------|--------|\n`;
    for (const e of autoLinks.slice(0, 20)) {
      output += `| ${e.fromName} | ${e.toName} | ${e.score.toFixed(3)} | ${e.reasons.join(', ')} |\n`;
    }
  }

  // Suggestions
  const suggestions = sortedEdges.filter(e => e.type === 'suggest');
  if (suggestions.length > 0) {
    output += `\n### 💡 Link Suggestions (confidence ${SUGGEST_THRESHOLD}–${AUTO_LINK_THRESHOLD})\n\n`;
    output += `| From | To | Score | Reason |\n`;
    output += `|------|----|-------|--------|\n`;
    for (const e of suggestions.slice(0, 30)) {
      output += `| ${e.fromName} | ${e.toName} | ${e.score.toFixed(3)} | ${e.reasons.join(', ')} |\n`;
    }
  }

  // Orphans
  const orphans = nodes.filter(n => n.connections === 0);
  if (orphans.length > 0) {
    output += `\n### 🔕 Orphan Notes (no connections)\n\n`;
    for (const o of orphans) {
      output += `- ${o.name}\n`;
    }
  }

  // Bridges
  if (bridges.length > 0) {
    output += `\n### 🌉 Bridge Notes (connect separate clusters)\n\n`;
    for (const b of bridges) {
      output += `- **${path.basename(b.id)}** — ${b.edgeCount} connections, strongest: ${b.strongest.toFixed(3)}\n`;
    }
  }

  // Query response
  if (query) {
    const result = answerQuery(notes, edges, query);
    output += `\n---\n\n## 🔍 Query: "${query}"\n\n`;
    if (result.answer) {
      output += result.answer + '\n';
    } else {
      output += `**Most relevant:** ${result.topNote} (relevance: ${result.relevance})\n\n`;
      if (result.related.length > 0) {
        output += `| Connected Note | Score | Type | Reason |\n`;
        output += `|----------------|-------|------|--------|\n`;
        for (const r of result.related) {
          output += `| ${r.name} | ${r.score.toFixed(3)} | ${r.type} | ${r.reasons.join(', ')} |\n`;
        }
      }
    }
  }

  return output;
}

function formatGraph(notes, edges) {
  const analysis = analyzeGraph(notes, edges);
  return JSON.stringify({ nodes: analysis.nodes, edges: analysis.edges, orphanCount: analysis.orphanCount }, null, 2);
}

// ── 9. Stop Words ──────────────────────────────────────────────────

const STOP_WORDS = new Set([
  'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out',
  'this', 'that', 'with', 'have', 'from', 'they', 'been', 'were', 'said', 'each', 'which', 'their',
  'will', 'way', 'about', 'many', 'then', 'them', 'would', 'make', 'like', 'into', 'time', 'very',
  'when', 'come', 'could', 'now', 'than', 'first', 'water', 'been', 'call', 'who', 'its', 'over',
  'such', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'other', 'just', 'now',
  'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
  'these', 'then', 'come', 'made', 'find', 'more', 'long', 'write', 'right', 'look', 'two', 'also',
  'more', 'through', 'must', 'look', 'great', 'before', 'help', 'before', 'through', 'most', 'even',
  '因为', '所以', '但是', '而且', '如果', '虽然', '这个', '那个', '什么', '怎么', '可以', '没有',
  '已经', '还是', '关于', '以及', '或者', '之后', '之前', '之后', '首先', '然后', '最后',
]);

// ── Main ───────────────────────────────────────────────────────────

function main() {
  console.error(`[note-linking] Scanning: ${NOTES_DIR}`);

  if (!fs.existsSync(NOTES_DIR)) {
    console.error(`[note-linking] ERROR: Directory not found: ${NOTES_DIR}`);
    process.exit(1);
  }

  const files = discoverNotes(NOTES_DIR);
  console.error(`[note-linking] Found ${files.length} notes`);

  if (files.length === 0) {
    console.error(`[note-linking] No .md/.txt/.org files found`);
    process.exit(0);
  }

  const notes = files.map(parseNote);
  console.error(`[note-linking] Parsed ${notes.length} notes, computing relationships...`);

  // Cache check
  const cacheKey = JSON.stringify(notes.map(n => n.path + ':' + n.words.slice(0, 5).join(',')));
  const cachedHash = hashStr(cacheKey);

  if (fs.existsSync(GRAPH_CACHE)) {
    try {
      const cached = JSON.parse(fs.readFileSync(GRAPH_CACHE, 'utf8'));
      if (cached.hash === cachedHash) {
        console.error(`[note-linking] Using cached graph (${cached.edges.length} edges)`);
        const analysis = analyzeGraph(notes, cached.edges);
        const output = OUTPUT_FORMAT === 'json'
          ? formatGraph(notes, cached.edges)
          : formatMarkdown(notes, cached.edges, analysis, QUERY);
        console.log(output);
        return;
      }
    } catch {}
  }

  const edges = buildGraph(notes);
  console.error(`[note-linking] Found ${edges.length} connections`);

  // Cache
  try {
    fs.writeFileSync(GRAPH_CACHE, JSON.stringify({ hash: cachedHash, edges, ts: Date.now() }));
  } catch {}

  const analysis = analyzeGraph(notes, edges);
  const output = OUTPUT_FORMAT === 'json'
    ? formatGraph(notes, edges)
    : formatMarkdown(notes, edges, analysis, QUERY);

  console.log(output);
}

function hashStr(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = Math.imul(31, h) + str.charCodeAt(i) | 0;
  }
  return h.toString(16);
}

main();
