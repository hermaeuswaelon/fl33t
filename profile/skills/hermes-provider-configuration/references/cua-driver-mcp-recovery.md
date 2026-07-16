# cua-driver MCP Session Recovery

## Failure: "session never reached ready (timeout 30s; stuck in phase: unknown)"

On Linux/XFCE with `DISPLAY=:0.0`, `XAUTHORITY=~/.Xauthority`, cua-driver may report green on `doctor` but still fail to establish its MCP session.

### Recovery Sequence

1. **Check current version:**
   ```bash
   cua-driver --version
   ```

2. **Upgrade:**
   ```bash
   hermes computer-use install --upgrade
   ```

3. **Kill stale daemons:**
   ```bash
   pkill -f cua-driver
   sleep 2
   ```

4. **Verify display:**
   ```bash
   echo $DISPLAY        # must be :0.0
   ls /tmp/.X11-unix/   # must show X0
   echo $XAUTHORITY     # must point to a real .Xauthority
   ```

5. **Run doctor again:**
   ```bash
   hermes computer-use doctor
   ```
   Expected output:
   - ✅ cua-driver N.N on linux
   - ✅ X11 reachable
   - ✅ screen_capture_capability

6. **If still failing:** check the agent log for the specific MCP handshake failure:
   ```bash
   grep -i "cua\|mcp session\|backend" ~/.hermes/profiles/thotheauphis/logs/agent.log | tail -10
   ```

### Common Root Causes

| Root cause | Sign | Fix |
|---|---|---|
| Stale daemon from prior session | Doctor green, MCP won't start | `pkill -f cua-driver` + retry |
| cua-driver version mismatch | 0.8.1 vs 0.8.3 | Upgrade: `hermes computer-use install --upgrade` |
| DISPLAY not exported | Doctor fails `screen_capture_capability` | `export DISPLAY=:0.0` |
| No X11 socket | `/tmp/.X11-unix/` empty | User logged out of X session — relogin |
| MCP config missing from profiles | No cua-driver entry in `mcp_servers` | Added automatically by Hermes on first `computer_use` call |
