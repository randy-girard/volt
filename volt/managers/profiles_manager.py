import contextlib

from PySide6.QtWidgets import QWidget, QPushButton, QListWidget
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from volt.windows import profile_window

from volt.models.profile import Profile
from volt.models.trigger import Trigger
from volt.models.trigger_group import TriggerGroup

class ProfilesManager(QWidget):
    def __init__(self, parent):
        super(ProfilesManager, self).__init__()

        self._parent = parent
        self.current_profile = None

        self.button = QPushButton("Add Profile")
        self.buttona = QPushButton("Edit Profile")
        self.buttonb = QPushButton("Remove Profile")

        self.buttona.setEnabled(False)
        self.buttonb.setEnabled(False)

        self.button.clicked.connect(self.addProfileWindow)
        self.buttona.clicked.connect(self.editProfileWindow)
        self.buttonb.clicked.connect(self.removeProfileWindow)

        self._parent.home_layout.addWidget(self.button, 1, 0)
        self._parent.home_layout.addWidget(self.buttona, 2, 0)
        self._parent.home_layout.addWidget(self.buttonb, 3, 0)

        self.profile_list = QListWidget()
        self.profile_list.itemClicked.connect(self.profileListItemClicked)
        self.profile_list.doubleClicked.connect(self.editProfileWindow)

    def load(self, json):
        for profile in json:
            Profile(self.profile_list, name=profile["name"],
                                       log_file=profile["log_file"],
                                       trigger_group_ids=profile.get("trigger_group_ids", []))


    def serialize(self):
        profiles = []
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            profiles.append(item.serialize())
        return profiles

    def profileListItemClicked(self, item):
        self.button.setEnabled(True)
        self.buttona.setEnabled(True)
        self.buttonb.setEnabled(True)

        self._parent.triggers_manager.trigger_list.blockSignals(True)
        self.current_profile = self.profile_list.currentItem()
        trigger_groups = self._parent.triggers_manager.trigger_list.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive);
        for trigger_group in trigger_groups:
            if type(trigger_group) is TriggerGroup:
                trigger_group.setCheckState(0, Qt.Unchecked)
        for trigger_group in trigger_groups:
            if type(trigger_group) is TriggerGroup and trigger_group.group_id in self.current_profile.trigger_group_ids:
                    trigger_group.setCheckState(0, Qt.Checked)
                    self._parent.triggers_manager.triggerListItemChangedOnParents(trigger_group, 0, Qt.Checked)
                    self._parent.triggers_manager.triggerListItemChangedOnChildren(trigger_group, 0, Qt.Checked)
        self._parent.triggers_manager.trigger_list.blockSignals(False)

        self._parent._parent.logreader.stop()
        if len(self.current_profile.log_file) > 0:
            self._parent._parent.logreader.setLogFile(self.current_profile.log_file)
            self._parent._parent.logreader.start()
            triggers = self._parent.triggers_manager.trigger_list.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive);
            for trigger in triggers:
                if type(trigger) is Trigger:
                    with contextlib.suppress(RuntimeError):
                        self._parent._parent.log_signal.disconnect(trigger.onLogUpdate)
                    self._parent._parent.log_signal.connect(trigger.onLogUpdate)

    def editProfileWindow(self, item):
        current_item = self.profile_list.currentItem()
        self.addProfileWindow(current_item)

    def addProfileWindow(self, item=None):
        self.profile_window = profile_window.ProfileWindow(self, item)
        self.profile_window.show()

    def removeProfileWindow(self):
        item = self.profile_list.currentItem()
        self.profile_list.takeItem(self.profile_list.row(item))
