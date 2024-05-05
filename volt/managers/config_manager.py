import json
import sys
import os
import xml.etree.ElementTree as ET

from PySide6.QtWidgets import QApplication, QWidget, QFileDialog

from volt.models.trigger_group import TriggerGroup
from volt.models.trigger import Trigger
from volt.models.category import Category
from volt.models.profile import Profile

class ConfigManager(QWidget):
    def __init__(self, parent):
        super(ConfigManager, self).__init__()

        self._parent = parent

    def save(self):
        config = {
            "top": self._parent.geometry().y(),
            "left": self._parent.geometry().x(),
            "width": self._parent.geometry().width(),
            "height": self._parent.geometry().height(),
            "profiles": self._parent.profiles_manager.serialize(),
            "overlays": self._parent.overlays_manager.serialize(),
            "trigger_groups": self._parent.triggers_manager.serialize(),
            "categories": self._parent.categories_manager.serialize()
        }

        json_out = json.dumps(config, indent=4)
        with open(self._parent.application_path + "/config.json", "w") as outfile:
            outfile.write(json_out)


    def load(self):
        if not os.path.isfile(self._parent.application_path + "/config.json"):
            json_out = json.dumps({}, indent=4)
            with open(self._parent.application_path + "/config.json", "w") as outfile:
                outfile.write(json_out)


        with open(self._parent.application_path + "/config.json", 'r') as openfile:
            json_object = json.load(openfile)

            self.setGeometry(json_object.get("left", 10),
                             json_object.get("top", 10),
                             json_object.get("width", 800),
                             json_object.get("height", 600))

            self._parent.home_manager.load(json_object)
            self._parent.overlays_manager.load(json_object)
            self._parent.categories_manager.load(json_object)


    def importSpellsUsConfig(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]

            root = TriggerGroup(group_id="9999999",
                                name="Spells",
                                comments="Import from spells_us.txt")
            self._parent.triggers_manager.trigger_list.addTopLevelItem(root)

            with open(filename) as spell_file:
                for line in spell_file:
                    values = line.strip().split('^')
                    name = values[1]
                    effect_text_you = values[6]
                    effect_text_other = values[7]
                    effect_text_worn_off = values[8]
                    duration = int(values[17])

                    node = Trigger(parent=self,
                                   name=f"{name} - YOU",
                                   timer_name=f"{name} (YOU)",
                                   duration=duration,
                                   search_text=effect_text_you,
                                   use_regex=False,
                                   category="Default",
                                   timer_type="RestartTimer",
                                   use_text=True,
                                   display_text=f"{name} (YOU)",
                                   use_text_to_voice=False,
                                   text_to_voice_text="",
                                   interrupt_speech=False,
                                   play_sound_file=False,
                                   sound_file_path="",
                                   restart_timer_matches=False,
                                   restart_timer_regardless=False,
                                   timer_end_early_triggers=[
                                       {
                                           "text": effect_text_worn_off,
                                           "use_regex": True
                                       }
                                   ])
                    QApplication.instance()._signals["logreader"].new_line.connect(node.onLogUpdate)
                    root.addChild(node)



    def importGinaConfig(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            filename = filenames[0]

            tree = ET.parse(filename)
            root = tree.getroot()

            self._parent.overlays_manager.clearOverlayWindows()
            for item in root.findall("./BehaviorGroups/Behavior"):
                window = item.find("./WindowLayout/WINDOWPLACEMENT/normalPosition")
                sort_method = item.find("SortMethod").text
                if sort_method == "OrderTriggered":
                    sort_method = "Order Triggered"
                elif sort_method == "TimeRemaining":
                    sort_method = "Time Remaining"
                else:
                    sort_method = "Order Triggered"

                config = {
                    "name": item.find("Name").text,
                    "type": item.find("BehaviorType").text,
                    "top": int(window.find("Top").text),
                    "left": int(window.find("Left").text),
                    "width": int(window.find("Right").text) - int(window.find("Left").text),
                    "height": int(window.find("Bottom").text) - int(window.find("Top").text),
                    "font": item.find("FontName").text,
                    "font_size": int(item.find("FontSize").text),
                    "sort_method": sort_method
                }
                self._parent.overlays_manager.createOverlay(config)

            self._parent.profiles_manager.profile_list.clear()
            for item in root.findall('./Characters/Character'):
                trigger_group_ids = [int(child.get("GroupId")) for child in item.findall("./TriggerGroups/TriggerGroup")]
                profile = Profile(name=item.find("DisplayName").text,
                                  log_file=item.find("LogFilePath").text,
                                  trigger_group_ids=trigger_group_ids)
                self._parent.profiles_manager.profile_list.addItem(profile)

            self._parent.triggers_manager.trigger_list.clear()
            for item in root.findall('./TriggerGroups/TriggerGroup'):
                root_item = self.importGinaConfigNested(item)
                self._parent.triggers_manager.trigger_list.addTopLevelItem(root_item)

            self._parent.categories_manager.category_list.clear()
            for item in root.findall('./Categories/Category'):
                category = Category(name=item.find("Name").text,
                                    timer_overlay=item.find("TimerOverlay").text,
                                    text_overlay=item.find("TextOverlay").text,
                                    timer_font_color=item.find("TimerStyle/FontColor").text,
                                    timer_bar_color=item.find("TimerStyle/TimerBarColor").text,
                                    text_font_color=item.find("TextStyle/FontColor").text)
                self._parent.categories_manager.category_list.addItem(category)


    def importGinaConfigNested(self, item):
        node = None
        if item.tag == "TriggerGroup":
            node = TriggerGroup(group_id=int(item.find("GroupId").text),
                                name=item.find("Name").text,
                                comments=item.find("Comments").text)
        elif item.tag == "Trigger":
           timer_type = item.find("TimerType").text
           if timer_type == "NoTimer":
               timer_type = "No Timer"
           elif timer_type == "Timer":
               timer_type = "Timer (Count Down)"
           elif timer_type == "Stopwatch":
               timer_type = "Stopwatch (Count Up)"
           elif timer_type == "RepeatTimer":
               timer_type = "Repeating Timer"

           timer_start_behavior = item.find("TimerStartBehavior").text
           if timer_start_behavior == "StartTimer":
               timer_start_behavior = "Start a new timer"
           elif timer_start_behavior == "RestartTimer":
               timer_start_behavior = "Restart current timer"
           elif timer_start_behavior == "IgnoreIfRunning":
               timer_start_behavior = "Do Nothing"

           media_file = item.find("MediaFileName")
           if media_file:
               media_file = media_file.text
           else:
               media_file = ""

           node = Trigger(parent=self,
                          name=item.find("Name").text,
                          timer_name=item.find("TimerName").text,
                          duration=int(item.find("TimerDuration").text),
                          search_text=item.find("TriggerText").text,
                          use_regex=bool(item.find("EnableRegex").text == "True"),
                          category=item.find("Category").text,
                          timer_type=timer_type,
                          use_text=bool(item.find("UseText").text == "True"),
                          display_text=item.find("DisplayText").text,
                          use_text_to_voice=bool(item.find("UseTextToVoice").text == "True"),
                          text_to_voice_text=item.find("TextToVoiceText").text,
                          timer_start_behavior=timer_start_behavior,
                          interrupt_speech=bool(item.find("InterruptSpeech").text == "True"),
                          play_sound_file=bool(item.find("PlayMediaFile").text == "True"),
                          sound_file_path=media_file,
                          restart_timer_matches=bool(item.find("RestartBasedOnTimerName").text == "True"),
                          restart_timer_regardless=bool(item.find("RestartBasedOnTimerName").text == "False"))

           node.notify_ending = bool(item.find("UseTimerEnding").text == "True")
           node.timer_ending_duration = int(item.find("TimerEndingTime").text)
           ending_early = item.find("TimerEndingTrigger")
           if ending_early:
               ending_media_file = item.find("MediaFileName")
               if ending_media_file:
                   ending_media_file = ending_media_file.text
               else:
                   ending_media_file = ""
               node.timer_ending_use_text = bool(ending_early.find("UseText").text == "True")
               node.timer_ending_display_text = ending_early.find("DisplayText").text
               node.timer_ending_use_text_to_voice = bool(ending_early.find("UseTextToVoice").text == "True")
               node.timer_ending_text_to_voice_text = ending_early.find("TextToVoiceText").text
               node.timer_ending_interrupt_speech = bool(ending_early.find("InterruptSpeech").text == "True")
               node.timer_ending_play_sound_file = bool(ending_early.find("PlayMediaFile").text == "True")
               node.timer_ending_sound_file_path = ending_media_file

           node.notify_ended = bool(item.find("UseTimerEnded").text == "True")
           ended_early = item.find("TimerEndedTrigger")
           if ended_early:
               ended_media_file = item.find("MediaFileName")
               if ended_media_file:
                   ended_media_file = ended_media_file.text
               else:
                   ended_media_file = ""
               node.timer_ended_use_text = bool(ended_early.find("UseText").text == "True")
               node.timer_ended_display_text = ended_early.find("DisplayText").text
               node.timer_ended_use_text_to_voice = bool(ended_early.find("UseTextToVoice").text == "True")
               node.timer_ended_text_to_voice_text = ended_early.find("TextToVoiceText").text
               node.timer_ended_interrupt_speech = bool(ended_early.find("InterruptSpeech").text == "True")
               node.timer_ended_play_sound_file = bool(ended_early.find("PlayMediaFile").text == "True")
               node.timer_ended_sound_file_path = ended_media_file

           end_early_triggers = []
           timer_early_enders = item.findall("./TimerEarlyEnders/EarlyEnder")
           for early_ender in timer_early_enders:
               record = {
                   "text": early_ender.find("EarlyEndText").text,
                   "use_regex": bool(early_ender.find("EnableRegex").text == "True")
               }
               end_early_triggers.append(record)
           node.timer_end_early_triggers = end_early_triggers

           QApplication.instance()._signals["logreader"].new_line.connect(node.onLogUpdate)
        for child in item.findall("./TriggerGroups/TriggerGroup"):
            node.addChild(self.importGinaConfigNested(child))
        for child in item.findall("./Triggers/Trigger"):
            node.addChild(self.importGinaConfigNested(child))
        return node
