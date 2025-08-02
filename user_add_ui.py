from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from db_ops import add_user

class UserAddWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("إضافة مستخدم")
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.role_input = QComboBox()
        self.role_input.addItems(["admin", "user"])
        self.dept_input = QLineEdit()

        self.add_btn = QPushButton("إضافة المستخدم")
        self.add_btn.clicked.connect(self.add_user)

        layout.addWidget(QLabel("اسم المستخدم"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("كلمة المرور"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("الصلاحية"))
        layout.addWidget(self.role_input)
        layout.addWidget(QLabel("القسم"))
        layout.addWidget(self.dept_input)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_input.currentText()
        department = self.dept_input.text()

        role_id = 1 if role == "admin" else 2
        add_user(username, password, role_id, department)
        QMessageBox.information(self, "تم", "تمت إضافة المستخدم بنجاح")
