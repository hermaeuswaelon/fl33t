# Bromium Portal Wiring — v3.2.1 Session

**Date:** July 17, 2026
**Context:** User reported TTS button and Voice button appeared non-functional in Bromium Portal. Close button (X) didn't close the portal. Browser wouldn't stay killed.

## TTS Wiring (speak_async)

### Problem
`espeak` was called via `subprocess.Popen` but audio output went nowhere — no ALSA device was specified, and `Popen` with no device opens ALSA's default which fails.

### Fix
Changed to espeak → WAV → aplay pipeline:

```python
wav = tempfile.mktemp(suffix=".wav")
subprocess.run(["espeak", "-w", wav, "-s", "145", "-p", "45", text],
              timeout=5, capture_output=True)
for dev in ("hw:1,0", "hw:0,3", "default"):
    r = subprocess.run(["aplay", "-q", "-D", dev, wav],
                      timeout=8, capture_output=True)
    if r.returncode == 0:
        break
os.unlink(wav)
```

### Test
```bash
espeak "test" -w /tmp/t.wav && aplay -D hw:1,0 /tmp/t.wav
```

### ALSA Device Layout
| Device | Path | Type |
|--------|------|------|
| Analog (card 1, dev 0) | `hw:1,0` | ALC3204 (speakers) |
| HDMI 0 (card 0, dev 3) | `hw:0,3` | HDMI output |
| HDMI 1 (card 0, dev 7) | `hw:0,7` | HDMI output |
| Default | `default` | Fails if no .asoundrc |

## Voice Button Wiring

### Problem
`_start_voice_listener` launched `bromium-voice.py --oneshot` which captures from microphone via:
1. `import whisper` → not installed (3.5GB torch dep)
2. Falls back to `speech_recognition` → needs pulseaudio + internet

Result: silent failure. `--oneshot` returned `{"heard": ""}` → portal's `if data.get("heard"):` skipped it.

### Fix
Changed to text dialog → `--say`:
```python
text = tk.simpledialog.askstring("🎤 Voice Command", "Enter your voice command:")
if text and text.strip():
    result = subprocess.run(
        [sys.executable, VOICE_CMD, "--say", text.strip()],
        timeout=15, capture_output=True, text=True)
    if result.stdout:
        data = json.loads(result.stdout)
```

`--say` mode was already fully implemented (line 499-501):
```python
elif sys.argv[1] == "--say":
    text = " ".join(sys.argv[2:])
    print(json.dumps({"command": text, "result": process_voice_command(text)}))
```

### Mic Alternative
To restore mic mode: `pip install openai-whisper` (needs torch, ~2GB, timed out at 180s in this session), revert `_start_voice_listener`.

## Close Button (WM_DELETE_WINDOW)

### Problem
Tkinter's X button closes the window but the process stays alive (threads keep running). No `WM_DELETE_WINDOW` protocol handler.

### Fix
```python
self.root.protocol("WM_DELETE_WINDOW", self._on_close)
self.root.bind("<Control-q>", lambda e: self._on_close())

def _on_close(self):
    self._log("🛑 Bromium Portal closing.")
    self.root.quit()
    sys.exit(0)
```
Must call `sys.exit(0)` — `root.quit()` alone only stops mainloop.

## Watchdog & Browser Restart

### Problem
Killing the bromium binary causes `dual-citizen-watchdog.service` to restart it in ~5-8 seconds.

### Fix
```bash
# Stop the watchdog
systemctl --user stop dual-citizen-watchdog.service
# Then kill browser
pkill -f bromium
pkill -f cef_controller
rm -f /tmp/aethelgard_cef.sock
```

To restart later:
```bash
# Start browser
~/projects/aethelgard/fleet/pascal/dual-citizen-v2/run_bromium.sh
# Re-enable watchdog
systemctl --user start dual-citizen-watchdog.service
```

## Performance Monitor

Added live system metrics to the portal status bar:

```python
# In _build_status_bar:
self._sb_perf = tk.Label(sb, text="", bg=PANEL_BG, fg=TEXT_DIM, font=FONT_TINY)
self._sb_perf.pack(side=tk.RIGHT, padx=4)
self._update_perf()

def _update_perf(self):
    import psutil
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0)
    self._sb_perf.configure(text=f"⬡ CPU {cpu:.0f}%  MEM {mem.percent:.0f}%")
    self.root.after(5000, self._update_perf)
```

## Hermes CLI Performance Output
```bash
hermes config set show_cost true
hermes config set timestamps true
```
Adds cost and timing to every Hermes response in the terminal.
