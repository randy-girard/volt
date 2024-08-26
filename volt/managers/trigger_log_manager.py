from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt

class TriggerLogManager(QWidget):
    def __init__(self, parent):
        super(TriggerLogManager, self).__init__()

        self._parent = parent

        self.tab = QWidget()
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Log Time", "Trigger", "Matched Text"])
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.layout.addWidget(self.table)
        self.tab.setLayout(self.layout)

    def addItem(self, time, trigger, text):
        time_item = QTableWidgetItem(time)
        trigger_item = QTableWidgetItem(trigger)
        text_item = QTableWidgetItem(text)
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, time_item)
        self.table.setItem(row_count, 1, trigger_item)
        self.table.setItem(row_count, 2, text_item)
        self.table.resizeColumnsToContents()        
        self.table.resizeRowsToContents()
