# login_ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import db_ops
from selection_ui import SelectionWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول")
        self.setGeometry(200, 200, 400, 200)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("اسم المستخدم:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("كلمة المرور:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المستخدم وكلمة المرور")
            return
        
        user = db_ops.verify_user(username, password)
        if user:
            self.hide()
            self.selection_window = SelectionWindow(
                current_user_id=user['id'],
                current_user_role_id=user['role_id'],
                current_user_department=user['department']
            )
            self.selection_window.show()
        else:
            QMessageBox.critical(self, "فشل", "بيانات الدخول غير صحيحة")