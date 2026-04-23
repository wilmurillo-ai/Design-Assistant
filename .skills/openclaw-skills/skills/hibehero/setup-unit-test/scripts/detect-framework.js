#!/usr/bin/env node
/**
 * Detects frontend project info like framework, language, package manager, etc.
 * Outputs JSON: { framework, typescript, packageManager, hasVitest, hasMSW, hasTestingLibrary }
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

function detectFramework(projectDir) {
  const result = {
    framework: 'unknown',
    typescript: false,
    packageManager: 'npm',
    hasVitest: false,
    hasMSW: false,
    hasTestingLibrary: false,
  }

  const pkgPath = path.join(projectDir, 'package.json')
  if (!fs.existsSync(pkgPath)) {
    return result
  }

  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'))
  const allDeps = {
    ...pkg.dependencies,
    ...pkg.devDependencies,
  }

  // Detect Framework
  if (allDeps['react'] || allDeps['react-dom'] || allDeps['next']) {
    result.framework = 'react'
  } else if (allDeps['vue'] || allDeps['nuxt']) {
    result.framework = 'vue'
  }

  // Detect TypeScript
  if (allDeps['typescript'] || fs.existsSync(path.join(projectDir, 'tsconfig.json'))) {
    result.typescript = true
  }

  // Detect Package Manager
  if (fs.existsSync(path.join(projectDir, 'pnpm-lock.yaml'))) {
    result.packageManager = 'pnpm'
  } else if (fs.existsSync(path.join(projectDir, 'yarn.lock'))) {
    result.packageManager = 'yarn'
  } else {
    result.packageManager = 'npm'
  }

  // Detect existing testing tools
  result.hasVitest = 'vitest' in allDeps
  result.hasMSW = 'msw' in allDeps
  result.hasTestingLibrary = Object.keys(allDeps).some(k => k.startsWith('@testing-library/'))

  return result
}

const projectDir = path.resolve(process.argv[2] || process.cwd())

// Security Check: Ensure projectDir is a valid directory
if (!fs.existsSync(projectDir) || !fs.statSync(projectDir).isDirectory()) {
  console.error('Error: Invalid project directory.')
  process.exit(1)
}

const result = detectFramework(projectDir)
console.log(JSON.stringify(result, null, 2))
