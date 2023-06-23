import traceback
import ctypes
import sys, os

application_path = os.path.dirname(os.path.abspath(sys.argv[0]))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from windows import main_window

def run():
    app = QApplication(sys.argv)
    w = main_window.MainWindow(application_path)
    w.show()
    app.exec()


if __name__ == "__main__":
    try:
        run()
    except:
        with open("crash-log.txt", "w") as f:
            traceback.print_exc(file=f)
        raise
