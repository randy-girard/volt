from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QPushButton, QListWidget, QWidget, QLabel, QComboBox, QLineEdit
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from utils.color_button import ColorButton

from models.category import Category

class CategoriesManager(QWidget):
    def __init__(self, parent):
        super(CategoriesManager, self).__init__()

        self._parent = parent

        self.category_tab = QWidget()
        self.category_layout = QGridLayout()
        self.category_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        button_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.addCategory)
        button_layout.addWidget(self.add_category_btn)

        self.remove_category_btn = QPushButton("Remove Category")
        self.remove_category_btn.clicked.connect(self.removeCategory)
        button_layout.addWidget(self.remove_category_btn)
        self.category_layout.addLayout(button_layout, 0, 0)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(200)
        self.category_list.itemClicked.connect(self.onCategorySelect)
        self.category_layout.addWidget(self.category_list, 1, 0)
        self.category_tab.setLayout(self.category_layout)

        self.category_panel = QWidget()
        self.category_panel_layout = QGridLayout()
        self.category_panel_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.category_name = QLineEdit(self)
        #self.category_name.setText()
        self.category_panel_layout.addWidget(QLabel("Name"), 0, 0)
        self.category_panel_layout.addWidget(self.category_name, 0, 1, 1, 2)

        self.category_text_overlays = QComboBox()
        self.category_panel_layout.addWidget(QLabel("Text"), 1, 0)
        self.category_panel_layout.addWidget(QLabel("Overlay"), 1, 1)
        self.category_panel_layout.addWidget(self.category_text_overlays, 1, 2)
        self.category_panel_layout.addWidget(QLabel("Colors"), 2, 1)
        self.text_color_picker_font = ColorButton("Font Color", color="#ffff00")
        self.category_panel_layout.addWidget(self.text_color_picker_font, 2, 2)

        self.category_timer_overlays = QComboBox()
        self.category_panel_layout.addWidget(QLabel("Timers"), 3, 0)
        self.category_panel_layout.addWidget(QLabel("Overlay"), 3, 1)
        self.category_panel_layout.addWidget(self.category_timer_overlays, 3, 2)
        self.category_panel_layout.addWidget(QLabel("Colors"), 4, 1)
        self.timer_color_picker_font = ColorButton("Font Color", color="#ffff00")
        self.category_panel_layout.addWidget(self.timer_color_picker_font, 4, 2)
        self.timer_color_picker_bar = ColorButton("Bar Color", color="#ff0000")
        self.category_panel_layout.addWidget(self.timer_color_picker_bar, 4, 3)

        self.category_save_btn = QPushButton("Save")
        self.category_save_btn.clicked.connect(self.saveCategory)
        self.category_panel_layout.addWidget(self.category_save_btn, 5, 0)

        self.category_layout.addLayout(self.category_panel_layout, 1, 1)

    def load(self, json):
        for category in json.get("categories", []):
            Category(self.category_list,
                     name=category.get("name"),
                     timer_overlay=category.get("timer_overlay"),
                     text_overlay=category.get("text_overlay"),
                     timer_font_color=category.get("timer_font_color", "#ffff00"),
                     timer_bar_color=category.get("timer_bar_color", "#ff0000"),
                     text_font_color=category.get("text_font_color", "#ff0000"))

        self.category_timer_overlays.clear()
        for timer_overlay in self._parent.overlays_manager.timer_overlays:
            self.category_timer_overlays.addItem(timer_overlay.data_model.name)

        self.category_text_overlays.clear()
        for text_overlay in self._parent.overlays_manager.text_overlays:
            self.category_text_overlays.addItem(text_overlay.data_model.name)

        if self.category_list.count() > 0:
            self.category_list.setCurrentRow(0)
            self.onCategorySelect(self.category_list.currentItem())


    def serialize(self):
        categories = []
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            categories.append(item.serialize())
        return categories

    def onCategorySelect(self, item):
        self.category_name.setText(item.name)
        if item.timer_overlay:
            self.category_timer_overlays.setCurrentText(item.timer_overlay)
        if item.text_overlay:
            self.category_text_overlays.setCurrentText(item.text_overlay)
        self.timer_color_picker_font.setColor(item.timer_font_color)
        self.timer_color_picker_bar.setColor(item.timer_bar_color)
        self.text_color_picker_font.setColor(item.text_font_color)

    def saveCategory(self):
        item = self.category_list.currentItem()
        item.setName(self.category_name.text())
        item.setTimerOverlay(self.category_timer_overlays.currentText())
        item.setTextOverlay(self.category_text_overlays.currentText())
        item.timer_font_color = self.timer_color_picker_font.color()
        item.timer_bar_color = self.timer_color_picker_bar.color()
        item.text_font_color = self.text_color_picker_font.color()

    def addCategory(self, event):
        category = Category(name="New Category")
        self.category_list.addItem(category)

    def removeCategory(self, event):
        item = self.category_list.currentItem()
        self.category_list.takeItem(self.category_list.row(item))
