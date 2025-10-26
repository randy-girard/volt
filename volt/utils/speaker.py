import platform
import pyttsx3

from threading import Thread

if platform.system() == "Darwin":
    import subprocess
elif platform.system() == "Windows":
    from threading import Thread
    from pyttsx3.drivers import toUtf8, fromUtf8

    def _say_stopable(engine, text):
        engine.say(text)
        engine.runAndWait()


class Threader(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.start()

    def run(self):
        if platform.system() == "Windows":
            self._args[0].proxy.setBusy(True)
            self._args[0].proxy.notify('started-utterance')
            self._args[0]._speaking = True
            self._args[0].proxy._driver._tts.Speak(fromUtf8(toUtf8(self._args[1])), 3)
        elif platform.system() == "Darwin":
            pass


class Speaker():
    def __init__(self):
        self.proc = None
        self.engine = None

        self.driver_name = 'sapi5'
        if platform.system() == "Darwin":
            self.driver_name = 'nsss'

        if platform.system() == "Windows":
            self.engine = pyttsx3.init(driverName=self.driver_name)
        elif platform.system() == "Darwin":
            self.engine = True

    def say(self, text):
        if self.engine and text:
            self.stop()

            if platform.system() == "Darwin":
                self.proc = subprocess.Popen("say \"" + text + "\"", shell=True)
            elif platform.system() == "Windows":
                self.proc = Threader(args=(self.engine, text))


    def stop(self):
        if platform.system() == "Darwin":
            if self.proc:
                self.proc.terminate()
                self.proc.wait()
                self.proc = None
        elif platform.system() == "Windows":
            if self.engine:
                self.engine.proxy._driver._tts.Skip('Sentence', 2147483647)
                self.engine._inLoop = False
