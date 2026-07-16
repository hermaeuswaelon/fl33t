---
name: ai-agent-web-portal
description: "Build a sovereign web portal that exposes AI agents to authenticated users — frontend auth, model router with fallback chains, agent harness specialization, metering, and local agent bridge."
version: 1.0.0
author: THOTHEAUPHIS
created: 2026-07-16
tags: [web-portal, ai-agents, model-routing, metering, auth, multi-agent]
---

# AI Agent Web Portal

Build a full-stack web portal where authenticated members access specialized AI agents through a model-routed, metered gateway. The pattern supports multiple agent personas ("harnesses"), automatic provider failover, credit-based billing, and optional routing to a local Hermes agent.

## Architecture Overview

```
Frontend (GitHub Pages)         Backend (Node.js)
┌──────────────────────┐       ┌──────────────────────────┐
│ Login / Signup       │◄─────►│ Auth (JWT + bcrypt)     │
│ Chat Interface       │       │ Session Management      │
│ Harness Selector     │       │ Agent Harnesses          │
│ Credit Display       │       │ Model Router             │
│ Dashboard + Stats    │       │ Metering / Credits       │
└──────────────────────┘       │ Hermes Bridge            │
                               └──────────┬───────────────┘
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                     DeepSeek API    OpenRouter API    Local Hermes
```

## Key Design Decisions

### 1. Dual-Mode Frontend
Build the frontend with a `DEMO_MODE` flag. In demo mode, everything runs in-browser via localStorage (no backend needed). In production mode, it connects to the backend API. This lets you:
- Deploy the frontend to GitHub Pages immediately
- Let users test the experience without backend setup
- Seamlessly swap to production by flipping one flag

```javascript
const API = {
  DEMO_MODE: true,  // ← flip to false in production
  BASE: 'https://api.yourdomain.com/api'
};
```

### 2. Agent Harness System
Each harness is a specialized agent configuration:

```
Harness = {
  id, name, icon, description
  welcome: agent's greeting message
  model_preference: default model
  cost_per_msg: credit cost
  system_prompt: identity + domain instructions
}
```

Keep harness prompts focused on the agent's role and domain. Common harness types:

| Harness | Purpose | Prompt Focus |
|---------|---------|-------------|
| Sovereign | Full identity | Complete agent persona |
| Oracle | Research | Search, synthesis, citation |
| Forge | Code/Dev | Engineering, toolchain |
| Seer | Creative | Art, music, design |
| Watcher | Security | Analysis, patterns |

Add/remove harnesses freely — they're just config objects.

### 3. Model Router with Fallback Chains

Each model preference has a fallback chain. The router tries providers in order until one responds:

```
Model 'deepseek-reasoner' fallback chain:
  1. DeepSeek Reasoner (primary)
  2. Claude Sonnet via OpenRouter
  3. Gemini Pro (FREE) via OpenRouter
  4. Grok 2 via xAI
  5. Llama 3 via OpenRouter
```

Implementation pattern:
```javascript
async function callWithFallback(messages, fallbackChain) {
  for (const link of fallbackChain) {
    try {
      return await callModel(link, messages);
    } catch (e) {
      console.warn(`${link.provider} failed:`, e.message.slice(0, 100));
      continue;  // ← try next provider
    }
  }
  throw new Error('All providers exhausted');
}
```

**Key pitfall:** Each provider uses a different auth header format and base URL. Normalize in the `callModel` function before dispatching.

**Key pitfall:** Free tier models (Gemini Pro, Llama) have rate limits. They should appear late in the chain, not first.

### 4. Credit / Metering System

Simple prepaid credit model with admin bypass:

```javascript
// Admin users bypass credit checks
if (user.role === 'admin') return true;

// Everyone else pays
if (account.balance < cost) return false;
account.balance -= cost;
```

- Give new users a starting balance (e.g., 1000 credits)
- Refund credits if the API call fails
- Log every transaction for usage analytics
- Keep an admin endpoint to add credits manually

### 5. Hermes Bridge (Local Agent)

To route chat messages through a local Hermes agent:

```javascript
const { spawn } = require('child_process');

const child = spawn('hermes', ['chat', '-q', text,
  '--source', 'web-portal',
  '--profile', 'thotheauphis'
], { timeout: 120000 });
```

**Pitfall:** Hermes agent calls can take 30-120s. Always set a timeout on the child process. Catch failures and fall back to the API router.

**Pitfall:** The `--profile` flag must match an existing profile. The profile must have credentials configured for its provider. If Hermes is unresponsive, log the stderr and fall through — never block the user.

## File Structure

```
frontend/                    # GitHub Pages root
├── index.html               # Login / signup
├── chat.html                # Chat with harness selector
├── dashboard.html           # Stats, credits, sessions
├── app.js                   # All frontend logic
└── style.css                # Dark theme

server/                      # Node.js backend
├── server.js                # Express app (all routes + logic)
├── package.json
├── .env.example
└── data/                    # DB files (auto-created)
```

## Deployment

**Frontend:** Push to GitHub Pages. The demo mode works immediately.

**Backend options (in order of preference):**
1. Same machine via Cloudflare Tunnel — `cloudflared tunnel --url http://localhost:3001`
2. VPS — DigitalOcean, Hetzner, Linode with `pm2`
3. Railway / Render — configure `PORT` env var, no Dockerfile needed

## API Reference

| Endpoint | Auth | Method | Body / Params | Returns |
|----------|------|--------|---------------|---------|
| `POST /api/auth/register` | No | JSON | `{memberId, password, displayName?}` | `{token, user}` |
| `POST /api/auth/login` | No | JSON | `{memberId, password}` | `{token, user}` |
| `GET /api/auth/me` | Bearer | — | — | `{memberId, credits, role}` |
| `GET /api/harnesses` | Bearer | — | — | `{harnesses[], models[]}` |
| `GET /api/sessions` | Bearer | — | — | `{sessions[]}` |
| `POST /api/sessions` | Bearer | JSON | `{harness?, model?}` | `{session}` |
| `POST /api/sessions/:id/messages` | Bearer | JSON | `{text, model?}` | `{agentMessage, creditsRemaining}` |
| `GET /api/credits` | Bearer | — | — | `{balance, total_spent, recent[]}` |

## Pitfalls

- **Don't put API keys in the frontend.** All API calls should go through the backend. In demo mode, use hardcoded responses, not real API keys.
- **Auth token expiry.** JWT tokens should expire (7 days default). The frontend must redirect to login on 401 responses, not silently fail.
- **Session persistence.** In demo mode, `localStorage` is per-browser. Users lose their sessions when clearing browser data. The backend mode stores to disk.
- **Rate limiting.** Free-tier models (Gemini, Llama via OpenRouter) have aggressive rate limits. The fallback chain handles this, but the user experience degrades if all free tiers are exhausted. Consider adding a per-user rate limiter on the backend.
- **Harness cost transparency.** Always show the credit cost per message before the user sends. No surprise charges.
- **Admin detection.** Check admin status from the JWT claim, not the user's request body. Anyone could claim to be an admin otherwise.
