#!/usr/bin/env python3
"""
Достаёт IP-адреса из таблицы users_joined:
- у юзера connected = TRUE
- в таблице ipset_up у этого username group_name = 'stationary'
- IP берётся из поля ifconfig_push (формат: "IP маска", берём первую часть)

Результат сохраняется в файл stationary_ips.txt (по одному IP на строку).
"""

from db import get_db_connection

GROUP_NAME = "stationary"
OUTPUT_FILE = "stationary_ips.txt"


def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.username, split_part(u.ifconfig_push, ' ', 1) AS ip
                FROM users_joined u
                JOIN ipset_up i ON i.username = u.username AND i.group_name = %s
                WHERE u.connected = TRUE
                  AND u.ifconfig_push IS NOT NULL
                  AND u.ifconfig_push <> ''
                ORDER BY ip
                """,
                (GROUP_NAME,),
            )
            rows = cursor.fetchall()

            if not rows:
                print("Подходящих записей не найдено.")
                return

            # Уникальные IP в том же порядке, что и выборка
            seen = set()
            ips = []
            for username, ip in rows:
                if ip and ip not in seen:
                    seen.add(ip)
                    ips.append(ip)
                print(f"  {username} -> {ip}")

            print(f"\nНайдено IP-адресов (уникальных): {len(ips)}")

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for ip in ips:
                    f.write(ip + "\n")

            print(f"Файл {OUTPUT_FILE} сохранён ({len(ips)} строк).")

    finally:
        conn.close()


if __name__ == "__main__":
    main()