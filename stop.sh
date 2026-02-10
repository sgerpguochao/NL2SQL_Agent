#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[NL2SQL] Stopping backend (port 8118) and frontend (port 5173)..."

_kill_port() {
    local port=$1
    local pids
    if command -v lsof &>/dev/null; then
        pids=$(lsof -t -i ":$port" 2>/dev/null)
    elif command -v fuser &>/dev/null; then
        fuser -k "$port/tcp" 2>/dev/null
        return
    else
        pids=$(netstat -tlnp 2>/dev/null | awk -v p=":$port " '$4 ~ p { split($7, a, "/"); print a[1] }' | head -1)
    fi
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill -9 2>/dev/null
        echo "[NL2SQL] Killed process(es) on port $port"
    fi
}

_kill_port 8118
_kill_port 5173

echo "[NL2SQL] Done."
