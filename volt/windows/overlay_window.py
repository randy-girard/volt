import sys
import time
from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QApplication, QFontComboBox, QComboBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from volt.triggers.timer import Timer
from volt.triggers.text_trigger import TextTrigger

from volt.utils.frameless_window_manager import FramelessWindowManager

from volt.models.overlay import Overlay

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
                                        type=config.get("type", "Timer"),
                                        font=config.get("font", "Arial"),
                                        font_size=config.get("font_size", 14),
                                        sort_method=config.get("sort_method", "Order Triggered"))

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

        self.trigger_layout = QVBoxLayout()
        self.trigger_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.trigger_layout.setSpacing(2)

        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolBar")
        #self.toolbar.setFixedHeight(50)
        self.toolbar_layout = QGridLayout(self.toolbar)
        self.toolbar_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.overlay_name_input = QLineEdit(self)
        self.overlay_name_input.setText(self.data_model.name)
        self.toolbar_layout.addWidget(self.overlay_name_input, 0, 0, 0, 2, Qt.AlignTop)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(partial(self._parent.saveOverlayWindow, self))
        self.toolbar_layout.addWidget(self.save_button, 0, 2)

        self.overlay_font_input = QFontComboBox(self)
        self.overlay_font_input.setCurrentFont(QFont(self.data_model.font))
        self.toolbar_layout.addWidget(self.overlay_font_input, 1, 0)
        self.overlay_font_size_input = QLineEdit(self)
        self.overlay_font_size_input.setText(str(self.data_model.font_size))
        self.toolbar_layout.addWidget(self.overlay_font_size_input, 1, 1)

        self.overlay_sort_method_input = QComboBox()
        self.overlay_sort_method_input.addItem("Order Triggered")
        self.overlay_sort_method_input.addItem("Time Remaining")
        self.overlay_sort_method_input.addItem("Timer Text")
        self.overlay_sort_method_input.addItem("Timer Text (Desc)")
        self.overlay_sort_method_input.setCurrentText(self.data_model.sort_method)
        self.toolbar_layout.addWidget(self.overlay_sort_method_input, 1, 2)

        self.toolbar.setLayout(self.toolbar_layout)
        self.layout.addWidget(self.toolbar)
        self.layout.addLayout(self.trigger_layout)

        self.setWidget(self.widget)
        self.setWidgetResizable(True)
        self.base_window_flags = self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool

        self.setWindowFlags(self.base_window_flags)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff);
        self.setTransparency(not is_new_window)

    def setButton(self, button):
        self.button = button

    def addTimer(self, text, duration, trigger=None, category=None, matches=None):
        timer = Timer(self, text, duration, trigger=trigger, category=category, matches=matches)
        self.trigger_layout.addWidget(timer)
        self.triggers.append(timer)

        self._parent.sortTriggers(self)

        return timer

    def addTextTrigger(self, text, category=None, matches=None):
        text_trigger = TextTrigger(self, text, category=category, matches=matches)
        self.trigger_layout.addWidget(text_trigger)
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
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
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
