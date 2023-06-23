import sys
import time
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QApplication
from PySide6.QtCore import Qt, QTimer

from triggers.timer import Timer
from triggers.text_trigger import TextTrigger

from utils.frameless_window_manager import FramelessWindowManager

from models.overlay import Overlay

if sys.platform == "darwin":
    from AppKit import NSWorkspace
elif sys.platform == "win32":
    from win32gui import GetWindowText, GetForegroundWindow

class OverlayWindow(FramelessWindowManager):
    def __init__(self, parent, config):
        super(OverlayWindow, self).__init__()

        self.is_transparent = True
        self._parent = parent
        self.triggers = []
        self.type = type

        self.data_model = Overlay(self, name=config.get("name", f"Default"),
                                        type=config.get("type", "Timer"))

        self.oldPos = self.pos()

        x = self.screen().availableGeometry().center().x()
        y = self.screen().availableGeometry().center().y()
        left = config.get("left", None)
        top = config.get("top", None)

        is_new_window = left == None and top == None

        self.setGeometry(left or x - 480 / 2,
                         top or y - 640 / 2,
                         config.get("width", 480),
                         config.get("height", 640))

        self.widget = QWidget()
        self.widget.setObjectName("mainWidget")
        self.widget.setMouseTracking(True)

        self.layout = QVBoxLayout(self.widget)
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.layout.setSpacing(2)

        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolBar")
        self.toolbar.setFixedHeight(50)
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.overlay_name_input = QLineEdit(self)
        self.overlay_name_input.setText(self.data_model.name)
        self.toolbar_layout.addWidget(self.overlay_name_input)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(partial(self._parent.saveOverlayWindow, self))
        self.toolbar_layout.addWidget(self.save_button)
        self.delete_button = QPushButton("Remove")
        self.delete_button.clicked.connect(partial(self._parent.destroyOverlayWindow, self))
        self.toolbar_layout.addWidget(self.delete_button)
        self.toolbar.setLayout(self.toolbar_layout)
        self.layout.addWidget(self.toolbar)

        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.base_window_flags = self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint

        self.setWindowFlags(self.base_window_flags)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);
        self.setTransparency(not is_new_window)

        #self.focusManager = QTimer()
        #self.focusManager.timeout.connect(self.onUpdateFocus)
        #self.focusManager.start(100)


    def setButton(self, button):
        self.button = button

    def onUpdateFocus(self):
        active_window_name = None

        if sys.platform == "darwin":
            active_window_name = (NSWorkspace.sharedWorkspace().activeApplication()["NSApplicationPath"])
        elif sys.platform == "win32":
            active_window_name = GetWindowText(GetForegroundWindow())

        # or is this window?
        if self.is_transparent and 'everquest' in active_window_name.lower():
            self.setVisible(True)
        elif not self.is_transparent:
            self.setVisible(True)
        else:
            self.setVisible(False)

    def addTimer(self, text, duration, trigger=None, category=None):
        timer = Timer(self, text, duration, trigger=trigger, category=category)
        self.layout.addWidget(timer)
        self.triggers.append(timer)

        return timer

    def addTextTrigger(self, text, category=None):
        text_trigger = TextTrigger(self, text, category=category)
        self.layout.addWidget(text_trigger)
        self.triggers.append(text_trigger)

    def serialize(self):
        hash = {
            "top": self.pos().y(),
            "left": self.pos().x(),
            "width": self.width(),
            "height": self.height()
        } | self.data_model.serialize()
        return hash


    def toggleShow(self):
        self.setTransparency(not self.is_transparent)

    def setTransparency(self, enabled):
        self.is_transparent = enabled
        if enabled:
            self.toolbar.hide()
            self.setWindowFlags(self.base_window_flags | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowDoesNotAcceptFocus)
            self.setAttribute(Qt.WA_ShowWithoutActivating, True)
            self.setAutoFillBackground(False)
            self.setCanManage(False)
        else:
            self.toolbar.show()
            self.setWindowFlags(self.base_window_flags)
            self.setAttribute(Qt.WA_ShowWithoutActivating, False)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
            self.setCanManage(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, enabled)
        self.setStyle(enabled)
        self.widget.show()
        self.show()


    def setStyle(self, is_transparent):
        opacity = 200
        if is_transparent:
            opacity = 0

        self.setStyleSheet(
            "OverlayWindow"
            "{"
                f"background: rgba(50, 50, 50, {opacity});"
                "border: 0px;"
            "}"

            "QWidget#mainWidget"
            "{"
                f"background: rgba(50, 50, 50, {opacity});"
                "border: 0px;"
            "}"

            "OverlayWindow QScrollArea"
            "{"
                f"background: rgba(50, 50, 50, {opacity});"
                "border: 0px;"
            "}"
        )


    def destroy(self):
        for trigger in self.triggers:
            trigger.destroy()
        self.deleteLater()

    # def mousePressEvent(self, event):
    #     self.oldPos = self.window().mapFromGlobal(event.globalPosition().toPoint())
    #
    # def mouseMoveEvent(self, event):
    #     delta = self.window().mapFromGlobal(event.globalPosition().toPoint() - self.oldPos)
    #     self.move(self.x() + delta.x(), self.y() + delta.y())
    #     self.oldPos = self.window().mapFromGlobal(event.globalPosition().toPoint())
