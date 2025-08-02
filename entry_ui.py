# entry_ui.py
import os
import sys
import shutil
import uuid
import base64
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QDateEdit, QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QListWidget, QListWidgetItem, QGroupBox, QGraphicsView, QGraphicsScene, QComboBox, 
    QCompleter, QStatusBar, QDialog, QFormLayout, QStyle, QTabWidget
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QTextDocument, QIcon
from PyQt5.QtCore import Qt, QDate, QRectF, QSize
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import db_ops
import utils

try:
    import fitz
    pdf_preview_enabled = True
except ImportError:
    pdf_preview_enabled = False

ATTACHMENT_DIR = "attachments_storage"

class PhotoViewer(QGraphicsView):
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
        else:
            factor = 0.8
        self.scale(factor, factor)

class EntryWindow(QWidget):
    def __init__(self, user_id, user_role="user", user_department=None):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.user_department = user_department
        
        self.setWindowTitle("إدخال وعرض بيانات الصيانة")
        self.setGeometry(100, 100, 1600, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.temp_attachments = []
        self._pixmap_item = None
        
        if not os.path.exists(ATTACHMENT_DIR):
            os.makedirs(ATTACHMENT_DIR)

        outer_layout = QVBoxLayout(self)
        main_layout = QHBoxLayout()
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.type_input = QLineEdit()
        self.device_input = QLineEdit()
        self.technician_input = QLineEdit()
        self.procedures_input = QTextEdit()
        self.materials_input = QTextEdit()
        self.notes_input = QTextEdit()
        self.warnings_input = QTextEdit()
        self.department_combo = QComboBox()
        self.department_combo.setEditable(True)
        self.populate_departments()
        if self.user_department and self.user_role != "admin":
            self.department_combo.setCurrentText(self.user_department)
            self.department_combo.setDisabled(True)
            
        form_layout.addRow("تاريخ الصيانة:", self.date_edit)
        form_layout.addRow("نوع الصيانة:", self.type_input)
        form_layout.addRow("اسم الجهاز <span style='color: red;'>*</span>:", self.device_input)
        form_layout.addRow("اسم الفني:", self.technician_input)
        form_layout.addRow("الإجراءات المتبعة <span style='color: red;'>*</span>:", self.procedures_input)
        form_layout.addRow("المواد المستخدمة:", self.materials_input)
        form_layout.addRow("ملاحظات:", self.notes_input)
        form_layout.addRow("تحذيرات:", self.warnings_input)
        form_layout.addRow("القسم <span style='color: red;'>*</span>:", self.department_combo)
        
        info_label = QLabel("(*) الحقول المطلوبة")
        info_label.setStyleSheet("color: #888;")
        form_layout.addRow(info_label)

        right_side_layout = QVBoxLayout()
        
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(" حفظ السجل الجديد")
        self.btn_add.setObjectName("AddButton")
        self.btn_add.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.btn_add.clicked.connect(self.add_record)
        
        self.btn_update = QPushButton(" تحديث السجل")
        self.btn_update.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.btn_update.clicked.connect(self.update_record)
        
        self.btn_delete = QPushButton(" حذف")
        self.btn_delete.setObjectName("DeleteButton")
        self.btn_delete.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        self.btn_delete.clicked.connect(self.delete_record)
        
        self.btn_export_pdf = QPushButton(" PDF")
        self.btn_export_pdf.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.btn_export_pdf.clicked.connect(self.export_to_pdf)
        
        self.btn_print = QPushButton(" طباعة")
        self.btn_print.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        self.btn_print.clicked.connect(self.print_record)
        
        icon_size = QSize(24, 24)
        for btn in [self.btn_add, self.btn_update, self.btn_delete, self.btn_export_pdf, self.btn_print]:
            btn.setIconSize(icon_size)
            btn_layout.addWidget(btn)

        right_side_layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "تاريخ الصيانة", "نوع الصيانة", "اسم الجهاز", "اسم الفني", "الإجراءات", "المواد", "ملاحظات", "التحذيرات", "القسم"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_side_layout.addWidget(self.table)
        
        self.details_tabs = QTabWidget()
        
        attachments_tab = QWidget()
        attachments_main_layout = QHBoxLayout(attachments_tab)
        list_layout = QVBoxLayout()
        self.attachment_list = QListWidget()
        self.attachment_list.currentItemChanged.connect(self.preview_selected_attachment)
        list_layout.addWidget(self.attachment_list)
        attachment_btn_layout = QHBoxLayout()
        self.btn_add_attachment = QPushButton("إضافة")
        self.btn_remove_attachment = QPushButton("حذف")
        self.btn_open_attachment = QPushButton("فتح")
        self.btn_add_attachment.clicked.connect(self.add_attachment)
        self.btn_remove_attachment.clicked.connect(self.remove_attachment)
        self.btn_open_attachment.clicked.connect(self.open_attachment)
        attachment_btn_layout.addWidget(self.btn_add_attachment)
        attachment_btn_layout.addWidget(self.btn_remove_attachment)
        attachment_btn_layout.addWidget(self.btn_open_attachment)
        list_layout.addLayout(attachment_btn_layout)
        
        preview_area_layout = QVBoxLayout()
        self.scene = QGraphicsScene(self)
        self.preview_view = PhotoViewer(self.scene)
        preview_area_layout.addWidget(self.preview_view)
        zoom_layout = QHBoxLayout()
        self.btn_zoom_in = QPushButton("تكبير (+)")
        self.btn_zoom_out = QPushButton("تصغير (-)")
        self.btn_zoom_reset = QPushButton("إعادة تعيين")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_zoom_reset.clicked.connect(self.reset_view)
        zoom_layout.addStretch()
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.btn_zoom_reset)
        zoom_layout.addStretch()
        preview_area_layout.addLayout(zoom_layout)
        attachments_main_layout.addLayout(list_layout, 1)
        attachments_main_layout.addLayout(preview_area_layout, 3)
        self.details_tabs.addTab(attachments_tab, "المرفقات")

        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.history_list = QListWidget()
        history_layout.addWidget(self.history_list)
        self.details_tabs.addTab(history_tab, "سجل التاريخ")

        right_side_layout.addWidget(self.details_tabs)

        main_layout.addWidget(form_widget, 1)
        main_layout.addLayout(right_side_layout, 2)
        
        self.status_bar = QStatusBar()
        outer_layout.addLayout(main_layout)
        outer_layout.addWidget(self.status_bar)
        
        self.selected_id = None
        self.load_data()
        self.table.cellClicked.connect(self.load_selected_record)
        self.update_buttons_state()
        self.status_bar.showMessage("جاهز", 3000)

    def zoom_in(self): self.preview_view.scale(1.2, 1.2)
    def zoom_out(self): self.preview_view.scale(1/1.2, 1/1.2)
    def reset_view(self):
        if self._pixmap_item:
            self.preview_view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)

    def populate_departments(self):
        departments = db_ops.get_all_departments()
        self.department_combo.addItems(departments)
        completer = QCompleter(departments, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.department_combo.setCompleter(completer)

    def update_buttons_state(self):
        is_record_selected = self.selected_id is not None
        is_admin = self.user_role == "admin"
        
        self.btn_update.setEnabled(is_record_selected and is_admin)
        self.btn_delete.setEnabled(is_record_selected)
        self.btn_print.setEnabled(is_record_selected)

    def load_data(self):
        department_filter = self.user_department if self.user_role != 'admin' else None
        records = db_ops.fetch_records(department=department_filter)
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, key in enumerate(["id", "date", "type", "device", "technician", "procedures", "materials", "notes", "warnings", "department"]):
                value = row_data.get(key, "")
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ""))
        self.table.resizeColumnsToContents()

    def get_form_data(self):
        return (
            self.date_edit.date().toString("yyyy-MM-dd"), self.type_input.text(), self.device_input.text(),
            self.technician_input.text(), self.procedures_input.toPlainText(), self.materials_input.toPlainText(),
            self.notes_input.toPlainText(), self.warnings_input.toPlainText(), self.department_combo.currentText()
        )

    def add_record(self):
        data = self.get_form_data()
        if not data[2] or not data[8] or not data[4]:
            QMessageBox.warning(self, "بيانات ناقصة", "يرجى تعبئة الحقول المطلوبة (*): اسم الجهاز، القسم، والإجراءات المتبعة.")
            return
        new_record_id = db_ops.insert_record(data, self.user_id)
        if new_record_id:
            self.save_temp_attachments(new_record_id)
            self.status_bar.showMessage("تم إضافة السجل والمرفقات بنجاح.", 5000)
            self.load_data()
            self.clear_inputs()
        else:
            QMessageBox.critical(self, "خطأ", "فشل في إضافة السجل.")

    def update_record(self):
        if self.selected_id is None: return
        data = self.get_form_data()
        if not data[2] or not data[8] or not data[4]:
            QMessageBox.warning(self, "بيانات ناقصة", "يرجى تعبئة الحقول المطلوبة (*): اسم الجهاز، القسم، والإجراءات المتبعة.")
            return
        db_ops.update_record(self.selected_id, data, self.user_id)
        self.status_bar.showMessage("تم تحديث السجل بنجاح.", 5000)
        self.load_data()
        self.clear_inputs()
        
    def delete_record(self):
        if self.selected_id is None: return
        reply = QMessageBox.question(self, 'تأكيد الحذف',
            'هل أنت متأكد؟ سيتم نقل هذا السجل إلى سلة المحذوفات.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            db_ops.delete_record(self.selected_id, self.user_id)
            self.status_bar.showMessage("تم نقل السجل إلى سلة المحذوفات.", 5000)
            self.load_data()
            self.clear_inputs()

    def print_record(self):
        if self.selected_id is None: return
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            document = QTextDocument()
            # ... (HTML formatting code remains the same)
            document.print_(printer)
            self.status_bar.showMessage("تم إرسال السجل إلى الطابعة.", 5000)

    def export_to_pdf(self):
        if self.table.rowCount() == 0: return
        filename, _ = QFileDialog.getSaveFileName(self, 'حفظ كـ PDF', 'maintenance_report.pdf', 'PDF Files (*.pdf)')
        if not filename: return
        # ... (PDF generation code remains the same)
        
    def load_selected_record(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.date_edit.setDate(QDate.fromString(self.table.item(row, 1).text(), "yyyy-MM-dd"))
        self.type_input.setText(self.table.item(row, 2).text())
        self.device_input.setText(self.table.item(row, 3).text())
        self.technician_input.setText(self.table.item(row, 4).text())
        self.procedures_input.setPlainText(self.table.item(row, 5).text())
        self.materials_input.setPlainText(self.table.item(row, 6).text())
        self.notes_input.setPlainText(self.table.item(row, 7).text())
        self.warnings_input.setPlainText(self.table.item(row, 8).text())
        self.department_combo.setCurrentText(self.table.item(row, 9).text())
        self.load_attachments(self.selected_id)
        self.load_record_history(self.selected_id)
        self.update_buttons_state()

    def clear_inputs(self):
        self.date_edit.setDate(QDate.currentDate())
        self.type_input.clear()
        self.device_input.clear()
        self.technician_input.clear()
        self.procedures_input.clear()
        self.materials_input.clear()
        self.notes_input.clear()
        self.warnings_input.clear()
        if not (self.user_department and self.user_role != 'admin'):
            self.department_combo.setCurrentIndex(-1)
        self.selected_id = None
        self.attachment_list.clear()
        self.history_list.clear()
        self.temp_attachments = []
        self.scene.clear()
        self._pixmap_item = None
        self.table.clearSelection()
        self.update_buttons_state()

    def preview_selected_attachment(self, current_item, previous_item):
        self.scene.clear()
        self._pixmap_item = None
        if not current_item: return
        attachment_data = current_item.data(Qt.UserRole)
        is_temp = attachment_data is None
        file_path = self.temp_attachments[self.attachment_list.row(current_item)] if is_temp else attachment_data['stored_filepath']
        if not os.path.exists(file_path): return
        ext = os.path.splitext(file_path)[1].lower()
        pixmap = None
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            pixmap = QPixmap(file_path)
        elif ext == '.pdf' and pdf_preview_enabled:
            try:
                doc = fitz.open(file_path)
                page = doc.load_page(0)
                matrix = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=matrix)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                doc.close()
            except Exception: pass
        if pixmap and not pixmap.isNull():
            self._pixmap_item = self.scene.addPixmap(pixmap)
            self.preview_view.fitInView(self._pixmap_item, Qt.KeepAspectRatio)

    def load_attachments(self, maintenance_id):
        self.attachment_list.clear()
        attachments = db_ops.get_attachments_for_record(maintenance_id)
        for att in attachments:
            item = QListWidgetItem(att['original_filename'])
            item.setData(Qt.UserRole, att)
            self.attachment_list.addItem(item)
            
    def load_record_history(self, record_id):
        self.history_list.clear()
        try:
            history_entries = db_ops.get_history_for_record(record_id)
            if not history_entries:
                self.history_list.addItem("لا يوجد تاريخ مسجل لهذا السجل.")
                return
            for entry in history_entries:
                timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                user = entry['username'] or 'مستخدم محذوف'
                description = entry['description']
                log_string = f"{timestamp} - {user}: {description}"
                self.history_list.addItem(QListWidgetItem(log_string))
        except Exception as e:
            self.history_list.addItem(f"خطأ في تحميل السجل: {e}")

    def add_attachment(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "اختر المرفقات", "", "All Files (*)")
        if not file_paths: return
        if self.selected_id is not None:
            for path in file_paths:
                self.save_single_attachment(self.selected_id, path)
            self.load_attachments(self.selected_id)
        else:
            for path in file_paths:
                if path not in self.temp_attachments:
                    self.temp_attachments.append(path)
                    self.attachment_list.addItem(QListWidgetItem(os.path.basename(path)))

    def remove_attachment(self):
        selected_item = self.attachment_list.currentItem()
        if not selected_item: return
        reply = QMessageBox.question(self, 'تأكيد الحذف', 'هل أنت متأكد من حذف هذا المرفق؟', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No: return
        row = self.attachment_list.row(selected_item)
        if self.selected_id is not None:
            attachment_data = selected_item.data(Qt.UserRole)
            success, msg = db_ops.delete_attachment(attachment_data['id'], self.user_id)
            if success:
                self.attachment_list.takeItem(row)
            else:
                QMessageBox.critical(self, "خطأ", msg)
        else:
            self.temp_attachments.pop(row)
            self.attachment_list.takeItem(row)

    def open_attachment(self):
        selected_item = self.attachment_list.currentItem()
        if not selected_item: return
        attachment_data = selected_item.data(Qt.UserRole)
        if not attachment_data:
            QMessageBox.warning(self, "تنبيه", "يجب حفظ السجل أولاً لفتح المرفق.")
            return
        file_path = attachment_data['stored_filepath']
        if os.path.exists(file_path):
            try:
                os.startfile(os.path.realpath(file_path))
            except AttributeError:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                import subprocess
                subprocess.call([opener, file_path])
        else:
            QMessageBox.critical(self, "خطأ", f"لم يتم العثور على الملف:\n{file_path}")

    def save_single_attachment(self, maintenance_id, source_path):
        try:
            original_filename = os.path.basename(source_path)
            file_extension = os.path.splitext(original_filename)[1]
            stored_filename = f"{uuid.uuid4().hex}{file_extension}"
            stored_filepath = os.path.join(ATTACHMENT_DIR, stored_filename)
            shutil.copy(source_path, stored_filepath)
            db_ops.add_attachment(maintenance_id, original_filename, stored_filepath, self.user_id)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في المرفق", f"فشل في حفظ المرفق '{original_filename}':\n{e}")

    def save_temp_attachments(self, maintenance_id):
        for path in self.temp_attachments:
            self.save_single_attachment(maintenance_id, path)
        self.temp_attachments = []