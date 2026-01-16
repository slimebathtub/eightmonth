

from data.db import get_conn


class TodayRepository:
    
    def get_done(self, date_str: str, milestone_id: int) -> bool:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT is_done FROM today_item WHERE date = ? AND milestone_id = ?;",
            (date_str, milestone_id),
        )
        row = cur.fetchone()
        conn.close()
        return row["is_done"] if row else False
    

    def set_done(self, date_str: str, milestone_id: int, is_done: bool) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO today_item (date, milestone_id, is_done)
            VALUES (?, ?, ?)
            ON CONFLICT(date, milestone_id) DO UPDATE SET
              is_done = excluded.is_done
            ;
            """,
            (date_str, milestone_id, int(is_done)),
        )
        conn.commit()
        conn.close()