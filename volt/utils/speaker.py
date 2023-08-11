import platform
import subprocess

class Speaker():
    def __init__(self):
        self.proc = None
        
        if platform.system() == "Darwin":
            pass
        else:
            pass

    def say(self, text):
        if platform.system() == "Darwin":
            self.proc = subprocess.Popen("say \"" + text + "\"", shell=True)
        else:
            self.proc = subprocess.Popen(f"mshta vbscript:Execute(\"CreateObject(\"\"SAPI.SpVoice\"\").Speak(\"\"{text}\"\")(window.close)\")")

    def stop(self):
        if self.proc:
            self.proc.terminate()
