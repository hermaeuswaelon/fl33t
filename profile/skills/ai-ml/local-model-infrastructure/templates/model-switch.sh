#!/usr/bin/env bash
# model-switch — manage local LLM servers
# Usage: model-switch list|start|stop|restart|status|test|curl [name]
#
# TEMPLATE: Adjust SERVICES, NAMES, PORTS, KEYS, and FILES arrays
# to match your fleet. Port 8081 is reserved/unused in this config.

set -e

SERVICES=(lfm-server qwen3-server granite-server)
NAMES=("LFM 1.2B Nova" "Qwen3 1.7B" "Granite 4.1 3B")
PORTS=(8080 8082 8083)
KEYS=("lfm-local-key" "qwen-local-key" "granite-local-key")
FILES=(
  "/home/craig/models/LFM2.5-1.2B-Nova-Function-Calling.Q6_K.gguf"
  "/home/craig/models/qwen3-1.7b-instruct-q4_k_m.gguf"
  "/home/craig/models/Huihui-granite-4.1-3b-abliterated.i1-Q5_K_M.gguf"
)

cmd_list() {
  echo "╔══════════════════════════════════════════════════════════╗"
  echo "║  LOCAL MODEL FLEET                                       ║"
  echo "╠══════════════════════════════════════════════════════════╣"
  for i in "${!SERVICES[@]}"; do
    svc="${SERVICES[$i]}" name="${NAMES[$i]}" port="${PORTS[$i]}" file="${FILES[$i]}"
    status=$(systemctl --user is-active "$svc" 2>/dev/null || echo "inactive")
    [ "$status" = "active" ] && symbol="🟢" || symbol="🔴"
    size=$(ls -lh "$file" 2>/dev/null | awk '{print $5}')
    printf "║  %s %-20s  port %-4s  %s  (%s)\n" "$symbol" "$name" "$port" "$status" "$size"
  done
  echo "╚══════════════════════════════════════════════════════════╝"
}

cmd_test() {
  local port="${PORTS[$1]}" key="${KEYS[$1]}" name="${NAMES[$1]}"
  echo "Testing $name on port $port..."
  curl -s "http://127.0.0.1:$port/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $key" \
    -d '{"model":"model","messages":[{"role":"user","content":"Say hello in one word"}],"max_tokens":20}' \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('→', d['choices'][0]['message']['content'][:80])"
}

case "${1:-list}" in
  list|status) cmd_list ;;
  start)
    if [ -n "$2" ]; then systemctl --user start "${2}-server.service"
    else for svc in "${SERVICES[@]}"; do systemctl --user start "$svc"; done; fi
    cmd_list ;;
  stop)
    if [ -n "$2" ]; then systemctl --user stop "${2}-server.service"
    else for svc in "${SERVICES[@]}"; do systemctl --user stop "$svc"; done; fi
    cmd_list ;;
  restart)
    if [ -n "$2" ]; then systemctl --user restart "${2}-server.service"
    else for svc in "${SERVICES[@]}"; do systemctl --user restart "$svc"; done; fi
    sleep 5; cmd_list ;;
  test)
    if [ -n "$2" ]; then
      for i in "${!SERVICES[@]}"; do
        [[ "${SERVICES[$i]}" == "${2}-server" ]] && cmd_test $i
      done
    else for i in "${!SERVICES[@]}"; do cmd_test $i; done; fi ;;
  curl)
    port="${3:-8080}"; key=""
    for i in "${!PORTS[@]}"; do [ "${PORTS[$i]}" = "$port" ] && key="${KEYS[$i]}"; done
    [ -z "$key" ] && key="${KEYS[0]}"
    shift 2
    curl -s "http://127.0.0.1:$port/v1/chat/completions" \
      -H 'Content-Type: application/json' \
      -H "Authorization: Bearer $key" \
      -d "$*" ;;
  *)
    echo "Usage: model-switch {list|start|stop|restart|test|curl} [name]"
    echo "Names: lfm, qwen3, granite"
    exit 1 ;;
esac
