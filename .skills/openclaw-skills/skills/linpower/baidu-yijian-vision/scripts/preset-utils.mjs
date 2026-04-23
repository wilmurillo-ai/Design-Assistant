#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

/**
 * preset-utils.mjs — Shared utilities for preset skills management
 */

// ---------------------------------------------------------------------------
// Preset skills file operations
// ---------------------------------------------------------------------------

/**
 * Write preset-skills.json
 * @param {object} data - Full preset data { version, description, lastUpdated, presetSkills }
 * @param {string} presetPath - Path to preset-skills.json
 */
export function writePresets(data, presetPath) {
  // Ensure directory exists
  fs.mkdirSync(path.dirname(presetPath), { recursive: true });
  fs.writeFileSync(presetPath, JSON.stringify(data, null, 2) + '\n');
}

/**
 * Read preset-skills.json
 * @param {string} presetPath - Path to preset-skills.json
 * @returns {object} Preset data
 */
export function readPresets(presetPath) {
  if (!fs.existsSync(presetPath)) {
    return {
      version: '1.0',
      description: 'Yijian preset skills library',
      lastUpdated: new Date().toISOString().split('T')[0],
      presetSkills: []
    };
  }
  try {
    return JSON.parse(fs.readFileSync(presetPath, 'utf-8'));
  } catch (err) {
    console.error(`Warning: Failed to read presets: ${err.message}`);
    return {
      version: '1.0',
      description: 'Yijian preset skills library',
      lastUpdated: new Date().toISOString().split('T')[0],
      presetSkills: []
    };
  }
}

// ---------------------------------------------------------------------------
// User registered skills file operations (skill.json)
// ---------------------------------------------------------------------------

/**
 * Write skill.json
 * @param {object} data - Full skill.json data { name, version, tools }
 * @param {string} skillPath - Path to skill.json
 */
export function writeSkill(data, skillPath) {
  // Ensure directory exists
  fs.mkdirSync(path.dirname(skillPath), { recursive: true });
  fs.writeFileSync(skillPath, JSON.stringify(data, null, 2) + '\n');
}

/**
 * Read skill.json
 * @param {string} skillPath - Path to skill.json
 * @returns {object} Skill data
 */
export function readSkill(skillPath) {
  if (!fs.existsSync(skillPath)) {
    return { name: 'yijian-register', version: '0.5.0', tools: [] };
  }
  try {
    return JSON.parse(fs.readFileSync(skillPath, 'utf-8'));
  } catch (err) {
    console.error(`Warning: Failed to read skill.json: ${err.message}`);
    return { name: 'yijian-register', version: '0.5.0', tools: [] };
  }
}
