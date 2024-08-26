from PySide6.QtWidgets import QListWidgetItem

class Profile(QListWidgetItem):
    def __init__(self, parent=None, name="", log_file="", trigger_ids=[]):
        super().__init__(name, parent)
        self._parent = parent
        self.setName(name)
        self.setLogFile(log_file)
        self.trigger_ids = trigger_ids

    def setName(self, val):
        self.name = val
        self.setText(val)

    def setLogFile(self, val):
        self.log_file = val

    def serialize(self):
        hash = {
            "name": self.name,
            "log_file": self.log_file,
            "trigger_ids": self.trigger_ids
        }
        return hash
