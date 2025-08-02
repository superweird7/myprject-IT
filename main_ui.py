from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# Assuming these are your custom windows
from entry_ui import EntryWindow
from search_ui import SearchWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام توثيق أعمال الصيانة")
        self.setGeometry(100, 100, 550, 350)
        self.setLayoutDirection(Qt.RightToLeft)

        # Set a light, friendly background for the main window
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Arial';
            }
        """)

        # Create the main layout with generous spacing
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        # Add a welcoming title with a warm color
        title_label = QLabel("نظام توثيق الصيانة")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #34495e; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Add a short subtitle for context and user guidance
        subtitle_label = QLabel("اختر إحدى الخيارات لإدارة بيانات الصيانة")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        layout.addWidget(subtitle_label)

        # Style the Entry button with a friendly blue tone
        self.btn_entry = QPushButton("إدخال بيانات الصيانة")
        self.btn_entry.setFont(QFont("Arial", 12))
        self.btn_entry.setFixedHeight(55)
        self.btn_entry.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #3a7bc8;
            }
            QPushButton:pressed {
                background-color: #2c62a3;
            }
        """)
        # Optional: Add icon for visual cue (uncomment if you have an icon file)
        # self.btn_entry.setIcon(QIcon("path/to/entry_icon.png"))
        self.btn_entry.clicked.connect(self.open_entry)
        layout.addWidget(self.btn_entry)

        # Style the Search button with a friendly teal tone
        self.btn_search = QPushButton("البحث في بيانات الصيانة")
        self.btn_search.setFont(QFont("Arial", 12))
        self.btn_search.setFixedHeight(55)
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #50c1b0;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #40a899;
            }
            QPushButton:pressed {
                background-color: #328c7e;
            }
        """)
        # Optional: Add icon for visual cue (uncomment if you have an icon file)
        # self.btn_search.setIcon(QIcon("path/to/search_icon.png"))
        self.btn_search.clicked.connect(self.open_search)
        layout.addWidget(self.btn_search)

        # Add stretch to keep content centered vertically
        layout.addStretch()

        self.setLayout(layout)

    def open_entry(self):
        self.entry_window = EntryWindow()
        self.entry_window.show()

    def open_search(self):
        self.search_window = SearchWindow()
        self.search_window.show()