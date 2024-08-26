import time
import re

from PySide6.QtWidgets import QApplication, QProgressBar, QSizePolicy, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot, QObject, Qt, QTimer, QPropertyAnimation
from PySide6.QtGui import QFont

class Timer(QWidget):
    RESOLUTION = 200

    signal = Signal()

    def __init__(self, parent, label, duration, trigger=None, category=None, matches=None):
        super().__init__()

        self.trigger = trigger
        self.category = category
        self.matches = matches
        self.active = True
        self.label = label
        self.parent = parent
        self.duration = duration
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 1);

        self.pbar = QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(1000)
        self.pbar.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.restartTimer()
        #self.pbar.valueChanged.connect(self.onUpdate)
        self.pbar.show()
        self.pbar.setStyleSheet(
            "QProgressBar"
            "{"
                f"color: {self.category.timer_font_color};"
                "background-color: rgba(0, 0, 0, 100);"
                "border: 0;"
            "}"

            "QProgressBar::chunk"
            "{"
                f"color: {self.category.timer_bar_color};"
                f"background: {self.category.timer_bar_color};"
            "}"
        )
        self.updateFont()
        self.adjustSize()


        #self.timer = QPropertyAnimation(self.pbar, b"value", self)
        #self.timer.setDuration(self.duration * 1000)
        #self.timer.setStartValue(1000)
        #self.timer.setEndValue(0)
        #self.timer.start()

        timer_update_ms = int(self.duration * 1000 / Timer.RESOLUTION)
        if timer_update_ms < 50:
            timer_update_ms = 50
        if timer_update_ms > 1000:
            timer_update_ms = 1000

        self.timer = QTimer()
        self.timer.timeout.connect(self.onUpdate)
        self.timer.start(timer_update_ms)
        self.layout.addWidget(self.pbar)

    def updateFont(self):
        font = QFont(self.parent.data_model.font, self.parent.data_model.font_size)
        self.pbar.setFont(font)

    def restartTimer(self):
        self.ending_notified = False
        self.starttime = time.time() * 1000
        self.endtime = self.starttime + (self.duration * 1000)
        ts = self.strfdelta((self.endtime - self.starttime), '%M:%S')
        self.pbar.setFormat(f"{ts} - {self.label}")
        self.pbar.setValue(1000)
        if self.trigger and self.trigger.timer_type == "Stopwatch (Count Up)":
            self.pbar.setValue(0)

    def onUpdateEmit(self):
        self.signal.emit()

    def onDoubleClick(self):
        self.destroy()

    def sortValue(self):
        if self.parent.data_model.sort_method == "Time Remaining":
            return self.endtime - (time.time() * 1000)
        elif self.parent.data_model.sort_method.startswith("Timer Text"):
            return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', self.label)]
        else:
            return self.starttime


    def onUpdate(self):
        done = False
        current_time = time.time() * 1000
        ratio = 1

        if self.duration > 0:
            ratio = (current_time - self.starttime) / (self.endtime - self.starttime)

        if self.trigger and self.trigger.timer_type == "Stopwatch (Count Up)":
            if self.duration > 0:
                done = ratio > 1
                delta = (ratio * (self.endtime - self.starttime))
            else:
                done = False
                delta = (current_time - self.starttime)
                ratio = 1
        else:
            ratio = 1 - ratio
            delta = (ratio * (self.endtime - self.starttime))
            done = ratio <= 0


        ts = self.strfdelta(delta, '%M:%S')
        self.pbar.setValue(int(ratio * 1000))
        self.pbar.setFormat(f"{ts} - {self.label}")
        self.pbar.update()

        if (self.ending_notified == False and delta <= self.trigger.timer_ending_duration * 1000):
            self.notifyEnding()
            self.ending_notified = True

        if(done):
            self.active = False
            self.notifyEnded()
            if self.trigger and self.trigger.timer_type == "Repeating Timer":
                self.parent.addTimer(self.label, self.duration, self.trigger)
            self.destroy()

    def removeFromLayout(self):
        self.pbar.setVisible(False)
        self.pbar.setTextVisible(False)
        self.parent.trigger_layout.removeWidget(self)

    def addToLayout(self):
        self.pbar.setVisible(True)
        self.pbar.setTextVisible(True)
        self.parent.trigger_layout.addWidget(self)

    def destroy(self):
        self.timer.stop()
        self.parent.triggers.remove(self)
        self.removeFromLayout()
        self.trigger.removeTimer(self)
        self.deleteLater()

    def notifyEnding(self):
        if self.trigger.notify_ending:
            for overlay in self.trigger.text_overlays:
                if overlay.data_model.name == self.category.text_overlay:
                    if self.trigger.timer_ending_use_text:
                        display_text = self.trigger.regex_engine.execute(self.trigger.timer_ending_display_text, self.matches)
                        overlay.addTextTrigger(self.trigger.timer_ending_display_text)

            if self.trigger.timer_ending_interrupt_speech:
                self.trigger.speaker.stop()

            if self.trigger.timer_ending_use_text_to_voice:
                text_to_say = self.trigger.timer_ending_text_to_voice_text
                if self.trigger.profiles_manager.current_profile:
                    text_to_say = self.trigger.regex_engine.execute(text_to_say)
                self.trigger.speaker.say(text_to_say)

            if self.trigger.timer_ending_play_sound_file:
                path = self.trigger.timer_ending_sound_file_path
                if len(path) > 0:
                    playsound(path, False)

    def notifyEnded(self):
        if self.trigger.notify_ended:
            for overlay in self.trigger.text_overlays:
                if overlay.data_model.name == self.category.text_overlay:
                    if self.trigger.timer_ended_use_text:
                        display_text = self.trigger.regex_engine.execute(self.trigger.timer_ended_display_text, self.matches)
                        overlay.addTextTrigger(display_text)

            if self.trigger.timer_ended_interrupt_speech:
                self.trigger.speaker.stop()

            if self.trigger.timer_ended_use_text_to_voice:
                text_to_say = self.trigger.timer_ended_text_to_voice_text
                if self.trigger.profiles_manager.current_profile:
                    text_to_say = self.trigger.regex_engine.execute(text_to_say, self.matches)
                self.trigger.speaker.say(text_to_say)

            if self.trigger.timer_ended_play_sound_file:
                path = self.trigger.timer_ended_sound_file_path
                if len(path) > 0:
                    playsound(path, False)


    def get_label(self, timestamp):
        return f"{timestamp} - {self.label}"


    def strfdelta(self, tdelta, fmt):
        seconds = tdelta / 1000

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%02d:%02d" % (minutes + (hour * 60), seconds)
