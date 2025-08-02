# stylesheet.py

STYLE_SHEET = """
    /* General Window and Font Styles */
    QWidget {
        font-family: Segoe UI, Arial, sans-serif;
        font-size: 10pt;
        background-color: #ecf0f1; /* Light Gray-Blue Background */
        color: #34495e; /* Dark Blue-Gray Text */
    }
    QDialog {
        background-color: #ffffff;
    }
    QTableWidget::item:selected {
        background-color: #aed6f1; /* Light Blue for selection */
        color: #2c3e50;
    }

    /* Primary/Default Buttons */
    QPushButton {
        background-color: #3498db; /* Bright Blue */
        color: white;
        border-radius: 5px;
        padding: 8px 12px;
        border: 1px solid #2980b9;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #5dade2;
    }
    QPushButton:pressed {
        background-color: #2e86c1;
    }
    QPushButton:disabled {
        background-color: #bdc3c7;
        border: 1px solid #a1a6a9;
    }

    /* Green "Add" button */
    QPushButton#AddButton, QDialogButtonBox QPushButton:first-child {
        background-color: #27ae60; /* Green */
        border: 1px solid #229954;
    }
    QPushButton#AddButton:hover, QDialogButtonBox QPushButton:first-child:hover {
        background-color: #2ecc71;
    }

    /* Red "Delete" button */
    QPushButton#DeleteButton {
        background-color: #c0392b; /* Red */
        border: 1px solid #a93226;
    }
    QPushButton#DeleteButton:hover {
        background-color: #e74c3c;
    }

    /* Input Fields */
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
        background-color: #ffffff;
        color: #34495e;
        border: 1px solid #bdc3c7;
        border-radius: 4px;
        padding: 5px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 1px solid #3498db; /* Blue Accent Color */
    }
    
    /* QComboBox Dropdown Arrow Fix */
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top left; /* Changed to left for RTL */
        width: 20px;
        border-left-width: 1px;
        border-left-color: #bdc3c7;
        border-left-style: solid;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
    }
    QComboBox::down-arrow {
        image: url(placeholder.png); /* This is a trick to make Qt draw the default arrow */
        width: 10px;
        height: 10px;
    }


    /* Table Styles */
    QTableWidget {
        background-color: #ffffff;
        gridline-color: #e5e7e9;
        border: 1px solid #bdc3c7;
    }
    QHeaderView::section {
        background-color: #34495e; /* Dark Blue-Gray header */
        color: #ecf0f1;
        padding: 6px;
        border: 1px solid #5d6d7e;
        font-weight: bold;
    }

    /* Tab and GroupBox Styles */
    QGroupBox {
        border: 1px solid #bdc3c7;
        border-radius: 5px;
        margin-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
    }
    QTabBar::tab {
        background: #e5e7e9;
        border: 1px solid #bdc3c7;
        padding: 8px 15px;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: #ecf0f1;
    }
    QTabWidget::pane {
        border: 1px solid #bdc3c7;
        border-top: none;
    }
    
    /* Status Bar */
    QStatusBar {
        font-weight: bold;
    }
    
    /* ScrollBar Styles */
    QScrollBar:vertical {
        border: none;
        background: #e5e7e9;
        width: 12px;
        margin: 12px 0 12px 0;
    }
    QScrollBar::handle:vertical {
        background: #bdc3c7;
        min-height: 20px;
        border-radius: 6px;
    }
    QScrollBar:horizontal {
        border: none;
        background: #e5e7e9;
        height: 12px;
        margin: 0 12px 0 12px;
    }
    QScrollBar::handle:horizontal {
        background: #bdc3c7;
        min-width: 20px;
        border-radius: 6px;
    }
"""