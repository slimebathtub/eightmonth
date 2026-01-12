from core.module.Task import Milestone, Task


def test_milestone_defaults():
    m = Milestone("A")
    assert m.title == "A"
    assert m.done is False
    assert m.description == ""
    assert m.weight == 1


def test_task_defaults_when_missing_keys():
    t = Task({})
    assert t.title == ""
    assert t.priority == 3
    assert t.progress_mode == "auto"
    assert t.progress_manual == 0
    assert t.milestones == []


def test_task_milestone_normalization():
    m1 = Milestone("A", True)
    m2 = {"title": "B", "done": False, "description": "", "weight": 2}
    t = Task({"milestones": [m1, m2]})
    assert len(t.milestones) == 2
    assert isinstance(t.milestones[0], Milestone)
    assert isinstance(t.milestones[1], Milestone)


def test_progress_manual_clamped():
    t = Task({"progress_mode": "manual", "progress_manual": 120})
    assert t.progress() == 100
    t = Task({"progress_mode": "manual", "progress_manual": -5})
    assert t.progress() == 0


def test_progress_auto_weighted():
    t = Task({
        "milestones": [
            {"title": "A", "done": True, "weight": 2},
            {"title": "B", "done": False, "weight": 1},
        ]
    })
    assert t.progress() == 67


def test_progress_auto_no_milestones():
    t = Task({})
    assert t.progress() == 0


def run_all():
    test_milestone_defaults()
    test_task_defaults_when_missing_keys()
    test_task_milestone_normalization()
    test_progress_manual_clamped()
    test_progress_auto_weighted()
    test_progress_auto_no_milestones()


if __name__ == "__main__":
    run_all()
    print("All Task/Milestone tests passed.")
