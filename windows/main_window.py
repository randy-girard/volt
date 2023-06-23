import json

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PySide6.QtCore import Signal, Slot, Qt, QEvent
from PySide6.QtGui import QStandardItemModel
from pubsub import pub

from models.category import Category

from utils.log_reader import LogReader
from utils.speaker import Speaker

from managers.home_manager import HomeManager
from managers.categories_manager import CategoriesManager
from managers.overlays_manager import OverlaysManager
from managers.config_manager import ConfigManager

class MainWindow(QWidget):
    log_signal = Signal(str)

    def __init__(self, application_path):
        super(MainWindow, self).__init__()

        geo = self.geometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.setGeometry(geo.x(), geo.y(), 800, 600)

        self.application_path = application_path
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.speaker = Speaker()

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.config_manager = ConfigManager(self)
        self.home_manager = HomeManager(self)
        self.profiles_manager = self.home_manager.profiles_manager
        self.triggers_manager = self.home_manager.triggers_manager
        self.categories_manager = CategoriesManager(self)
        self.overlays_manager = OverlaysManager(self)

        self.main_layout.addWidget(self.profiles_manager.profile_list)
        self.main_layout.addWidget(self.triggers_manager.trigger_list)

        self.setLayout(self.layout)

        self.config_manager.load()

        self.setupTabs()
        self.layout.addWidget(self.main_widget)

        self.logreader = LogReader()
        self.log_signal.connect(self.onLogUpdate)

        pub.subscribe(self.log_handler, 'log')


    def setupTabs(self):
        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(150)
        self.tabs.currentChanged.connect(self.onTabChange)
        self.tabs.addTab(self.home_manager.home_tab, "Home")
        self.tabs.addTab(self.overlays_manager.overlay_tab, "Overlays")
        self.tabs.addTab(self.categories_manager.category_tab, "Categories")
        self.layout.addWidget(self.tabs)


    def onTabChange(self, index):
        if index == 2: # Categories tab
            self.main_widget.setVisible(False)
            self.tabs.setFixedHeight(570)
            self.setFixedHeight(600)
        else:
            self.main_widget.setVisible(True)
            self.tabs.setFixedHeight(150)
            self.setFixedHeight(600)

    def destroy(self):
        self.logreader.stop()
        self.overlays_manager.destroy()

    def closeEvent(self, event):
        self.destroy()

    def log_handler(self, text):
        self.log_signal.emit(text)


    @Slot(str)
    def onLogUpdate(self, text):
        pass
        #print(str)
