#!/usr/bin/env sh
# Reproducible HTTP benchmark harness for django-lightning.
#
# Uses an industry-standard Rust/C load generator (oha preferred, wrk fallback)
# instead of a Python client, so the load generator is never the bottleneck.
# Every run captures hardware specs, git commit, and exact run parameters so
# results are honest, comparable, and reproducible.
#
# Usage:
#   ./scripts/bench.sh [PATH] [DURATION] [CONNECTIONS]
#
#   BENCH_URL=http://127.0.0.1:8000  ./scripts/bench.sh /health 30s 64
#   AUTH_HEADER="Authorization: Bearer <jwt>" ./scripts/bench.sh /api/native/users
#
# Recommended server invocation before benchmarking (release build, no DEBUG):
#   uv run maturin develop --release
#   DEBUG=false uv run manage.py runbolt --port 8000 --processes $(nproc || sysctl -n hw.ncpu)

set -eu

BASE_URL="${BENCH_URL:-http://127.0.0.1:8000}"
TARGET_PATH="${1:-/health}"
DURATION="${2:-30s}"
CONNECTIONS="${3:-64}"
WARMUP="${WARMUP:-5s}"
URL="${BASE_URL}${TARGET_PATH}"

echo "## django-lightning benchmark: ${TARGET_PATH}"
echo ""
echo "### Environment"
echo ""
echo "- Date        : $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "- Git commit  : $(git rev-parse --short HEAD 2>/dev/null || echo 'n/a')"
echo "- OS          : $(uname -srm)"
case "$(uname -s)" in
  Darwin)
    echo "- CPU         : $(sysctl -n machdep.cpu.brand_string)"
    echo "- Cores       : $(sysctl -n hw.ncpu)"
    echo "- Memory      : $(( $(sysctl -n hw.memsize) / 1073741824 )) GB"
    ;;
  Linux)
    echo "- CPU         : $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
    echo "- Cores       : $(nproc)"
    echo "- Memory      : $(( $(grep -m1 MemTotal /proc/meminfo | awk '{print $2}') / 1048576 )) GB"
    ;;
esac
echo "- Target      : ${URL}"
echo "- Duration    : ${DURATION} (warmup ${WARMUP})"
echo "- Connections : ${CONNECTIONS}"
echo ""

if command -v oha >/dev/null 2>&1; then
  TOOL="oha"
elif command -v wrk >/dev/null 2>&1; then
  TOOL="wrk"
else
  echo "ERROR: neither 'oha' nor 'wrk' found." >&2
  echo "Install one of:" >&2
  echo "  cargo install oha        (or: brew install oha)" >&2
  echo "  brew install wrk         (or: apt install wrk)" >&2
  exit 1
fi
echo "- Tool        : ${TOOL}"
echo ""

run_oha() {
  dur="$1"
  if [ -n "${AUTH_HEADER:-}" ]; then
    oha --no-tui -z "${dur}" -c "${CONNECTIONS}" -H "${AUTH_HEADER}" "${URL}"
  else
    oha --no-tui -z "${dur}" -c "${CONNECTIONS}" "${URL}"
  fi
}

run_wrk() {
  dur="$1"
  if [ -n "${AUTH_HEADER:-}" ]; then
    wrk -d "${dur}" -c "${CONNECTIONS}" -t "${WRK_THREADS:-8}" --latency \
      -H "${AUTH_HEADER}" "${URL}"
  else
    wrk -d "${dur}" -c "${CONNECTIONS}" -t "${WRK_THREADS:-8}" --latency "${URL}"
  fi
}

echo "### Warmup (${WARMUP}, discarded)"
echo ""
if [ "${TOOL}" = "oha" ]; then
  run_oha "${WARMUP}" >/dev/null 2>&1 || true
else
  run_wrk "${WARMUP}" >/dev/null 2>&1 || true
fi
echo "done"
echo ""

echo "### Measured run (${DURATION})"
echo ""
echo '```'
if [ "${TOOL}" = "oha" ]; then
  run_oha "${DURATION}"
else
  run_wrk "${DURATION}"
fi
echo '```'
