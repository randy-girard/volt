import time
import os
import signal
import select
import sys
import re

from datetime import datetime
from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtWidgets import QApplication

from volt.utils.log_watcher import LogWatcher
from threading import Thread
from threading import Event

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class LogReaderHandler(PatternMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        # Keep track of the last read position for each file
        self.file_position = None

        super(LogReaderHandler, self).__init__(*args, **kwargs)

    def process_new_lines(self, file_path):
        last_pos = self.file_position or os.path.getsize(file_path)
        with open(file_path, 'r') as f:
            f.seek(last_pos)
            for line in f:
                if(len(line.strip()) > 0):
                    timestamp, text = self.parse_line(line)
                    QApplication.instance()._signals["logreader"].new_line.emit(timestamp, text)
            self.file_position = f.tell()  # update last read position

    def on_created(self, event):
        print(event)

    def on_modified(self, event):
        if not event.is_directory:
            self.process_new_lines(event.src_path)

    def parse_line(self, line):
        """
        Parses and then returns an everquest log entry's date and text.
        """
        index = line.find("]") + 1
        sdate = line[1:index - 1].strip()
        text = line[index:].strip()
        return datetime.strptime(sdate, '%a %b %d %H:%M:%S %Y'), text

class LogReader():
    def __init__(self):
        self.running = Event()
        self.thread = None
        self.observer = None
        self.watcher = None
        self.watching = True

    def start(self):
        filename = os.path.basename(self.log_file)
        path = os.path.dirname(self.log_file)

        handler = LogReaderHandler(patterns = [filename])

        # Set up observer
        self.observer = Observer()
        self.observer.schedule(handler, path=path, recursive=False)
        self.observer.start()

        self.running.set()
        #self.thread = Thread(target=self.run, args=(self.running,))
        #self.thread.start()

    def stop(self):
        self.running.clear()
        if self.watcher:
            self.watcher.close()
        if self.thread:
            self.thread.join()
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        if hasattr(self, 'handler'):
            self.handler.file_positions.clear()
            self.handler = None

    def setLogFile(self, log_file):
        self.log_file = log_file

    def run(self, running):
        if os.path.isfile(self.log_file):
            self.watcher = self.init_tail_file(self.log_file)
            while running.is_set():
                self.watcher.loop(blocking=False)
                time.sleep(0.1)

    def parse_line(self, line):
        """
        Parses and then returns an everquest log entry's date and text.
        """
        index = line.find("]") + 1
        sdate = line[1:index - 1].strip()
        text = line[index:].strip()
        return datetime.strptime(sdate, '%a %b %d %H:%M:%S %Y'), text

    def callback(self, filename, lines):
        for line in lines:
            if(len(line.strip()) > 0):
                timestamp, text = self.parse_line(line)
                QApplication.instance()._signals["logreader"].new_line.emit(timestamp, text)

    def init_tail_file(self, filename):
        return LogWatcher(".",
                          self.callback,
                          ["log"],
                          filename,
                          persistent_checkpoint=False,
                          file_signature_bytes=32,
                          strict_extension_check=True)
