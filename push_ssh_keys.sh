#!/usr/bin/env bash
#
# Читает IP-адреса из файла (по умолчанию stationary_ips.txt)
# и для каждого IP копирует локальный публичный ключ на роутер.
# Авторизация на роутере выполняется по приватному ключу
# ~/.ssh/irz_collector_key, подключение на порт 9827.
#
# Перед добавлением проверяется, есть ли ключ уже в
# ~/.ssh/authorized_keys на роутере — повторно он НЕ дописывается.
#
#   cat ~/.ssh/id_rsa_router.pub | ssh -i ~/.ssh/irz_collector_key -p 9827 \
#       -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
#       root@<IP> "..."
#
# ВАЖНО: работает с любого хоста, в том числе со старыми версиями OpenSSH
# (accept-new поддерживается с 7.6, для более старых используется no).
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

# Определяем версию OpenSSH — accept-new поддерживается с 7.6, иначе no.
SSH_VERSION=$(ssh -V 2>&1 | sed -n 's/^OpenSSH_\([0-9][0-9]*\)\.\([0-9][0-9]*\).*/\1\2/p')
if [[ "$SSH_VERSION" =~ ^[0-9]+$ ]] && (( 10#$SSH_VERSION >= 76 )); then
    HOST_KEY_CHECKING="accept-new"
else
    HOST_KEY_CHECKING="no"
fi

# Порт SSH (все роутеры слушают нестандартный порт 9827).
SSH_PORT="${SSH_PORT:-9827}"

# Логин на роутер (по умолчанию root — как в исходной команде).
SSH_USER="${SSH_USER:-root}"

# Опции ssh:
#  -i <ключ>                    — авторизация по приватному ключу
#  -p <порт>                    — нестандартный порт
#  BatchMode=yes                — не ждать ввода пароля (не зависнуть)
#  ConnectTimeout=5             — таймаут подключения 5 сек
#  StrictHostKeyChecking=...    — авто-приём ключа нового хоста
#  UserKnownHostsFile=/dev/null — не трогать known_hosts (как в алиасе)
#  LogLevel=ERROR               — показывать только ошибки
SSH_OPTS=(
    -i "$PRIV_KEY"
    -p "$SSH_PORT"
    -o BatchMode=yes
    -o ConnectTimeout=5
    -o StrictHostKeyChecking="$HOST_KEY_CHECKING"
    -o UserKnownHostsFile=/dev/null
    -o LogLevel=ERROR
)

REMOTE_CMD="mkdir -p ~/.ssh && chmod 700 ~/.ssh && KEY=\$(cat) && (grep -qxF \"\$KEY\" ~/.ssh/authorized_keys 2>/dev/null && echo __ALREADY__ || (printf '%s\n' \"\$KEY\" >> ~/.ssh/authorized_keys && echo __ADDED__)) && chmod 600 ~/.ssh/authorized_keys"

total=0
ok=0
skip=0
fail=0

while IFS= read -r addr; do
    # пропускаем пустые строки и комментарии (#)
    [[ -z "$addr" || "$addr" == \#* ]] && continue

    total=$((total + 1))

    result=$(cat "$KEY_FILE" | ssh "${SSH_OPTS[@]}" "${SSH_USER}@$addr" "$REMOTE_CMD" 2>/dev/null)
    rc=$?

    if (( rc != 0 )); then
        fail=$((fail + 1))
        echo "[FAIL] $addr"
    elif [[ "$result" == *__ALREADY__* ]]; then
        skip=$((skip + 1))
        echo "[SKIP] $addr — ключ уже есть в authorized_keys"
    else
        ok=$((ok + 1))
        echo "[OK]   $addr — ключ добавлен"
    fi
done < "$IP_FILE"

echo
echo "Готово. Обработано: $total, добавлено: $ok, уже было: $skip, ошибок: $fail"