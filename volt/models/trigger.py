import re

from playsound import playsound
from datetime import datetime

from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Signal, Slot, Qt

from volt.utils.regex_engine import RegexEngine

class Trigger(QTreeWidgetItem):
    def __init__(self, name="", timer_name="", search_text="", duration=0, use_regex=False,
                       category="", timer_type="", use_text=False, display_text="", use_text_to_voice=False,
                       text_to_voice_text="", timer_start_behavior="", interrupt_speech=False,
                       play_sound_file=False, sound_file_path="", restart_timer_matches=False,
                       restart_timer_regardless=False,
                       notify_ending=False, timer_ending_duration=0, timer_ending_use_text=False,
                       timer_ending_display_text="", timer_ending_use_text_to_voice=False,
                       timer_ending_text_to_voice_text="", timer_ending_interrupt_speech=False,
                       timer_ending_play_sound_file=False, timer_ending_sound_file_path="",
                       notify_ended=False, timer_ended_use_text=False,
                       timer_ended_display_text="", timer_ended_use_text_to_voice=False,
                       timer_ended_text_to_voice_text="", timer_ended_interrupt_speech=False,
                       timer_ended_play_sound_file=False, timer_ended_sound_file_path="",
                       timer_end_early_triggers=[],
                       variables=[],
                       counter_duration=0,
                       reset_counter_if_unmatched=False,
                       parent=None,
                       checked=Qt.CheckState.Unchecked,
                       trigger_id=None):

        checked = self.fromCheckState(checked)

        super().__init__()
        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(0, checked)

        self.enabled = False
        self.counter = 0
        self.last_matched_at = None
        self.search_text = search_text
        self.use_regex = use_regex
        self.owner = parent
        self.trigger_id = trigger_id
        if self.trigger_id == None:
            self.trigger_id = id(self)
        self.last_timer = None
        self.timers = []
        self.variable_values = {}

        # TODO: Fix this deep accessing
        self.speaker = self.owner._parent.speaker
        self.category_list = self.owner._parent.categories_manager.category_list
        self.timer_overlays = self.owner._parent.overlays_manager.timer_overlays
        self.text_overlays = self.owner._parent.overlays_manager.text_overlays
        self.profiles_manager = self.owner._parent.profiles_manager
        self.trigger_log_manager = self.owner._parent.trigger_log_manager

        self.regex_engine = RegexEngine(self.profiles_manager.current_profile)
        self.regex_engine_enders = []

        self.setName(name)
        self.setTimerName(timer_name)
        self.setDuration(duration)
        self.setCategory(category)
        self.setTimerType(timer_type)
        self.setUseText(use_text)
        self.setDisplayText(display_text)
        self.setUseTextToVoice(use_text_to_voice)
        self.setTextToVoiceText(text_to_voice_text)
        self.setTimerStartBehavior(timer_start_behavior)
        self.setInterruptSpeech(interrupt_speech)
        self.setPlaySoundFile(play_sound_file)
        self.setSoundFilePath(sound_file_path)

        self.restart_timer_matches = restart_timer_matches
        self.restart_timer_regardless = restart_timer_regardless

        self.notify_ending = notify_ending
        self.timer_ending_duration = timer_ending_duration
        self.timer_ending_use_text = timer_ending_use_text
        self.timer_ending_display_text = timer_ending_display_text
        self.timer_ending_use_text_to_voice = timer_ending_use_text_to_voice
        self.timer_ending_text_to_voice_text = timer_ending_text_to_voice_text
        self.timer_ending_interrupt_speech = timer_ending_interrupt_speech
        self.timer_ending_play_sound_file = timer_ending_play_sound_file
        self.timer_ending_sound_file_path = timer_ending_sound_file_path

        self.notify_ended = notify_ended
        self.timer_ended_use_text = timer_ended_use_text
        self.timer_ended_display_text = timer_ended_display_text
        self.timer_ended_use_text_to_voice = timer_ended_use_text_to_voice
        self.timer_ended_text_to_voice_text = timer_ended_text_to_voice_text
        self.timer_ended_interrupt_speech = timer_ended_interrupt_speech
        self.timer_ended_play_sound_file = timer_ended_play_sound_file
        self.timer_ended_sound_file_path = timer_ended_sound_file_path

        self.timer_end_early_triggers = timer_end_early_triggers

        self.variables = variables

        self.counter_duration = counter_duration
        self.reset_counter_if_unmatched = reset_counter_if_unmatched

        self.compileExpressions()

    def manageEvents(self, is_checked):
        if is_checked:
            if not self.enabled:
                self.enabled = True
                QApplication.instance()._signals["logreader"].new_line.connect(self.onLogUpdate)
        else:
            self.enabled = False
            QApplication.instance()._signals["logreader"].new_line.disconnect(self.onLogUpdate)


    def isChecked(self):
        return self.checkState(0) == Qt.CheckState.Checked

    def fromCheckState(self, checkState):
        if checkState == 0:
            return Qt.CheckState.Unchecked
        elif checkState == 1:
            return Qt.CheckState.PartiallyChecked
        elif checkState == 2:
            return Qt.CheckState.Checked
        else:
            return checkState

    def checkStateToInt(self, checkState):
        if checkState == Qt.CheckState.Unchecked:
            return 0
        if checkState == Qt.CheckState.PartiallyChecked:
            return 1
        if checkState == Qt.CheckState.Checked:
            return 2


    def setName(self, val):
        self.name = val
        self.setText(0, val)

    def setTimerName(self, val):
        self.timer_name = val

    def setSearchText(self, val):
        self.search_text = val

    def setDuration(self, val):
        self.duration = float(val)

    def setUseRegex(self, val):
        self.use_regex = val

    def setCategory(self, val):
        self.category = val

    def setTimerType(self, val):
        self.timer_type = val

    def setUseText(self, val):
        self.use_text = val

    def setDisplayText(self, val):
        self.display_text = val

    def setUseTextToVoice(self, val):
        self.use_text_to_voice = val

    def setTextToVoiceText(self, val):
        self.text_to_voice_text = val

    def setTimerStartBehavior(self, val):
        self.timer_start_behavior = val

    def setInterruptSpeech(self, val):
        self.interrupt_speech = val

    def setPlaySoundFile(self, val):
        self.play_sound_file = val

    def setSoundFilePath(self, val):
        self.sound_file_path = val

    def serialize(self):
        hash = {
            "type": "Trigger",
            "trigger_id": self.trigger_id,
            "name": self.name,
            "timer_name": self.timer_name,
            "search_text": self.search_text,
            "duration": self.duration,
            "use_regex": self.use_regex,
            "category": self.category,
            "timer_type": self.timer_type,
            "use_text": self.use_text,
            "display_text": self.display_text,
            "use_text_to_voice": self.use_text_to_voice,
            "text_to_voice_text": self.text_to_voice_text,
            "timer_start_behavior": self.timer_start_behavior,
            "interrupt_speech": self.interrupt_speech,
            "play_sound_file": self.play_sound_file,
            "sound_file_path": self.sound_file_path,
            "restart_timer_matches": self.restart_timer_matches,
            "restart_timer_regardless": self.restart_timer_regardless,
            "notify_ending": self.notify_ending,
            "timer_ending_duration": self.timer_ending_duration,
            "timer_ending_use_text": self.timer_ending_use_text,
            "timer_ending_display_text": self.timer_ending_display_text,
            "timer_ending_use_text_to_voice": self.timer_ending_use_text_to_voice,
            "timer_ending_text_to_voice_text": self.timer_ending_text_to_voice_text,
            "timer_ending_interrupt_speech": self.timer_ending_interrupt_speech,
            "timer_ending_play_sound_file": self.timer_ending_play_sound_file,
            "timer_ending_sound_file_path": self.timer_ending_sound_file_path,
            "notify_ended": self.notify_ended,
            "timer_ended_use_text": self.timer_ended_use_text,
            "timer_ended_display_text": self.timer_ended_display_text,
            "timer_ended_use_text_to_voice": self.timer_ended_use_text_to_voice,
            "timer_ended_text_to_voice_text": self.timer_ended_text_to_voice_text,
            "timer_ended_interrupt_speech": self.timer_ended_interrupt_speech,
            "timer_ended_play_sound_file": self.timer_ended_play_sound_file,
            "timer_ended_sound_file_path": self.timer_ended_sound_file_path,
            "timer_end_early_triggers": self.timer_end_early_triggers,
            "variables": self.variables,
            "counter_duration": self.counter_duration,
            "reset_counter_if_unmatched": self.reset_counter_if_unmatched,
            "checked": self.checkStateToInt(self.checkState(0))
        }
        return hash

    def compileExpressions(self):
        self.regex_engine_enders = []
        self.regex_variables = []
        search_text = self.search_text

        if not self.use_regex:
            search_text = search_text.replace("*", "\w+")
        try:
            self.regex_engine.compile(search_text)
        except Exception as e:
            print(e)
            print(self.search_text)

        for trigger in self.timer_end_early_triggers:
            regex_engine = RegexEngine(self)
            text = trigger["text"]
            if len(text) > 0:
                if not trigger["use_regex"]:
                    text = text.replace("*", "\w+")
                regex_engine.compile(text)
                self.regex_engine_enders.append(regex_engine)

        for variable in self.variables:
            regex_engine = RegexEngine(self)
            text = variable["search"]
            if len(text) > 0:
                text = text.replace("*", "\w+")
                regex_engine.compile(text)
                item = {
                  "regex_engine": regex_engine,
                  "variable": variable
                }
                self.regex_variables.append(item)

    def onLogUpdate(self, text):
        # Strip out the timestamp
        stripped_str = re.sub("^\[.*?\] ", "", text)


        # Remove whitespace
        stripped_str = stripped_str.strip()

        for item in self.regex_variables:
            engine = item["regex_engine"]
            var = item["variable"]

            var_matches = engine.match(stripped_str)
            if var_matches:
                result = engine.execute(var["value"], matches=var_matches)
                if result:
                    self.variable_values[var["name"]] = result

        if len(self.timers) > 0:
            for ender in self.regex_engine_enders:
                m = ender.match(stripped_str)
                if m:
                    for timer in self.timers.copy():
                        timer.destroy()

        if self.owner and self.regex_engine.expression and self.isChecked():
            m = self.regex_engine.match(stripped_str)

            now = datetime.utcnow().strftime('%s')

            if self.last_matched_at and int(now) > int(self.last_matched_at) + int(self.counter_duration):
                self.counter = 0

            if m:
                self.last_matched_at = now

                name = self.timer_name
                name = self.regex_engine.execute(name, matches=m)

                # Replace counter
                self.counter += 1

                if name:
                    name = name.replace("{COUNTER}", str(self.counter))
                    name = name.replace("{counter}", str(self.counter))

                for key, value in self.variable_values.items():
                    name = name.replace(f"{{var:{key}}}", str(value))

                if self.interrupt_speech:
                    self.speaker.stop()

                if self.use_text_to_voice:
                    text_to_say = self.text_to_voice_text
                    if self.profiles_manager.current_profile:
                        text_to_say = self.regex_engine.execute(text_to_say, matches=m)
                    self.speaker.say(text_to_say)

                if self.play_sound_file and len(self.sound_file_path) > 0:
                    path = self.sound_file_path
                    playsound(path, False)

                categories = self.category_list.findItems(self.category, Qt.MatchExactly)
                for category in categories:
                    if name and len(name) > 0:
                        for overlay in self.timer_overlays:
                            if overlay.data_model.name == category.timer_overlay:
                                add_timer = True

                                if len(self.timers) > 0:
                                    if self.timer_start_behavior == "Restart current timer":
                                        for timer in self.timers:
                                            timer.label = name

                                            if self.restart_timer_matches:
                                                if timer.label == name:
                                                    timer.restartTimer()
                                                    add_timer = False
                                            else:
                                                timer.restartTimer()
                                                add_timer = False
                                    elif self.timer_start_behavior == "Do Nothing":
                                        add_timer = False

                                if add_timer:
                                    duration = self.duration
                                    if self.regex_engine.duration != None:
                                        duration = self.regex_engine.duration

                                    timer = overlay.addTimer(name, duration, trigger=self, category=category, matches=m)
                                    self.trigger_log_manager.addItem(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"), name, stripped_str)
                                    QApplication.instance()._signals['timers'].append(timer)
                                    self.timers.append(timer)

                    for overlay in self.text_overlays:
                        if overlay.data_model.name == category.text_overlay:
                            if self.use_text:
                                overlay.addTextTrigger(self.regex_engine.execute(self.display_text, matches=m), category=category, matches=m)
                                self.trigger_log_manager.addItem(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"), name, stripped_str)

    def removeTimer(self, timer):
        QApplication.instance()._signals['timers'].remove(timer)
        self.timers.remove(timer)

    def getTimers(self):
        return self.timers
