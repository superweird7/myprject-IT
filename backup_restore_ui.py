# backup_restore_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import db_ops
import os
from datetime import datetime

class BackupRestoreWorker(QThread):
    """Worker thread to perform backup/restore operations without freezing the UI."""
    finished = pyqtSignal(bool, str) # Signal emitted when operation finishes (success, message)

    def __init__(self, operation, file_path=None):
        super().__init__()
        self.operation = operation # 'backup' or 'restore'
        self.file_path = file_path

    def run(self):
        try:
            if self.operation == 'backup':
                success, msg = db_ops.backup_database(self.file_path)
            elif self.operation == 'restore':
                success, msg = db_ops.restore_database(self.file_path)
            else:
                success, msg = False, f"عملية غير معروفة: {self.operation}"
            self.finished.emit(success, msg)
        except Exception as e:
            self.finished.emit(False, f"استثناء في الخلفية:\n{str(e)}")


class BackupRestoreWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نسخ احتياطي واستعادة")
        self.setGeometry(200, 200, 600, 400)
        self.setLayoutDirection(Qt.RightToLeft)
        self.worker = None # To hold the background worker thread
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Backup Section ---
        backup_label = QLabel("<b>إنشاء نسخة احتياطية:</b>")
        layout.addWidget(backup_label)

        self.backup_info_label = QLabel("سيتم حفظ النسخة الاحتياطية كملف .sql في الموقع الذي تختاره.")
        layout.addWidget(self.backup_info_label)

        backup_btn_layout = QHBoxLayout()
        self.btn_create_backup = QPushButton("إنشاء نسخة احتياطية")
        self.btn_create_backup.clicked.connect(self.create_backup)
        backup_btn_layout.addWidget(self.btn_create_backup)
        layout.addLayout(backup_btn_layout)

        # --- Restore Section ---
        restore_label = QLabel("<b>استعادة من نسخة احتياطية:</b>")
        layout.addWidget(restore_label)

        self.restore_info_label = QLabel("اختر ملف .sql للاستعادة منه. تحذير: هذا سيستبدل البيانات الحالية!")
        layout.addWidget(self.restore_info_label)

        restore_btn_layout = QHBoxLayout()
        self.btn_select_restore_file = QPushButton("اختر ملف النسخة الاحتياطية")
        self.btn_select_restore_file.clicked.connect(self.select_restore_file)
        restore_btn_layout.addWidget(self.btn_select_restore_file)

        self.btn_perform_restore = QPushButton("تنفيذ الاستعادة")
        self.btn_perform_restore.clicked.connect(self.perform_restore)
        self.btn_perform_restore.setDisabled(True) # Disabled until a file is selected
        restore_btn_layout.addWidget(self.btn_perform_restore)
        layout.addLayout(restore_btn_layout)

        # --- Status and Progress ---
        self.status_label = QLabel("الحالة: جاهز")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Make it indeterminate initially
        self.progress_bar.setVisible(False) # Hide initially
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150) # Limit height
        layout.addWidget(QLabel("سجل العمليات:"))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def log_message(self, message):
        """Append a message to the log text area."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def start_operation(self, operation, file_path=None):
        """Starts the backup or restore operation in a background thread."""
        self.status_label.setText(f"الحالة: جاري {operation}...")
        self.progress_bar.setVisible(True)
        self.btn_create_backup.setDisabled(True)
        self.btn_select_restore_file.setDisabled(True)
        self.btn_perform_restore.setDisabled(True)
        self.log_message(f"بدء {operation}...")

        self.worker = BackupRestoreWorker(operation, file_path)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()

    def on_operation_finished(self, success, message):
        """Handles the result when the background operation finishes."""
        self.progress_bar.setVisible(False)
        self.btn_create_backup.setDisabled(False)
        self.btn_select_restore_file.setDisabled(False)
        # Re-enable restore button only if a file was previously selected
        if hasattr(self, 'restore_file_path') and self.restore_file_path:
            self.btn_perform_restore.setDisabled(False)

        if success:
            self.status_label.setText("الحالة: تم بنجاح")
            self.log_message(f"نجاح: {message}")
            QMessageBox.information(self, "نجاح", message)
        else:
            self.status_label.setText("الحالة: فشل")
            self.log_message(f"خطأ: {message}")
            QMessageBox.critical(self, "خطأ", message)

        self.worker = None # Clean up worker reference

    def create_backup(self):
        """Handles the 'Create Backup' button click."""
        # Suggest a default filename with timestamp
        default_filename = f"maintenance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ النسخة الاحتياطية", default_filename, "SQL Files (*.sql)"
        )
        if file_path:
            # Ensure .sql extension
            if not file_path.lower().endswith('.sql'):
                file_path += '.sql'
            self.start_operation('backup', file_path)

    def select_restore_file(self):
        """Handles the 'Select Restore File' button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف النسخة الاحتياطية", "", "SQL Files (*.sql)"
        )
        if file_path:
            self.restore_file_path = file_path
            self.btn_perform_restore.setDisabled(False)
            self.log_message(f"تم اختيار ملف الاستعادة: {os.path.basename(file_path)}")
            self.status_label.setText(f"الحالة: ملف مختار - {os.path.basename(file_path)}")

    def perform_restore(self):
        """Handles the 'Perform Restore' button click."""
        # Confirmation dialog is crucial for restore
        reply = QMessageBox.question(
            self, 'تأكيد الاستعادة',
            'هل أنت متأكد أنك تريد استعادة هذا الملف؟\nهذا سيؤدي إلى فقدان جميع البيانات الحالية في قاعدة البيانات!',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if hasattr(self, 'restore_file_path') and self.restore_file_path:
                self.start_operation('restore', self.restore_file_path)
            else:
                # Should not happen if button is disabled correctly, but good check
                QMessageBox.warning(self, "خطأ", "لم يتم اختيار ملف استعادة.")
