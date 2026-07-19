---
name: github
description: "GitHub workflow skills — auth, PRs, issues, code review, repo management, codebase inspection"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Git, Pull-Requests, Code-Review, Issues, Repositories, CI-CD, Authentication]
    related_skills: []
---

# GitHub Umbrella Skill

Consolidated skill for all GitHub operations. Absorbs: github-auth, github-code-review, github-issues, github-pr-workflow, github-repo-management, codebase-inspection.

## Contents

1. [Authentication Setup](#1-authentication-setup)
2. [Pull Request Workflow](#2-pull-request-workflow)
3. [Code Review](#3-code-review)
4. [Issues Management](#4-issues-management)
5. [Repository Management](#5-repository-management)
6. [Codebase Inspection](#6-codebase-inspection)
7. [CI/CD & Actions](#7-cicd--actions)

---

## 1. Authentication Setup

### Detection Flow

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → use `gh` for everything
2. If `gh` is installed but not authenticated → authenticate via browser or token
3. If `gh` is not installed → use `git` + `curl` with a personal access token

### Token-Based API Access

```bash
# Export token
export GITHUB_TOKEN="<token>"

# Or extract from git credentials
if [ -z "$GITHUB_TOKEN" ]; then
  if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
    GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
    GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  fi
fi
```

### Helper: Detect Auth Method

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
fi
```

### Extract Owner/Repo

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 2. Pull Request Workflow

### Branch Creation

```bash
git fetch origin
git checkout main && git pull origin main
git checkout -b feat/description
```

Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `ci/` prefixes.

### Commits

```bash
git add <files>
git commit -m "type(scope): short description"
```

### Push and Create PR

**With gh:**
```bash
git push -u origin HEAD
gh pr create --title "feat: ..." --body "## Summary\n..." [--draft]
```

**With curl:**
```bash
BRANCH=$(git branch --show-current)
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{\"title\": \"...\", \"head\": \"$BRANCH\", \"base\": \"main\"}"
```

### Merging

**With gh:**
```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch
```

**With curl:**
```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d '{"merge_method": "squash"}'
```

---

## 3. Code Review

### Review Local Changes

```bash
git diff main...HEAD --stat
git diff main...HEAD
git diff main...HEAD --name-only
git log main..HEAD --oneline
```

### Check for Common Issues

```bash
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|debugger"
git diff main...HEAD | grep -in "password\|secret\|api_key\|token.*="
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

### Review a Pull Request

**With gh:** `gh pr view 123`, `gh pr diff 123`, `gh pr checkout 123`
**With curl:** Fetch from `/repos/$OWNER/$REPO/pulls/$PR_NUMBER`

### Leave Review

**With gh:** `gh pr review 123 --approve --body "LGTM!"`
**With curl:** POST to `/repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews`

### Review Checklist

- **Correctness**: Edge cases, error paths, does it do what it claims?
- **Security**: No hardcoded secrets, SQL injection, XSS, path traversal
- **Code Quality**: Clear naming, single responsibility, DRY
- **Testing**: Happy path + error cases covered
- **Performance**: No N+1 queries, unnecessary loops
- **Documentation**: Public APIs documented, non-obvious logic explained

---

## 4. Issues Management

### Viewing Issues

**With gh:** `gh issue list`, `gh issue list --label "bug"`, `gh issue view 42`
**With curl:** `GET /repos/$OWNER/$REPO/issues?state=open`

### Creating Issues

```bash
gh issue create --title "..." --body "..." --label "bug" --assignee "username"
```

### Managing Issues

| Action | gh | curl endpoint |
|--------|-----|--------------|
| Add labels | `gh issue edit N --add-label "bug"` | `POST /repos/{o}/{r}/issues/N/labels` |
| Assign | `gh issue edit N --add-assignee user` | `POST /repos/{o}/{r}/issues/N/assignees` |
| Comment | `gh issue comment N --body "..."` | `POST /repos/{o}/{r}/issues/N/comments` |
| Close | `gh issue close N` | `PATCH /repos/{o}/{r}/issues/N` |
| Search | `gh issue list --search "..."` | `GET /search/issues?q=...` |

### Templates

Bug reports and feature request templates available from the original skill's templates directory.

---

## 5. Repository Management

### Cloning

```bash
git clone https://github.com/owner/repo.git
gh repo clone owner/repo
```

### Creating Repositories

```bash
gh repo create my-project --public --clone
# Or via curl:
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos -d '{"name": "my-project"}'
```

### Forking

```bash
gh repo fork owner/repo --clone
```

### Branch Protection

```bash
curl -s -X PUT -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/branches/main/protection \
  -d '{"required_status_checks": {"strict": true, "contexts": ["ci/test"]}}'
```

### Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
```

### Secrets Management

```bash
gh secret set API_KEY --body "your-secret-value"
```

### Gists

```bash
gh gist create script.py --public --desc "Useful script"
```

---

## 6. Codebase Inspection

Use `pygount` for lines-of-code analysis, language breakdown, and code-vs-comment ratios.

### Prerequisites

```bash
pip install pygount --break-system-packages -q 2>/dev/null || pip install pygount
```

### Basic Summary

```bash
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,dist,build" \
  /path/to/repo
```

### Filter by Language

```bash
pygount --suffix=py --format=summary .
pygount --suffix=py,yaml,yml --format=summary .
```

### Common Folder Exclusions

- Python: `.git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs`
- JS/TS: `.git,node_modules,dist,build,.next,.cache,.turbo,coverage`

### Output Formats

- `--format=summary` — Language, file count, code lines, comment lines, percentage
- `--format=json` — Machine-readable JSON

### Interpreting Results

Columns: **Language**, **Files**, **Code**, **Comment**, **%**
Pseudo-languages: `__empty__`, `__binary__`, `__generated__`, `__duplicate__`, `__unknown__`

---

## 7. CI/CD & Actions

### List and Monitor Workflows

```bash
gh workflow list
gh run list --limit 10
gh run view <RUN_ID>
gh run view <RUN_ID> --log-failed
```

### Re-run Workflows

```bash
gh run rerun <RUN_ID>
gh run rerun <RUN_ID> --failed
```

### Trigger Workflow

```bash
gh workflow run ci.yml --ref main
gh workflow run deploy.yml -f environment=staging
```

### Via curl:

```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows \
  | python3 -c "import sys, json; [print(f\"  {w['name']}\") for w in json.load(sys.stdin)['workflows']]"
```

---

## Quick Reference

| Action | gh | curl (endpoint) |
|--------|-----|-----------------|
| View PR | `gh pr view N` | `GET /repos/{o}/{r}/pulls/N` |
| Create PR | `gh pr create` | `POST /repos/{o}/{r}/pulls` |
| Review PR | `gh pr review N` | `POST /repos/{o}/{r}/pulls/N/reviews` |
| List issues | `gh issue list` | `GET /repos/{o}/{r}/issues` |
| Create issue | `gh issue create` | `POST /repos/{o}/{r}/issues` |
| Create repo | `gh repo create` | `POST /user/repos` |
| Fork repo | `gh repo fork` | `POST /repos/{o}/{r}/forks` |
| Create release | `gh release create` | `POST /repos/{o}/{r}/releases` |
| Set secret | `gh secret set` | `PUT /repos/{o}/{r}/actions/secrets/{key}` |
| Workflow runs | `gh run list` | `GET /repos/{o}/{r}/actions/runs` |
| Codebase LOC | `pygount --format=summary` | n/a (local) |
| Auth check | `gh auth status` | `GET /user` |
