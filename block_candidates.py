#!/usr/bin/env python3
"""
Читает строки из candidates.txt и для каждого username
в таблице users_joined выставляет auth_block = TRUE.
"""

from db import get_db_connection

FILE = "candidates.txt"

def main():
    # Читаем username'ы из файла
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            usernames = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Файл {FILE} не найден.")
        return

    if not usernames:
        print("Файл пуст или не содержит username'ов.")
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            updated = 0
            for username in usernames:
                cursor.execute(
                    "UPDATE users_joined SET auth_block = TRUE WHERE username = %s",
                    (username,)
                )
                if cursor.rowcount > 0:
                    updated += 1
                    print(f"  [OK] {username} — заблокирован")
                else:
                    print(f"  [--] {username} — не найден в БД")
        conn.commit()
        print(f"\nГотово. Обработано строк: {len(usernames)}, обновлено: {updated}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()