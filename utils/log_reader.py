import time
import os
import signal
import select
import sys

from utils.log_watcher import LogWatcher

from pubsub import pub
from threading import Thread
from threading import Event

class LogReader():
    def __init__(self):
        self.running = Event()
        self.thread = None

    def start(self):
        self.running.set()

        self.thread = Thread(target=self.run, args=(self.running,))
        self.thread.start()


    def stop(self):
        self.running.clear()
        if self.thread:
            self.thread.join()

    def setLogFile(self, log_file):
        self.log_file = log_file

    def run(self, running):
        if os.path.isfile(self.log_file):
            watcher = LogWatcher(".", self.callback, ["log"],
                         self.log_file,
                         persistent_checkpoint=False,
                         mask_rotated_file_name=False,
                         deterministic_rotation=False,
                         file_signature_bytes=32,
                         strict_extension_check=True)
            while running.is_set():
                watcher.loop(blocking=False)
                time.sleep(0.1)
        #tail = Tail(self.log_file)
        #tail.register_callback(self.emit)
        #tail.follow(s=0.1, run=running)


    #def emit(self, text):
    #    pub.sendMessage('log', text=text.strip("\n"))

    def callback(self, filename, lines):
        for line in lines:
            pub.sendMessage('log', text=line.strip("\n"))
