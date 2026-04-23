# readme-badges

Generate beautiful badge strings (Shields.io) for GitHub READMEs. Natural language input, instant output.

## Usage

```
Generate badges for my GitHub README: [list features/stats]
Add a build status badge for GitHub Actions
Add a license badge
Generate badges showing: Python 3.11, PyPI downloads, test coverage
```

## What it does

Generates Shields.io badge URLs and markdown embed code from plain English descriptions. Supports:

- **GitHub Actions** — build, test, deploy status
- **Package registries** — PyPI, npm, crates.io, Maven
- **Code quality** — coverage, code size, license
- **Social** — GitHub stars, forks, watchers
- **Dynamic** — any Shields.io custom badge

## Examples

| Input | Output |
|-------|--------|
| "build passing for GitHub Actions" | `![Build](https://github.com/user/repo/actions/workflows/ci.yml/badge.svg)` |
| "PyPI version and downloads" | `![PyPI](https://img.shields.io/pypi/v/package.svg)` |
| "license MIT" | `![License](https://img.shields.io/badge/license-MIT-blue.svg)` |
| "npm downloads" | `![npm](https://img.shields.io/npm/dm/package.svg)` |

## Features

- Auto-detects platform (GitHub Actions, PyPI, npm, etc.)
- Generates raw markdown + HTML output
- Copy-paste ready
- Preview URLs so you can verify before using

## Notes

- Uses shields.io (free, no API key needed)
- Supports custom colors, labels, badges
- For GitHub Actions badges, you need the workflow filename
