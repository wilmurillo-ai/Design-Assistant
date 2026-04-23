const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
function arg(name) { const i = process.argv.indexOf(name); return i >= 0 ? process.argv[i + 1] : null; }
const skillDir = path.resolve(arg('--skill'));
const outPath = path.resolve(arg('--out'));
const skillFile = path.join(skillDir, 'SKILL.md');
const issues = [];
if (!fs.existsSync(skillFile)) issues.push('missing_SKILL_md');
let frontmatter = {};
if (fs.existsSync(skillFile)) {
  const text = fs.readFileSync(skillFile, 'utf8').replace(/^\uFEFF/, '');
  const m = text.match(/^---\n([\s\S]*?)\n---/);
  if (!m) issues.push('missing_frontmatter');
  else {
    for (const line of m[1].split(/\r?\n/)) {
      const idx = line.indexOf(':');
      if (idx > 0) frontmatter[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
}
const folderName = path.basename(skillDir);
if (frontmatter.name && frontmatter.name !== folderName) issues.push('folder_name_mismatch');
if (!frontmatter.name) issues.push('missing_name');
if (!frontmatter.description || frontmatter.description.length < 40) issues.push('description_too_weak');
const clutter = ['README.md','CHANGELOG.md','INSTALL.md','INSTALLATION_GUIDE.md','QUICK_REFERENCE.md'].filter(f => fs.existsSync(path.join(skillDir, f)));
if (clutter.length) issues.push(`clutter_files:${clutter.join(',')}`);
const scriptDir = path.join(skillDir, 'scripts');
const syntax = [];
if (fs.existsSync(scriptDir)) {
  for (const file of fs.readdirSync(scriptDir)) {
    if (!file.endsWith('.js')) continue;
    const res = spawnSync(process.execPath, ['--check', path.join(scriptDir, file)], { encoding: 'utf8' });
    if (res.status !== 0) syntax.push(file);
  }
}
if (syntax.length) issues.push(`script_syntax_fail:${syntax.join(',')}`);
const result = { ok: issues.length === 0, skill: skillDir, issues, folderName, frontmatter, checkedScripts: fs.existsSync(scriptDir) ? fs.readdirSync(scriptDir).filter(f=>f.endsWith('.js')).length : 0 };
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(result, null, 2), 'utf8');
process.stdout.write(JSON.stringify(result, null, 2) + '\n');
