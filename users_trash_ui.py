# users_trash_ui.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import db_ops

class UsersTrashWindow(QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowTitle("سلة محذوفات المستخدمين")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("هنا المستخدمون الذين تم حذفهم. يمكن استعادتهم أو حذفهم نهائياً."))
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المستخدم", "الصلاحية", "القسم"])
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        self.btn_restore = QPushButton("استعادة المحدد")
        self.btn_delete_perm = QPushButton("حذف نهائي للمحدد")
        self.btn_delete_perm.setObjectName("DeleteButton")
        self.btn_close = QPushButton("إغلاق")
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_delete_perm)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_delete_perm.clicked.connect(self.delete_permanently)
        self.btn_close.clicked.connect(self.accept)
        self.load_deleted_users()

    def load_deleted_users(self):
        users = db_ops.fetch_deleted_users()
        self.table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(user['username']))
            self.table.setItem(i, 2, QTableWidgetItem(user['role_name']))
            self.table.setItem(i, 3, QTableWidgetItem(user['department']))
        self.table.resizeColumnsToContents()

    def get_selected_user_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد مستخدم أولاً.")
            return None
        return int(self.table.item(self.table.currentRow(), 0).text())

    def restore_selected(self):
        user_id = self.get_selected_user_id()
        if user_id:
            db_ops.restore_user(user_id, self.current_user_id)
            QMessageBox.information(self, "نجاح", "تم استعادة المستخدم بنجاح.")
            self.load_deleted_users()

    def delete_permanently(self):
        user_id = self.get_selected_user_id()
        if user_id:
            reply = QMessageBox.warning(self, 'تأكيد الحذف النهائي', "هل أنت متأكد؟ لا يمكن التراجع عن هذا الإجراء.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                db_ops.permanently_delete_user(user_id, self.current_user_id)
                self.load_deleted_users()