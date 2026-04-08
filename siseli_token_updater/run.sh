#!/usr/bin/env sh
set -e

# === Siseli Token Updater ===
# Читаем настройки из /data/options.json (стандартный путь HA аддонов)
OPTIONS_FILE="/data/options.json"

ACCOUNT=$(jq -r '.account' "$OPTIONS_FILE")
PASSWORD=$(jq -r '.password' "$OPTIONS_FILE")
INTERVAL=$(jq -r '.interval_minutes' "$OPTIONS_FILE")

export ACCOUNT
export PASSWORD

echo "================================================"
echo "Siseli Token Updater v0.1.1"
echo "Аккаунт: ${ACCOUNT}"
echo "Интервал: ${INTERVAL} минут"
echo "================================================"

# Главный цикл
while true; do
    echo ""
    echo "[$(date)] Обновляю токен..."

    timeout 120 node /app/get_token.js || {
        echo "[$(date)] ОШИБКА: скрипт завершился с ошибкой"
        echo "[$(date)] Повторю через 5 минут..."
        sleep 300
        continue
    }

    echo "[$(date)] Жду ${INTERVAL} минут до следующего обновления..."
    sleep $((INTERVAL * 60))
done
