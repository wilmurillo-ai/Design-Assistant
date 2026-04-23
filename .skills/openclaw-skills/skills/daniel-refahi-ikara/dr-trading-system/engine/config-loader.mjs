import fs from 'node:fs/promises';
import path from 'node:path';

function parseSimpleYaml(text) {
  const root = {};
  const stack = [{ indent: -1, container: root }];

  const parseScalar = (raw) => {
    const value = raw.trim();
    if (value === 'true') return true;
    if (value === 'false') return false;
    if (value === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
    return value;
  };

  const lines = text.split(/\r?\n/);

  for (let i = 0; i < lines.length; i += 1) {
    const original = lines[i];
    if (!original.trim() || original.trimStart().startsWith('#')) continue;

    const indent = original.match(/^\s*/)[0].length;
    const line = original.trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) stack.pop();
    const parent = stack[stack.length - 1].container;

    if (line.startsWith('- ')) {
      if (!Array.isArray(parent)) throw new Error(`Invalid YAML list placement at line ${i + 1}`);
      parent.push(parseScalar(line.slice(2)));
      continue;
    }

    const sep = line.indexOf(':');
    if (sep === -1) throw new Error(`Invalid YAML line ${i + 1}: ${line}`);

    const key = line.slice(0, sep).trim();
    const rest = line.slice(sep + 1).trim();

    if (rest) {
      parent[key] = parseScalar(rest);
      continue;
    }

    let nextNonEmpty = null;
    for (let j = i + 1; j < lines.length; j += 1) {
      if (!lines[j].trim() || lines[j].trimStart().startsWith('#')) continue;
      nextNonEmpty = lines[j];
      break;
    }

    const nextTrim = nextNonEmpty ? nextNonEmpty.trim() : '';
    const child = nextTrim.startsWith('- ') ? [] : {};
    parent[key] = child;
    stack.push({ indent, container: child });
  }

  return root;
}

async function readYaml(filePath) {
  const raw = await fs.readFile(filePath, 'utf8');
  return parseSimpleYaml(raw);
}

function assertFields(obj, fields, kind) {
  for (const field of fields) {
    if (!(field in obj)) throw new Error(`${kind} missing required field: ${field}`);
  }
}

export async function loadRuntimeConfig({ rootDir, jobId }) {
  const jobsDir = path.join(rootDir, 'jobs');
  const jobPath = path.join(jobsDir, `${jobId}.yml`);
  const job = await readYaml(jobPath);
  assertFields(job, ['job_id', 'watchlist_id', 'strategy', 'risk', 'schedule'], 'job');

  const watchlistPath = path.join(rootDir, 'watchlists', `${job.watchlist_id}.yml`);
  const watchlist = await readYaml(watchlistPath);
  assertFields(watchlist, ['watchlist_id', 'symbols', 'market'], 'watchlist');

  const strategyId = job.strategy?.strategy_id;
  const strategyVersion = job.strategy?.strategy_version;
  if (!strategyId || !strategyVersion) throw new Error('job.strategy missing strategy_id or strategy_version');

  const strategyPath = path.join(rootDir, 'strategies', `${strategyId}_${strategyVersion}.yml`);
  const strategy = await readYaml(strategyPath);
  assertFields(strategy, ['strategy_id', 'version', 'entry', 'exit', 'position_sizing'], 'strategy');

  const templateId = job.reporting?.report_template_id;
  const templatePath = templateId ? path.join(rootDir, 'templates', `${templateId}.yml`) : null;
  const reportTemplate = templatePath ? await readYaml(templatePath) : null;

  return {
    rootDir,
    jobId,
    paths: { jobPath, watchlistPath, strategyPath, templatePath },
    job,
    watchlist,
    strategy,
    reportTemplate
  };
}
