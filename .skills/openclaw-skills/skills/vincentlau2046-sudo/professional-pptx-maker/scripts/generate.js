#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

class ProfessionalPPTXMaker {
  constructor(options = {}) {
    this.options = options;
    this.inputFile = options.input;
    this.outputFile = options.output;
    this.templateFile = options.template;
    this.theme = options.theme || 'finance';
    this.dryRun = options.dryRun || false;
    this.projectDir = options.projectDir || 'pptx_project';
  }

  run() {
    try {
      if (!this.inputFile) throw new Error('--input is required');
      if (!this.outputFile) throw new Error('--output is required');
      
      const args = ['--input', this.inputFile, '--output', this.outputFile];
      
      if (this.templateFile) args.push('--template', this.templateFile);
      if (this.theme) args.push('--theme', this.theme);
      if (this.dryRun) args.push('--dry-run');
      if (this.projectDir) args.push('--project-dir', this.projectDir);
      
      const pythonScript = path.join(__dirname, '../main.py');
      console.log(`🚀 Professional PPTX Maker - agent-slides core implementation`);
      console.log(`📄 Input: ${this.inputFile}`);
      console.log(`💾 Output: ${this.outputFile}`);
      
      execFileSync('python3', [pythonScript, ...args], {
        stdio: 'inherit',
        cwd: path.dirname(pythonScript)
      });
      
    } catch (error) {
      console.error(`❌ Professional PPTX generation failed: ${error.message}`);
      process.exit(1);
    }
  }
}

function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: professional-pptx-maker --input <file> --output <file.pptx>');
    console.log('Options:');
    console.log('  --template <file.pptx>    Custom template file');
    console.log('  --theme <finance|tech>    Theme (default: finance)');
    console.log('  --dry-run                Validate without generating PPTX');
    console.log('  --project-dir <dir>      Project directory (default: pptx_project)');
    process.exit(1);
  }
  
  const options = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--input') options.input = args[++i];
    else if (arg === '--output') options.output = args[++i];
    else if (arg === '--template') options.template = args[++i];
    else if (arg === '--theme') options.theme = args[++i];
    else if (arg === '--dry-run') options.dryRun = true;
    else if (arg === '--project-dir') options.projectDir = args[++i];
  }
  
  new ProfessionalPPTXMaker(options).run();
}

if (require.main === module) main();