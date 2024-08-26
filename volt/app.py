import os
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from volt.windows import main_window
from volt.utils.log_reader_signals import LogReaderSignals
from volt.utils.regex_engine import RegexEngine

try:
    from plugins.nParse.helpers import resource_path, config
    from plugins.nParse.helpers.settings import SettingsSignals
    from plugins.nParse.parsers.maps import Maps
    from plugins.nParse.parsers.maps.window import MapsSignals
    from plugins.nParse.parsers.discord import Discord

    config.load('nparse.config.json')
    config.verify_settings()
except ImportError:
    pass

class App(QApplication):
    def __init__(self, *args):
        super().__init__(*args)

        self.loaded = False
        self.plugins = {}

        self._signals = {}
        self._signals['logreader'] = LogReaderSignals()
        self._signals['timers'] = []

        self.config_manager = None

        try:
            self._signals['settings'] = SettingsSignals()
            self._signals['maps'] = MapsSignals()
            QApplication.instance()._discord = Discord()
            QApplication.instance()._map = Maps()
            QApplication.instance()._signals["logreader"].new_line.connect(
                QApplication.instance()._map.parse
            )
            self.setStyleSheet(open(resource_path(os.path.join('data', 'ui', '_.css'))).read())
        except:
            pass

        application_path = os.path.dirname(os.path.abspath(*args[0]))

        w = main_window.MainWindow(application_path)
        self.loaded = True
        w.show()

    def save(self):
        if self.config_manager and self.loaded:
            self.config_manager.save()
