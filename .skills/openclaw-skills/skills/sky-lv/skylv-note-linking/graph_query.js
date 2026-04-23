/**
 * graph_query.js — Query the knowledge graph
 * 
 * Usage: node graph_query.js <notesDir> <query> [depth]
 * Example: node graph_query.js ~/.qclaw/workspace "memory system" 2
 */

const fs = require('fs');
const path = require('path');

const NOTES_DIR = process.argv[2] || path.join(process.env.USERPROFILE || process.env.HOME, '.qclaw', 'workspace');
const QUERY = process.argv.slice(3).join(' ');
const DEPTH = parseInt(process.argv[process.argv.length - 1]) || 2;
const GRAPH_CACHE = path.join(process.env.TEMP || '/tmp', 'note-linking-graph.json');

if (!QUERY) {
  console.error('Usage: node graph_query.js <notesDir> <query> [depth]');
  process.exit(1);
}

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
        if (stat.size <= 1024 * 1024) {
          files.push({ path: full, relPath: path.relative(dir, full) });
        }
      } catch {}
    }
  }
  return files;
}

function parseNote(file) {
  const raw = fs.readFileSync(file.path, 'utf8');
  const lines = raw.split('\n');
  let frontmatter = {};
  let contentStart = 0;
  if (raw.startsWith('---')) {
    const endIdx = raw.indexOf('---', 3);
    if (endIdx > 0) {
      frontmatter = parseFrontmatter(raw.slice(3, endIdx).trim());
      contentStart = endIdx + 3;
    }
  }
  const rawContent = raw.slice(contentStart).trim();
  const wikilinks = [...rawContent.matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)].map(m => m[1].toLowerCase());
  const headings = lines.filter(l => /^#{1,6}\s+/.test(l)).map(l => l.replace(/^#+\s+/, '').trim());
  const words = rawContent.toLowerCase().replace(/[#*`\[\]|()]/g, ' ').split(/\s+/).filter(w => w.length > 3);
  const STOP_WORDS = new Set(['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'this', 'that', 'with', 'have', 'from', 'they', 'been', 'were', 'will', 'way', 'about', 'many', 'then', 'them', 'would', 'make', 'like', 'into', 'time', 'very', 'when', 'come', 'could', 'now', 'than', 'first', 'your', 'good', 'some', 'see', 'these', 'then', 'into', 'year', 'find', 'more', 'long', 'write', 'right', 'look', 'also', 'through', 'most', 'even', 'because', 'these', 'those', 'where', 'when', 'what', 'which', 'there', 'here', 'only', 'some', 'each', 'being', 'them', 'other', 'such', 'given', 'same', 'after', 'before']);
  return {
    path: file.path, relPath: file.relPath,
    name: path.basename(file.path, path.extname(file.path)),
    nameLower: path.basename(file.path, path.extname(file.path)).toLowerCase(),
    frontmatter, wikilinks, headings,
    wordSet: new Set(words.filter(w => !STOP_WORDS.has(w))),
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

function searchNotes(notes, query) {
  const queryWords = query.toLowerCase().replace(/[#*`\[\]|()]/g, ' ').split(/\s+/).filter(w => w.length > 2);
  return notes.map(note => {
    let score = 0;
    const matchedWords = queryWords.filter(w => note.wordSet.has(w));
    score += matchedWords.length * 2;
    const headingMatch = note.headings.filter(h => queryWords.some(qw => h.toLowerCase().includes(qw))).length;
    score += headingMatch * 5;
    if (queryWords.some(qw => note.nameLower.includes(qw))) score += 10;
    return { note, score, matchedWords };
  }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
}

function findPath(notes, from, to, depth) {
  // BFS path finding
  const noteMap = new Map(notes.map(n => [n.relPath, n]));
  if (!noteMap.has(from) || !noteMap.has(to)) return null;

  const cache = GRAPH_CACHE;
  let edges = [];
  if (fs.existsSync(cache)) {
    try {
      const cached = JSON.parse(fs.readFileSync(cache, 'utf8'));
      edges = cached.edges || [];
    } catch {}
  }

  const adj = new Map();
  for (const e of edges) {
    if (!adj.has(e.from)) adj.set(e.from, []);
    if (!adj.has(e.to)) adj.set(e.to, []);
    adj.get(e.from).push({ node: e.to, score: e.score });
    adj.get(e.to).push({ node: e.from, score: e.score });
  }

  const queue = [[from, [from]]];
  const visited = new Set([from]);

  while (queue.length > 0) {
    const [current, path] = queue.shift();
    if (current === to) return path;

    if (path.length >= depth) continue;

    const neighbors = adj.get(current) || [];
    for (const { node, score } of neighbors) {
      if (!visited.has(node)) {
        visited.add(node);
        queue.push([node, [...path, node]]);
      }
    }
  }
  return null;
}

function main() {
  if (!fs.existsSync(NOTES_DIR)) {
    console.error(`Directory not found: ${NOTES_DIR}`);
    process.exit(1);
  }

  const files = discoverNotes(NOTES_DIR);
  const notes = files.map(parseNote);

  console.log(`\n## 🔍 Query: "${QUERY}"\n`);
  console.log(`Notes scanned: ${notes.length}\n`);

  const results = searchNotes(notes, QUERY);

  if (results.length === 0) {
    console.log(`No results for: "${QUERY}"`);
    return;
  }

  console.log(`### Top ${Math.min(results.length, 5)} Results\n`);
  for (let i = 0; i < Math.min(results.length, 5); i++) {
    const { note, score, matchedWords } = results[i];
    console.log(`**${i + 1}. ${note.name}** (${note.relPath})`);
    console.log(`   Score: ${score} | Matched: ${matchedWords.slice(0, 8).join(', ')}`);
    if (note.headings.length > 0) {
      console.log(`   Headings: ${note.headings.slice(0, 3).join(' | ')}`);
    }
    console.log();
  }

  // Find path between top 2 results
  if (results.length >= 2) {
    const path = findPath(notes, results[0].note.relPath, results[1].note.relPath, DEPTH);
    console.log(`### 🔗 Path: "${results[0].note.name}" → "${results[1].note.name}"\n`);
    if (path) {
      console.log(`Path found (depth ${path.length - 1}): ${path.join(' → ')}`);
    } else {
      console.log(`No path found within depth ${DEPTH}`);
    }
  }
}

main();
