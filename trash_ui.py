# trash_ui.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import db_ops

class TrashWindow(QDialog):
    def __init__(self, current_user_id, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.setWindowTitle("سلة محذوفات السجلات")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("هنا السجلات التي تم حذفها. يمكن استعادتها أو حذفها نهائياً."))
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "التاريخ", "الجهاز", "القسم"])
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
        self.load_deleted_records()

    def load_deleted_records(self):
        records = db_ops.fetch_deleted_records()
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(str(record['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(record['date'])))
            self.table.setItem(i, 2, QTableWidgetItem(record['device']))
            self.table.setItem(i, 3, QTableWidgetItem(record['department']))
        self.table.resizeColumnsToContents()

    def get_selected_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "خطأ", "الرجاء تحديد سجل أولاً.")
            return None
        return int(self.table.item(self.table.currentRow(), 0).text())

    def restore_selected(self):
        rec_id = self.get_selected_id()
        if rec_id:
            db_ops.restore_record(rec_id, self.current_user_id)
            QMessageBox.information(self, "نجاح", "تم استعادة السجل بنجاح.")
            self.load_deleted_records()

    def delete_permanently(self):
        rec_id = self.get_selected_id()
        if rec_id:
            reply = QMessageBox.warning(self, 'تأكيد الحذف النهائي', "هل أنت متأكد؟ لا يمكن التراجع عن هذا الإجراء.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                db_ops.permanently_delete_record(rec_id, self.current_user_id)
                self.load_deleted_records()