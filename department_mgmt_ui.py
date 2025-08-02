# department_mgmt_ui.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
import db_ops

class DepartmentManagementWindow(QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowTitle("إدارة الأقسام")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(400, 500)
        layout = QVBoxLayout(self)
        self.dept_list = QListWidget()
        layout.addWidget(self.dept_list)
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("إضافة قسم")
        self.btn_edit = QPushButton("تعديل القسم")
        self.btn_delete = QPushButton("حذف القسم")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)
        self.btn_add.clicked.connect(self.add_department)
        self.btn_edit.clicked.connect(self.edit_department)
        self.btn_delete.clicked.connect(self.delete_department)
        self.load_departments()

    def load_departments(self):
        self.dept_list.clear()
        self.dept_list.addItems(db_ops.get_all_departments())

    def add_department(self):
        text, ok = QInputDialog.getText(self, "إضافة قسم جديد", "اسم القسم:")
        if ok and text.strip():
            success, msg = db_ops.add_department(text.strip(), self.current_user_id)
            QMessageBox.information(self, "نتيجة", msg)
            if success: self.load_departments()

    def edit_department(self):
        selected_item = self.dept_list.currentItem()
        if not selected_item: return
        old_name = selected_item.text()
        text, ok = QInputDialog.getText(self, "تعديل اسم القسم", "الاسم الجديد:", text=old_name)
        if ok and text.strip() and text.strip() != old_name:
            dept_id = db_ops.get_department_id_by_name(old_name)
            if dept_id:
                success, msg = db_ops.update_department(dept_id, text.strip(), self.current_user_id)
                QMessageBox.information(self, "نتيجة", msg)
                if success: self.load_departments()

    def delete_department(self):
        selected_item = self.dept_list.currentItem()
        if not selected_item: return
        dept_name = selected_item.text()
        reply = QMessageBox.question(self, 'تأكيد الحذف', f"هل أنت متأكد من حذف القسم '{dept_name}'؟\nلا يمكن حذف القسم إذا كان مستخدماً.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            dept_id = db_ops.get_department_id_by_name(dept_name)
            if dept_id:
                success, msg = db_ops.delete_department(dept_id, self.current_user_id)
                QMessageBox.warning(self, "نتيجة", msg)
                if success: self.load_departments()