#!/usr/bin/env node
// Postinstall: print copy instructions for supported agent platforms.
// Does not auto-write files — agents/operators choose where to place the skill.

if (process.env.npm_config_loglevel === "silent") process.exit(0);

const path = require("path");
const skillPath = path.join(__dirname, "SKILL.md");

console.log("\n@bankofbots/skill installed.");
console.log("Skill file: " + skillPath);
console.log("\nTo activate for your platform, copy the skill directory to:");
console.log("  Claude Code : .claude/skills/bankofbots/");
console.log("  OpenClaw    : ~/.openclaw/skills/bankofbots/");
console.log("\nQuick copy (from your project root):");
console.log("  cp -r node_modules/@bankofbots/skill/SKILL.md node_modules/@bankofbots/skill/references .claude/skills/bankofbots/");
console.log("\nOr read it programmatically:");
console.log('  require("@bankofbots/skill")  // returns { skillPath, referencesDir, content }');
console.log("");
