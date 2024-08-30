from PyQt6.QtCore import QObject, pyqtSignal

class LogReaderSignals(QObject):
    new_line = pyqtSignal(object, str)
    def __init__(self):
        super().__init__()
