# Contributing

Thanks for contributing to ClawRecipes. This guide helps you get set up and run the project tooling.

## Prerequisites

- **Node 20+**
- **OpenClaw** (optional; needed only for smoke tests)

## Setup

```bash
git clone https://github.com/JIGGAI/ClawRecipes.git
cd ClawRecipes
npm ci
```

Run `npm ci` first. It runs the `prepare` script (husky), so pre-commit hooks are installed automatically.

## Commands

| Command | Description |
|---------|-------------|
| `npm test` | Unit tests (vitest) |
| `npm run test:coverage` | Coverage report; thresholds in `vitest.config.ts` (60% lines/statements, 90% functions, 65% branches) |
| `npm run smell-check` | ESLint, jscpd, pattern checks (`scripts/smell-check.mjs`) |
| `npm run lint` | ESLint on src/ and index.ts |
| `npm run lint:fix` | ESLint with auto-fix |
| `npm run test:smoke` | Scaffold smoke (optional; requires OpenClaw and workspace config) |
| `npx vitest run tests/workspace.test.ts` | Run a single test file |

## Pre-commit

Husky runs on commit:

1. **lint-staged**: ESLint on staged `.ts` files
2. **npm test**: Full test suite

Docs-only commits skip lint-staged but still run tests.

## CI

`.github/workflows/ci.yml` runs on push/PR to `main` and `feature/*`:

- `npm ci`
- `npm audit --audit-level=high` (continue-on-error)
- `npm run test:coverage`
- `npm run smell-check`

## Making changes

Before opening a PR:

1. Run `npm test`
2. Run `npm run smell-check`

## Fork workflow

If you're contributing from a fork:

1. Fork the repo on GitHub
2. Clone your fork
3. Create a branch (`git checkout -b feature/your-feature`)
4. Make changes, run tests and smell-check
5. Push and open a PR to `main`

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for codebase structure, handler map, and data flow.
