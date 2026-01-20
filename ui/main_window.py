from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.components.sidebar import SideBar
from ui.pages.future_page import FuturePage
from ui.pages.notes_page import NotesPage
from ui.pages.tasks_page import TasksPage
from ui.pages.today_page import TodayPage
from PySide6.QtWidgets import QMessageBox

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QObject, QEvent
from PySide6.QtWidgets import QApplication, QWidget

from PySide6.QtGui import QFontDatabase


class _WindowSpy(QObject):
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Show, QEvent.Hide):
            if isinstance(obj, QWidget) and obj.isWindow():
                txt = getattr(obj, "text", lambda: "")()
                parent = obj.parent()
                pname = parent.__class__.__name__ if parent else None
                print(f"[WIN] {event.type()} {obj.__class__.__name__} title='{obj.windowTitle()}' text='{txt}' parent={pname} obj={hex(id(obj))}")
        return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("[MainWindow] init")


        self.setWindowTitle("Test")
        self.resize(900,600)

        central = QWidget()
        side_content_layout = QHBoxLayout()
        
        # sidebar
        self.sidebar = SideBar()

        # center content area: stack ( to switch between pages )
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: rgb(0,0,0);")

        self.pages = {
            "notes": NotesPage(),
            "today": TodayPage(),
            "future": FuturePage(),
            "tasks": TasksPage()
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        # set up the default page
        self.stack.setCurrentWidget(self.pages["today"])
        
        # received signal from sidebar
        self.sidebar.page_changed.connect(self.on_page_changed)

        side_content_layout.addWidget(self.sidebar)
        side_content_layout.addWidget(self.stack)

        central.setLayout(side_content_layout)
        side_content_layout.setStretch(0, 1)
        side_content_layout.setStretch(1, 4)

        self.pages['future'].open_task_request.connect(self._open_task_from_future)

        self.setCentralWidget(central)
        
        self._win_spy = _WindowSpy()
        QApplication.instance().installEventFilter(self._win_spy)
        
        self._load_styles()
        self._load_fonts()
    

    def _load_styles(self):

        def load_qss(*paths):
            css = ""
            for p in paths:
                with open(p, "r", encoding="utf-8") as f:
                    css += f.read() + "\n"
            return css

        self.setStyleSheet(load_qss(
            "ui/style/main.qss",
            "ui/style/sidebar.qss"
        ))

    def _load_fonts(self):
        print("[fonts] loading...")
        font_id = QFontDatabase.addApplicationFont("assets/font/ProtestRevolution-Regular.ttf")
        print("[fonts] font_id =", font_id)
        print("[fonts] families =", QFontDatabase.applicationFontFamilies(font_id))

    
    
    def open_task_request(self, task_id: str, milestone_id: int):
        self.sidebar.set_active("tasks")          # 如果你有高亮
        self.stack.setCurrentWidget(self.pages["tasks"])

        # 2) 叫 TasksPage 顯示那個 task
        self.pages["tasks"].open_task(task_id, milestone_id)

    def switch_page(self, page_name: str):
        page = self.pages.get(page_name)
        if page:
            self.stack.setCurrentWidget(page)
        
    def on_page_changed(self, key: str):
        if key == "today":
            self.pages["today"].reload_today()
        if key == "tasks":
            self.pages["tasks"].reload_tasks()

        self.stack.setCurrentWidget(self.pages[key])
        return
    
    def _open_task_from_future(self, task_id: str, milestone_id: int):
        # 1) switch page
        self.switch_page("tasks")  # or stack.setCurrentWidget(self.tasks_page)
        # 2) select & highlight
        self.pages["tasks"].select_task(task_id, milestone_id)
            




