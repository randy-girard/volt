from PySide6.QtWidgets import QWidget, QPushButton, QTreeWidget
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QStandardItemModel

from volt.windows import trigger_window
from volt.windows import trigger_group_window

from volt.models.trigger_group import TriggerGroup
from volt.models.trigger import Trigger

class TriggersManager(QWidget):
    def __init__(self, parent):
        super(TriggersManager, self).__init__()

        self._parent = parent

        self.button2 = QPushButton("Add Trigger Group")
        self.button2a = QPushButton("Edit Trigger Group")
        self.button2b = QPushButton("Remove Trigger Group")

        self.button2.clicked.connect(self.addTriggerGroupWindow)
        self.button2a.clicked.connect(self.editTriggerOrTriggerGroup)
        self.button2b.clicked.connect(self.removeTriggerGroup)

        self.button2a.setEnabled(False)
        self.button2b.setEnabled(False)

        self._parent.home_layout.addWidget(self.button2, 1, 1)
        self._parent.home_layout.addWidget(self.button2a, 2, 1)
        self._parent.home_layout.addWidget(self.button2b, 3, 1)

        self.button3 = QPushButton("Add Trigger")
        self.button3a = QPushButton("Edit Trigger")
        self.button3b = QPushButton("Remove Trigger")

        self.button3.clicked.connect(self.addTrigger)
        self.button3a.clicked.connect(self.editTriggerOrTriggerGroup)
        self.button3b.clicked.connect(self.removeTrigger)

        self.button3.setEnabled(False)
        self.button3a.setEnabled(False)
        self.button3b.setEnabled(False)

        self._parent.home_layout.addWidget(self.button3, 1, 2)
        self._parent.home_layout.addWidget(self.button3a, 2, 2)
        self._parent.home_layout.addWidget(self.button3b, 3, 2)

        self.trigger_list = QTreeWidget()
        self.trigger_list.setHeaderHidden(True)
        self.trigger_list.itemChanged.connect(self.triggerListItemChanged)
        self.trigger_list.itemClicked.connect(self.triggerListItemClicked)
        self.trigger_list.doubleClicked.connect(self.addTriggerOrTriggerGroupWindow)


    def load(self, json):
        for item in json:
            root = self.deserializeChildren(item)
            self.trigger_list.addTopLevelItem(root)


    def deserializeChildren(self, item, parent=None):
        node = None
        if item["type"] == "Trigger":
                node = Trigger(parent=self._parent,
                               name=item["name"],
                               timer_name=item["timer_name"],
                               search_text=item["search_text"],
                               use_regex=bool(item["use_regex"]),
                               duration=int(item["duration"]),
                               category=item.get("category", ""),
                               timer_type=item.get("timer_type", "Timer (Count Down)"),
                               use_text=bool(item.get("use_text", False)),
                               display_text=item.get("display_text", ""),
                               use_text_to_voice=bool(item.get("use_text_to_voice", False)),
                               text_to_voice_text=item.get("text_to_voice_text", ""),
                               timer_start_behavior=item.get("timer_start_behavior", "Start a new timer"),
                               interrupt_speech=bool(item.get("interrupt_speech", False)),
                               play_sound_file=bool(item.get("play_sound_file", False)),
                               sound_file_path=item.get("sound_file_path"),
                               restart_timer_matches=bool(item.get("restart_timer_matches", False)),
                               restart_timer_regardless=bool(item.get("restart_timer_regardless", False)),
                               notify_ending=bool(item.get("notify_ending", False)),
                               timer_ending_duration=int(item.get("timer_ending_duration", 0)),
                               timer_ending_use_text=bool(item.get("timer_ending_use_text", False)),
                               timer_ending_display_text=item.get("timer_ending_display_text"),
                               timer_ending_use_text_to_voice=bool(item.get("timer_ending_use_text_to_voice", False)),
                               timer_ending_text_to_voice_text=item.get("timer_ending_text_to_voice_text"),
                               timer_ending_interrupt_speech=bool(item.get("timer_ending_interrupt_speech", False)),
                               timer_ending_play_sound_file=bool(item.get("timer_ending_play_sound_file", False)),
                               timer_ending_sound_file_path=item.get("timer_ending_sound_file_path"),
                               notify_ended=bool(item.get("notify_ended", False)),
                               timer_ended_use_text=bool(item.get("timer_ended_use_text", False)),
                               timer_ended_display_text=item.get("timer_ended_display_text"),
                               timer_ended_use_text_to_voice=bool(item.get("timer_ended_use_text_to_voice", False)),
                               timer_ended_text_to_voice_text=item.get("timer_ended_text_to_voice_text"),
                               timer_ended_interrupt_speech=bool(item.get("timer_ended_interrupt_speech", False)),
                               timer_ended_play_sound_file=bool(item.get("timer_ended_play_sound_file", False)),
                               timer_ended_sound_file_path=item.get("timer_ended_sound_file_path"),
                               timer_end_early_triggers=item.get("timer_end_early_triggers", []))
                self._parent._parent.log_signal.connect(node.onLogUpdate)
        elif item["type"] == "TriggerGroup":
            node = TriggerGroup(name=item["name"],
                                comments=item["comments"],
                                group_id=item.get("group_id", None),
                                checked=item.get("checked", 0))
        for child in item["children"]:
            node.addChild(self.deserializeChildren(child, node))
        return node


    def serialize(self):
        trigger_groups = []
        for i in range(self.trigger_list.topLevelItemCount()):
            item = self.trigger_list.topLevelItem(i)
            group = self.serializeTriggerGroup(item)
            trigger_groups.append(group)
        return trigger_groups


    def serializeTriggerGroup(self, parent):
        hash = parent.serialize()
        hash["children"] = []

        if parent.childCount() > 0:
            for i in range(parent.childCount()):
                item = parent.child(i)
                hash["children"].append(self.serializeTriggerGroup(item))

        return hash


    def triggerListItemClicked(self, item):
        if type(item) is Trigger:
            self.button2.setEnabled(True)
            self.button2a.setEnabled(False)
            self.button2b.setEnabled(False)
            self.button3.setEnabled(False)
            self.button3a.setEnabled(True)
            self.button3b.setEnabled(True)
        elif type(item) is TriggerGroup:
            self.button2.setEnabled(True)
            self.button2a.setEnabled(True)
            self.button2b.setEnabled(True)
            self.button3.setEnabled(True)
            self.button3a.setEnabled(False)
            self.button3b.setEnabled(False)


    def triggerListItemChanged(self, widgetItem, column):
        self.trigger_list.blockSignals(True)
        is_checked = widgetItem.checkState(column)
        self.triggerListItemChangedOnChildren(widgetItem, column, is_checked)
        self.triggerListItemChangedOnParents(widgetItem, column, is_checked)
        self.trigger_list.blockSignals(False)

        group_ids = []
        self.current_profile = self._parent.profiles_manager.profile_list.currentItem()
        trigger_groups = self.trigger_list.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive);
        for trigger_group in trigger_groups:
            if type(trigger_group) is TriggerGroup and trigger_group.checkState(0) == Qt.Checked:
                group_ids.append(trigger_group.group_id)
        self.current_profile.trigger_group_ids = group_ids

    def triggerListItemChangedOnChildren(self, widgetItem, column, is_checked):
        for i in range(widgetItem.childCount()):
            child = widgetItem.child(i)

            if type(child) is TriggerGroup:
                child.setCheckState(column, is_checked)

            self.triggerListItemChangedOnChildren(child, column, is_checked)

    def triggerListItemChangedOnParents(self, widgetItem, column, is_checked):
        parent = widgetItem.parent()
        if parent:
            checked_count = 0
            partial_count = 0
            group_count = 0
            trigger_count = 0
            child_count = parent.childCount()
            for i in range(child_count):
                child = parent.child(i)
                if type(child) is TriggerGroup:
                    group_count += 1
                    state = child.checkState(column)
                    if state == Qt.CheckState.Checked:
                        checked_count += 1
                    elif state == Qt.CheckState.PartiallyChecked:
                        partial_count += 1
                if type(child) is Trigger:
                    trigger_count += 1

            if checked_count + partial_count == 0 and trigger_count == 0:
                parent.setCheckState(column, Qt.CheckState.Unchecked)
            elif checked_count == group_count:
                parent.setCheckState(column, Qt.CheckState.Checked)
            elif checked_count + partial_count == group_count:
                parent.setCheckState(column, Qt.CheckState.PartiallyChecked)
            else:
                parent.setCheckState(column, Qt.CheckState.PartiallyChecked)
            self.triggerListItemChangedOnParents(parent, column, is_checked)

    def addTrigger(self):
        trigger_group = None
        item = self.trigger_list.currentItem()

        if type(item) is TriggerGroup:
            trigger_group = item

        self.editTriggerOrTriggerGroupWindow(Trigger(parent=self._parent), trigger_group, True)

    def editTriggerOrTriggerGroup(self):
        item = self.trigger_list.currentItem()
        self.editTriggerOrTriggerGroupWindow(item, None)

    def removeTrigger(self):
        self.removeTriggerOrTriggerGroup()

    def removeTriggerGroup(self):
        self.removeTriggerOrTriggerGroup()

    def removeTriggerOrTriggerGroup(self):
        item = self.trigger_list.currentItem()
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            self.trigger_list.takeTopLevelItem(self.trigger_list.indexOfTopLevelItem(item))

    def addTriggerGroupWindow(self):
        parent_group = None
        item = self.trigger_list.currentItem()
        if item and type(item) is TriggerGroup:
            parent_group = item

        self.editTriggerOrTriggerGroupWindow(TriggerGroup(), trigger_group=parent_group)

    def addTriggerOrTriggerGroupWindow(self, item=None):
        current_item = None
        if item:
            current_item = self.trigger_list.currentItem()
        self.editTriggerOrTriggerGroupWindow(current_item)

    def editTriggerOrTriggerGroupWindow(self, item, trigger_group=None, is_new=False):
        if type(item) is Trigger:
            self.trigger_window = trigger_window.TriggerWindow(self, item, trigger_group, is_new)
            self.trigger_window.show()
        else:
            self.trigger_group_window = trigger_group_window.TriggerGroupWindow(self, item, trigger_group)
            self.trigger_group_window.show()
