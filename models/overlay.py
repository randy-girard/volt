from PySide6.QtWidgets import QListWidgetItem

class Overlay(object):
    def __init__(self, parent=None, name="", type=""):
        super().__init__()
        self._parent = parent
        self.setName(name)
        self.setType(type)

    def setName(self, val):
        self.name = val

    def setType(self, val):
        self.type = val

    def serialize(self):
        hash = {
            "name": self.name,
            "type": self.type
        }
        return hash
