# Browser Recovery Workflow — Finding the Dual Citizen When Paths Are Dead

## The Problem

Scripts reference binaries at paths that no longer exist due to repo restructures. The browser `dual_citizen_v2` expects:
- `~/aethelgard-repo/fleet/pascal/dual-citizen-v2/` → now at `~/projects/aethelgard/fleet/pascal/dual-citizen-v2/`
- `~/CEF4Delphi/cef_binary_current/Release/` → now at `~/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_131.4.1+chromium-131.0.6778.265_linux64/Release/`

## Discovery Chain (Proven)

```
1. Desktop launchers
   → ~/Desktop/Scripts-Launchers/bromium.sh
   → ~/Desktop/Scripts-Launchers/super_browser.sh
   → Reveal expected paths (dead)\n
2. Systemd user services
   → systemctl --user list-units | grep dual
   → ~/.config/systemd/user/dual-citizen-watchdog.service
   → Points to watchdog script\n
3. Watchdog script
   → ~/.NOTTHEONETOEDIT/scripts/browser-watchdog.sh
   → Reveals ACTUAL expected paths (BIN, WORKDIR, LD_LIB)\n
4. Binary hunt
   → find /home/craig -type f -executable -size +10M | grep -v node_modules | grep -v venv
   → Found at ~/projects/aethelgard/fleet/pascal/dual-citizen-v2/dual_citizen_v2
   → Also found ~/.local/bin/cef-browser (Python lifecycle manager)\n
5. Symlink bridge
   → ln -s ~/projects/aethelgard ~/aethelgard-repo  (if needed)
   → ln -s ~/projects/aethelgard/fleet/pascal/dual-citizen-v2 ~/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2
   → mkdir -p ~/CEF4Delphi/cef_binary_current && ln -sf ~/.aethelgard/workspace/browser/CEF4Delphi/cef_binary_<version>/Release ~/CEF4Delphi/cef_binary_current/Release
```

## Launch Command (Once Symlinks Exist)

```bash
cd /home/craig/.NOTTHEONETOEDIT/fleet/pascal/dual-citizen-v2 && \
  LD_LIBRARY_PATH="/home/craig/CEF4Delphi/cef_binary_current/Release" \
  DISPLAY=:0 \
  ./dual_citizen_v2
```

## Verification

```bash
# Socket appears after ~8-15s
ls -la /tmp/aethelgard_cef.sock

# Process tree
ps aux | grep dual_citizen
# Should show: main binary + zygote + network service + utility processes

# Re-enable the watchdog
systemctl --user daemon-reload
systemctl --user enable --now dual-citizen-watchdog.service
systemctl --user status dual-citizen-watchdog.service
```

## Pitfalls

- The `cef-browser` Python CLI (at `~/.local/bin/cef-browser`) also has hardcoded paths. It looks for `~/aethelgard-repo/fleet/pascal/...` — won't work until symlinks are in place.
- The original `bromium.sh` and `super_browser.sh` launchers on the Desktop also have dead paths.
- LD_LIBRARY_PATH must point to the exact directory containing `libcef.so` (~1.35GB file). Wrong path = silent crash.
- DISPLAY=:0 must be set. Without it, the binary exits immediately with no output.
