import re
import sys

from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLineEdit, QCheckBox, QLabel, QComboBox, QTabWidget, QHBoxLayout, QPushButton, QVBoxLayout, QGroupBox, QRadioButton, QFileDialog, QTableWidget, QHeaderView, QTableWidgetItem, QAbstractItemView
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel, QKeyEvent

from volt.models.trigger import Trigger

class TriggerEndEarlyTable(QTableWidget):
    def __init__(self, rows, cols):
        super().__init__(rows, cols)

    def keyPressEvent(self, event: QKeyEvent):
        num_rows = self.rowCount()
        col = self.currentColumn()
        row = self.currentRow()
        if row > 0 and event.key() == Qt.Key_Up:
            self.setCurrentCell(row - 1, col)
        elif row < num_rows - 1 and event.key() == Qt.Key_Down:
            self.setCurrentCell(row + 1, col)
        elif event.key() == Qt.Key_Return:  # 16777220 # Enter
            if row >= num_rows - 1:
                self.insertRow(self.rowCount())
                item = QTableWidgetItem();
                item.setFlags(item.flags() | Qt.ItemIsEditable);
                item.setData(Qt.DisplayRole, "");
                self.setItem(num_rows, 0, item);
                item2 = QTableWidgetItem();
                item2.setCheckState(Qt.Unchecked);
                self.setItem(num_rows, 1, item2);
                self.resizeRowsToContents()
            self.setCurrentCell(row + 1, col)
        elif num_rows > 1 and event.key() == Qt.Key_Delete:
            self.removeRow(row)
            self.setCurrentCell(row - 1, col)

