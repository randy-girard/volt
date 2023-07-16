from PySide6.QtWidgets import QListWidgetItem

class Overlay(object):
    def __init__(self, parent=None, name="", type="", font="Arial", font_size=14):
        super().__init__()
        self._parent = parent
        self.setName(name)
        self.setType(type)

        self.font = font
        self.font_size = font_size

    def setName(self, val):
        self.name = val

    def setType(self, val):
        self.type = val

    def serialize(self):
        hash = {
            "name": self.name,
            "type": self.type,
            "font": self.font,
            "font_size": int(self.font_size)
        }
        return hash
