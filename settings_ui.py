# settings_ui.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox, QLabel
from PyQt5.QtCore import QSettings

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("الإعدادات")
        self.setMinimumWidth(350)
        self.settings = QSettings("MyCompany", "MaintenanceApp")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["فاتح (النظام)", "داكن"])
        form_layout.addRow("مظهر التطبيق:", self.theme_combo)
        self.date_range_spinbox = QSpinBox()
        self.date_range_spinbox.setRange(1, 60)
        self.date_range_spinbox.setSuffix(" شهر")
        form_layout.addRow("نطاق التاريخ الافتراضي للبحث:", self.date_range_spinbox)
        layout.addLayout(form_layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        layout.addWidget(QLabel("ملاحظة: تغيير المظهر يتطلب إعادة تشغيل التطبيق."))
        self.load_settings()

    def load_settings(self):
        theme = self.settings.value("theme", "Light", type=str)
        if theme.lower() == "dark":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)
        default_months = self.settings.value("default_date_range_months", 12, type=int)
        self.date_range_spinbox.setValue(default_months)

    def save_settings(self):
        theme = "Dark" if self.theme_combo.currentIndex() == 1 else "Light"
        self.settings.setValue("theme", theme)
        self.settings.setValue("default_date_range_months", self.date_range_spinbox.value())
        self.accept()