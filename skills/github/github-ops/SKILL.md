---
name: github-ops
type: skill
description: "Complete GitHub operations: auth, repos, issues, PRs, code review, CI, releases — unified gh/curl workflows."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, gh-cli, REST-API, Git, Code-Review, CI/CD, Issues, PRs, Releases, Repositories]
    related_skills: [codebase-inspection, requesting-code-review]
---

# GitHub Operations (github-ops)

Complete GitHub workflow skill covering authentication, repository management, issues, pull requests, code review, CI/CD monitoring, and releases. All operations work with both `gh` CLI (when available) and `git` + `curl` (universal fallback).

## Table of Contents

1. [Authentication](#1-authentication)
2. [Repository Management](#2-repository-management)
3. [Issues Management](#3-issues-management)
4. [Pull Request Workflow](#4-pull-request-workflow)
5. [Code Review](#5-code-review)
6. [CI/CD & GitHub Actions](#6-cicd--github-actions)
7. [Releases](#7-releases)
8. [Reference Files](#8-reference-files)

---

## 1. Authentication

See `references/auth-setup.md` for complete setup guide covering:
- Git-only auth (HTTPS token, SSH keys) — no `gh` required
- gh CLI auth (interactive, token-based)
- Token extraction from git credentials / env
- Troubleshooting common auth issues

### Quick Auth Detection (use at start of any workflow)

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Extract token from env or git credentials
  if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
    export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
    export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\\([^@]*\\)@.*|\\1|')
  fi
fi
```

---

## 2. Repository Management

See `references/repo-management.md` for:
- Cloning (HTTPS, SSH, shallow, specific branch)
- Creating repos (user, org, from template, from local dir)
- Forking and keeping forks in sync
- Repo settings (visibility, topics, branch protection)
- Secrets management (GitHub Actions)
- GitHub Actions workflows (list, trigger, rerun, logs)
- Gists

---

## 3. Issues Management

See `references/issues-management.md` for:
- Viewing, searching, filtering issues
- Creating issues (bug reports, feature requests with templates)
- Managing labels, assignees, comments
- Closing/reopening with reasons
- Issue triage workflow
- Bulk operations

---

## 4. Pull Request Workflow

See `references/pr-workflow.md` for:
- Branch creation and naming conventions
- Conventional commits
- Creating PRs (gh + curl)
- Monitoring CI status
- Auto-fixing CI failures (loop pattern)
- Merging (squash, auto-merge)
- Complete workflow example

---

## 5. Code Review

See `references/code-review.md` for:
- Local pre-push review (git diff analysis)
- PR review on GitHub (checkout, diff, comments)
- Inline review comments (single and batch)
- Formal review submission (approve/request changes/comment)
- Review checklist (correctness, security, quality, testing, performance, docs)
- Review output template

---

## 6. CI/CD & GitHub Actions

See `references/ci-troubleshooting.md` for:
- Reading CI logs (gh + curl)
- Common failure patterns (tests, lint, types, build, auth, timeout, Docker)
- Auto-fix decision tree
- Re-running after fix

---

## 7. Releases

See `references/releases.md` for:
- Creating releases (draft, prerelease, generate notes)
- Uploading assets (binaries)
- Listing and downloading releases

---

## 8. Reference Files

This skill includes these support files:

### Scripts
- `scripts/gh-env.sh` — Auto-detects auth method, sets GH_* vars

### Templates
- `templates/bug-report.md`
- `templates/feature-request.md`
- `templates/pr-body-bugfix.md`
- `templates/pr-body-feature.md`
- `templates/review-output.md`

### References
- `references/auth-setup.md`
- `references/repo-management.md`
- `references/issues-management.md`
- `references/pr-workflow.md`
- `references/code-review.md`
- `references/ci-troubleshooting.md`
- `references/releases.md`
- `references/telegram-debug.md`
- `references/conventional-commits.md`
- `references/github-api-cheatsheet.md`