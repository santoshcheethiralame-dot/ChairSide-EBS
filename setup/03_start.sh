#!/usr/bin/env bash
# Start the ERPNext dev server (web on :8000, socketio, workers, scheduler). Run as the normal WSL user.
source "$(dirname "$0")/local.env"
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$BENCH_DIR" || exit 1
for c in config/redis_cache.conf config/redis_queue.conf; do
  port=$(awk '/^port/{print $2}' "$c")
  redis-cli -p "$port" ping >/dev/null 2>&1 || redis-server "$c" --daemonize yes
done
grep -q '^redis' Procfile && sed -i '/^redis/d' Procfile
exec bench start
