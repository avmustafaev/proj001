#!/usr/bin/env python3
"""
Достаёт из таблицы ipset_up все имена учёток (username),
которые состоят в группе all, и сохраняет их в файл all_group_users.txt.
"""

from db import get_db_connection

GROUP_NAME = "all"
OUTPUT_FILE = "all_group_users.txt"


def main():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT username
                FROM ipset_up
                WHERE group_name = %s
                ORDER BY username
                """,
                (GROUP_NAME,),
            )
            rows = cursor.fetchall()

            if not rows:
                print(f"В группе '{GROUP_NAME}' записей не найдено.")
                return

            usernames = [row[0] for row in rows if row[0]]

            print(f"Учёток в группе '{GROUP_NAME}': {len(usernames)}")
            for username in usernames:
                print(f"  {username}")

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for username in usernames:
                    f.write(username + "\n")

            print(f"\nФайл {OUTPUT_FILE} сохранён ({len(usernames)} строк).")

    finally:
        conn.close()


if __name__ == "__main__":
    main()