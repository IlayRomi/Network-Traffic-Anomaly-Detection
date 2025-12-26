#!/usr/bin/env bash
set -u

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZEEK_LOG_DIR="/mnt/c/Users/elair/zeek_logs"
IFACE="eth0"
ZEEK_BIN="/opt/zeek/bin/zeek"
MODEL_RUNNER="src/realtime/model_runner.py"
DASH_APP="src/dashboard/app.py"

PID_DIR="$PROJECT_ROOT/results/realtime"
LOG_DIR="$PROJECT_ROOT/results/logs"

ZEEK_PID="$PID_DIR/zeek.pid"
RUNNER_PID="$PID_DIR/runner.pid"
DASH_PID="$PID_DIR/dashboard.pid"

mkdir -p "$PID_DIR" "$LOG_DIR" "$ZEEK_LOG_DIR"

echo "== NIDS START =="
echo "Project:   $PROJECT_ROOT"
echo "Zeek logs: $ZEEK_LOG_DIR"
echo "Iface:     $IFACE"
echo "Dashboard: http://localhost:8501"
echo ""

is_running() { kill -0 "$1" 2>/dev/null; }

start_bg() {
  local name="$1"
  local pidfile="$2"
  local outlog="$3"
  local errlog="$4"
  shift 4

  echo "[*] Starting $name..."
  ("$@") >"$outlog" 2>"$errlog" &
  local pid=$!
  echo "$pid" > "$pidfile"
  sleep 0.3

  if is_running "$pid"; then
    echo "    [OK] $name (pid=$pid)"
  else
    echo "    [FAIL] $name did not stay running."
    echo "    See logs:"
    echo "      $outlog"
    echo "      $errlog"
    exit 1
  fi
}

# preflight
if [[ ! -x "$ZEEK_BIN" ]]; then
  echo "[FAIL] Zeek binary not found at: $ZEEK_BIN"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "[FAIL] python3 not found"
  exit 1
fi

if ! command -v streamlit >/dev/null 2>&1; then
  echo "[FAIL] streamlit not found. Install: python3 -m pip install streamlit"
  exit 1
fi

# ensure sudo won't prompt in background
if ! sudo -n true 2>/dev/null; then
  echo "[!] Sudo needs password first. Run:"
  echo "    sudo -v"
  echo "Then re-run:"
  echo "    ./scripts/start_all.sh"
  exit 1
fi

start_bg "Zeek" "$ZEEK_PID" "$LOG_DIR/zeek.out.log" "$LOG_DIR/zeek.err.log" \
  bash -lc "cd '$ZEEK_LOG_DIR' && sudo '$ZEEK_BIN' -C -i '$IFACE'"

start_bg "Model runner" "$RUNNER_PID" "$LOG_DIR/runner.out.log" "$LOG_DIR/runner.err.log" \
  bash -lc "cd '$PROJECT_ROOT' && python3 '$MODEL_RUNNER'"

start_bg "Dashboard" "$DASH_PID" "$LOG_DIR/dashboard.out.log" "$LOG_DIR/dashboard.err.log" \
  bash -lc "cd '$PROJECT_ROOT' && streamlit run '$DASH_APP' --server.headless true --server.port 8501"

echo ""
echo "✅ All started."
echo "Open: http://localhost:8501"
echo "PIDs: $PID_DIR"
echo "Logs: $LOG_DIR"
