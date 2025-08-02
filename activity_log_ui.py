# activity_log_ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import db_ops

class ActivityLogWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سجل الأنشطة")
        self.setGeometry(200, 200, 1000, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        self.refresh_button = QPushButton("تحديث السجل")
        self.refresh_button.clicked.connect(self.load_log)
        layout.addWidget(self.refresh_button)
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المستخدم", "الإجراء", "نوع السجل", "معرف السجل", "الوصف", "الوقت والتاريخ"])
        layout.addWidget(self.table)
        self.load_log()

    def load_log(self):
        try:
            log_entries = db_ops.fetch_activity_log()
            self.table.setRowCount(len(log_entries))
            for row_idx, entry in enumerate(log_entries):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(entry['id'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(entry['username'] or "مستخدم محذوف"))
                self.table.setItem(row_idx, 2, QTableWidgetItem(entry['action']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(entry['record_type']))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(entry['record_id']) if entry['record_id'] else ""))
                self.table.setItem(row_idx, 5, QTableWidgetItem(entry['description'] or ""))
                timestamp_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if entry['timestamp'] else ""
                self.table.setItem(row_idx, 6, QTableWidgetItem(timestamp_str))
            self.table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل سجل الأنشطة:\n{str(e)}")