---
name: skylv-git-pruner
slug: skylv-git-pruner
version: 1.0.0
description: "Safely removes merged and stale Git branches. Identifies branches already on main/master. Triggers: clean branches, remove old branches, delete merged branches, git cleanup."
author: SKY-LV
license: MIT
tags: [git, cleanup, branch-management, devtools]
keywords: [git, branch, cleanup, prune, delete]
triggers: git pruner, clean branches, delete merged branches
---

# Git Branch Pruner

## Overview
Safely identifies and removes merged, stale, and orphaned Git branches.

## When to Use
- User asks to "clean up branches" or "delete merged branches"
- Branch list is too long to manage

## How It Works

### Step 1: Identify main branch
git branch --show-current
git remote show origin | findstr "HEAD branch"

### Step 2: List all branches
git branch -a --format "%(refname:short) %(upstream:short) %(committerdate:short)"

### Step 3: Categorize
Merged: already in main/master
Stale: no commit in 90+ days
Orphaned: no upstream tracking
Active: recent commits under 30 days

### Step 4: Safe deletion
1. Always show user what will be deleted first
2. Exclude protected branches: main, master, develop, release/*
3. Exclude branches with unpushed commits
4. Ask for confirmation before deletion

## Output Format
Merged branches (safe to delete):
  feature-old-login -> DELETE
  bugfix-typo-2024 -> DELETE

Protected (do not delete):
  main <- current
  develop

Commands: git branch -d (safe) or git branch -D (force)
Remote: git push origin --delete branch-name