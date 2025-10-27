from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt

class TriggerGroup(QTreeWidgetItem):
    def __init__(self, name="", trigger_group=None, comments="", group_id=None, checked=Qt.CheckState.Unchecked):
        checked = self.fromCheckState(checked)

        super().__init__()
        self.setTriggerGroup(trigger_group)
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(0, checked)
        self.setName(name)
        self.setComments(comments)

        self.group_id = group_id

    def setName(self, val):
        self.name = val
        self.setText(0, val)

    def getFullTriggerName(self):
        name = ""
        if self.trigger_group:
            name = self.trigger_group.getFullTriggerName()
            return name + " / " + self.name
        else:
            return self.name

    def setTriggerGroup(self, trigger_group):
        self.trigger_group = trigger_group

    def setComments(self, val):
        self.comments = val

    def isChecked(self):
        return self.checkState(0) == Qt.CheckState.Checked

    def fromCheckState(self, checkState):
        if checkState == 0:
            return Qt.CheckState.Unchecked
        elif checkState == 1:
            return Qt.CheckState.PartiallyChecked
        elif checkState == 2:
            return Qt.CheckState.Checked
        else:
            return checkState

    def checkStateToInt(self, checkState):
        if checkState == Qt.CheckState.Unchecked:
            return 0
        if checkState == Qt.CheckState.PartiallyChecked:
            return 1
        if checkState == Qt.CheckState.Checked:
            return 2

    def serialize(self):
        hash = {
            "type": "TriggerGroup",
            "name": self.name,
            "group_id": self.group_id,
            "comments": self.comments,
            "checked": self.checkStateToInt(self.checkState(0))
        }
        return hash
