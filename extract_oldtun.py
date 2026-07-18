#!/usr/bin/env python3
"""
Читает строки (username) из файла vib.txt,
ищет их в таблице users_joined,
извлекает поля ifconfig_push, iroute, description
и сохраняет в oldtun.txt в формате: username | ifconfig_push | iroute | description
"""

from db import get_db_connection

INPUT_FILE = "vib.txt"
OUTPUT_FILE = "oldtun.txt"


def main():
    # Читаем username из vib.txt
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        usernames = [line.strip() for line in f if line.strip()]

    if not usernames:
        print(f"Файл {INPUT_FILE} пуст.")
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT username, ifconfig_push, iroute, description
                FROM users_joined
                WHERE username IN %s
                ORDER BY username
                """,
                (tuple(usernames),)
            )
            rows = cursor.fetchall()

            lines = []
            for username, ifconfig_push, iroute, description in rows:
                ifconfig = ifconfig_push if ifconfig_push else ""
                iroute_val = iroute if iroute else ""
                desc = description if description else ""
                line = f"{username} | {ifconfig} | {iroute_val} | {desc}"
                lines.append(line)

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")

            print(f"Найдено username из {INPUT_FILE} в users_joined: {len(lines)}")
            print(f"Не найдено в БД: {len(usernames) - len(lines)}")
            print(f"Файл {OUTPUT_FILE} сохранён ({len(lines)} строк).")

    finally:
        conn.close()


if __name__ == "__main__":
    main()