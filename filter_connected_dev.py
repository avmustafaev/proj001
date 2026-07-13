#!/usr/bin/env python3
"""
Из таблицы users_joined достать username и description, где connected = TRUE,
и проверить в таблице tunel, что поле dev для этого username
равно tun1, tun2, tun3, tun5, tun6, tun7, tun8 или tun9.

Результат сохраняется в файл candidates_dev.txt в формате: username | description
"""

from db import get_db_connection

ALLOWED_DEV = ("tun1", "tun2", "tun3", "tun5", "tun6", "tun7", "tun8", "tun9")
OUTPUT_FILE = "candidates_dev.txt"


def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT u.username, u.description
                FROM users_joined u
                JOIN tunel t ON u.username = t.username
                WHERE u.connected = TRUE
                  AND t.dev IN %s
                ORDER BY u.username
                """,
                (ALLOWED_DEV,)
            )
            rows = cursor.fetchall()

            if not rows:
                print("Нет подходящих записей.")
                return

            lines = []
            for username, description in rows:
                desc = description if description else ""
                line = f"{username} | {desc}"
                lines.append(line)

            print(f"Найдено username (connected=TRUE, dev в {ALLOWED_DEV}): {len(lines)}")
            for line in lines:
                print(f"  {line}")

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for line in lines:
                    f.write(line + "\n")

            print(f"\nФайл {OUTPUT_FILE} сохранён ({len(lines)} строк).")

    finally:
        conn.close()


if __name__ == "__main__":
    main()