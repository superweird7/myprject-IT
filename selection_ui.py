# selection_ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from entry_ui import EntryWindow
from search_ui import SearchWindow
from admin_dashboard_ui import AdminDashboardWindow
from activity_log_ui import ActivityLogWindow
from reports_ui import ReportWindow
from settings_ui import SettingsWindow
import db_ops

class SelectionWindow(QWidget):
    def __init__(self, current_user_id, current_user_role_id, current_user_department=None):
        super().__init__()
        self.setWindowTitle("اختيار العملية")
        self.setGeometry(300, 300, 400, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.current_user_id = current_user_id
        self.current_user_role_id = current_user_role_id
        self.current_user_role = db_ops.get_role_name_by_id(current_user_role_id)
        self.current_user_department = current_user_department
        
        layout = QVBoxLayout(self)
        
        self.btn_entry = QPushButton("إدخال وعرض بيانات الصيانة")
        self.btn_entry.clicked.connect(self.open_entry)
        layout.addWidget(self.btn_entry)
        
        self.btn_search = QPushButton("البحث في بيانات الصيانة")
        self.btn_search.clicked.connect(self.open_search)
        layout.addWidget(self.btn_search)
        
        if self.current_user_role == "admin":
            self.btn_admin_dashboard = QPushButton("لوحة تحكم الأدمن")
            self.btn_admin_dashboard.clicked.connect(self.open_admin_dashboard)
            layout.addWidget(self.btn_admin_dashboard)
            
            self.btn_activity_log = QPushButton("سجل الأنشطة")
            self.btn_activity_log.clicked.connect(self.open_activity_log)
            layout.addWidget(self.btn_activity_log)
            
            self.btn_reports = QPushButton("التقارير والإحصائيات")
            self.btn_reports.clicked.connect(self.open_reports)
            layout.addWidget(self.btn_reports)

        self.btn_settings = QPushButton("الإعدادات")
        self.btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(self.btn_settings)

    def open_entry(self):
        self.entry_window = EntryWindow(
            user_id=self.current_user_id,
            user_role=self.current_user_role,
            user_department=self.current_user_department
        )
        self.entry_window.show()

    def open_search(self):
        self.search_window = SearchWindow(
            user_role=self.current_user_role, 
            user_department=self.current_user_department
        )
        self.search_window.show()

    def open_admin_dashboard(self):
        self.admin_dashboard_window = AdminDashboardWindow(current_user_id=self.current_user_id)
        self.admin_dashboard_window.show()

    def open_activity_log(self):
        self.activity_log_window = ActivityLogWindow()
        self.activity_log_window.show()

    def open_reports(self):
        self.reports_window = ReportWindow()
        self.reports_window.show()

    def open_settings(self):
        dialog = SettingsWindow(self)
        dialog.exec_()