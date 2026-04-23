/**
 * export.js — Export knowledge graph as Obsidian markdown, JSON, or CSV
 * 
 * Usage: node export.js <notesDir> <format> [outputFile]
 * Formats: obsidian | json | csv | mermaid
 */

const fs = require('fs');
const path = require('path');

const NOTES_DIR = process.argv[2] || path.join(process.env.USERPROFILE || process.env.HOME, '.qclaw', 'workspace');
const FORMAT = (process.argv[3] || 'obsidian').toLowerCase();
const OUTPUT = process.argv[4] || null;
const GRAPH_CACHE = path.join(process.env.TEMP || '/tmp', 'note-linking-graph.json');

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
        if (stat.size <= 1024 * 1024) files.push({ path: full, relPath: path.relative(dir, full) });
      } catch {}
    }
  }
  return files;
}

function parseNote(file) {
  const raw = fs.readFileSync(file.path, 'utf8');
  let contentStart = 0;
  if (raw.startsWith('---')) {
    const endIdx = raw.indexOf('---', 3);
    if (endIdx > 0) contentStart = endIdx + 3;
  }
  const rawContent = raw.slice(contentStart).trim();
  const wikilinks = [...rawContent.matchAll(/\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g)].map(m => m[1]);
  const headings = raw.split('\n').filter(l => /^#{1,6}\s+/.test(l)).map(l => l.replace(/^#+\s+/, '').trim());
  return {
    path: file.path, relPath: file.relPath,
    name: path.basename(file.path, path.extname(file.path)),
    wikilinks, headings,
  };
}

function exportObsidian(notes, edges) {
  let out = '# Knowledge Graph Export\n\n';
  out += `Generated: ${new Date().toISOString()}\n`;
  out += `Notes: ${notes.length} | Links: ${edges.length}\n\n`;
  out += '---\n\n';

  // Backlinks index
  const backlinks = new Map();
  for (const e of edges) {
    if (!backlinks.has(e.to)) backlinks.set(e.to, []);
    backlinks.get(e.to).push({ from: e.from, fromName: e.fromName, score: e.score, reasons: e.reasons });
  }

  // Auto-links (add to source notes)
  for (const e of edges.filter(ee => ee.type === 'auto')) {
    const notePath = path.join(NOTES_DIR, e.from);
    if (fs.existsSync(notePath)) {
      let content = fs.readFileSync(notePath, 'utf8');
      const linkText = `[[${e.toName}]]`;
      if (!content.includes(linkText)) {
        content += `\n\n## Related\n\n- ${linkText} (${e.reasons.join(', ')})\n`;
        fs.writeFileSync(notePath, content);
        out += `✅ Added [[${e.toName}]] to ${e.fromName}\n`;
      }
    }
  }

  // Backlinks report
  out += '\n## Backlinks Index\n\n';
  for (const [note, links] of backlinks) {
    const noteName = path.basename(note, path.extname(note));
    out += `### ${noteName}\n`;
    out += `Found in: ${links.length} notes\n`;
    for (const link of links.sort((a, b) => b.score - a.score)) {
      out += `- [[${link.fromName}]] (${link.score.toFixed(3)}) — ${link.reasons.join(', ')}\n`;
    }
    out += '\n';
  }

  // Mermaid graph
  out += '## Graph View (Mermaid)\n\n';
  out += '```mermaid\ngraph TD\n';
  const seen = new Set();
  for (const e of edges) {
    if (!seen.has(e.from + e.to)) {
      seen.add(e.from + e.to);
      out += `  ${slug(e.fromName)}["${e.fromName}"]\n`;
      out += `  ${slug(e.toName)}["${e.toName}"]\n`;
      out += `  ${slug(e.fromName)} -->|"${e.score.toFixed(2)}"| ${slug(e.toName)}\n`;
    }
  }
  out += '```\n';

  return out;
}

function slug(name) {
  return name.replace(/[^a-zA-Z0-9]/g, '_').replace(/__+/g, '_');
}

function exportJSON(notes, edges) {
  const backlinks = new Map();
  for (const e of edges) {
    if (!backlinks.has(e.to)) backlinks.set(e.to, []);
    backlinks.get(e.to).push({ from: e.from, score: e.score, reasons: e.reasons });
  }
  return JSON.stringify({ notes: notes.map(n => ({ name: n.name, relPath: n.relPath, headings: n.headings })), edges, backlinks: [...backlinks.entries()], generated: new Date().toISOString() }, null, 2);
}

function exportCSV(notes, edges) {
  let csv = 'from,to,score,type,reasons\n';
  for (const e of edges) {
    csv += `"${e.fromName}","${e.toName}",${e.score},"${e.type}","${e.reasons.join('; ')}"\n`;
  }
  return csv;
}

function exportMermaid(notes, edges) {
  let out = '# Knowledge Graph — Mermaid Format\n\n```mermaid\ngraph TD\n';
  const nodes = new Map();
  for (const e of edges) {
    nodes.set(e.fromName, e.from);
    nodes.set(e.toName, e.to);
  }
  for (const [name] of nodes) {
    out += `  ${slug(name)}["${name}"]\n`;
  }
  out += '\n';
  const seen = new Set();
  for (const e of edges) {
    const key = e.fromName + '→' + e.toName;
    if (!seen.has(key)) {
      seen.add(key);
      out += `  ${slug(e.fromName)} -->|"${e.score.toFixed(2)}"| ${slug(e.toName)}\n`;
    }
  }
  out += '```\n';
  return out;
}

function main() {
  if (!fs.existsSync(NOTES_DIR)) {
    console.error(`Directory not found: ${NOTES_DIR}`); process.exit(1);
  }

  const files = discoverNotes(NOTES_DIR);
  const notes = files.map(parseNote);

  let edges = [];
  if (fs.existsSync(GRAPH_CACHE)) {
    try { edges = JSON.parse(fs.readFileSync(GRAPH_CACHE, 'utf8')).edges || []; } catch {}
  }

  let output;
  switch (FORMAT) {
    case 'obsidian': output = exportObsidian(notes, edges); break;
    case 'json': output = exportJSON(notes, edges); break;
    case 'csv': output = exportCSV(notes, edges); break;
    case 'mermaid': output = exportMermaid(notes, edges); break;
    default: output = exportMermaid(notes, edges);
  }

  if (OUTPUT) {
    fs.writeFileSync(OUTPUT, output);
    console.error(`Exported to: ${OUTPUT}`);
    console.log(output);
  } else {
    console.log(output);
  }
}

main();
