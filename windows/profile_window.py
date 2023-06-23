from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from models.profile import Profile

class ProfileWindow(QWidget):
    def __init__(self, parent, profile=None):
        super(ProfileWindow, self).__init__()

        self.setWindowTitle("Profile Editor")
        self._parent = parent
        self._profile = profile or Profile()

        geo = self.geometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.setGeometry(geo)

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.name_input = QLineEdit(self)
        self.name_input.setText(self._profile.name)
        self.layout.addWidget(QLabel("Name"), 0, 0)
        self.layout.addWidget(self.name_input, 0, 1, 1, 2)

        self.logfile_input = QLineEdit(self)
        self.logfile_input.setText(self._profile.log_file)
        self.logfile_select_btn = QPushButton("Select Log File")
        self.logfile_select_btn.clicked.connect(self.selectLogFile)
        self.layout.addWidget(QLabel("Log File"), 1, 0)
        self.layout.addWidget(self.logfile_input, 1, 1)
        self.layout.addWidget(self.logfile_select_btn, 1, 2)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveProfile)

        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelProfile)

        self.button_layout = QGridLayout()
        self.button_layout.addWidget(self.saveBtn, 0, 0)
        self.button_layout.addWidget(self.cancelBtn, 0, 1)

        self.layout.addLayout(self.button_layout, 2, 0, 1, 3, alignment=Qt.AlignRight)

        self.setLayout(self.layout)

    def selectLogFile(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.AnyFile)

        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.logfile_input.setText(filenames[0])


    def saveProfile(self):
        self._profile.setName(self.name_input.text())
        self._profile.setLogFile(self.logfile_input.text())
        self._parent.profile_list.addItem(self._profile)
        self.destroy()

    def cancelProfile(self):
        self.destroy()

    def destroy(self):
        self.name_input.setText("")
        self.logfile_input.setText("")
        self.close()
        self.deleteLater()
