import time
import os
import signal
import select
import sys

from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtWidgets import QApplication

from volt.utils.log_watcher import LogWatcher
from threading import Thread
from threading import Event

class LogReader():
    def __init__(self):
        self.running = Event()
        self.thread = None
        self.watcher = None
        self.watching = True

    def start(self):
        self.running.set()
        self.thread = Thread(target=self.run, args=(self.running,))
        self.thread.start()

    def stop(self):
        self.running.clear()
        if self.watcher:
            self.watcher.close()
        if self.thread:
            self.thread.join()

    def setLogFile(self, log_file):
        self.log_file = log_file

    def run(self, running):
        if os.path.isfile(self.log_file):
            self.watcher = self.init_tail_file(self.log_file)
            while running.is_set():
                self.watcher.loop(blocking=False)
                time.sleep(0.1)

    def callback(self, filename, lines):
        for line in lines:
            if(len(line.strip()) > 0):
                QApplication.instance()._signals["logreader"].new_line.emit(line)

    def init_tail_file(self, filename):
        return LogWatcher(".",
                          self.callback,
                          ["log"],
                          filename,
                          persistent_checkpoint=False,
                          file_signature_bytes=32,
                          strict_extension_check=True)
