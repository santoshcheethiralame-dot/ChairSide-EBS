#!/usr/bin/env bash
# Run as root inside WSL Ubuntu 24.04. Installs Node 20 + yarn, configures MariaDB for Frappe.
set -e
source "$(dirname "$0")/local.env"
if ! command -v node >/dev/null || ! node --version | grep -q '^v20'; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - >/tmp/node.log 2>&1
  apt-get install -y -qq nodejs >>/tmp/node.log 2>&1
fi
command -v yarn >/dev/null || npm install -g yarn >>/tmp/node.log 2>&1
node --version; yarn --version

cat > /etc/mysql/mariadb.conf.d/99-frappe.cnf <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF
systemctl restart mariadb
mariadb -uroot -p"$DB_ROOT_PW" -e "SELECT 1" >/dev/null 2>&1 || \
  mariadb -e "ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('$DB_ROOT_PW'); FLUSH PRIVILEGES;"
systemctl enable --now redis-server >/dev/null 2>&1
echo "system ok"
