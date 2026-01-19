from data.db import get_conn
from core.module.note import Note
from typing import Optional

class NoteRepository:

    def list_notes(self) -> list[Note]:
        conn = get_conn()
        rows = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM note ORDER BY updated_at DESC, id DESC"
        ).fetchall()

        notes = []
        for row in rows:
            notes.append(Note(
                id=row["id"],
                title=row["title"] or "",
                content=row["content"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            ))
        conn.close()
        return notes
    
    def create_note(self, title: str, content: str) -> Note:
        conn = get_conn()
        cur = conn.execute(
            "INSERT INTO note (title, content) VALUES (?, ?)",
            (title, content),
        )
        note_id = int(cur.lastrowid)
        conn.commit()

        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM note WHERE id=?",
            (note_id,),
        ).fetchone()
        conn.close()

        return Note(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    
    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        conn = get_conn()
        cur = conn.execute("SELECT * FROM note WHERE id = ?", (note_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Note(
                id=row["id"],
                title=row["title"],
                content=row["content"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
        return None
    
    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None) -> None:
        conn = get_conn()
        cur = conn.cursor()
        fields = []
        params = []
        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if content is not None:
            fields.append("content = ?")
            params.append(content)
        if title is None and content is None:
            conn.close()
            return
        if fields:
            params.append(note_id)
            cur.execute(
                f"UPDATE note SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                params,
            )
            conn.commit()
        conn.close()
    
    def delete_note(self, note_id: int) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM note WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()

    