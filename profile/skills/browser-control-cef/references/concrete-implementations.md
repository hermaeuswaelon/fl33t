# Cross-Reference: Concrete Implementations

This umbrella skill covers the general CEF browser control pattern.
Concrete implementations and session-specific details live in:

| Skill | Topic |
|-------|-------|
| `bromium-control` | Bromium Dual-Citizen browser: IPC protocol, extensions, AI agent, portal, launch scripts |
| `bromium-control/references/bromium-content-script-bridge.md` | Isolated world → main world bridge pattern |
| `bromium-control/references/bromium-fleet-bus-bh-tool.md` | Fleet bus HTTP API + `bh` Hermes browser driver CLI |
| `bromium-control/references/bromium-stealth-verification.md` | Automation undetectability validation |

## CEF Browser Detection Checklist
When encountering a new CEF browser to automate:

1. **Find the socket**: Check `/tmp/*.sock`, `/run/*.sock`, look for `CEF` in process list
2. **Test basic IPC**: health, navigate, get_title — if these work, the IPC protocol is likely this pattern
3. **Test eval**: Try `evaluate_js` with `code` param, then `get_eval`
4. **Test extensions**: If extensions are loaded but content scripts don't inject, it's the isolated world issue
5. **Check stealth**: Verify `navigator.webdriver`, plugins, webgl
