from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor, QIcon, QBrush
# Assuming db_ops.py exists and contains these functions:
# def insert_record(data): ...
# def fetch_records(): ...
# def delete_record(record_id): ...
# def update_record(record_id, data): ...
# For demonstration, let's mock these functions if db_ops is not available.
# In a real application, ensure db_ops.py is correctly implemented.
try:
    from db_ops import insert_record, fetch_records, delete_record, update_record
except ImportError:
    print("Warning: db_ops.py not found. Using mock functions.")
    def insert_record(data):
        print(f"Mock insert: {data}")
    def fetch_records():
        print("Mock fetch")
        # Return dummy data for demonstration
        return [
            (1, "2023-01-15", "Preventive", "Server Rack A", "John Doe", "Cleaned filters, checked cables", "Compressed air, cable ties", "All systems nominal", "None"),
            (2, "2023-02-20", "Corrective", "HVAC Unit 3", "Jane Smith", "Replaced faulty capacitor", "Capacitor (10uF)", "Unit now cooling", "Monitor temperature closely"),
        ]
    def delete_record(record_id):
        print(f"Mock delete: {record_id}")
    def update_record(record_id, data):
        print(f"Mock update: ID {record_id}, Data {data}")


class MaintenanceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام توثيق أعمال الصيانة")
        self.setGeometry(100, 100, 1000, 700) # Slightly increased height for better spacing
        self.setLayoutDirection(Qt.RightToLeft)

        self.inputs = {}
        self.selected_id = None

        self.apply_global_styles()
        self.build_ui()
        self.load_data()

    def apply_global_styles(self):
        # Set a default font for a more professional look
        default_font = QFont("Arial", 11)
        self.setFont(default_font)

        # Apply a simple stylesheet for overall theming
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f7f6; /* Light grey background */
                color: #333;
            }
            QLabel {
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #fff; /* White background for inputs */
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #007bff; /* Blue border on focus */
            }
            QPushButton {
                background-color: #28a745; /* Green for save */
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px; /* Consistent button width */
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton#delete_btn { /* Specific style for delete button */
                background-color: #dc3545; /* Red for delete */
            }
            QPushButton#delete_btn:hover {
                background-color: #c82333;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                gridline-color: #ddd; /* Lighter grid lines */
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #a8dadc; /* Light blue for selected rows */
                color: #333;
            }
            QTableWidget::horizontalHeader {
                background-color: #007bff; /* Blue header */
                color: white;
                font-weight: bold;
                padding: 5px;
                border-bottom: 2px solid #0056b3;
            }
            QTableWidget::section {
                padding: 8px;
                border: 1px solid #ccc;
            }
            .error-label { /* For potential error messages */
                color: red;
                font-weight: normal;
            }
        """)

    def build_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Input Section
        input_form_layout = QVBoxLayout()
        input_form_layout.setSpacing(10) # Space between input groups

        fields = [
            ("date", "تاريخ الصيانة"),
            ("type", "نوع الصيانة"),
            ("device", "اسم الجهاز"),
            ("technician", "اسم الفني"),
            ("procedures", "الإجراءات المتبعة"),
            ("materials", "المواد المستخدمة"),
            ("notes", "ملاحظات"),
            ("warnings", "تحذيرات")
        ]

        for key, label_text in fields:
            label = QLabel(label_text)
            if key in ["procedures", "materials", "notes", "warnings"]:
                input_widget = QTextEdit()
                input_widget.setMinimumHeight(80) # Give more space to text areas
            else:
                input_widget = QLineEdit()

            input_form_layout.addWidget(label)
            input_form_layout.addWidget(input_widget)
            self.inputs[key] = input_widget

        # Buttons Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15) # Space between buttons

        btn_save = QPushButton("حفظ")
        btn_save.clicked.connect(self.save_record)
        btn_save.setToolTip("حفظ سجل الصيانة الحالي")
        button_layout.addWidget(btn_save)

        btn_clear = QPushButton("مسح") # Added a clear button
        btn_clear.clicked.connect(self.clear_inputs)
        btn_clear.setToolTip("مسح جميع حقول الإدخال")
        button_layout.addWidget(btn_clear)

        btn_delete = QPushButton("حذف")
        btn_delete.clicked.connect(self.delete_record)
        btn_delete.setObjectName("delete_btn") # Assign object name for specific styling
        btn_delete.setToolTip("حذف السجل المحدد حاليًا")
        button_layout.addWidget(btn_delete)

        # Add buttons to the main layout, aligned to the right if possible
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        main_layout.addLayout(input_form_layout)
        main_layout.addWidget(button_container)


        # Table Section
        self.table = QTableWidget()
        self.table.setSortingEnabled(True) # Enable sorting
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Make table non-editable directly

        # Adjust column count and headers
        headers = ["ID"] + [label for _, label in fields]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Configure header resizing
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setStretchLastSection(False) # Allow last column to not stretch

        # Set selection behavior to select entire rows
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection) # Allow only one row selection

        self.table.cellClicked.connect(self.on_row_select)
        self.table.cellDoubleClicked.connect(self.on_row_double_click) # Optional: double-click to edit

        main_layout.addWidget(self.table)

        # Adjust spacing within the main layout
        main_layout.setSpacing(15)
        # Add some padding around the main layout
        main_layout.setContentsMargins(20, 20, 20, 20)


    def save_record(self):
        # Basic validation: Ensure essential fields are not empty
        if not self.inputs["date"].text() or not self.inputs["device"].text():
            # In a real app, you'd show a message box or status bar message
            print("Error: Date and Device are required.")
            return

        data_values = {}
        for key in ["date", "type", "device", "technician", "procedures", "materials", "notes", "warnings"]:
            widget = self.inputs[key]
            if isinstance(widget, QTextEdit):
                data_values[key] = widget.toPlainText()
            else:
                data_values[key] = widget.text()

        # Convert data_values to a tuple in the correct order for DB operations
        data_tuple = tuple(data_values[k] for k in ["date", "type", "device", "technician", "procedures", "materials", "notes", "warnings"])

        if self.selected_id is None:
            insert_record(data_tuple)
            print("Record saved successfully.")
        else:
            update_record(self.selected_id, data_tuple)
            print(f"Record with ID {self.selected_id} updated successfully.")
            self.selected_id = None # Reset selection after update

        self.load_data()
        self.clear_inputs()

    def load_data(self):
        try:
            records = fetch_records()
            self.table.setRowCount(len(records))

            # Map database columns to table columns, including ID at index 0
            column_map = {
                0: "id", 1: "date", 2: "type", 3: "device", 4: "technician",
                5: "procedures", 6: "materials", 7: "notes", 8: "warnings"
            }

            for row_idx, row_data in enumerate(records):
                for col_idx in range(self.table.columnCount()):
                    # Ensure we don't go out of bounds for row_data
                    if col_idx < len(row_data):
                        value = row_data[col_idx]
                    else:
                        value = "" # Empty string if data is missing for a column

                    item_text = str(value) if value is not None else ""
                    item = QTableWidgetItem(item_text)

                    # Make ID column non-editable and center-aligned if desired
                    if col_idx == 0:
                        item.setTextAlignment(Qt.AlignCenter)
                        # item.setFlags(item.flags() & ~Qt.ItemIsEditable) # Already set globally

                    self.table.setItem(row_idx, col_idx, item)

            # Resize columns to fit content after loading data
            self.table.resizeColumnsToContents()
            # Re-apply stretch for better initial appearance if needed
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.horizontalHeader().setStretchLastSection(False)

        except Exception as e:
            print(f"Error loading data: {e}")
            # In a real app, display an error message to the user

    def on_row_select(self, row, column):
        # Get the ID from the first column (ID column)
        id_item = self.table.item(row, 0)
        if id_item:
            try:
                self.selected_id = int(id_item.text())
                self.populate_inputs_from_row(row)
            except ValueError:
                print(f"Invalid ID found: {id_item.text()}")
                self.selected_id = None
        else:
            self.selected_id = None

        # Highlight the selected row
        self.table.selectRow(row)

    def on_row_double_click(self, row, column):
        """Optional: Double-clicking a row could also populate inputs for editing."""
        self.on_row_select(row, column)

    def populate_inputs_from_row(self, row):
        """Populates the input fields based on the selected row in the table."""
        keys = ["date", "type", "device", "technician", "procedures", "materials", "notes", "warnings"]
        for idx, key in enumerate(keys, start=1): # Start from index 1 because ID is at 0
            item_widget = self.table.item(row, idx)
            if item_widget:
                value = item_widget.text()
                widget = self.inputs[key]
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)
            else:
                # Clear input if no item exists in table for this cell
                widget = self.inputs[key]
                if isinstance(widget, QTextEdit):
                    widget.clear()
                else:
                    widget.setText("")


    def clear_inputs(self):
        """Clears all input fields and resets the selected ID."""
        for widget in self.inputs.values():
            if isinstance(widget, QTextEdit):
                widget.clear()
            else:
                widget.setText("")
        self.selected_id = None
        # Deselect any row in the table
        self.table.clearSelection()

    def delete_record(self):
        if self.selected_id:
            try:
                delete_record(self.selected_id)
                print(f"Record with ID {self.selected_id} deleted successfully.")
                self.selected_id = None
                self.load_data()
                self.clear_inputs()
            except Exception as e:
                print(f"Error deleting record: {e}")
                # Display error message to user
        else:
            print("No record selected for deletion.")
            # Display message to user


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_app = MaintenanceApp()
    main_app.show()
    sys.exit(app.exec_())