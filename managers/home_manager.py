from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from managers.profiles_manager import ProfilesManager
from managers.triggers_manager import TriggersManager
from managers.config_manager import ConfigManager

class HomeManager(QWidget):
    def __init__(self, parent):
        super(HomeManager, self).__init__()

        self._parent = parent

        self.home_tab = QWidget()
        self.home_tab.setFixedHeight(150)

        self.home_layout = QGridLayout()
        self.home_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.profiles_manager = ProfilesManager(self)
        self.triggers_manager = TriggersManager(self)

        button4 = QPushButton("Save Config")
        button5 = QPushButton("Import GINA Config")

        button4.clicked.connect(self._parent.config_manager.save)
        button5.clicked.connect(self._parent.config_manager.importGinaConfig)

        self.home_layout.addWidget(button4, 1, 3)
        self.home_layout.addWidget(button5, 1, 4)

        self.home_tab.setLayout(self.home_layout)


    def load(self, json):
        self.profiles_manager.load(json.get("profiles", []))
        self.triggers_manager.load(json.get("trigger_groups", []))
