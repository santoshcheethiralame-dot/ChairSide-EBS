#!/usr/bin/env bash
# Run as the normal WSL user (carbo). Installs bench, Frappe + ERPNext v15, creates the site.
set -e
source "$(dirname "$0")/local.env"
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
command -v uv >/dev/null || pipx install uv
command -v bench >/dev/null || pipx install frappe-bench
cd "$HOME"
if [ ! -d "$BENCH_DIR" ]; then
  bench init --frappe-branch version-15 --skip-redis-config-generation frappe-bench
fi
cd "$BENCH_DIR"
bench setup redis >/dev/null 2>&1 || true
[ -d apps/erpnext ] || bench get-app --branch version-15 erpnext
# the installer enqueues jobs: bench's own redis (cache :13000, queue :11000) must be up
for c in config/redis_cache.conf config/redis_queue.conf; do redis-server "$c" --daemonize yes; done
if [ "$1" = "--fresh" ] && [ -d "sites/$SITE" ]; then
  bench drop-site "$SITE" --force --db-root-username root --db-root-password "$DB_ROOT_PW" --no-backup
fi
if [ ! -d "sites/$SITE" ]; then
  bench new-site "$SITE" --db-root-username root --db-root-password "$DB_ROOT_PW" --admin-password "$ADMIN_PW"
fi
bench --site "$SITE" list-apps | grep -q erpnext || bench --site "$SITE" install-app erpnext
bench --site "$SITE" enable-scheduler
bench --site "$SITE" set-config developer_mode 0
bench use "$SITE"
echo "BENCH DONE"
