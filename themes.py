# themes.py

DARK_THEME_QSS = """
    QWidget {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 0px solid #555;
    }
    QTableWidget {
        background-color: #3c3c3c;
        gridline-color: #555;
    }
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox {
        background-color: #3c3c3c;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
    }
    QPushButton {
        background-color: #555;
        color: #f0f0f0;
        border: 1px solid #666;
        border-radius: 4px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #666;
    }
    QPushButton:pressed {
        background-color: #777;
    }
    QHeaderView::section {
        background-color: #444;
        color: #f0f0f0;
        padding: 4px;
        border: 1px solid #555;
    }
    QTabBar::tab {
        background: #3c3c3c;
        border: 1px solid #555;
        padding: 8px;
    }
    QTabBar::tab:selected {
        background: #555;
    }
"""

LIGHT_THEME_QSS = "" # An empty string will revert to the default system theme