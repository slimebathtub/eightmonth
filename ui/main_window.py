from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.components.sidebar import SideBar
from ui.pages.future_page import FuturePage
from ui.pages.notes_page import NotesPage
from ui.pages.tasks_page import TasksPage
from ui.pages.today_page import TodayPage
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

        self.setCentralWidget(central)

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
        
        