class TriggerWindow(QWidget):
    def __init__(self, parent, trigger=None, trigger_group=None, is_new=False):
        super(TriggerWindow, self).__init__()

        self.setWindowTitle("Trigger Editor")
        self._parent = parent
        self.category_list = self._parent._parent._parent.categories_manager.category_list
        self._trigger_group = trigger_group
        self._trigger = None
        self._is_new = is_new

        if trigger:
            self._trigger = trigger
        else:
            self._trigger = Trigger()

        geo = self.geometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.setGeometry(geo)

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.trigger_input = QLineEdit(self)
        self.trigger_input.setText(self._trigger.name)
        self.layout.addWidget(QLabel("Trigger Name", self), 0, 0)
        self.layout.addWidget(self.trigger_input, 0, 1)

        self.search_text_input = QLineEdit(self)
        self.search_text_input.setText(self._trigger.search_text)
        self.layout.addWidget(QLabel("Search Text", self), 1, 0)
        self.layout.addWidget(self.search_text_input, 1, 1)

        self.use_regex_cb = QCheckBox("Use Regex")
        self.use_regex_cb.setChecked(self._trigger.use_regex)
        self.layout.addWidget(self.use_regex_cb, 2, 0)

        self.category_select = QComboBox()
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            self.category_select.addItem(item.name, item)
        self.category_select.setCurrentText(self._trigger.category)
        self.layout.addWidget(QLabel("Category"), 3, 0)
        self.layout.addWidget(self.category_select, 3, 1)

        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.saveTrigger)

        self.cancelBtn = QPushButton("Cancel")
        self.cancelBtn.clicked.connect(self.cancelTrigger)

        self.button_layout = QGridLayout()
        self.button_layout.addWidget(self.saveBtn, 0, 0)
        self.button_layout.addWidget(self.cancelBtn, 0, 1)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.buildBasicTab(), "Basic")
        self.tabs.addTab(self.buildTimerTab(), "Timer")
        self.tabs.addTab(self.buildTimerEndingTab(), "Timer Ending")
        self.tabs.addTab(self.buildTimerEndedTab(), "Timer Ended")
        self.tabs.addTab(self.buildCounterTab(), "Counter")

        self.layout.addWidget(self.tabs, 4, 0, 1, 2)
        self.layout.addLayout(self.button_layout, 5, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.layout)

    def buildBasicTab(self):
        self.basic_tab = QWidget()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        box = QGroupBox("Text Settings")
        self.use_text = QCheckBox()
        self.use_text.setChecked(self._trigger.use_text)
        label1 = QLabel("Display Text")
        self.display_text = QLineEdit()
        self.display_text.setText(self._trigger.display_text)
        text_settings_layout = QGridLayout()
        text_settings_layout.addWidget(self.use_text, 0, 0)
        text_settings_layout.addWidget(label1, 0, 1)
        text_settings_layout.addWidget(self.display_text, 0, 2)
        box.setLayout(text_settings_layout)
        layout.addWidget(box)

        box2 = QGroupBox("Audio Settings")
        radio1 = QRadioButton("No Sound")
        self.use_text_to_voice = QRadioButton("Use Text To Speech")
        self.use_text_to_voice.setChecked(self._trigger.use_text_to_voice)
        text_to_say_label = QLabel("Text to Say")
        self.text_to_voice_text = QLineEdit()
        self.text_to_voice_text.setText(self._trigger.text_to_voice_text)
        self.interrupt_speech = QCheckBox("Interrupt Speed")
        self.interrupt_speech.setChecked(self._trigger.interrupt_speech)

        self.play_sound_file = QRadioButton("Play Sound File")
        self.play_sound_file.setChecked(self._trigger.play_sound_file)
        self.sound_file_path = QLineEdit()
        self.sound_file_path.setText(self._trigger.sound_file_path)
        self.sound_file_finder = QPushButton("...")
        self.sound_file_finder.clicked.connect(self.onClickSoundFileFinder)

        audio_settings_layout = QGridLayout()
        audio_settings_layout.addWidget(radio1, 0, 0)
        audio_settings_layout.addWidget(self.use_text_to_voice, 1, 0)
        audio_settings_layout.addWidget(text_to_say_label, 2, 1)
        audio_settings_layout.addWidget(self.text_to_voice_text, 2, 2)
        audio_settings_layout.addWidget(self.interrupt_speech, 3, 2)
        audio_settings_layout.addWidget(self.play_sound_file, 4, 0)
        audio_settings_layout.addWidget(QLabel("Sound File"), 5, 1)
        audio_settings_layout.addWidget(self.sound_file_path, 5, 2)
        audio_settings_layout.addWidget(self.sound_file_finder, 5, 3)
        box2.setLayout(audio_settings_layout)
        layout.addWidget(box2)

        self.basic_tab.setLayout(layout)

        return self.basic_tab

    def buildTimerTab(self):
        self.timer_tab = QWidget()
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.timer_type_input = QComboBox()
        self.timer_type_input.addItem("No Timer")
        self.timer_type_input.addItem("Timer (Count Down)")
        self.timer_type_input.addItem("Stopwatch (Count Up)")
        self.timer_type_input.addItem("Repeating Timer")
        self.timer_type_input.setCurrentText(self._trigger.timer_type)
        layout.addWidget(QLabel("Timer Type"), 1, 0)
        layout.addWidget(self.timer_type_input, 1, 1)

        self.timer_name_input = QLineEdit(self)
        self.timer_name_input.setText(self._trigger.timer_name)
        layout.addWidget(QLabel("Timer Name"), 2, 0)
        layout.addWidget(self.timer_name_input, 2, 1)

        seconds = self._trigger.duration % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        duration_layout = QHBoxLayout()
        duration_layout.setAlignment(Qt.AlignLeft)
        self.duration_h_input = QLineEdit(self)
        self.duration_h_input.setText(str(hours))
        self.duration_h_input.setFixedWidth(25)
        self.duration_h_label = QLabel("h")
        self.duration_h_label.setFixedWidth(15)

        self.duration_m_input = QLineEdit(self)
        self.duration_m_input.setText(str(minutes))
        self.duration_m_input.setFixedWidth(25)
        self.duration_m_label = QLabel("m")
        self.duration_m_label.setFixedWidth(15)

        self.duration_s_input = QLineEdit(self)
        self.duration_s_input.setText(str(seconds))
        self.duration_s_input.setFixedWidth(25)
        self.duration_s_label = QLabel("s")
        self.duration_s_label.setFixedWidth(15)

        self.duration_ms_input = QLineEdit(self)
        self.duration_ms_input.setText("0")
        self.duration_ms_input.setFixedWidth(25)
        self.duration_ms_label = QLabel("ms")
        self.duration_ms_label.setFixedWidth(15)

        layout.addWidget(QLabel("Duration"), 3, 0)
        duration_layout.addWidget(self.duration_h_input)
        duration_layout.addWidget(self.duration_h_label)
        duration_layout.addWidget(self.duration_m_input)
        duration_layout.addWidget(self.duration_m_label)
        duration_layout.addWidget(self.duration_s_input)
        duration_layout.addWidget(self.duration_s_label)
        duration_layout.addWidget(self.duration_ms_input)
        duration_layout.addWidget(self.duration_ms_label)
        layout.addLayout(duration_layout, 3, 1)


        layout.addWidget(QLabel("If timer is already running when triggered again:"), 4, 0)
        self.timer_start_behavior = QComboBox()
        self.timer_start_behavior.addItem("Start a new timer")
        self.timer_start_behavior.addItem("Restart current timer")
        self.timer_start_behavior.addItem("Do Nothing")
        self.timer_start_behavior.setCurrentText(self._trigger.timer_start_behavior)
        self.timer_start_behavior.currentTextChanged.connect(self.onTimerBehaviorChange)
        layout.addWidget(self.timer_start_behavior, 4, 1)

        self.restart_timer_matches = QRadioButton("Restart instance if Timer Name matches")
        self.restart_timer_matches.setChecked(self._trigger.restart_timer_matches)
        self.restart_timer_regardless = QRadioButton("Restart instance regardless of Timer Name")
        self.restart_timer_regardless.setChecked(self._trigger.restart_timer_regardless)
        layout.addWidget(self.restart_timer_matches, 5, 1)
        layout.addWidget(self.restart_timer_regardless, 6, 1)

        layout.addWidget(QLabel("End early text (For multiple possible values, add a row for each):"), 7, 0, 1, 2)

        self.end_early_triggers = TriggerEndEarlyTable(0, 2)
        self.end_early_triggers.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.end_early_triggers.verticalHeader().setVisible(False)
        self.end_early_triggers.setSelectionBehavior(QAbstractItemView.SelectRows);
        header = self.end_early_triggers.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.end_early_triggers.setHorizontalHeaderLabels(["Search Text", "Use Regex"]);

        if len(self._trigger.timer_end_early_triggers) > 0:
            idx = 0
            for trigger in self._trigger.timer_end_early_triggers:
                self.end_early_triggers.insertRow(self.end_early_triggers.rowCount())
                item = QTableWidgetItem();
                item.setFlags(item.flags() | Qt.ItemIsEditable);
                item.setData(Qt.DisplayRole, trigger["text"]);
                self.end_early_triggers.setItem(idx, 0, item);
                item2 = QTableWidgetItem();
                item2.setCheckState(Qt.Checked if trigger["use_regex"] else Qt.Unchecked);
                self.end_early_triggers.setItem(idx, 1, item2);
                idx += 1
        else:
            self.end_early_triggers.insertRow(self.end_early_triggers.rowCount())
            item = QTableWidgetItem();
            item.setFlags(item.flags() | Qt.ItemIsEditable);
            item.setData(Qt.DisplayRole, "");
            self.end_early_triggers.setItem(0, 0, item);
            item2 = QTableWidgetItem();
            item2.setCheckState(Qt.Unchecked);
            self.end_early_triggers.setItem(0, 1, item2);
        self.end_early_triggers.resizeRowsToContents()
        layout.addWidget(self.end_early_triggers, 8, 0, 1, 2)

        self.onTimerBehaviorChange(self.timer_start_behavior.currentText())

        self.timer_tab.setLayout(layout)

        return self.timer_tab

    def onTimerBehaviorChange(self, value):
        if value == "Restart current timer":
            self.restart_timer_matches.setVisible(True)
            self.restart_timer_regardless.setVisible(True)
        else:
            self.restart_timer_matches.setVisible(False)
            self.restart_timer_regardless.setVisible(False)

    def buildTimerEndingTab(self):
        self.timer_ending_tab = QWidget()
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.notify_ending = QCheckBox("Notify when timer is down to")
        self.notify_ending.setChecked(self._trigger.notify_ending)
        layout.addWidget(self.notify_ending, 0, 0)

        seconds = self._trigger.timer_ending_duration % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        duration_layout = QHBoxLayout()
        duration_layout.setAlignment(Qt.AlignLeft)
        self.timer_ending_duration_h_input = QLineEdit(self)
        self.timer_ending_duration_h_input.setText(str(hours))
        self.timer_ending_duration_h_input.setFixedWidth(25)
        self.timer_ending_duration_h_label = QLabel("h")
        self.timer_ending_duration_h_label.setFixedWidth(15)

        self.timer_ending_duration_m_input = QLineEdit(self)
        self.timer_ending_duration_m_input.setText(str(minutes))
        self.timer_ending_duration_m_input.setFixedWidth(25)
        self.timer_ending_duration_m_label = QLabel("m")
        self.timer_ending_duration_m_label.setFixedWidth(15)

        self.timer_ending_duration_s_input = QLineEdit(self)
        self.timer_ending_duration_s_input.setText(str(seconds))
        self.timer_ending_duration_s_input.setFixedWidth(25)
        self.timer_ending_duration_s_label = QLabel("s")
        self.timer_ending_duration_s_label.setFixedWidth(15)

        duration_layout.addWidget(self.timer_ending_duration_h_input)
        duration_layout.addWidget(self.timer_ending_duration_h_label)
        duration_layout.addWidget(self.timer_ending_duration_m_input)
        duration_layout.addWidget(self.timer_ending_duration_m_label)
        duration_layout.addWidget(self.timer_ending_duration_s_input)
        duration_layout.addWidget(self.timer_ending_duration_s_label)
        layout.addLayout(duration_layout, 0, 1)

        box = QGroupBox("Text Settings")
        self.timer_ending_use_text = QCheckBox()
        self.timer_ending_use_text.setChecked(self._trigger.timer_ending_use_text)
        label1 = QLabel("Display Text")
        self.timer_ending_display_text = QLineEdit()
        self.timer_ending_display_text.setText(self._trigger.timer_ending_display_text)
        text_settings_layout = QGridLayout()
        text_settings_layout.addWidget(self.timer_ending_use_text, 0, 0)
        text_settings_layout.addWidget(label1, 0, 1)
        text_settings_layout.addWidget(self.timer_ending_display_text, 0, 2)
        box.setLayout(text_settings_layout)
        layout.addWidget(box, 1, 0, 1, 2)

        box2 = QGroupBox("Audio Settings")
        radio1 = QRadioButton("No Sound")
        self.timer_ending_use_text_to_voice = QRadioButton("Use Text To Speech")
        self.timer_ending_use_text_to_voice.setChecked(self._trigger.timer_ending_use_text_to_voice)
        text_to_say_label = QLabel("Text to Say")
        self.timer_ending_text_to_voice_text = QLineEdit()
        self.timer_ending_text_to_voice_text.setText(self._trigger.timer_ending_text_to_voice_text)
        self.timer_ending_interrupt_speech = QCheckBox("Interrupt Speed")
        self.timer_ending_interrupt_speech.setChecked(self._trigger.timer_ending_interrupt_speech)

        self.timer_ending_play_sound_file = QRadioButton("Play Sound File")
        self.timer_ending_play_sound_file.setChecked(self._trigger.timer_ending_play_sound_file)
        self.timer_ending_sound_file_path = QLineEdit()
        self.timer_ending_sound_file_path.setText(self._trigger.timer_ending_sound_file_path)
        self.timer_ending_sound_file_finder = QPushButton("...")
        self.timer_ending_sound_file_finder.clicked.connect(self.onClickTimerEndingSoundFileFinder)

        audio_settings_layout = QGridLayout()
        audio_settings_layout.addWidget(radio1, 0, 0)
        audio_settings_layout.addWidget(self.timer_ending_use_text_to_voice, 1, 0)
        audio_settings_layout.addWidget(text_to_say_label, 2, 1)
        audio_settings_layout.addWidget(self.timer_ending_text_to_voice_text, 2, 2)
        audio_settings_layout.addWidget(self.timer_ending_interrupt_speech, 3, 2)
        audio_settings_layout.addWidget(self.timer_ending_play_sound_file, 4, 0)
        audio_settings_layout.addWidget(QLabel("Sound File"), 5, 1)
        audio_settings_layout.addWidget(self.timer_ending_sound_file_path, 5, 2)
        audio_settings_layout.addWidget(self.timer_ending_sound_file_finder, 5, 3)
        box2.setLayout(audio_settings_layout)
        layout.addWidget(box2, 2, 0, 1, 2)

        self.timer_ending_tab.setLayout(layout)

        return self.timer_ending_tab

    def buildTimerEndedTab(self):
        self.timer_ended_tab = QWidget()
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.notify_ended = QCheckBox("Notify when timer ends")
        self.notify_ended.setChecked(self._trigger.notify_ended)
        layout.addWidget(self.notify_ended, 0, 0)

        box = QGroupBox("Text Settings")
        self.timer_ended_use_text = QCheckBox()
        self.timer_ended_use_text.setChecked(self._trigger.timer_ended_use_text)
        label1 = QLabel("Display Text")
        self.timer_ended_display_text = QLineEdit()
        self.timer_ended_display_text.setText(self._trigger.timer_ended_display_text)
        text_settings_layout = QGridLayout()
        text_settings_layout.addWidget(self.timer_ended_use_text, 0, 0)
        text_settings_layout.addWidget(label1, 0, 1)
        text_settings_layout.addWidget(self.timer_ended_display_text, 0, 2)
        box.setLayout(text_settings_layout)
        layout.addWidget(box, 1, 0)

        box2 = QGroupBox("Audio Settings")
        radio1 = QRadioButton("No Sound")
        self.timer_ended_use_text_to_voice = QRadioButton("Use Text To Speech")
        self.timer_ended_use_text_to_voice.setChecked(self._trigger.timer_ended_use_text_to_voice)
        text_to_say_label = QLabel("Text to Say")
        self.timer_ended_text_to_voice_text = QLineEdit()
        self.timer_ended_text_to_voice_text.setText(self._trigger.timer_ended_text_to_voice_text)
        self.timer_ended_interrupt_speech = QCheckBox("Interrupt Speed")
        self.timer_ended_interrupt_speech.setChecked(self._trigger.timer_ended_interrupt_speech)

        self.timer_ended_play_sound_file = QRadioButton("Play Sound File")
        self.timer_ended_play_sound_file.setChecked(self._trigger.timer_ended_play_sound_file)
        self.timer_ended_sound_file_path = QLineEdit()
        self.timer_ended_sound_file_path.setText(self._trigger.timer_ended_sound_file_path)
        self.timer_ended_sound_file_finder = QPushButton("...")
        self.timer_ended_sound_file_finder.clicked.connect(self.onClickTimerEndedSoundFileFinder)

        audio_settings_layout = QGridLayout()
        audio_settings_layout.addWidget(radio1, 0, 0)
        audio_settings_layout.addWidget(self.timer_ended_use_text_to_voice, 1, 0)
        audio_settings_layout.addWidget(text_to_say_label, 2, 1)
        audio_settings_layout.addWidget(self.timer_ended_text_to_voice_text, 2, 2)
        audio_settings_layout.addWidget(self.timer_ended_interrupt_speech, 3, 2)
        audio_settings_layout.addWidget(self.timer_ended_play_sound_file, 4, 0)
        audio_settings_layout.addWidget(QLabel("Sound File"), 5, 1)
        audio_settings_layout.addWidget(self.timer_ended_sound_file_path, 5, 2)
        audio_settings_layout.addWidget(self.timer_ended_sound_file_finder, 5, 3)
        box2.setLayout(audio_settings_layout)
        layout.addWidget(box2, 2, 0)

        self.timer_ended_tab.setLayout(layout)

        return self.timer_ended_tab

    def buildCounterTab(self):
        self.counter_tab = QWidget()

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        seconds = self._trigger.counter_duration % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60


        self.reset_counter = QCheckBox("Reset counter if unmatched for")
        self.reset_counter.setChecked(self._trigger.reset_counter_if_unmatched)
        layout.addWidget(self.reset_counter, 0, 0)

        self.counter_duration_h_input = QLineEdit(self)
        self.counter_duration_h_input.setText(str(hours))
        self.counter_duration_h_input.setFixedWidth(25)
        self.counter_duration_h_label = QLabel("h")
        self.counter_duration_h_label.setFixedWidth(15)

        self.counter_duration_m_input = QLineEdit(self)
        self.counter_duration_m_input.setText(str(minutes))
        self.counter_duration_m_input.setFixedWidth(25)
        self.counter_duration_m_label = QLabel("m")
        self.counter_duration_m_label.setFixedWidth(15)

        self.counter_duration_s_input = QLineEdit(self)
        self.counter_duration_s_input.setText(str(seconds))
        self.counter_duration_s_input.setFixedWidth(25)
        self.counter_duration_s_label = QLabel("s")
        self.counter_duration_s_label.setFixedWidth(15)

        layout.addWidget(self.counter_duration_h_input, 0, 1)
        layout.addWidget(self.counter_duration_h_label, 0, 2)
        layout.addWidget(self.counter_duration_m_input, 0, 3)
        layout.addWidget(self.counter_duration_m_label, 0, 4)
        layout.addWidget(self.counter_duration_s_input, 0, 5)
        layout.addWidget(self.counter_duration_s_label, 0, 6)

        self.counter_tab.setLayout(layout)

        return self.counter_tab


    def saveTrigger(self):
        self._trigger.setName(self.trigger_input.text())
        self._trigger.setSearchText(self.search_text_input.text())
        self._trigger.setTimerName(self.timer_name_input.text())
        self._trigger.setUseRegex(self.use_regex_cb.isChecked())
        self._trigger.setUseText(self.use_text.isChecked())
        self._trigger.setCategory(self.category_select.currentText())
        self._trigger.setTimerType(self.timer_type_input.currentText())
        self._trigger.setDisplayText(self.display_text.text())
        self._trigger.setUseTextToVoice(self.use_text_to_voice.isChecked())
        self._trigger.setTextToVoiceText(self.text_to_voice_text.text())
        self._trigger.setTimerStartBehavior(self.timer_start_behavior.currentText())
        self._trigger.setInterruptSpeech(self.interrupt_speech.isChecked())
        self._trigger.setPlaySoundFile(self.play_sound_file.isChecked())
        self._trigger.setSoundFilePath(self.sound_file_path.text())

        if self.timer_start_behavior.currentText() == "Restart current timer":
            self._trigger.restart_timer_matches = self.restart_timer_matches.isChecked()
            self._trigger.restart_timer_regardless = self.restart_timer_regardless.isChecked()
        else:
            self._trigger.restart_timer_matches = False
            self._trigger.restart_timer_regardless = False

        duration = int(self.duration_h_input.text() or 0) * 60 * 60
        duration += int(self.duration_m_input.text() or 0) * 60
        duration += int(self.duration_s_input.text() or 0)
        self._trigger.setDuration(duration)

        timer_ending_duration = int(self.timer_ending_duration_h_input.text() or 0) * 60 * 60
        timer_ending_duration += int(self.timer_ending_duration_m_input.text() or 0) * 60
        timer_ending_duration += int(self.timer_ending_duration_s_input.text() or 0)
        self._trigger.timer_ending_duration = timer_ending_duration
        self._trigger.notify_ending = self.notify_ending.isChecked()
        self._trigger.timer_ending_use_text = self.timer_ending_use_text.isChecked()
        self._trigger.timer_ending_display_text = self.timer_ending_display_text.text()
        self._trigger.timer_ending_use_text_to_voice = self.timer_ending_use_text_to_voice.isChecked()
        self._trigger.timer_ending_text_to_voice_text = self.timer_ending_text_to_voice_text.text()
        self._trigger.timer_ending_interrupt_speech = self.timer_ending_interrupt_speech.isChecked()
        self._trigger.timer_ending_play_sound_file = self.timer_ending_play_sound_file.isChecked()
        self._trigger.timer_ending_sound_file_path = self.timer_ending_sound_file_path.text()

        self._trigger.notify_ended = self.notify_ended.isChecked()
        self._trigger.timer_ended_use_text = self.timer_ended_use_text.isChecked()
        self._trigger.timer_ended_display_text = self.timer_ended_display_text.text()
        self._trigger.timer_ended_use_text_to_voice = self.timer_ended_use_text_to_voice.isChecked()
        self._trigger.timer_ended_text_to_voice_text = self.timer_ended_text_to_voice_text.text()
        self._trigger.timer_ended_interrupt_speech = self.timer_ended_interrupt_speech.isChecked()
        self._trigger.timer_ended_play_sound_file = self.timer_ended_play_sound_file.isChecked()
        self._trigger.timer_ended_sound_file_path = self.timer_ended_sound_file_path.text()

        counter_duration = int(self.counter_duration_h_input.text() or 0) * 60 * 60
        counter_duration += int(self.counter_duration_m_input.text() or 0) * 60
        counter_duration += int(self.counter_duration_s_input.text() or 0)
        self._trigger.reset_counter_if_unmatched = self.reset_counter.isChecked()
        self._trigger.counter_duration = counter_duration


        self._trigger.timer_end_early_triggers = []
        for row in range(self.end_early_triggers.rowCount()):
            text = self.end_early_triggers.item(row, 0).text()
            use_regex = self.end_early_triggers.item(row, 1).checkState() == Qt.Checked
            item = {
              "text": text,
              "use_regex": use_regex
            }
            self._trigger.timer_end_early_triggers.append(item)


        if self._is_new:
            if self._trigger_group:
                self._trigger_group.addChild(self._trigger)
            else:
                self._parent.trigger_list.addTopLevelItem(self._trigger)
            QApplication.instance()._signals["logreader"].new_line.connect(self._trigger.onLogUpdate)

        self._trigger.compileExpressions()

        self.destroy()

    def cancelTrigger(self):
        self.destroy()

    def destroy(self):
        self.trigger_input.setText("")
        self.search_text_input.setText("")
        self.timer_name_input.setText("")
        self.use_regex_cb.setChecked(False)
        self.close()
        self.deleteLater()

    def onClickSoundFileFinder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]
            self.sound_file_path.setText(filename)

    def onClickTimerEndingSoundFileFinder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]
            self.timer_ending_sound_file_path.setText(filename)

    def onClickTimerEndedSoundFileFinder(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]
            self.timer_ended_sound_file_path.setText(filename)
