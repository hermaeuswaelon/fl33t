# Provider Configuration Reference

Provider configurations for the model router in `server.js`.

## DeepSeek

```javascript
{
  name: 'DeepSeek',
  base: 'https://api.deepseek.com/v1',
  models: {
    'deepseek-reasoner': { model: 'deepseek-reasoner', cost_per_1k: 0.00055 },
    'deepseek-chat': { model: 'deepseek-chat', cost_per_1k: 0.00027 },
    'deepseek-coder': { model: 'deepseek-coder', cost_per_1k: 0.00027 }
  }
}
// Auth: Bearer token via DEEPSEEK_API_KEY env var
```

**Pricing note:** DeepSeek is the cheapest premium provider (~$0.55/M input tokens for Reasoner). Excellent for reasoning-heavy harnesses like Sovereign and Watcher.

## OpenRouter

```javascript
{
  name: 'OpenRouter',
  base: 'https://openrouter.ai/api/v1',
  models: {
    'claude-sonnet': { model: 'anthropic/claude-sonnet-4', cost_per_1k: 0.003 },
    'claude-haiku': { model: 'anthropic/claude-3.5-haiku', cost_per_1k: 0.0008 },
    'gemini-pro': { model: 'google/gemini-2.0-pro-exp-02-05:free', cost_per_1k: 0 },
    'llama-3': { model: 'meta-llama/llama-3.3-70b-instruct', cost_per_1k: 0.00025 },
  }
}
// Auth: Bearer token via OPENROUTER_API_KEY
// Headers: include HTTP-Referer for ranking
```

**Notes:**
- The `:free` suffix on Gemini models means they route through the free tier. Rate limited.
- Always include `HTTP-Referer` header — OpenRouter uses it for rankings.
- `claude-sonnet-4` is the latest Sonnet as of mid-2026. Check `openrouter.ai/models` for current model names.

## xAI Grok

```javascript
{
  name: 'xAI Grok',
  base: 'https://api.x.ai/v1',
  models: {
    'grok-2': { model: 'grok-2-latest', cost_per_1k: 0.002 }
  }
}
// Auth: Bearer token via XAI_API_KEY
```

## Fallback Chain Design

Each model preference defines an ordered fallback chain. The primary model should be the best quality/cost ratio. Later entries should be cheaper or free-tier alternatives.

```javascript
const FALLBACK_CHAINS = {
  'deepseek-reasoner': [
    { provider: 'deepseek', model: 'deepseek-reasoner', key: () => process.env.DEEPSEEK_API_KEY },
    { provider: 'openrouter', model: 'claude-sonnet', key: () => process.env.OPENROUTER_API_KEY },
    { provider: 'openrouter', model: 'gemini-pro', key: () => process.env.OPENROUTER_API_KEY },
    { provider: 'grok', model: 'grok-2', key: () => process.env.XAI_API_KEY },
    { provider: 'openrouter', model: 'llama-3', key: () => process.env.OPENROUTER_API_KEY }
  ]
};
```

### Design Rules
1. **Primary should be your cheapest quality model** — the one you expect to handle 90%+ of traffic
2. **Free tiers go late in the chain** — they're rate-limited and unreliable; use them as last resort
3. **Each link has its own key() function** — lazy evaluation means missing keys just skip that link
4. **Log every failure** — `console.warn` is enough for debugging; real production should structured-log
5. **Timeout per model call at 30s** — a provider that hangs should not block the whole chain

## Hermes Bridge

When `HERMES_BRIDGE=true` in `.env`, the Sovereign harness routes through the local Hermes CLI:

```javascript
const child = spawn('hermes', [
  'chat', '-q', text,
  '--source', 'thotheauphis-ao-web',
  '--profile', 'thotheauphis'
], {
  cwd: process.env.HOME,
  timeout: 120000,
  env: { ...process.env, HERMES_NO_GATEWAY: '1' }
});
```

**Environment variable `HERMES_NO_GATEWAY=1`** — prevents the spawned Hermes from trying to start its own gateway process.

**Timeout of 120s** — Hermes agent responses can take 30-90s for complex reasoning tasks.

**CWD set to HOME** — Hermes reads config from `~/.hermes/`. Without this, it may use the server's working directory and find no profile.

**Fallback behavior** — if Hermes fails (timeout, exit code, no output), fall through to the API model router. Never let a Hermes failure block the user.

## Cost Model for Metering

```javascript
cost_per_msg = harness.base_cost * model.cost_multiplier
```

Recommended base costs per harness (in "credit units"):
- Sovereign: 5
- Oracle: 3
- Forge: 5
- Seer: 4
- Watcher: 6

Model cost multipliers (relative to base):
- deepseek-reasoner: 1.0
- deepseek-chat: 0.5
- deepseek-coder: 1.0
- claude-sonnet: 3.0
- grok-2: 2.5
- gemini-pro: 0 (free)
- llama-3: 0.5

**Admin bypass:** `user.role === 'admin'` skips all credit checks.
