# ⧉ Warp (Oz) API Key — Where to Get It ⧉

The user needs a `wk-xxx` token for `WARP_API_KEY` env var (Oz CLI/API auth).
This is **NOT** the same as BYOK model keys (OpenAI/Anthropic keys for model inference).

## Three Methods to Create a Key

### 1. 🌐 Oz Web App (recommended, no desktop app needed)
1. Go to [oz.warp.dev](https://oz.warp.dev)
2. Click **"Login with Warp"** → authenticate via GitHub (user already has an account)
3. Navigate to Settings → Cloud Platform → Oz Cloud API Keys
   (or try `/settings/api-keys` path after login)
4. Click **+ Create API Key**
5. Scope: **Personal** (runs as the user, uses their GitHub permissions)
6. Name: something descriptive (e.g., `"aethelgard"`, `"hermes-bridge"`)
7. Expiration: **Never** (or 90d if rotating)
8. **COPY THE KEY IMMEDIATELY** — it is shown once and never retrievable
9. Format: `wk-xxx...`

### 2. 🖥️ Warp Desktop App (if installed)
Settings → Cloud platform → Oz Cloud API Keys → + Create API Key
(same flow as web app)

### 3. ⌨️ Oz CLI (if `oz` is installed)
```bash
# First authenticate
oz login
# Then create key (prints once)
oz api-key create "aethelgard" --no-expiration
```

## Usage
```bash
export WARP_API_KEY="wk-xxx..."
oz agent run --prompt "hello"
```

## Key Caveats
- Format is always `wk-...` — if it doesn't start with `wk-`, it's the wrong thing
- Personal keys use the **user's GitHub permissions** and credit pool
- Agent keys run as a cloud agent scoped to a team
- **Cannot be retrieved after creation** — store in password manager or `.env`
- Delete via: `oz api-key expire <name> --force`

## Distinction from BYOK
| Credential | Format | Purpose | Where to Set |
|-----------|--------|---------|-------------|
| `WARP_API_KEY` | `wk-xxx` | Oz CLI/API authentication | Env var or `--api-key` flag |
| BYOK model key | `sk-...` (OpenAI) | Model inference provider auth | Warp Settings → AI → Manage models |
