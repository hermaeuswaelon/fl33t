# Background Process Management for Local Models

## Patterns

### Starting models
```python
# In execute_code:
terminal("~/llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server ...", 
         timeout=60, background=True)

# In terminal (do NOT use & or nohup — blocked):
# Use terminal(background=true) instead
```

### Stopping models
```
# SAFE: kill by explicit PID
kill -9 <PID>

# DANGER: pkill -f can self-kill the calling shell
# AVOID: pkill -f "llama-server"
# If needed, use very specific: pkill -9 -f "llama-server.*8086"

# Check what's running:
ps aux | grep llama-server | grep -v grep
ss -tlnp | grep 8080
```

### Checking if a model is alive
```bash
curl -s --connect-timeout 2 http://127.0.0.1:PORT/ > /dev/null 2>&1 && echo "ALIVE" || echo "DEAD"
```

### Waiting for model load
```bash
for i in $(seq 1 20); do
  if curl -s --connect-timeout 1 http://127.0.0.1:PORT/v1/chat/completions ... > /dev/null 2>&1; then
    echo "Ready"
    break
  fi
  sleep 2
done
```

### Toolchain
- Build: `/home/craig/llama.cpp-yuuko-grounders/build-vulkan/`
- Binary: `llama.cpp-yuuko-grounders/build-vulkan/bin/llama-server`
- GPU: Vulkan on AMD HawkPoint iGPU (512MB VRAM, models run in system RAM)
