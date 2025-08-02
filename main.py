import sys, os
if sys.executable.endswith('pythonw.exe'):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.path.join(os.getenv('TEMP'), 'stderr-{}'.format(os.path.basename(sys.argv[0]))), "w")
    
# main.py
import sys
from PyQt5.QtWidgets import QApplication
from login_ui import LoginWindow
from stylesheet import STYLE_SHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())