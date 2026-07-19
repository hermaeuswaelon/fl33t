# Dashboard Build Fix

**Problem:** `hermes dashboard` crashes immediately with `CancelledError` / `KeyboardInterrupt`  
**Root cause:** Web UI never built. No `dist/` directory to serve.

## Fix

```bash
cd /opt/hermes-agent/web
npm run build
```

Build output goes to `../hermes_cli/web_dist/` (NOT `web/dist/` — Vite's configured to output there).

**Output structure:**
```
hermes_cli/web_dist/
├── index.html          # 0.5 KB
├── favicon.ico         # 8.5 KB
├── fonts/              # 7 woff2 files ~290 KB
├── fonts-terminal/     # terminal font files
└── assets/
    ├── index-*.css     # 114 KB (18 KB gzipped)
    └── index-*.js      # 1,972 KB (564 KB gzipped)
```

## Verification

```bash
# Start
hermes dashboard --port 9120 --no-open

# Check HTTP
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9120/
# → 200

# Stop
hermes dashboard --stop
```

## Options

| Flag | When to use |
|------|------------|
| `--no-open` | Headless / automated / CI |
| `--skip-build` | After first successful build (saves 1s) |
| `--port 0` | Auto-assign port |
| `--isolated` | Per-profile server (not machine-level) |
| `--stop` | Kill all dashboard processes |

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `CancelledError` / `KeyboardInterrupt` | No web build | `npm run build` |
| Gateway websocket closed (1012) | Background process killed (SIGHUP from parent shell) | Keep parent alive or use systemd service |
| HTTP 404 on `/` | Build corrupted or stale | Rebuild: `npm run build` |
| Event loop stalled Ns | GIL pressure from heavy Python calls | Normal warning, not fatal |
