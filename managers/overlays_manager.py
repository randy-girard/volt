from functools import partial

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from windows import overlay_window

from models.overlay import Overlay

class OverlaysManager(QWidget):
    def __init__(self, parent):
        super(OverlaysManager, self).__init__()

        self._parent = parent

        self.timer_overlays = []
        self.text_overlays = []

        self.overlay_tab = QWidget()
        self.overlay_layout = QVBoxLayout()
        self.overlay_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self.overlay_timers_layout = QHBoxLayout()
        self.overlay_timers_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.overlay_text_layout = QHBoxLayout()
        self.overlay_text_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.overlay_layout.addLayout(self.overlay_timers_layout)
        self.overlay_layout.addLayout(self.overlay_text_layout)

        self.addTimerOverlayButton = QPushButton("Add Timer Overlay")
        self.addTimerOverlayButton.clicked.connect(partial(self.createOverlay, { "type": "Timer" }))
        self.overlay_timers_layout.addWidget(self.addTimerOverlayButton)

        self.addTextOverlayButton = QPushButton("Add Text Overlay")
        self.addTextOverlayButton.clicked.connect(partial(self.createOverlay, { "type": "Text" }))
        self.overlay_text_layout.addWidget(self.addTextOverlayButton)

        self.overlay_tab.setLayout(self.overlay_layout)

    def load(self, json):
        for item in json.get("overlays", []):
            self.createOverlay(item)


    def serialize(self):
        overlays = []
        for overlay in self.timer_overlays:
            overlays.append(overlay.serialize())
        for overlay in self.text_overlays:
            overlays.append(overlay.serialize())
        return overlays

    def onOverlayButtonClick(self, overlay):
        overlay.toggleShow()

    def createOverlay(self, item):
        overlay = overlay_window.OverlayWindow(self, item)
        overlay.show()

        if overlay.data_model.type == "Timer":
            self._parent.categories_manager.category_timer_overlays.addItem(overlay.data_model.name)
            button = QPushButton(overlay.data_model.name)
            button.clicked.connect(partial(self.onOverlayButtonClick, overlay))
            overlay.setButton(button)
            self.overlay_timers_layout.addWidget(button)
            self.timer_overlays.append(overlay)
        elif overlay.data_model.type == "Text":
            self._parent.categories_manager.category_text_overlays.addItem(overlay.data_model.name)
            button = QPushButton(overlay.data_model.name)
            button.clicked.connect(partial(self.onOverlayButtonClick, overlay))
            overlay.setButton(button)
            self.overlay_text_layout.addWidget(button)
            self.text_overlays.append(overlay)


    def saveOverlayWindow(self, overlay):
        old_name = overlay.data_model.name
        overlay.data_model.name = overlay.overlay_name_input.text()
        overlay.button.setText(overlay.overlay_name_input.text())
        if overlay.data_model.type == "Timer":
            idx = self._parent.categories_manager.category_timer_overlays.findText(old_name)
            self._parent.categories_manager.category_timer_overlays.setItemText(idx, overlay.overlay_name_input.text())
        elif overlay.data_model.type == "Text":
            idx = self._parent.categories_manager.category_text_overlays.findText(old_name)
            self._parent.categories_manager.category_text_overlays.setItemText(idx, overlay.overlay_name_input.text())
        overlay.toggleShow()


    def destroyOverlayWindow(self, overlay):
        if overlay.data_model.type == "Timer":
            idx = self._parent.categories_manager.category_timer_overlays.findText(overlay.data_model.name)
            self._parent.categories_manager.category_timer_overlays.removeItem(idx)
            self.overlay_timers_layout.removeWidget(overlay)
            self.timer_overlays.remove(overlay)
        elif overlay.data_model.type == "Text":
            idx = self._parent.categories_manager.category_text_overlays.findText(overlay.data_model.name)
            self._parent.categories_manager.category_text_overlays.removeItem(idx)
            self.overlay_text_layout.removeWidget(overlay)
            self.text_overlays.remove(overlay)
        overlay.button.deleteLater()
        overlay.destroy()

    def clearOverlayWindows(self):
        for overlay in self.timer_overlays.copy():
            self.destroyOverlayWindow(overlay)
        for overlay in self.text_overlays.copy():
            self.destroyOverlayWindow(overlay)

    def destroy(self):
        for overlay in self.timer_overlays:
            overlay.button.deleteLater()
            overlay.destroy()
        for overlay in self.text_overlays:
            overlay.button.deleteLater()
            overlay.destroy()
