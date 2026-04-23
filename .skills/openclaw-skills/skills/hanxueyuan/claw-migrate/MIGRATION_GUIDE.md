# claw-migrate v2.2.0 Migration Guide

**Version**: v2.2.0  
**Release Date**: 2026-03-15  
**Type**: Refactoring version (functionality compatible)

---

## 📋 Overview

v2.2.0 is a major refactoring version, main goals:
- Reduce code volume by 22%
- Reduce duplicate code by 75%
- Increase code reuse rate from 45% to 72%

**Important**: This version maintains backward functionality compatibility, but internal code structure has significant changes.

---

## 🔄 Major Changes

### 1. New Modules

The following modules are newly added, providing better code organization:

| Module | Purpose | Description |
|------|------|------|
| `src/auth.js` | Unified authentication | Token acquisition logic centralized management |
| `src/logger.js` | Unified logging | All log output unified format |
| `src/config-loader.js` | Configuration management | Configuration load/save/validate |
| `src/file-utils.js` | File utilities | File operation utility functions |
| `src/migration.js` | Migration logic | Migration logic extracted from index.js |
| `src/wizard.js` | Wizard utilities | Interactive wizard tools |
| `src/commands/*` | Command processing | Command processing logic split |

### 2. Module Refinement

The following modules have been refined, some functions moved to new modules:

| Module | Change | Migration Target |
|------|------|------|
| `src/index.js` | 553 lines → 210 lines | Command processing → `commands/` |
| `src/backup.js` | 240 lines → 155 lines | getToken → `auth.js` |
| `src/restore.js` | 175 lines → 125 lines | getToken → `auth.js` |
| `src/config-manager.js` | 259 lines → 220 lines | loadConfig → `config-loader.js` |
| `src/utils.js` | 105 lines → 95 lines | print* → `logger.js` |

### 3. API Changes

#### Internal API (Does not affect users)

| Original API | New Location | Impact Scope |
|--------|--------|----------|
| `utils.printHeader()` | `logger.printHeader()` | Internal modules |
| `utils.printSuccess()` | `logger.printSuccess()` | Internal modules |
| `utils.printError()` | `logger.printError()` | Internal modules |
| `utils.printWarning()` | `logger.printWarning()` | Internal modules |
| `utils.printInfo()` | `logger.printInfo()` | Internal modules |
| `utils.printProgress()` | `logger.printProgress()` | Internal modules |
| `backup.getToken()` | `auth.getToken()` | Internal modules |
| `restore.getToken()` | `auth.getToken()` | Internal modules |
| `config-manager.loadConfig()` | `config-loader.loadConfig()` | Internal modules |
| `config-manager.saveConfig()` | `config-loader.saveConfig()` | Internal modules |

#### User API (Fully Compatible)

Command line interface fully compatible, no changes needed:

```bash
# All commands remain unchanged
openclaw skill run claw-migrate setup
openclaw skill run claw-migrate backup
openclaw skill run claw-migrate restore
openclaw skill run claw-migrate config --edit
openclaw skill run claw-migrate scheduler --start
```

---

## 📦 Upgrade Steps

### For Regular Users

**No action required**, fully functionality compatible.

### For Developers/Contributors

1. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

2. **Install Dependencies** (if changed)
   ```bash
   npm install
   ```

3. **Run Tests**
   ```bash
   npm test
   ```

4. **Update Custom Scripts** (if any)
   
   If your code directly references internal modules, need to update imports:
   
   ```javascript
   // Old code
   const { printHeader } = require('./utils');
   const { getToken } = require('./backup');
   
   // New code
   const { printHeader } = require('./logger');
   const { getToken } = require('./auth');
   ```

---

## 🔍 Code Migration Reference

### Migrate from utils.js

```javascript
// Old: require('./utils')
const { printHeader, printSuccess, printError } = require('./utils');

// New: require('./logger')
const { printHeader, printSuccess, printError } = require('./logger');
```

### Migrate from backup.js/restore.js

```javascript
// Old: Instance method
const executor = new BackupExecutor(config);
const token = await executor.getToken();

// New: Standalone module
const { getToken } = require('./auth');
const token = await getToken(config);
```

### Migrate from config-manager.js

```javascript
// Old: Class method
const manager = new ConfigManager();
const config = await manager.loadConfig();

// New: Standalone module
const { loadConfig } = require('./config-loader');
const config = await loadConfig();
```

---

## 🧪 Test Verification

Run complete test suite to verify upgrade:

```bash
# Syntax check
npm run lint

# Run all tests
npm test

# Run specific tests
npm run test:backup
npm run test:restore
npm run test:config
```

**Expected Result**: All 92 test cases pass

---

## ⚠️ Known Issues

None. This version has been fully tested, functionality fully compatible with v2.1.x.

---

## 📞 Issue Feedback

If you encounter problems, please provide feedback via:

- **GitHub Issues**: https://github.com/hanxueyuan/claw-migrate/issues
- **Discussions**: https://github.com/hanxueyuan/claw-migrate/discussions

---

## 📚 Related Documentation

- [REFACTORING_REPORT.md](./REFACTORING_REPORT.md) - Detailed refactoring report
- [CODE_SIMPLIFICATION_REPORT.md](./CODE_SIMPLIFICATION_REPORT.md) - Code simplification review
- [README.md](./README.md) - Usage guide

---

**Last Updated**: 2026-03-15  
**Maintainer**: OpenClaw Team
