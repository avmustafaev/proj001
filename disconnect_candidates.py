"""
Скрипт для поиска username кандидатов на отключение:
1. Берём username и description из users_joined, где connected = true
2. Если в description есть " • ", извлекаем текст до этих символов → check0
3. Из check0 проверяем username в users_joined: если auth_block = false → check1
4. Из check1 проверяем в last_disconnect: disconn_dt старше 24 часов → check2
5. Сохраняем check2 в текстовый файл
"""

import psycopg2
from datetime import datetime, timedelta, timezone
from db import get_db_connection


SEPARATOR = " • "


def main():
    conn = get_db_connection()
    cursor = conn.cursor()

    # =========================================================
    # Шаг 1: username и description из users_joined где connected = true
    # =========================================================
    cursor.execute("""
        SELECT username, description
        FROM users_joined
        WHERE connected = TRUE
    """)
    rows = cursor.fetchall()

    check0 = []
    for username, description in rows:
        if description and SEPARATOR in description:
            # Берём текст до разделителя " • "
            text_before = description.split(SEPARATOR)[0].strip()
            check0.append(text_before)

    print(f"Шаг 1: подключено пользователей: {len(rows)}")
    print(f"Шаг 2: извлечено кандидатов из description: {len(check0)}")
    print("check0:", check0)

    if not check0:
        print("Нет кандидатов. Завершение.")
        cursor.close()
        conn.close()
        return

    # =========================================================
    # Шаг 3: проверяем каждый элемент check0 как username в users_joined
    #         на условие auth_block = false
    # =========================================================
    check1 = []
    for candidate_username in check0:
        cursor.execute("""
            SELECT username
            FROM users_joined
            WHERE username = %s AND auth_block = FALSE
        """, (candidate_username,))
        row = cursor.fetchone()
        if row:
            check1.append(row[0])

    print(f"\nШаг 3: прошли проверку auth_block = false: {len(check1)}")
    print("check1:", check1)

    if not check1:
        print("Нет записей, прошедших проверку. Завершение.")
        cursor.close()
        conn.close()
        return

    # =========================================================
    # Шаг 4: проверяем в last_disconnect disconn_dt старше 24 часов
    # =========================================================
    check2 = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)

    for username in check1:
        cursor.execute("""
            SELECT disconn_dt
            FROM last_disconnect
            WHERE username = %s
        """, (username,))
        row = cursor.fetchone()

        if row and row[0] is not None:
            disconn_dt = row[0]
            # Если disconn_dt без tzinfo — локализуем в UTC
            if disconn_dt.tzinfo is None:
                disconn_dt = disconn_dt.replace(tzinfo=timezone.utc)

            if disconn_dt < cutoff_time:
                check2.append(username)
        else:
            # Если записи в last_disconnect нет — считаем что давно не было
            # и добавляем
            check2.append(username)

    print(f"\nШаг 4: прошли проверку disconn_dt > 24ч: {len(check2)}")
    print("check2:", check2)

    if not check2:
        print("Нет кандидатов для сохранения. Завершение.")
        cursor.close()
        conn.close()
        return

    # =========================================================
    # Шаг 5: сохраняем список в файл
    # =========================================================
    output_file = "candidates.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for username in check2:
            f.write(f"{username}\n")

    print(f"\nСохранено {len(check2)} username в {output_file}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()