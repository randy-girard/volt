import time
import os
import signal
import select
import sys

from volt.utils.log_watcher import LogWatcher
from threading import Thread
from threading import Event

from PySide6.QtCore import QFileSystemWatcher, Signal

class LogMonitor(QFileSystemWatcher):
    new_line = Signal(object)

    def __init__(self, profiles_manager):
        super().__init__()

        self._profiles_manager = profiles_manager
        self._files = self._profiles_manager.files
        self._watcher = QFileSystemWatcher(self._files)
        self._watcher.fileChanged.connect(self._file_changed_safe_wrap)

        self._stats = {
            'log_file': '',
        }

    def addLogFile(self, log_file):
        if log_file not in self._files:
            self._files.append(log_file)
            self._watcher.addPath(log_file)

    def removeLogFile(self, log_file):
        if log_file in self._files:
            self._files.remove(log_file)
            self._watcher.removePath(log_file)

    def stop(self):
        if self._watcher:
            try:
                self._watcher.fileChanged.disconnect(self._file_changed_safe_wrap)
            except:
                pass
            self._watcher.deleteLater()
            self._watcher = None

    def _file_changed_safe_wrap(self, changed_file):
        try:
            self._file_changed(changed_file)
        except FileNotFoundError:
            print("File not found: %s; did it move?")

    def _file_changed(self, changed_file):
        if changed_file != self._stats['log_file']:
            self._stats['log_file'] = changed_file
            self._profiles_manager.setActiveByFile(changed_file)
