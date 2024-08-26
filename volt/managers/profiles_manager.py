import contextlib

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QListWidget
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel, QColor

from volt.windows import profile_window

from volt.models.profile import Profile
from volt.models.trigger import Trigger
from volt.models.trigger_group import TriggerGroup

from volt.utils.log_reader import LogReader

class ProfilesManager(QWidget):
    def __init__(self, parent):
        super(ProfilesManager, self).__init__()

        self._parent = parent
        self.files = []
        self.current_profile = None
        self.selected_profile = None

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

        self.logreader = LogReader()

    def load(self, json):
        for profile in json:
            self.files.append(profile["log_file"])
            Profile(self.profile_list, name=profile["name"],
                                       log_file=profile["log_file"],
                                       trigger_ids=profile.get("trigger_ids", []))


    def serialize(self):
        profiles = []
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            profiles.append(item.serialize())
        return profiles

    def editProfileWindow(self, item):
        current_item = self.profile_list.currentItem()
        self.addProfileWindow(current_item)

    def addProfileWindow(self, item=None):
        self.profile_window = profile_window.ProfileWindow(self, item)
        self.profile_window.show()

    def removeProfileWindow(self):
        item = self.profile_list.currentItem()
        self.profile_list.takeItem(self.profile_list.row(item))
        QApplication.instance().save()

    def profileListItemClicked(self, item):
        self.setTriggers(item)
        self.selected_profile = item
        self.button.setEnabled(True)
        self.buttona.setEnabled(True)
        self.buttonb.setEnabled(True)

    def setActiveByFile(self, file):
        for i in range(self.profile_list.count()):
            item = self.profile_list.item(i)
            item.setBackground( QColor('#ffffff'))
            if item.log_file == file:
                self.current_profile = item
                if self.selected_profile == None:
                    self.profile_list.setCurrentItem(item)
                    self.profileListItemClicked(item)

                item.setBackground( QColor('#7fc97f') )

                self.button.setEnabled(True)
                self.buttona.setEnabled(True)
                self.buttonb.setEnabled(True)

                self.logreader.stop()
                if len(item.log_file) > 0:
                    self.logreader.setLogFile(item.log_file)
                    self.logreader.start()


    def setTriggers(self, profile):
        self._parent.triggers_manager.trigger_list.blockSignals(True)
        triggers = self._parent.triggers_manager.trigger_list.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive);
        for trigger in triggers:
            trigger.setCheckState(0, Qt.Unchecked)
        for trigger in triggers:
            if type(trigger) is Trigger and trigger.trigger_id in profile.trigger_ids:
                trigger.setCheckState(0, Qt.Checked)
                self._parent.triggers_manager.triggerListItemChangedOnParents(trigger, 0, Qt.Checked)
                trigger.manageEvents(True)
        self._parent.triggers_manager.trigger_list.blockSignals(False)
