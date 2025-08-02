# reports_ui.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QDateEdit, QComboBox
)
from PyQt5.QtCore import Qt, QDate, QSettings
from PyQt5.QtGui import QFont
import db_ops

# --- Matplotlib and Arabic Shaping Imports ---
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import arabic_reshaper
from bidi.algorithm import get_display

# --- Matplotlib Font Setup ---
try:
    font_path = "c:/windows/fonts/arial.ttf"
    matplotlib.font_manager.fontManager.addfont(font_path)
    matplotlib.rc('font', family='Arial')
except FileNotFoundError:
    print("Arial font not found for charts.")

# --- Helper function to correctly display Arabic text ---
def shape_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("التقارير والإحصائيات")
        self.setGeometry(100, 100, 1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()
        settings = QSettings("MyCompany", "MaintenanceApp")
        default_months = settings.value("default_date_range_months", 1, type=int)

        filter_layout.addWidget(QLabel("من تاريخ:"))
        self.date_from_edit = QDateEdit(calendarPopup=True)
        self.date_from_edit.setDate(QDate.currentDate().addMonths(-default_months))
        filter_layout.addWidget(self.date_from_edit)

        filter_layout.addWidget(QLabel("إلى تاريخ:"))
        self.date_to_edit = QDateEdit(calendarPopup=True)
        self.date_to_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.date_to_edit)

        filter_layout.addWidget(QLabel("حسب القسم:"))
        self.department_combo = QComboBox()
        self.department_combo.addItem("الجميع")
        self.department_combo.addItems(db_ops.get_all_departments())
        filter_layout.addWidget(self.department_combo)

        self.btn_generate = QPushButton("توليد التقرير")
        self.btn_generate.clicked.connect(self.generate_report)
        filter_layout.addWidget(self.btn_generate)
        layout.addLayout(filter_layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.dept_chart_tab = QWidget()
        self.tabs.addTab(self.dept_chart_tab, "رسم بياني (حسب القسم)")
        self.setup_dept_chart_tab()

        self.type_chart_tab = QWidget()
        self.tabs.addTab(self.type_chart_tab, "رسم بياني (حسب النوع)")
        self.setup_type_chart_tab()
        
        self.dept_tab = QWidget()
        self.tabs.addTab(self.dept_tab, "جدول (سجلات لكل قسم)")
        self.setup_dept_tab()
        
        self.devices_tab = QWidget()
        self.tabs.addTab(self.devices_tab, "جدول (أنواع الأجهزة)")
        self.setup_devices_tab()
        
        self.techs_tab = QWidget()
        self.tabs.addTab(self.techs_tab, "جدول (الفنيون)")
        self.setup_techs_tab()
        
        self.generate_report()

    def setup_dept_chart_tab(self):
        layout = QVBoxLayout(self.dept_chart_tab)
        self.dept_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.dept_canvas)
        self._dept_ax = self.dept_canvas.figure.subplots()

    def setup_type_chart_tab(self):
        layout = QVBoxLayout(self.type_chart_tab)
        self.type_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.type_canvas)
        self._type_ax = self.type_canvas.figure.subplots()

    def setup_dept_tab(self):
        layout = QVBoxLayout(self.dept_tab)
        self.dept_table = QTableWidget()
        self.dept_table.setColumnCount(2)
        self.dept_table.setHorizontalHeaderLabels(["القسم", "عدد السجلات"])
        layout.addWidget(self.dept_table)

    def setup_devices_tab(self):
        layout = QVBoxLayout(self.devices_tab)
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(2)
        self.devices_table.setHorizontalHeaderLabels(["نوع الجهاز", "عدد السجلات"])
        layout.addWidget(self.devices_table)

    def setup_techs_tab(self):
        layout = QVBoxLayout(self.techs_tab)
        self.techs_table = QTableWidget()
        self.techs_table.setColumnCount(2)
        self.techs_table.setHorizontalHeaderLabels(["اسم الفني", "عدد السجلات"])
        layout.addWidget(self.techs_table)

    def generate_report(self):
        date_from = self.date_from_edit.date().toString("yyyy-MM-dd")
        date_to = self.date_to_edit.date().toString("yyyy-MM-dd")
        department = self.department_combo.currentText()
        if department == "الجميع": department = None

        try:
            records_per_dept = db_ops.get_records_per_department(date_from, date_to)
            device_types = db_ops.get_device_type_counts(date_from, date_to, department)
            technicians = db_ops.get_technician_counts(date_from, date_to, department)
            
            self.populate_dept_tab(records_per_dept)
            self.populate_devices_tab(device_types)
            self.populate_techs_tab(technicians)
            
            self.update_department_chart(records_per_dept)
            self.update_type_chart(device_types)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في توليد التقرير:\n{str(e)}")

    def update_department_chart(self, data):
        self._dept_ax.clear()
        if not data:
            self._dept_ax.text(0.5, 0.5, shape_arabic_text('لا توجد بيانات للعرض'), ha='center', va='center')
            self.dept_canvas.draw()
            return
            
        departments = [shape_arabic_text(item['department'] if item['department'] else 'غير محدد') for item in data]
        counts = [item['count'] for item in data]
        
        self._dept_ax.barh(departments, counts, color='skyblue')
        self._dept_ax.set_xlabel(shape_arabic_text('عدد سجلات الصيانة'))
        self._dept_ax.set_title(shape_arabic_text('سجلات الصيانة حسب القسم'))
        self._dept_ax.invert_yaxis()
        self.dept_canvas.figure.tight_layout()
        self.dept_canvas.draw()

    def update_type_chart(self, data):
        self._type_ax.clear()
        if not data:
            self._type_ax.text(0.5, 0.5, shape_arabic_text('لا توجد بيانات للعرض'), ha='center', va='center')
            self.type_canvas.draw()
            return

        types = [shape_arabic_text(item['device_type'] if item['device_type'] else 'غير محدد') for item in data]
        counts = [item['count'] for item in data]

        self._type_ax.pie(counts, labels=types, autopct=lambda p: f'{p:.1f}%')
        self._type_ax.axis('equal')
        self._type_ax.set_title(shape_arabic_text('توزيع أنواع الصيانة'))
        self.type_canvas.figure.tight_layout()
        self.type_canvas.draw()

    def populate_dept_tab(self, data):
        self.dept_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.dept_table.setItem(i, 0, QTableWidgetItem(row['department']))
            self.dept_table.setItem(i, 1, QTableWidgetItem(str(row['count'])))

    def populate_devices_tab(self, data):
        self.devices_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.devices_table.setItem(i, 0, QTableWidgetItem(row['device_type']))
            self.devices_table.setItem(i, 1, QTableWidgetItem(str(row['count'])))
            
    def populate_techs_tab(self, data):
        self.techs_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.techs_table.setItem(i, 0, QTableWidgetItem(row['technician']))
            self.techs_table.setItem(i, 1, QTableWidgetItem(str(row['count'])))