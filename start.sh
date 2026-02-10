#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "[NL2SQL] Starting backend (port 8118, conda env: nl2sql_vc)..."
(cd "$ROOT/backend" && nohup conda run -n nl2sql_vc python -m uvicorn app.main:app --reload --port 8118 > ../.backend.log 2>&1 &)
sleep 2

echo "[NL2SQL] Starting frontend (port 5173, host 0.0.0.0)..."
(cd "$ROOT/frontend" && nohup npx vite --host 0.0.0.0 > ../.frontend.log 2>&1 &)

echo ""
echo "[NL2SQL] Backend:  http://127.0.0.1:8118"
echo "[NL2SQL] Frontend: http://0.0.0.0:5173  (also http://127.0.0.1:5173)"
echo "[NL2SQL] Logs: .backend.log / .frontend.log"
echo "[NL2SQL] Run ./stop.sh to stop."
