# admin_dashboard_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QTextEdit, QFileDialog, QDialog
)
from PyQt5.QtCore import Qt
import db_ops
import os
from datetime import datetime
from user_mgmt_ui import UserManagementWindow
from user_edit_ui import UserEditWindow
from department_mgmt_ui import DepartmentManagementWindow
from trash_ui import TrashWindow
from users_trash_ui import UsersTrashWindow

class AdminDashboardWindow(QWidget):
    def __init__(self, current_user_id):
        super().__init__()
        self.current_user_id = current_user_id
        self.setWindowTitle("لوحة تحكم الأدمن")
        self.setGeometry(100, 100, 1200, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        welcome_label = QLabel("لوحة تحكم الأدمن")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(welcome_label)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.overview_tab = QWidget()
        self.tabs.addTab(self.overview_tab, "نظرة عامة")
        self.setup_overview_tab()
        
        self.users_tab = QWidget()
        self.tabs.addTab(self.users_tab, "الإدارة")
        self.setup_users_tab()
        
        self.backup_restore_tab = QWidget()
        self.tabs.addTab(self.backup_restore_tab, "نسخ احتياطي واستعادة")
        self.setup_backup_restore_tab()
        
        self.refresh_dashboard()

    def setup_overview_tab(self):
        layout = QVBoxLayout(self.overview_tab)
        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        layout.addWidget(self.overview_text)

    def setup_users_tab(self):
        layout = QVBoxLayout(self.users_tab)
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["المعرف", "اسم المستخدم", "الصلاحية", "القسم"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.users_table)
        
        user_actions_layout = QHBoxLayout()
        self.btn_add_user = QPushButton("إضافة مستخدم")
        self.btn_add_user.setObjectName("AddButton")
        self.btn_add_user.clicked.connect(self.open_user_management)
        user_actions_layout.addWidget(self.btn_add_user)
        
        self.btn_edit_user = QPushButton("تعديل المستخدم")
        self.btn_edit_user.clicked.connect(self.open_edit_user_dialog)
        self.btn_edit_user.setDisabled(True)
        user_actions_layout.addWidget(self.btn_edit_user)
        
        self.btn_delete_user = QPushButton("حذف المستخدم")
        self.btn_delete_user.setObjectName("DeleteButton")
        self.btn_delete_user.clicked.connect(self.delete_selected_user)
        self.btn_delete_user.setDisabled(True)
        user_actions_layout.addWidget(self.btn_delete_user)
        
        user_actions_layout.addStretch()
        
        self.btn_manage_depts = QPushButton("إدارة الأقسام")
        self.btn_manage_depts.clicked.connect(self.open_department_management)
        user_actions_layout.addWidget(self.btn_manage_depts)
        
        self.btn_open_trash = QPushButton("سلة محذوفات السجلات")
        self.btn_open_trash.clicked.connect(self.open_trash_bin)
        user_actions_layout.addWidget(self.btn_open_trash)
        
        self.btn_open_users_trash = QPushButton("سلة محذوفات المستخدمين")
        self.btn_open_users_trash.clicked.connect(self.open_users_trash_bin)
        user_actions_layout.addWidget(self.btn_open_users_trash)
        
        layout.addLayout(user_actions_layout)
        
        self.users_table.itemSelectionChanged.connect(self.update_user_action_buttons_state)

    def setup_backup_restore_tab(self):
        layout = QVBoxLayout(self.backup_restore_tab)
        
        backup_label = QLabel("<b>إنشاء نسخة احتياطية:</b>")
        layout.addWidget(backup_label)
        self.btn_create_backup = QPushButton("إنشاء نسخة احتياطية")
        self.btn_create_backup.clicked.connect(self.create_backup)
        layout.addWidget(self.btn_create_backup)
        
        restore_label = QLabel("<b>استعادة من نسخة احتياطية:</b>")
        layout.addWidget(restore_label)
        restore_btn_layout = QHBoxLayout()
        self.btn_select_restore_file = QPushButton("اختر ملف النسخة الاحتياطية")
        self.btn_select_restore_file.clicked.connect(self.select_restore_file)
        restore_btn_layout.addWidget(self.btn_select_restore_file)
        self.btn_perform_restore = QPushButton("تنفيذ الاستعادة")
        self.btn_perform_restore.clicked.connect(self.perform_restore)
        self.btn_perform_restore.setDisabled(True)
        restore_btn_layout.addWidget(self.btn_perform_restore)
        layout.addLayout(restore_btn_layout)
        
        self.status_label = QLabel("الحالة: جاهز")
        layout.addWidget(self.status_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel("سجل العمليات:"))
        layout.addWidget(self.log_text)

    def refresh_dashboard(self):
        self.load_overview_data()
        self.load_users_data()
        
    def load_overview_data(self):
        total_records = db_ops.get_total_record_count()
        total_users = db_ops.get_total_user_count()
        admin_count = db_ops.get_user_role_count('admin')
        user_count = db_ops.get_user_role_count('user')
        overview_content = (f"<b>إحصائيات عامة:</b><ul>"
                            f"<li><b>إجمالي سجلات الصيانة:</b> {total_records}</li>"
                            f"<li><b>إجمالي المستخدمين:</b> {total_users}</li>"
                            f"<li><b>عدد الأدمنز:</b> {admin_count}</li>"
                            f"<li><b>عدد المستخدمين العاديين:</b> {user_count}</li></ul>")
        self.overview_text.setHtml(overview_content)

    def load_users_data(self):
        try:
            users = db_ops.fetch_all_users()
            self.users_table.setRowCount(len(users))
            for row_idx, user_data in enumerate(users):
                self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user_data.get('id', ''))))
                self.users_table.setItem(row_idx, 1, QTableWidgetItem(user_data.get('username', '')))
                self.users_table.setItem(row_idx, 2, QTableWidgetItem(user_data.get('role_name', '')))
                self.users_table.setItem(row_idx, 3, QTableWidgetItem(user_data.get('department', '')))
            self.users_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة المستخدمين:\n{str(e)}")

    def open_user_management(self):
        dialog = UserManagementWindow(self.current_user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_dashboard()

    def open_edit_user_dialog(self):
        user_data = self.get_selected_user_data()
        if not user_data: return
        dialog = UserEditWindow(user_data, self.current_user_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_dashboard()

    def delete_selected_user(self):
        user_data = self.get_selected_user_data()
        if not user_data: return
        if user_data['id'] == self.current_user_id:
            QMessageBox.warning(self, "غير مسموح", "لا يمكنك حذف حسابك الخاص.")
            return
        reply = QMessageBox.question(self, 'تأكيد', f"هل أنت متأكد أنك تريد نقل المستخدم '{user_data['username']}' إلى سلة المحذوفات؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = db_ops.delete_user(user_data['id'], self.current_user_id)
            QMessageBox.information(self, "نتيجة", msg)
            self.refresh_dashboard()

    def open_department_management(self):
        dialog = DepartmentManagementWindow(self.current_user_id, self)
        dialog.exec_()
        self.refresh_dashboard()

    def open_trash_bin(self):
        dialog = TrashWindow(self.current_user_id, self)
        dialog.exec_()
        self.refresh_dashboard()

    def open_users_trash_bin(self):
        dialog = UsersTrashWindow(self.current_user_id, self)
        dialog.exec_()
        self.refresh_dashboard()
        
    def get_selected_user_data(self):
        selected_rows = self.users_table.selectionModel().selectedRows()
        if not selected_rows: return None
        row = selected_rows[0].row()
        return {'id': int(self.users_table.item(row, 0).text()), 'username': self.users_table.item(row, 1).text(), 'role_name': self.users_table.item(row, 2).text(), 'department': self.users_table.item(row, 3).text()}

    def update_user_action_buttons_state(self):
        is_user_selected = bool(self.users_table.selectedItems())
        self.btn_edit_user.setDisabled(not is_user_selected)
        self.btn_delete_user.setDisabled(not is_user_selected)

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def create_backup(self):
        default_filename = f"maintenance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        file_path, _ = QFileDialog.getSaveFileName(self, "حفظ النسخة الاحتياطية", default_filename, "SQL Files (*.sql)")
        if file_path:
            if not file_path.lower().endswith('.sql'):
                file_path += '.sql'
            self.status_label.setText("الحالة: جاري إنشاء النسخة الاحتياطية...")
            self.log_message(f"بدء إنشاء النسخة الاحتياطية في: {file_path}")
            success, msg = db_ops.backup_database(file_path)
            if success:
                self.status_label.setText("الحالة: تم الإنشاء بنجاح")
                QMessageBox.information(self, "نجاح", msg)
            else:
                self.status_label.setText("الحالة: فشل")
                QMessageBox.critical(self, "خطأ", msg)
            self.log_message(msg)

    def select_restore_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملف النسخة الاحتياطية", "", "SQL Files (*.sql)")
        if file_path:
            self.restore_file_path = file_path
            self.btn_perform_restore.setDisabled(False)
            self.log_message(f"تم اختيار ملف الاستعادة: {os.path.basename(file_path)}")
            self.status_label.setText(f"الحالة: ملف مختار - {os.path.basename(file_path)}")

    def perform_restore(self):
        if not hasattr(self, 'restore_file_path') or not self.restore_file_path:
            QMessageBox.warning(self, "خطأ", "لم يتم اختيار ملف استعادة.")
            return
        reply = QMessageBox.question(self, 'تأكيد الاستعادة','هل أنت متأكد أنك تريد استعادة هذا الملف؟\nسيؤدي هذا إلى الكتابة فوق جميع البيانات الحالية!',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.status_label.setText("الحالة: جاري استعادة النسخة الاحتياطية...")
            self.log_message(f"بدء استعادة من: {self.restore_file_path}")
            success, msg = db_ops.restore_database(self.restore_file_path)
            if success:
                self.status_label.setText("الحالة: تمت الاستعادة بنجاح")
                QMessageBox.information(self, "نجاح", msg)
                self.refresh_dashboard()
            else:
                self.status_label.setText("الحالة: فشل")
                QMessageBox.critical(self, "خطأ", msg)
            self.log_message(msg)