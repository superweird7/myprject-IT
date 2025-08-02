# main_window_ui.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

# Import all the panels
from entry_ui import EntryWindow
from search_ui import SearchWindow
from admin_dashboard_ui import AdminDashboardWindow
from reports_ui import ReportWindow
from activity_log_ui import ActivityLogWindow

class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info = user_info
        
        self.setWindowTitle("نظام توثيق الصيانة")
        self.setGeometry(50, 50, 1800, 950)
        self.setObjectName("MainWindow")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setIconSize(QSize(32, 32))
        layout.addWidget(self.sidebar)

        # Content Area
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)

        # Connect sidebar selection to content switching
        self.sidebar.currentItemChanged.connect(self.switch_panel)

        self.populate_sidebar()

    def populate_sidebar(self):
        # --- Create instances of all panels ---
        self.entry_panel = EntryWindow(
            user_id=self.user_info['id'],
            user_role=self.user_info['role_name'],
            user_department=self.user_info['department']
        )
        self.search_panel = SearchWindow(
            user_role=self.user_info['role_name'],
            user_department=self.user_info['department']
        )
        
        # --- Add panels to content stack and sidebar ---
        self.add_panel("إدخال البيانات", QStyle.SP_FileIcon, self.entry_panel)
        self.add_panel("بحث", QStyle.SP_FileDialogInfoView, self.search_panel)
        
        if self.user_info['role_name'] == 'admin':
            self.reports_panel = ReportWindow()
            self.activity_log_panel = ActivityLogWindow()
            self.admin_dashboard_panel = AdminDashboardWindow(self.user_info['id'])

            self.add_panel("التقارير", QStyle.SP_FileDialogDetailedView, self.reports_panel)
            self.add_panel("لوحة التحكم", QStyle.SP_DesktopIcon, self.admin_dashboard_panel)
            self.add_panel("سجل الأنشطة", QStyle.SP_DialogNormalButton, self.activity_log_panel)
            
        self.sidebar.setCurrentRow(0)

    def add_panel(self, name, icon_enum, widget):
        item = QListWidgetItem(name)
        icon = self.style().standardIcon(icon_enum)
        item.setIcon(icon)
        item.setTextAlignment(Qt.AlignCenter)
        item.setSizeHint(QSize(60, 60))
        
        self.sidebar.addItem(item)
        self.content_stack.addWidget(widget)

    def switch_panel(self, current, previous):
        if current:
            index = self.sidebar.row(current)
            self.content_stack.setCurrentIndex(index)