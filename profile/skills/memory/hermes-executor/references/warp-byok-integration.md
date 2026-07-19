# Warp BYOK & Integration Reference

> Source: Scraped from docs.warp.dev (July 18, 2026). Full docs cache: ~/.hermes/profiles/thotheauphis/cache/web/docs.warp.dev-aff219a576.md (342K chars)

## BYOK (Bring Your Own Key) — Core Architecture

**What it is:** Connect OpenAI/Anthropic/Google API keys to Warp's agent harness. Keys stored **locally** in OS keychain, never on Warp's servers. Agent harness still runs server-side.

**Availability:** Free + all paid plans (since May 21, 2026). Constraint: individuals & orgs ≤10 employees. Larger need Business/Enterprise.

### Flow
1. Local client pulls key from OS keychain → sends to Warp backend with prompt
2. Warp's backend assembles full request (system prompt, context, tools)
3. Uses **your key in-flight** to call provider → response streams back
4. Warp **never stores** the key — ephemeral in-flight only

### Supported Providers (BYOK)
| Provider | Auth | Models Available |
|----------|------|-----------------|
| OpenAI | API key (OS keychain) | GPT-5.x series (GPT-5.6 Sol/Terra/Luna, GPT-5.5, GPT-5.4, GPT-5.3/5.2 Codex) |
| Anthropic | API key (OS keychain) | Claude Fable 5, Sonnet 5, Opus 4.8/4.7/4.6/4.5, Sonnet 4.6/4.5, Haiku 4.5 |
| Google | API key (OS keychain) | Gemini 3.1 Pro, Gemini 3.5 Flash |
| xAI/Grok | SuperGrok subscription (browser auth) | Grok 4.5, Grok 4.3, Grok Build 0.1 |

### Critical Behavior
- **Auto models** (Auto/Responsive/Cost-efficient/Genius/Open-weights) ALWAYS consume Warp credits even with BYOK — must manually select a specific provider model
- **Default failover:** No fallback to Warp credits if BYOK fails. Optional toggle to enable Warp-credit fallback
- **ZDR:** Warp's ZDR doesn't extend to your provider account when using BYOK — check provider's retention terms
- **Cloud Agents:** BYOK does NOT work with cloud agents (keys are local-only)
- **Platform credits:** On Business/Enterprise, local BYOK runs consume platform credits (billing starts Jul 1, 2026 on self-serve plans)

### Enabling BYOK
Settings → search "API keys" → add key for provider → key icon appears next to supported models in model picker.

## Custom Inference Endpoints

Route Warp's agents through **any OpenAI-compatible endpoint**. Available on Free + all paid.

### Supported Destinations
| Target | Use Case |
|--------|----------|
| OpenRouter | Multi-provider aggregation behind one OpenAI-compatible API |
| LiteLLM | Self-hosted proxy, unified API across providers |
| z.ai | Direct provider with OpenAI-compatible surface |
| Internal gateways | Corporate AI gateways (MUST be at public URL) |
| Local models via tunnel | Ollama/LM Studio/vLLM + ngrok/Cloudflare Tunnel |

**Network requirement:** Endpoint MUST be at public HTTPS URL. No localhost/private IP. Use ngrok for local models.

### Configuration
Settings → search "inference endpoint" → add base URL + API key + model IDs → custom models appear in model picker.

## OSS Build Config Paths (Linux)

| Bucket | Path |
|--------|------|
| Settings file | `~/.config/warp-terminal/settings.toml` (stable) or `~/.config/warp-terminal-preview/settings.toml` (preview) |
| OSS settings | `~/.warp-oss/` (channel-suffixed — separate from stable) |
| Portable data | `${XDG_DATA_HOME:-$HOME/.local/share}/warp-terminal/` (themes, tab configs, workflows) |
| Non-portable state | `${XDG_STATE_HOME:-$HOME/.local/state}/warp-terminal/` (logs, DB, codebase index) |
| MCP config | `~/.warp/.mcp.json` |
| Skills | `~/.warp/skills/` |
| Agent config | `~/.agents/` |
| Settings schema | `/opt/warpdotdev/warp-terminal/resources/settings_schema.json` |

Settings file is **TOML v1.1**, hot-reloaded, version-controllable. Edit directly or via Settings panel.

## WARP_API_KEY (Oz CLI Auth) — Distinct from BYOK

| Credential | Purpose | Format |
|-----------|---------|--------|
| `WARP_API_KEY` env var | Oz CLI/API authentication | `wk-xxx...` |
| BYOK model keys | Provider inference auth (in settings) | `sk-...` (OpenAI), etc. |
| Endpoint API key | Custom inference endpoint auth | Varies by endpoint |

Create API keys: Oz web app (oz.warp.dev) → Cloud Platform → API Keys. Types: Personal (attributed to you) or Agent (scoped to cloud agent). Expiration: 1d/30d/90d/never.

```bash
export WARP_API_KEY="wk-xxx..."
oz agent run --prompt "analyze this codebase"
```

## Three-Way Comparison

| Feature | BYOK | Custom Endpoint | BYOLLM |
|---------|------|----------------|--------|
| Provider | OpenAI, Anthropic, Google | Any OpenAI-compatible | AWS Bedrock (+more coming) |
| Key storage | Local OS keychain | Local OS keychain | Cloud-native IAM |
| Works with Cloud Agents? | ❌ No | ❌ No | ✅ Yes |
| Plan | Free + all paid | Free + all paid | Enterprise only |
| Config level | User | User | Admin/team |

## Pricing & Platform Credits (as of Jul 18, 2026)

| Plan | Monthly Credits | BYOK? | Platform Credits |
|------|----------------|-------|-----------------|
| Free | 0 (no agent AI) | ✅ | ❌ (preview until Jul 1) |
| Build | $20/mo / 1,500 credits | ✅ | ❌ |
| Max | Higher allowance | ✅ | ❌ |
| Business | Per-seat | ✅ | ✅ Local BYOK runs |
| Enterprise | Contract | ✅ + team-managed | ✅ Always |

Three credit buckets: AI credits (model call), compute credits (sandbox), platform credits (run lifecycle, integrations, APIs, observability). All draw from same pool.

## Integration Checkpoints for Aethelgard

| Item | Status | Action |
|------|--------|--------|
| `WARP_API_KEY` | Not set | Create in Oz web app → export |
| BYOK model key(s) | Not set | Add in Settings → AI → Manage models |
| Warp account | Not created | Settings → Sign up |
| Oz CLI | Not installed | `apt install oz-stable` (after adding Warp repo) |
| settings.toml | Not configured | Set theme, keybindings, agent profiles |
| MCP bridge | Not wired | Configure `~/.warp/.mcp.json` to point at Aethelgard tools |
| Warp TUI binary | ✅ Built at ~/warp/target/release/warp-tui-oss | Launches via `warp` command |
