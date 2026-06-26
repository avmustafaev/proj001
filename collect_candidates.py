#!/usr/bin/env python3
"""
1. Из таблицы users_joined достать description с вхождением " • "
2. Извлечь строку до " • " — это username, сохранить в список check-user0
3. Для каждого username из check-user0 проверить auth_block = FALSE,
   такие username добавить в check-user1
4. Сохранить check-user1 в файл candidate1.txt
"""

from db import get_db_connection

SEPARATOR = " • "
OUTPUT_FILE = "candidate1.txt"


def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Ищем строки с description, содержащим " • " и lastlogin не NULL
            cursor.execute(
                "SELECT username, description FROM users_joined "
                "WHERE description LIKE %s AND lastlogin IS NOT NULL",
                (f"%{SEPARATOR}%",)
            )
            rows = cursor.fetchall()

            if not rows:
                print("Нет записей с description, содержащим ' • '.")
                return

            # 2. Формируем check-user0
            check_user0 = []
            for username, description in rows:
                # Извлекаем часть до разделителя
                if SEPARATOR in description:
                    extracted = description.split(SEPARATOR, 1)[0].strip()
                else:
                    extracted = username  # fallback
                check_user0.append(extracted)

            print(f"check-user0 (всего {len(check_user0)}):")
            for u in check_user0:
                print(f"  {u}")

            # 3. Для каждого username проверяем auth_block = FALSE
            check_user1 = []
            for ext_username in check_user0:
                cursor.execute(
                    "SELECT username FROM users_joined "
                    "WHERE username = %s AND auth_block = FALSE",
                    (ext_username,)
                )
                result = cursor.fetchone()
                if result:
                    check_user1.append(result[0])

            print(f"\ncheck-user1 (auth_block = FALSE, всего {len(check_user1)}):")
            for u in check_user1:
                print(f"  {u}")

            # 4. Сохраняем в файл candidate1.txt
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for u in check_user1:
                    f.write(u + "\n")

            print(f"\nФайл {OUTPUT_FILE} сохранён ({len(check_user1)} строк).")

    finally:
        conn.close()


if __name__ == "__main__":
    main()