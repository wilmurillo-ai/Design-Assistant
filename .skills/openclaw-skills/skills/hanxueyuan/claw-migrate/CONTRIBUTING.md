# Contributing to claw-migrate

Welcome to contribute to the claw-migrate project!

## 🚀 Quick Start

### Development Environment Setup

```bash
# Clone repository
git clone https://github.com/hanxueyuan/claw-migrate.git
cd claw-migrate

# Install dependencies
npm install

# Run tests
npm test

# Run code linting
npm run lint
```

## 📝 Commit Conventions

We use [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `style:` Code style adjustment
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool configuration

### Examples

```bash
git commit -m "feat: add batch migration support"
git commit -m "fix: fix GitHub API authentication issue"
git commit -m "docs: update README usage examples"
```

## 🧪 Testing Requirements

All PRs must:
- ✅ Pass all existing tests
- ✅ Add test cases for new features
- ✅ Not reduce code coverage

### Run Tests

```bash
# Run all tests
npm test

# Run single test file
node tests/merger.test.js
```

## 📋 Code Review Checklist

Please confirm before submitting PR:

- [ ] Code passes lint check
- [ ] All tests pass
- [ ] Added necessary documentation
- [ ] Updated CHANGELOG.md (if applicable)
- [ ] Followed code style guidelines

## 🔧 Development Flow

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 💬 Issue Feedback

Encountering problems? Please create an [Issue](https://github.com/hanxueyuan/claw-migrate/issues)

---

Thank you for your contribution! 🎉
