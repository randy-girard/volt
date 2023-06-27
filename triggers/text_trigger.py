from PySide6.QtWidgets import QApplication, QProgressBar, QSizePolicy, QLabel
from PySide6.QtCore import Signal, Slot, QObject, Qt, QTimer
from PySide6.QtGui import QPainter, QColor

from datetime import datetime, timedelta

class TextTrigger(QLabel):
    signal = Signal()

    def __init__(self, parent, label, category=None, matches=None):
        super().__init__()

        self.active = True
        self.starttime = datetime.now()
        self.endtime = self.starttime + timedelta(seconds=5)
        self.label = label
        self.parent = parent
        self.category = category
        self.matches = matches

        if self.category:
            self.setStyleSheet(
                "OverlayWindow QLabel"
                "{"
                    f"color: {self.category.text_font_color};"
                "}"
            )
        else:
            self.setStyleSheet(
                "OverlayWindow QLabel"
                "{"
                    "color: #ffff00;"
                "}"
            )

        self.adjustSize()
        self.setText(label)

        self.signal.connect(self.onUpdate)

        self.timer = QTimer()
        self.timer.timeout.connect(self.onUpdateEmit)
        self.timer.start(100)

    def onUpdateEmit(self):
        self.signal.emit()

    def onDoubleClick(self):
        self.destroy()

    @Slot()
    def onUpdate(self):
        if self.active:
            ratio = 1 - (datetime.now() - self.starttime) / (self.endtime - self.starttime)
            if(ratio < 0):
                self.active = False
                self.destroy()

    def destroy(self):
        self.timer.stop()
        self.parent.triggers.remove(self)
        self.parent.layout.removeWidget(self)
        self.setParent(None)
        self.setVisible(False)
        self = None
