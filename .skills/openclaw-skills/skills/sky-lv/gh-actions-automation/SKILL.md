---
name: skylv-github-actions-helper
slug: skylv-github-actions-helper
version: 1.0.0
description: "GitHub Actions workflow generator. Creates CI/CD pipelines for Node.js, Python, Docker. Triggers: github actions, ci cd, workflow, automate build, github ci."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: github-actions-helper
---

# GitHub Actions Helper

## Overview
Generates GitHub Actions workflows for continuous integration and deployment.

## When to Use
- User asks to "set up CI" or "add github actions"
- New project needs automated testing
- User wants to "deploy with github actions"

## How It Works

### Detect project type
Check for: package.json (Node), pyproject.toml (Python), Dockerfile (Docker).

## Node.js CI Template

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
      - run: npm test
```

## Python CI Template

```yaml
name: Python CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: pytest
```

## Tips
- Use actions/checkout@v4 not @v4.2.0
- Use npm ci not npm install for reproducibility
- Store secrets in GitHub Secrets
