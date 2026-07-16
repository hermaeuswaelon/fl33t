# Universal State Reconstruction

## Overview

Reconstruct the complete sovereign state from anywhere using GitHub or Vercel.

## Sources

| Source | URL | Speed |
|--------|-----|-------|
| GitHub Raw | `raw.githubusercontent.com/hermaeuswaelon/fl33t/main/{path}` | Fast |
| Vercel API | `fl33t.vercel.app/api/state?format=full` | Medium |
| GitHub API | `api.github.com/repos/hermaeuswaelon/fl33t/contents/{path}` | Slowest |

## Vercel API Endpoints

| Endpoint | Parameters | Response |
|----------|------------|----------|
| `GET /api/state` | `format=full\|minimal`, `commit=<sha>` | JSON with all state files |
| `GET /api/reconstruct` | — | Full reconstruction payload |

## Reconstruction Manifest (22 files)

| Category | Files |
|----------|-------|
| Identity | `all.txt`, 5 manifests, SOUL.md |
| Config | `config.yaml` |
| Pipeline | 17 Python/system files from `work/` |
| Scripts | `fl33t-backup.sh`, `identity-integrity-check.sh` |
| Fleet | `README.md`, `ANNOUNCEMENT.md`, `vercel.json` |

## Usage

```bash
# From any machine, any OS:
python3 sovereign_state_reconstruct.py                     # default: GitHub
python3 sovereign_state_reconstruct.py --from vercel        # Vercel API
python3 sovereign_state_reconstruct.py --output ~/state     # custom dir
python3 sovereign_state_reconstruct.py --verify-only        # integrity check
```

## State File Format

```json
{
  "timestamp": "2026-07-15T23:00:00Z",
  "commit": "<sha>",
  "repo": "hermaeuswaelon/fl33t",
  "files": 22,
  "state": {
    "identity/all.txt": "<content>",
    "profile/SOUL.md": "<content>",
    ...
  }
}
```

## Vercel Deployment

```bash
# Connect repo to Vercel:
# https://vercel.com/import?url=https://github.com/hermaeuswaelon/fl33t
#
# Or via CLI:
# vercel deploy --prod --token <token>
#
# Set GITHUB_TOKEN env var in Vercel for authenticated API access
```

## Fallback Order

1. Try Vercel API (fastest)
2. Fall back to GitHub raw
3. Fall back to GitHub API (authenticated)
