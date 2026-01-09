## ✅ Features in this skeleton

- Add / edit / delete tasks
- Per-task milestones (checklist)
- One-time reminders powered by APScheduler
- Windows notifications via `win10toast` (falls back to Tkinter popup if not available)
- SQLite persistence (no server required)

## 🚀 Quick start (Windows)

1. using py
2. Run the app:

```bat
python app.py
```

### Packaging to .exe (optional)

```bat
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed app.py
```

The executable will be in `dist/app.exe`.

## 🧱 Project layout

```
todo_app/
│
├─ app.py
│
├─ ui/
│   ├─ main_window.py
│   ├─ sidebar.py
│   │
│   ├─ pages/
│   │   ├─ today_page.py
│   │   ├─ notes_page.py
│   │   ├─ future_page.py
│   │   └─ tasks_page.py
│   │
│   ├─ components/
│   │   ├─ task_card.py
│   │   ├─ top_bar.py
│   │   ├─ dialogs.py       # Add Task / Edit Task Dialog
│   │   └─ toggles.py
│   │
│   └─ styles/
│       └─ theme.qss
│
├─ core/
│   ├─ models.py
│   └─ services.py
│
├─ data/ 
│   ├─ db.py
│   └─ repositories.py
│
└─ assets/
    ├─ icons/
    └─ images/

```
