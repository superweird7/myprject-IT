# search_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QTextEdit, QStatusBar, QHBoxLayout
)
from PyQt5.QtCore import Qt
import db_ops
import utils

class SearchWindow(QWidget):
    MAX_CELL_TEXT_LENGTH = 50

    def __init__(self, user_role="user", user_department=None):
        super().__init__()
        self.setWindowTitle("بحث شامل في السجلات")
        self.setGeometry(150, 150, 1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        self.user_role = user_role
        self.user_department = user_department
        
        main_layout = QVBoxLayout(self)

        # --- Simplified Search Input ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("ابحث عن أي كلمة:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("اكتب هنا للبحث في جميع الحقول...")
        search_layout.addWidget(self.search_input)
        
        btn_search = QPushButton("بحث")
        btn_search.clicked.connect(self.perform_search)
        search_layout.addWidget(btn_search)

        main_layout.addLayout(search_layout)

        # --- Results Table ---
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "التاريخ", "النوع", "الجهاز", "الفني", "الإجراءات", "المواد", "ملاحظات", "التحذيرات", "القسم"])
        self.table.cellDoubleClicked.connect(self.show_full_details)
        main_layout.addWidget(self.table)

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.perform_search() # Perform an initial search to show all records

    def perform_search(self):
        self.status_bar.showMessage("جاري البحث...")
        
        keyword = self.search_input.text().strip()
        
        department_filter = None
        if self.user_role != 'admin' or self.user_department:
            department_filter = self.user_department

        results = db_ops.search_all_fields(keyword, department_filter)
        
        self.table.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, key in enumerate(["id", "date", "type", "device", "technician", "procedures", "materials", "notes", "warnings", "department"]):
                value = row_data.get(key, "")
                display_text = str(value) if value else ""
                if len(display_text) > self.MAX_CELL_TEXT_LENGTH:
                    display_text = display_text[:self.MAX_CELL_TEXT_LENGTH] + "..."
                item = QTableWidgetItem(display_text)
                if value:
                    item.setData(Qt.UserRole, str(value))
                self.table.setItem(row_idx, col_idx, item)
        
        self.status_bar.showMessage(f"تم العثور على {len(results)} سجل.", 5000)

    def show_full_details(self, row, col):
        try:
            record_id = self.table.item(row, 0).text()
            def get_full_text(col_index):
                item = self.table.item(row, col_index)
                if item:
                    full_text = item.data(Qt.UserRole)
                    return full_text if full_text is not None else item.text()
                return ""
            details_content = f"""
                <b>المعرف:</b> {record_id}<br>
                <b>التاريخ:</b> {get_full_text(1)}<br>
                <b>النوع:</b> {get_full_text(2)}<br>
                <b>الجهاز:</b> {get_full_text(3)}<br>
                <b>الفني:</b> {get_full_text(4)}<br>
                <b>القسم:</b> {get_full_text(9)}<br><br>
                <b>الإجراءات المتبعة:</b><br>{get_full_text(5) or 'لا توجد'}<br><br>
                <b>المواد المستخدمة:</b><br>{get_full_text(6) or 'لا توجد'}<br><br>
                <b>ملاحظات:</b><br>{get_full_text(7) or 'لا توجد'}<br><br>
                <b>تحذيرات:</b><br>{get_full_text(8) or 'لا توجد'}<br>
            """
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"تفاصيل السجل - ID: {record_id}")
            details_dialog.setLayoutDirection(Qt.RightToLeft)
            layout = QVBoxLayout()
            details_text = QTextEdit()
            details_text.setReadOnly(True)
            details_text.setHtml(details_content)
            layout.addWidget(details_text)
            details_dialog.setLayout(layout)
            details_dialog.resize(600, 400)
            details_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في عرض التفاصيل الكاملة:\n{str(e)}")