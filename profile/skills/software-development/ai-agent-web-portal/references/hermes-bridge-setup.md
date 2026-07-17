# Hermes Bridge Setup — Local Agent Integration

Route web portal chat through the machine's local Hermes agent so users reach the real sovereign intelligence, not just an API call.

## Prerequisites

- Hermes CLI installed (`which hermes`)
- Target profile configured with credentials (e.g., `thotheauphis`)
- Node.js server with `child_process` access

## Configuration

```bash
# .env
HERMES_BRIDGE=true
HERMES_PROFILE=thotheauphis  # profile the agent instance uses
```

## Server-Side Implementation

```javascript
const { spawn } = require('child_process');

async function callLocalHermes(text) {
  return new Promise((resolve, reject) => {
    const child = spawn('hermes', [
      'chat', '-q', text,
      '--source', 'web-portal',
      '--profile', process.env.HERMES_PROFILE || 'thotheauphis'
    ], {
      cwd: process.env.HOME,
      timeout: 120000,  // 2 min max — Hermes can take time
      env: { ...process.env, HERMES_NO_GATEWAY: '1' }
    });

    let output = '';
    let error = '';
    child.stdout.on('data', (d) => { output += d.toString(); });
    child.stderr.on('data', (d) => { error += d.toString(); });
    child.on('close', (code) => {
      if (code === 0 && output.trim()) {
        resolve(output.trim());
      } else if (output.trim()) {
        resolve(output.trim());  // partial output still useful
      } else {
        reject(new Error(`Hermes exit ${code}: ${error.slice(0, 200)}`));
      }
    });
    child.on('error', (e) => reject(e));
  });
}
```

## Integration Pattern (in message handler)

```javascript
if (harnessId === 'sovereign' && process.env.HERMES_BRIDGE === 'true') {
  try {
    const response = await callLocalHermes(text);
    return { content: response, model: 'local-hermes', provider: 'hermes' };
  } catch (e) {
    console.warn('Hermes bridge failed, falling back to API:', e.message);
    // Fall through to model router
  }
}
```

## Pitfalls

- **2-minute timeout is mandatory.** Hermes agent calls can take 30-120s depending on model and provider. Without a timeout, an unresponsive Hermes process hangs the HTTP request forever.
- **`HERMES_NO_GATEWAY=1` env var** prevents the spawned Hermes from trying to connect to the gateway (which would fail or cause a loop).
- **Profile must exist.** The `--profile` flag must match an existing profile in `~/.hermes/profiles/`. If the profile is missing or misconfigured, the spawn will fail silently.
- **Fallback is required.** Always catch Hermes bridge failures and fall through to the model router. The user should never see a timeout error.
- **Session isolation.** Each chat message spawns a fresh Hermes process. This is intentional — it isolates conversations and prevents context bleeding between portal users.
