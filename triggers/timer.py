import time

from PySide6.QtWidgets import QApplication, QProgressBar, QSizePolicy, QWidget
from PySide6.QtCore import Signal, Slot, QObject, Qt, QTimer, QPropertyAnimation

class Timer(QWidget):
    signal = Signal()

    def __init__(self, parent, label, duration, trigger=None, category=None):
        super().__init__()

        self.trigger = trigger
        self.category = category
        self.active = True
        self.label = label
        self.parent = parent
        self.duration = duration

        self.pbar = QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(1000)
        self.restartTimer()
        #self.pbar.valueChanged.connect(self.onUpdate)
        self.pbar.show()
        self.pbar.setStyleSheet(
            "QProgressBar"
            "{"
                f"color: {self.category.timer_font_color};"
                "background-color: transparent;"
                "border: 0;"
            "}"

            "QProgressBar::chunk"
            "{"
                f"color: {self.category.timer_bar_color};"
                f"background: {self.category.timer_bar_color};"
            "}"
        )
        self.adjustSize()

        #self.timer = QPropertyAnimation(self.pbar, b"value", self)
        #self.timer.setDuration(self.duration * 1000)
        #self.timer.setStartValue(1000)
        #self.timer.setEndValue(0)
        #self.timer.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.onUpdate)
        self.timer.start(50)

        self.parent.layout.addWidget(self.pbar)

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

    #def onUpdate(self, value):
    def onUpdate(self):
        done = False
        current_time = time.time() * 1000
        ratio = (current_time - self.starttime) / (self.endtime - self.starttime)
        if self.trigger and self.trigger.timer_type == "Stopwatch (Count Up)":
            done = ratio > 1
        else:
            ratio = 1 - ratio
            done = ratio < 0

        delta = (ratio * (self.endtime - self.starttime))

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

    def destroy(self):
        self.timer.stop()
        self.parent.triggers.remove(self)
        self.pbar.setVisible(False)
        self.pbar.setTextVisible(False)
        self.parent.layout.removeWidget(self.pbar)
        self.parent.layout.removeWidget(self)
        self.trigger.removeTimer(self)

    def notifyEnding(self):
        if self.trigger.notify_ending:
            for overlay in self.trigger.text_overlays:
                if overlay.data_model.name == self.category.text_overlay:
                    if self.trigger.timer_ending_use_text:
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
                        overlay.addTextTrigger(self.trigger.timer_ended_display_text)

            if self.trigger.timer_ended_interrupt_speech:
                self.trigger.speaker.stop()

            if self.trigger.timer_ended_use_text_to_voice:
                text_to_say = self.trigger.timer_ended_text_to_voice_text
                if self.trigger.profiles_manager.current_profile:
                    text_to_say = self.trigger.regex_engine.execute(text_to_say)
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
