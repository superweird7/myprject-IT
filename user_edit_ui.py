# user_edit_ui.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import db_ops

class UserEditWindow(QDialog):
    def __init__(self, user_data, current_user_id, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.current_user_id = current_user_id
        self.setWindowTitle("تعديل بيانات المستخدم")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.username_input = QLineEdit(self.user_data['username'])
        self.username_input.setReadOnly(True)
        form_layout.addRow("اسم المستخدم:", self.username_input)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setCurrentText(self.user_data['role_name'])
        form_layout.addRow("الصلاحية:", self.role_combo)
        self.department_combo = QComboBox()
        self.populate_departments()
        self.department_combo.setCurrentText(self.user_data['department'])
        form_layout.addRow("القسم:", self.department_combo)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("كلمة المرور الجديدة:", self.password_input)
        layout.addLayout(form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_changes)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def populate_departments(self):
        self.department_combo.addItems(db_ops.get_all_departments())

    def save_changes(self):
        role_name = self.role_combo.currentText()
        department = self.department_combo.currentText()
        new_password = self.password_input.text()
        if not department:
            QMessageBox.warning(self, "خطأ", "حقل القسم لا يمكن أن يكون فارغاً.")
            return
        success, msg = db_ops.update_user(user_id=self.user_data['id'], role_name=role_name, department=department, new_password=new_password if new_password else None, current_user_id=self.current_user_id)
        QMessageBox.information(self, "نتيجة", msg)
        if success: self.accept()