import sqlite3
from data.db import get_conn


class RelaxRepository:
    # ---- relax_item ----
    def list_relax_items(self) -> list[sqlite3.Row]:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM relax_item ORDER BY title ASC;")
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_relax_item(self, title: str) -> int:
        title = title.strip()
        if not title:
            raise ValueError("Relax title cannot be empty")

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO relax_item (title) VALUES (?);", (title,))
            conn.commit()
            new_id = cur.lastrowid
        except sqlite3.IntegrityError as e:
            # title UNIQUE 重複
            conn.close()
            raise
        conn.close()
        return int(new_id)

    def delete_relax_item(self, relax_id: int) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM relax_item WHERE id = ?;", (relax_id,))
        conn.commit()
        conn.close()

    # ---- today_relax ----
    def list_today_relax_ids(self, date_str: str) -> set[int]:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT relax_id FROM today_relax WHERE date = ?;", (date_str,))
        rows = cur.fetchall()
        conn.close()
        return {int(r["relax_id"]) for r in rows}

    def add_to_today(self, date_str: str, relax_id: int) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO today_relax (date, relax_id, is_done) VALUES (?, ?, 0);",
            (date_str, relax_id),
        )
        conn.commit()
        conn.close()

    def remove_from_today(self, date_str: str, relax_id: int) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM today_relax WHERE date = ? AND relax_id = ?;", (date_str, relax_id))
        conn.commit()
        conn.close()

    def toggle_today_done(self, date_str: str, relax_id: int) -> int:
        """切換今天這個 relax 的完成狀態，回傳 new_is_done(0/1)"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO today_relax(date, relax_id, is_done)
            VALUES (?, ?, 1)
            ON CONFLICT(date, relax_id) DO UPDATE SET
              is_done = CASE WHEN is_done = 1 THEN 0 ELSE 1 END
            ;
            """,
            (date_str, relax_id),
        )
        conn.commit()
        cur.execute("SELECT is_done FROM today_relax WHERE date = ? AND relax_id = ?;", (date_str, relax_id))
        row = cur.fetchone()
        conn.close()
        return int(row["is_done"]) if row else 0
