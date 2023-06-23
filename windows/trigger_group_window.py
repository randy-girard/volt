from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from models.trigger_group import TriggerGroup

class TriggerGroupWindow(QWidget):
    def __init__(self, parent, trigger_group=None, parent_group=None):
        super(TriggerGroupWindow, self).__init__()

        self.setWindowTitle("Trigger Group Editor")
        self._parent = parent
        self._trigger_group = trigger_group or TriggerGroup()
        self._parent_group = parent_group

        geo = self.geometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.setGeometry(geo)

        self.layout = QGridLayout()

        self.trigger_groupname_input = QLineEdit(self)
        self.trigger_groupname_input.setText(self._trigger_group.name)
        self.layout.addWidget(QLabel("Trigger Group Name", self), 0, 0)
        self.layout.addWidget(self.trigger_groupname_input, 0, 1)

        self.comments_input = QTextEdit(self)
        self.comments_input.setText(self._trigger_group.comments)
        self.layout.addWidget(QLabel("Comments", self), 1, 0, alignment=Qt.AlignTop)
        self.layout.addWidget(self.comments_input, 1, 1)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveTriggerGroup)

        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelTriggerGroup)

        self.button_layout = QGridLayout()
        self.button_layout.addWidget(self.saveBtn, 0, 0)
        self.button_layout.addWidget(self.cancelBtn, 0, 1)

        self.layout.addLayout(self.button_layout, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.layout)

    def saveTriggerGroup(self):
        self._trigger_group.setName(self.trigger_groupname_input.text())
        self._trigger_group.setComments(self.comments_input.toPlainText())

        max_group_id = -1
        items = self._parent.trigger_list.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive);
        for item in items:
            if type(item) is TriggerGroup and item.group_id > max_group_id:
                max_group_id = item.group_id
        self._trigger_group.group_id = max_group_id + 1

        if self._parent_group == None:
            self._parent.trigger_list.addTopLevelItem(self._trigger_group)
        else:
            self._parent_group.addChild(self._trigger_group)


        self.destroy()

    def cancelTriggerGroup(self):
        self.destroy()

    def destroy(self):
        self.trigger_groupname_input.setText("")
        self.comments_input.setText("")
        self.close()
        self.deleteLater()
