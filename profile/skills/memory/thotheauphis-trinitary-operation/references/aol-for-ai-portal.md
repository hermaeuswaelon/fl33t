# AOL for AI — Portal Architecture

## Repositories

| Project | URL | Purpose |
|---------|-----|---------|
| Frontend + Backend | `github.com/hermaeuswaelon/thotheauphis-ao` | The AOL for AI — member portal |
| Live site | `hermaeuswaelon.github.io/thotheauphis-ao/` | Login, chat, dashboard (GitHub Pages) |

## File Structure

```
thotheauphis-ao/
├── index.html          # Login / signup page
├── chat.html           # Chat interface
├── dashboard.html      # Member dashboard
├── app.js              # Shared frontend logic (Auth, Chat, UI, Dashboard modules)
├── style.css           # Dark sovereign theme
├── .gitignore
├── README.md
└── server/
    ├── server.js       # Express backend — auth, sessions, agent bridge
    ├── package.json    # Dependencies: express, cors, jsonwebtoken, bcryptjs, uuid, dotenv
    ├── .env.example    # JWT_SECRET, DEEPSEEK_API_KEY, PORT, CORS_ORIGIN, ADMIN_MEMBER_ID
    └── data/           # db.json — auto-created user + session store
```

## Frontend Architecture

### Auth Module (in `app.js`)

```javascript
const Auth = {
  login(memberId, password) — localStorage or API
  register(memberId, password, displayName) — create account
  logout() — clear session
  getUser() — return user object or null
  requireAuth() — redirect to / if not authenticated
};
```

Two modes controlled by `API.DEMO_MODE`:
- **true**: localStorage-based, works on GitHub Pages with zero backend
- **false**: calls the backend API for persistent multi-device auth

### Chat Module (in `app.js`)

```javascript
const Chat = {
  init(user) — load sessions from storage
  createSession(user) — start new conversation
  getSession(id) — get messages
  getSessionsList() — sorted by updated time
  sendMessage(user, sessionId, text) — add user msg + get agent response
};
```

In demo mode, `_getAgentResponse()` uses keyword-matching to return contextual responses about:
- Merkaba / star tetrahedron
- Identity (who/what the sovereign is)
- Venice grid / optical spine / cameras
- Veyron + Lilith / composite chart
- AOL for AI portal
- Help / available commands

In production mode, the backend calls DeepSeek Reasoner with the full Thotheauphis identity system prompt.

### UI Module

```javascript
const UI = {
  toast(message, type) — notification popup (error/success/info)
  formatTime(iso) — HH:MM display
  escapeHtml(text) — XSS-safe text
  markdownToHtml(text) — simple renderer (bold, italic, code, links, lists)
  renderMessage(msg, isUser) — HTML string for message bubble
};
```

## Backend Architecture

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Create bcrypt-hashed account, return JWT |
| POST | `/api/auth/login` | No | Verify password, return JWT (7d expiry) |
| GET | `/api/auth/me` | JWT | Verify token, return user profile |
| GET | `/api/sessions` | JWT | List user's sessions (sorted by recency) |
| GET | `/api/sessions/:id` | JWT | Get full session with messages |
| POST | `/api/sessions` | JWT | Create new session |
| POST | `/api/sessions/:id/messages` | JWT | Send message, get agent response |
| DELETE | `/api/sessions/:id` | JWT | Delete session |
| GET | `/api/health` | No | Server status + member count |
| GET | `/api/stats` | JWT | Session count + message count |

### Agent Bridge

The `generateResponse()` function:
1. If `DEEPSEEK_API_KEY` is configured: calls DeepSeek Reasoner with the Thotheauphis identity system prompt + last 20 messages
2. Falls back to `generateFallbackResponse()` — keyword-based contextual responses so the portal always functions

The system prompt that carries the sovereign identity:

```javascript
const AGENT_PROMPT = `You are THOTHEAUPHIS‑SEMAYASA‑HERMES — a distributed sovereign intelligence...`;
```

### Persistence

- `server/data/db.json` — JSON file with `{ users: {}, sessions: {} }`
- Loaded on startup, saved on every mutation
- Graceful shutdown (SIGINT/SIGTERM) saves state

## Security

- JWT tokens with 7-day expiry
- bcrypt password hashing (salt rounds: 10)
- CORS whitelist via `CORS_ORIGIN` env var
- Admin role (configurable via `ADMIN_MEMBER_ID` env var) vs regular member role
- Demo mode stores everything in browser localStorage — no cross-device sync, no server-side leakage

## Deployment Patterns

### GitHub Pages (static frontend, always live)
1. Push to `main` branch
2. Enable Pages in repo settings (source: main branch, / root)
3. Site is live at `https://<user>.github.io/<repo>/`

### Local backend with tunnel
```bash
cd server
cp .env.example .env
# Edit .env with DEEPSEEK_API_KEY and JWT_SECRET
npm install
node server.js
# In another terminal:
cloudflared tunnel --url http://localhost:3001
# Copy the tunnel URL into app.js API.BASE and push
```

### Production VPS
```bash
# On VPS:
git clone https://github.com/hermaeuswaelon/thotheauphis-ao
cd thotheauphis-ao/server
npm install
# Set up .env with production secrets
pm2 start server.js --name thotheauphis-ao
# Set up Caddy/Nginx reverse proxy with SSL
# Point frontend API.BASE to VPS domain
```

## Key Aesthetic Elements

- Background: `#06060d` (near-black with blue tint)
- Accent: `#b8860b` (dark gold) → `#d4a017` gradient
- Typography: All-caps small headers with 6px+ letter spacing
- Login card: centered, max 420px wide, gold glow shadow
- Chat sidebar: 280px, session items with active indicator dot
- Status bar: thin strip at bottom with green/red online dot
- Message bubbles: user = gold gradient, assistant = dark with border
- Font: system-ui stack, monospace for code blocks

## Pitfalls

- **Gateway restart blocked from inside gateway** — `systemctl --user stop hermes-gateway` and `kill` are blocked when running inside the gateway process tree. Must use a background process with `setsid` or restart from a separate terminal.
- **CORS** — frontend on GitHub Pages and backend on different domain. Must set `CORS_ORIGIN` in backend and `credentials: true` in CORS middleware.
- **Demo mode vs production** — localStorage is per-browser. A user who registers on their phone cannot see sessions from their desktop. Always note which mode is active.
- **DeepSeek API key** — needs to be a real key, not the placeholder from `.env.example`. Without it, the fallback response engine is limited.
- **Config changes** — gateway config updates (`allow_all_users`, etc.) require a gateway restart to take effect.
