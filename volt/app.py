import os, sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from volt.windows import main_window

class App():
    def run(self, args):
        application_path = os.path.dirname(os.path.abspath(args[0]))

        app = QApplication(args)
        w = main_window.MainWindow(application_path)
        w.show()
        app.exec()
