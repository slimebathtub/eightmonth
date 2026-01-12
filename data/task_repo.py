from typing import Any, Optional
from core.module.Task import Task
from data.db import get_conn
from core.module.Task import Milestone

def row_to_task(r) -> Task:
    return Task(
        id=r["id"],
        title=r["title"],
        priority=r["priority"],
        progress_mode=r["progress_mode"],
        progress_manual=r["progress_manual"],
        start_date=r["start_date"],
        due_date=r["due_date"],
        milestones=[],
    )

def row_to_milestone(r) -> Milestone:
    return Milestone(
        id = r['id'],
        title = r['title'],
        done = bool(r['done']),
        description=r['description'],
        due_date = r['due_date'],
        sort_order=r['sort_order']
    )

class TaskRepository:
    
    def list_tasks(self) -> list[Task]:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM tasks ORDER BY updated_at DESC").fetchall()
        conn.close()

        tasks = []
        for r in rows:
            tasks.append(Task(
                id=r["id"],
                title=r["title"],
                priority=r["priority"],
                progress_mode=r["progress_mode"],
                progress_manual=r["progress_manual"],
                start_date=r["start_date"],
                due_date=r["due_date"],
                milestones=[]
            ))
        return tasks
    
    def upsert_task(self, task: Task) -> None:
        try:
            pm = int(task.progress_manual)
        except (TypeError, ValueError):
            pm = 0

        conn = get_conn()
        conn.execute(
            """
            INSERT INTO tasks (id, title, priority, progress_mode, progress_manual, start_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              title=excluded.title,
              priority=excluded.priority,
              progress_mode=excluded.progress_mode,
              progress_manual=excluded.progress_manual,
              start_date=excluded.start_date,
              due_date=excluded.due_date,
              updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now')
            """,
            (task.id, task.title, task.priority, task.progress_mode, pm, task.start_date, task.due_date),
        )
        conn.commit()
        conn.close()
    
    """
    def replace_milestones(self, task: Task) -> None:
        conn = get_conn()
        conn.execute("DELETE FROM milestones WHERE task_id=?", (task.id,))

        for idx, m in enumerate(task.milestones):
            conn.execute(
            INSERT INTO milestones (task_id, title, done, due_date, sort_order, description)
            VALUES (?, ?, ?, ?, ?, ?)
            , (task.id, m.title, int(m.done), getattr(m, "due_date", None), idx, m.description))

        conn.commit()
        conn.close()
    """

    
    #---------task action-----------
    def create_task(self, task: Task) -> str:
        self.upsert_task(task)
        return task.id
    
    def update_task(self, task: Task):
        self.upsert_task(task)

    def delete_task(self, task_id: str):
        conn = get_conn()
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()

    #---------milstone action-----------
    def add_milestone(self, task_id: str, milestone: Milestone):
        conn = get_conn()
        cur = conn.execute(
            """
            INSERT INTO milestones (task_id, title, done, description, due_date, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                milestone.title,
                int(bool(milestone.done)),
                milestone.description,
                milestone.due_date,
                milestone.sort_order,
            ),
        )
        conn.commit()
        new_id = int(cur.lastrowid)
        conn.close()
        return new_id

    def delete_milestone(self, milestone_id: int):
        conn = get_conn()
        conn.execute("DELETE FROM milestones WHERE id = ?", (milestone_id,))
        conn.commit()
        conn.close()    
    
    def update_milestone(
        self, 
        milestone_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        sort_order: Optional[int] = None,
        done: Optional[bool] = None,
    ):
        fields: list[str] = []
        params: list[object] = []

        
        if title is not None:
            fields.append("title=?")
            params.append(title)
        if description is not None:
            fields.append("description=?")
            params.append(description)
        if due_date is not None:
            fields.append("due_date=?")
            params.append(due_date)
        if sort_order is not None:
            fields.append("sort_order=?")
            params.append(int(sort_order))
        if done is not None:
            fields.append("done=?")
            params.append(int(bool(done)))
        
        if not fields:
            return

        params.append(milestone_id)

        conn = get_conn()
        conn.execute(f"UPDATE milestones SET {', '.join(fields)} WHERE id=?", params)
        conn.commit()
        conn.close()

    def set_milestone_done(self, milestone_id: int, done: bool):
        conn = get_conn()
        conn.execute('UPDATE milestones SET done=? WHERE id =?', (int(bool(done)), milestone_id))
        conn.commit()
        conn.close()
    
    #---------read info for UI---------------
    def get_task(self, task_id: str):
        conn = get_conn()
        tr = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if tr is None:
            conn.close()
            return None
        
        task = row_to_task(tr)
        mrs = conn.execute(
            "SELECT * FROM milestones WHERE task_id=? ORDER BY sort_order ASC, id ASC",
            (task_id,),
        ).fetchall()
        task.milestones = [row_to_milestone(r) for r in mrs]
        conn.close()
        return task

    def list_tasks_with_milestones(self) -> list[Task]:
        conn = get_conn()

        task_rows = conn.execute(
            "SELECT * FROM tasks ORDER BY updated_at DESC"
        ).fetchall()
        tasks = [row_to_task(r) for r in task_rows]
        by_id = {t.id: t for t in tasks}

        ms_rows = conn.execute(
            "SELECT * FROM milestones ORDER BY task_id, sort_order ASC, id ASC"
        ).fetchall()
        for r in ms_rows:
            tid = r["task_id"]
            if tid in by_id:
                by_id[tid].milestones.append(row_to_milestone(r))

        conn.close()
        return tasks


