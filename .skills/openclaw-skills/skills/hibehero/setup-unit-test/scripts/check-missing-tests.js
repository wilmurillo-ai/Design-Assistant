#!/usr/bin/env node
/**
 * Checks if Git staged source files have corresponding unit test files.
 * Outputs source file paths missing tests (one per line) for use by the pre-commit hook.
 *
 * Usage: node check-missing-tests.js [project-dir]
 *
 * Logic:
 *   1. Get staged .ts/.tsx/.vue source files via git diff --cached.
 *   2. Exclude non-business files (test files, configurations, stories, etc.).
 *   3. Check if corresponding .test.ts/.test.tsx exists under tests/unit/.
 *   4. Output file paths missing tests.
 *
 * Exit Codes:
 *   0 — All files have tests (or no files need checking).
 *   1 — Missing tests found (paths output to stdout).
 */

import { execSync } from 'child_process'
import fs from 'fs'
import path from 'path'

const projectDir = path.resolve(process.argv[2] || process.cwd())

// Security Check: Validate directory
if (!fs.existsSync(projectDir) || !fs.statSync(projectDir).isDirectory()) {
  console.error('Error: Invalid project directory.')
  process.exit(1)
}

// Security Check: Verify Git environment
try {
  execSync('git rev-parse --is-inside-work-tree', { cwd: projectDir, stdio: 'ignore' })
} catch (e) {
  console.error('Error: Not a git repository.')
  process.exit(1)
}

// Get list of staged files (added and modified only)
function getStagedFiles() {
  try {
    const output = execSync('git diff --cached --name-only --diff-filter=ACM', {
      cwd: projectDir,
      encoding: 'utf-8',
    })
    return output.trim().split('\n').filter(Boolean)
  } catch {
    return []
  }
}

// Check if it's business source code requiring tests
function isBusinessSource(filePath) {
  // Only focus on files in the src/ directory
  if (!filePath.startsWith('src/')) return false

  // Only focus on .ts / .tsx / .vue files
  if (!/\.(ts|tsx|vue)$/.test(filePath)) return false

  // Exclude test files, stories, type definitions, and re-export index files
  const excludePatterns = [
    /\.test\./,
    /\.spec\./,
    /\.stories\./,
    /\.d\.ts$/,
    /\/index\.(ts|tsx)$/,  // Pure re-export index files
    /\/types\//,           // Type definition directories
    /\/constants\//,       // Constants directories (usually don't need tests)
  ]

  return !excludePatterns.some(p => p.test(filePath))
}

// Derive test file path from source path
// src/utils/format.ts → tests/unit/utils/format.test.ts
// src/components/Button.tsx → tests/unit/components/Button.test.tsx
function getTestFilePath(srcPath) {
  const relativePath = srcPath.replace(/^src\//, '')
  const ext = path.extname(relativePath)
  const withoutExt = relativePath.slice(0, -ext.length)

  // Use .test.ts for .vue files
  const testExt = ext === '.vue' ? '.test.ts' : `.test${ext}`
  return path.join('tests', 'unit', withoutExt + testExt)
}

// Main logic
const stagedFiles = getStagedFiles()
const businessFiles = stagedFiles.filter(isBusinessSource)

const missingTests = businessFiles.filter(srcFile => {
  const testFile = getTestFilePath(srcFile)
  const fullPath = path.join(projectDir, testFile)
  return !fs.existsSync(fullPath)
})

if (missingTests.length > 0) {
  missingTests.forEach(f => console.log(f))
  process.exit(1)
} else {
  process.exit(0)
}
