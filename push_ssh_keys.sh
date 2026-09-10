#!/usr/bin/env bash
#
# Читает IP-адреса из файла (по умолчанию stationary_ips.txt)
# и для каждого IP копирует локальный публичный ключ на роутер.
# Авторизация на роутере выполняется по приватному ключу
# ~/.ssh/irz_collector_key.
#
#   cat ~/.ssh/id_rsa_router.pub | ssh -i ~/.ssh/irz_collector_key root@<IP> \
#       "mkdir -p ~/.ssh && chmod 700 ~/.ssh && \
#        cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
#
# Использование:
#   ./push_ssh_keys.sh [файл_с_ip] [путь_к_публичному_ключу] [путь_к_приватному_ключу]
#
# Пример:
#   ./push_ssh_keys.sh
#   ./push_ssh_keys.sh my_ips.txt ~/.ssh/id_ed25519.pub ~/.ssh/irz_collector_key

set -u

IP_FILE="${1:-stationary_ips.txt}"
KEY_FILE="${2:-$HOME/.ssh/id_rsa_router.pub}"
PRIV_KEY="${3:-$HOME/.ssh/irz_collector_key}"

if [[ ! -f "$IP_FILE" ]]; then
    echo "ОШИБКА: файл с IP '$IP_FILE' не найден."
    exit 1
fi

if [[ ! -f "$KEY_FILE" ]]; then
    echo "ОШИБКА: файл публичного ключа '$KEY_FILE' не найден."
    exit 1
fi

if [[ ! -f "$PRIV_KEY" ]]; then
    echo "ОШИБКА: файл приватного ключа '$PRIV_KEY' не найден."
    exit 1
fi

# Опции ssh:
#  -i <ключ>                    — авторизация по приватному ключу
#  BatchMode=yes                — не ждать ввода пароля (не зависнуть)
#  ConnectTimeout=5             — таймаут подключения 5 сек
#  StrictHostKeyChecking=accept-new — автоматически принимать ключ нового хоста
#  LogLevel=ERROR               — показывать только ошибки
SSH_OPTS=(
    -i "$PRIV_KEY"
    -o BatchMode=yes
    -o ConnectTimeout=5
    -o StrictHostKeyChecking=accept-new
    -o LogLevel=ERROR
)

REMOTE_CMD="mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

total=0
ok=0
fail=0

while IFS= read -r addr; do
    # пропускаем пустые строки и комментарии (#)
    [[ -z "$addr" || "$addr" == \#* ]] && continue

    total=$((total + 1))

    if cat "$KEY_FILE" | ssh "${SSH_OPTS[@]}" "root@$addr" "$REMOTE_CMD" 2>/dev/null; then
        ok=$((ok + 1))
        echo "[OK]   $addr"
    else
        fail=$((fail + 1))
        echo "[FAIL] $addr"
    fi
done < "$IP_FILE"

echo
echo "Готово. Обработано: $total, успешно: $ok, ошибок: $fail"