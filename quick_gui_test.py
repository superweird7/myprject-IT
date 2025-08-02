# quick_gui_test.py
import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel('PyQt5 is working!')
label.resize(200, 100)
label.show()
sys.exit(app.exec_())