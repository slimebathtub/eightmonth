from data.db import init_db
from data.task_repo import TaskRepository
from core.module.Task import Task, Milestone

init_db()
repo = TaskRepository()

# 1 新增 Task
t = Task(title="hello", priority=2, progress_mode="auto", progress_manual=0)
repo.create_task(t)

# 4 新增 milestone
mid = repo.add_milestone(t.id, Milestone(title="m1", description="demo", sort_order=0))

# 7 完成 milestone
repo.set_milestone_done(mid, True)

# 3 修改 Task
t.title = "hello (edited)"
repo.update_task(t)

# 6 修改 milestone
repo.update_milestone(mid, title="m1 (edited)", description="changed")

# 5 刪 milestone
repo.delete_milestone(mid)

# 2 刪 Task
repo.delete_task(t.id)

