from PySide6.QtWidgets import QListWidgetItem

class Category(QListWidgetItem):
    def __init__(self, parent=None, name="", timer_overlay=None, text_overlay=None,
                       timer_font_color="#ffff00", timer_bar_color="#ff0000",
                       text_font_color="#ffff00"):
        super().__init__(name, parent)
        self._parent = parent

        self.name = name
        self.setText(name)

        self.timer_overlay = timer_overlay
        self.text_overlay = text_overlay
        self.timer_font_color = timer_font_color
        self.timer_bar_color = timer_bar_color
        self.text_font_color = text_font_color

    def setName(self, val):
        self.name = val
        self.setText(val)

    def setTimerOverlay(self, overlay):
        self.timer_overlay = overlay

    def setTextOverlay(self, overlay):
        self.text_overlay = overlay

    def serialize(self):
        hash = {
            "name": self.name,
            "timer_overlay": self.timer_overlay,
            "text_overlay": self.text_overlay,
            "timer_font_color": self.timer_font_color,
            "timer_bar_color": self.timer_bar_color,
            "text_font_color": self.text_font_color
        }
        return hash
