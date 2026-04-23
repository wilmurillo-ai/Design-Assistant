<p align="center">
  <img src="./assets/icon.svg" width="120" height="120" alt="ShieldClaw Logo">
</p>

# ShieldClaw - Security Skill Suite for OpenClaw

> 🛡️ Protecting your OpenClaw environment like a shield, safeguarding user data and system security

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-200%2B%20passing-brightgreen.svg)](./)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./)

## ✨ Features

- 🔍 **Scan** - Security scanning for OpenClaw Skills, detecting potential risks
- 🛡️ **Guard** - Real-time behavior monitoring and interception
- 📊 **Audit** - Operation logging and security reporting
- 🔐 **Vault** - Sensitive data encryption and secure storage

## 🚀 Quick Start

### Requirements

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- OpenClaw >= 1.0.0

### Installation

```bash
# Install from ClawHub
claw install shieldclaw

# Or install via OpenClaw IDE
# Open Plugin Marketplace → Search "ShieldClaw" → Install
```

### Usage

```typescript
import { createCore, featureGate } from '@shieldclaw/core';

// Initialize ShieldClaw
const core = createCore({
  dbPath: './shieldclaw.db',
  logDir: './logs',
});

// Check feature availability
if (featureGate.check('scan.advanced').allowed) {
  // Perform advanced security scan
}
```

## 🏗️ Architecture

```
shieldclaw/
├── packages/
│   ├── core/           # Core foundation (types + shared services)
│   ├── scan/           # Scan plugin - Skill security scanning
│   ├── guard/          # Guard plugin - Real-time monitoring
│   ├── audit/          # Audit plugin - Logging and reporting
│   └── vault/          # Vault plugin - Sensitive data encryption
├── apps/
│   └── openclaw-integration/  # OpenClaw integration example
└── tests/              # Test suite
```

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/yourname/shieldclaw.git
cd shieldclaw

# Install dependencies
pnpm install

# Build all packages
pnpm run build

# Run tests
pnpm run test

# Development mode
pnpm run dev
```

## 📊 Test Coverage

- **Total Tests**: 200+
- **Core Module**: 68 tests
- **Scan Module**: 12 tests
- **Guard Module**: 20 tests
- **Audit Module**: 39 tests
- **Vault Module**: 61 tests

```bash
# Run specific module tests
pnpm run test:core
pnpm run test:scan
pnpm run test:guard
```

## 📖 Documentation

- [English Documentation](./docs/en/README.md)
- [中文文档](./docs/zh/README.md)
- [API Reference](./docs/api/README.md)
- [Changelog](./CHANGELOG.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

### Contributors

<a href="https://github.com/yourname/shieldclaw/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourname/shieldclaw" />
</a>

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenClaw](https://openclaw.io) - The IDE platform
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3) - SQLite wrapper
- [electron-store](https://github.com/sindresorhus/electron-store) - Configuration storage

## 📞 Support

- 💬 [Discussions](https://github.com/yourname/shieldclaw/discussions)
- 🐛 [Issue Tracker](https://github.com/yourname/shieldclaw/issues)
- 📧 Email: support@shieldclaw.io

## 🔗 Links

- 🌐 [Website](https://shieldclaw.io)
- 🛒 [ClawHub Marketplace](https://clawhub.io/plugins/shieldclaw)
- 🐦 [Twitter](https://twitter.com/shieldclaw)

---

<p align="center">
  Made with ❤️ by ShieldClaw Team
</p>
