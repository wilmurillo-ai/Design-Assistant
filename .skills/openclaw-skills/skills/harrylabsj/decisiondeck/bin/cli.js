#!/usr/bin/env node

const DecisionDeck = require('../src/index.js');
const pkg = require('../package.json');

function parseArgs(argv) {
  const options = { _: [] };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (!arg.startsWith('-')) {
      options._.push(arg);
      continue;
    }

    const key = arg.replace(/^-+/, '');
    const next = argv[i + 1];
    const hasValue = typeof next !== 'undefined' && !next.startsWith('-');
    options[key] = hasValue ? next : true;
    if (hasValue) {
      i += 1;
    }
  }

  return options;
}

function printHelp() {
  console.log(`DecisionDeck ${pkg.version}

Usage:
  deck brief --file notes.md
  deck brief --text "..."
  deck compare --file options.md --options "方案A,方案B"
  deck conflicts --file materials.md
  deck kickoff --file research.md
  deck gaps --file research.md
  deck analyze --file research.md --json

Commands:
  brief             Produce the default one-page decision brief
  compare           Rank explicit or inferred options
  conflicts         Summarize where materials disagree
  kickoff           Turn materials into a kickoff-ready brief
  gaps              Surface the missing evidence that matters
  analyze           Return the distilled structure as JSON

Options:
  --file <path>     Read input from a file
  --text <text>     Read input from inline text
  --decision <txt>  Override the decision question
  --audience <txt>  Override the target reader, such as boss or client
  --options <csv>   Comma-separated option names
  --json            Print JSON output
  --help            Show this help
  --version         Show version
`);
}

function requireInput(options) {
  if (!options.file && !options.text) {
    throw new Error('Please provide --file or --text');
  }
}

function parseOptionList(raw) {
  if (!raw) {
    return [];
  }
  return String(raw)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function writeOutput(engine, result, asJson) {
  if (asJson) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }
  console.log(engine.render(result));
}

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];

  if (!command || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  if (command === '--version' || command === '-v') {
    console.log(pkg.version);
    return;
  }

  const options = parseArgs(argv.slice(1));
  const engine = new DecisionDeck();
  const shared = {
    decision: options.decision,
    audience: options.audience,
    options: parseOptionList(options.options)
  };

  try {
    switch (command) {
      case 'brief':
        requireInput(options);
        writeOutput(engine, engine.brief(options, shared), options.json);
        return;
      case 'compare':
        requireInput(options);
        writeOutput(engine, engine.compare(options, shared), options.json);
        return;
      case 'conflicts':
        requireInput(options);
        writeOutput(engine, engine.conflicts(options, shared), options.json);
        return;
      case 'kickoff':
        requireInput(options);
        writeOutput(engine, engine.kickoff(options, shared), options.json);
        return;
      case 'gaps':
        requireInput(options);
        writeOutput(engine, engine.gaps(options, shared), options.json);
        return;
      case 'analyze':
        requireInput(options);
        console.log(JSON.stringify(engine.analyze(options, shared), null, 2));
        return;
      default:
        throw new Error(`Unknown command: ${command}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
