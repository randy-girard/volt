import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from volt.windows import main_window
from volt.utils.log_reader_signals import LogReaderSignals

class App(QApplication):
    def __init__(self, *args):
        super().__init__(*args)

        self._signals = {}
        self._signals['logreader'] = LogReaderSignals()

        application_path = os.path.dirname(os.path.abspath(*args[0]))

        w = main_window.MainWindow(application_path)
        w.show()
