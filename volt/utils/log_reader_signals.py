from PySide6.QtCore import QObject, Signal

class LogReaderSignals(QObject):
    new_line = Signal(object, str)
    def __init__(self):
        super().__init__()
