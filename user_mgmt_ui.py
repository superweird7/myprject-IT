# user_mgmt_ui.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import db_ops

class UserManagementWindow(QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مستخدم جديد")
        self.setLayoutDirection(Qt.RightToLeft)
        self.current_user_id = current_user_id
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("اسم المستخدم الجديد:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("كلمة المرور:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("الصلاحية:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        layout.addWidget(self.role_combo)
        layout.addWidget(QLabel("القسم:"))
        self.department_combo = QComboBox()
        self.populate_departments()
        layout.addWidget(self.department_combo)
        self.add_button = QPushButton("إضافة مستخدم")
        self.add_button.setObjectName("AddButton")
        self.add_button.clicked.connect(self.add_user)
        layout.addWidget(self.add_button)

    def populate_departments(self):
        self.department_combo.addItems(db_ops.get_all_departments())

    def add_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()
        department = self.department_combo.currentText()
        if not username or not password or not department:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال جميع البيانات المطلوبة")
            return
        success, msg = db_ops.add_user(username, password, role, department, self.current_user_id)
        QMessageBox.information(self, "نتيجة", msg)
        if success: self.accept()