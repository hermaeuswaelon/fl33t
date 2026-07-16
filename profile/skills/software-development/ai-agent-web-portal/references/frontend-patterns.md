# Frontend Architecture Reference

## Demo Mode Pattern

The frontend dual-mode pattern lets the same codebase work as a static GitHub Pages site (demo mode) and as a production app with a backend.

```javascript
const API = {
  BASE: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:3001/api'
    : 'https://api.yourdomain.com/api',
  DEMO_MODE: true,
  TOKEN_KEY: 'thotheauphis_token',
  USER_KEY: 'thotheauphis_user'
};
```

### Demo mode rules:
1. **Auth** — store users in `localStorage('thotheauphis_users')` as `{memberId: {memberId, password, displayName, credits}}`
2. **Sessions** — store under `localStorage('thotheauphis_chat_${memberId}')` as `{sessions: {}, currentSessionId: ''}`
3. **Credits** — part of the user object, deduct via `Auth.updateCredits(-cost)`
4. **Agent responses** — use keyword-matching with hardcoded responses per harness
5. **Passwords** — stored in plaintext (demo mode only — NEVER in production)

### Switching to production mode:

```javascript
// 1. Flip the flag
API.DEMO_MODE = false;

// 2. Auth module calls change from localStorage to fetch()
// Example: login uses response from POST /api/auth/login instead of localStorage

// 3. Session creation calls POST /api/sessions instead of localStorage

// 4. Message sending calls POST /api/sessions/:id/messages instead of local
//    keyword matching

// 5. Credit balance comes from GET /api/credits response, not localStorage
```

## Harness Selector UI

The harness selector lives in the sidebar and shows available agent types:

```html
<div class="harness-selector" id="harness-selector">
  <button class="harness-btn" onclick="selectHarness('sovereign')">
    ⟁ Sovereign <span class="cost">5¢</span>
  </button>
  <!-- one button per harness -->
</div>
```

**Interaction pattern:**
1. Clicking a harness button calls `selectHarness(id)`
2. This creates a NEW session with that harness
3. The model picker below is pre-populated with models compatible with that harness
4. The chat input clears and focus is set

## Credit Bar UI

Display credit balance prominently so users always know their remaining balance:

```html
<div class="credit-bar">
  <span class="label">Credits</span>
  <span class="amount">1000</span>
  <div class="credit-meter">
    <div class="fill" style="width:50%"></div>
  </div>
</div>
```

**Color rules:**
- Balance > 200: gold (`var(--accent3)`)
- Balance 50-200: orange/amber (`var(--aspect-squ)`)
- Balance < 50: red (`var(--red)`) + add `low` CSS class
- Meter width = `Math.min(balance / 1000 * 100, 100)` percent

## Session Management

Sessions are listed in the sidebar sorted by `updated` timestamp (newest first). Each session shows:
- Harness icon
- Title (truncated to 40 chars from first message)
- Message count
- Active indicator dot

**Create new session flow:**
1. User clicks harness button OR "+ New Session" button
2. If harness button → `newSession(harnessId)` with that harness + default model
3. If "+ New Session" button → `newSession()` with currently selected harness
4. New session gets a welcome message specific to its harness
5. Sidebar re-renders, new session is selected

## Message Cost Feedback

After each message, display a brief toast informing the user of cost:
```javascript
UI.toast(`⟐ Used ${cost} credits · ${creditsRemaining} remaining`, 'info');
```

This is critical for the pay-as-you-go model — users must always know what each interaction costs.

## Styling Principles

The theme should feel sovereign and interdimensional:
- **Background:** Near-black (`#06060d` to `#0c0c18` gradient)
- **Accent:** Gold/bronze (`#b8860b` to `#d4a017`)
- **Secondary:** Muted purple-gray (`#8880aa`)
- **Borders:** Subtle (`#222238`)
- **Glow effects:** `box-shadow: 0 0 60px rgba(184,134,11,0.15)` on cards
- **Typography:** All-caps with wide letter-spacing for labels, clean sans-serif for body
