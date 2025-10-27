import unittest
import re

from volt.models.category import Category
from volt.triggers.timer import Timer
from volt.windows.overlay_window import OverlayWindow
from volt.managers.overlays_manager import OverlaysManager
from volt.utils.log_reader import LogReader

from PySide6.QtWidgets import QApplication

class TestTest(unittest.TestCase):
    #def setUp(self):
        #self.app = QApplication.instance() or QApplication()
        #self.app.current_profile = None

    def test_sort_value(self):
        #manager = OverlaysManager(parent=None)
        #parent = OverlayWindow(parent=manager, config={})
        #category = Category()
        #timer = Timer(parent=parent, label='test', duration=10, category=category)
        l = LogReader()
        line = "[Sun Aug 11 10:51:53 2024] Hi Bob."
        line ="Player has been poisoned."
        for i in range(10000000):
            re.search("^{s}(?: has be)en poisoned\.$", line)
            #"^{c}".replace("${", "{")
            #"^{c}".replace("^{", "{")
            #a = l.parse_line(line)
            #b = l.parse_line2(line)
            #self.assertEqual(a, b)
            #stripped_line = stripped_line.strip()
            #re.sub("(\^|\$)\{", "{", "^{c}")
            #self.assertEqual("^{c}".replace("^{", "{"), "{c}")
            #self.assertEqual("^{c}".replace("${", "{"), "^{c}")
            #text = text.replace("^{", "{")
            #text = text.replace("${", "{")
            #self.assertEqual(re.sub("(\^|\$)\{", "{", "^{c}"), "{c}")
            #timer.sortValue()
