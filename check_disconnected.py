"""
Скрипт для поиска пар username, где:
1. Берём username с auth_block = true (список check1)
2. Ищем username, у которого в description упоминается имя из check1 (new_username)
3. Если у new_username connected = false — сохраняем пару в файл
"""

import psycopg2
from db import get_db_connection


def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    # =========================================================
    # Шаг 1: достаём username с auth_block = true
    # =========================================================
    cursor.execute("""
        SELECT username
        FROM users_joined
        WHERE auth_block = TRUE
    """)
    rows = cursor.fetchall()
    check1 = [row[0] for row in rows if row[0]]

    print(f"Шаг 1: найдено {len(check1)} username с auth_block = true")
    print("check1:", check1)

    if not check1:
        print("Нет записей с auth_block = true. Завершение.")
        cursor.close()
        conn.close()
        return

    # =========================================================
    # Шаг 2: для каждого имени из check1 ищем new_username
    # =========================================================
    pairs = []

    for name in check1:
        # Ищем username, у которого в description упоминается name
        # Ищем точное совпадение слова в description
        # Используем regex: перед именем начало строки или не буква/цифра/подчёркивание,
        # после имени конец строки или не буква/цифра/подчёркивание
        cursor.execute("""
            SELECT username, connected
            FROM users_joined
            WHERE description ~* %s
        """, (f'(^|[^_[:alnum:]]){name}($|[^_[:alnum:]])',))
        found_rows = cursor.fetchall()

        for new_username, connected in found_rows:
            # Пропускаем, если new_username совпадает с исходным
            if new_username == name:
                continue

            c = False if connected is None else connected

            if not c:
                pairs.append((name, new_username))
                print(f"  Найдена пара: {name} -> {new_username} (connected = {c})")

    # =========================================================
    # Шаг 3: сохраняем результат
    # =========================================================
    with open("check_disconnected_pairs.txt", "w", encoding="utf-8") as f:
        for name, new_username in pairs:
            f.write(f"{name} {new_username}\n")

    print(f"\nИтого пар: {len(pairs)}")
    print("Результат сохранён в check_disconnected_pairs.txt")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()