from PySide6.QtWidgets import QApplication, QScrollArea
from PySide6.QtCore import Qt

class FramelessWindowManager(QScrollArea):
    def __init__(self):
        super().__init__()

        self.can_manage = True
        self.border_size = 20
        self.dragging = False
        self.moving = False
        self.drag_direction = None
        self.setMouseTracking(True)

    def setCanManage(self, mode):
        self.can_manage = mode
        if not mode:
            self.drag_direction = None

    def setBorderSize(self, size):
        self.border_size = size

    def mousePressEvent(self, event):
        self.drag_direction = None
        x, y = event.pos().x(), event.pos().y()
        w, h = self.width(), self.height()

        if self.can_manage:
            if x < self.border_size and y < self.border_size:
                self.dragging = True
                self.drag_direction = "left/up"
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            elif x < self.border_size and y > h - self.border_size:
                self.dragging = True
                self.drag_direction = "left/down"
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            elif x > w - self.border_size and y < self.border_size:
                self.dragging = True
                self.drag_direction = "right/up"
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            elif x > w - self.border_size and y > h - self.border_size:
                self.dragging = True
                self.drag_direction = "right/down"
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            elif x < self.border_size and (self.border_size < y < h - self.border_size):
                self.dragging = True
                self.drag_direction = "left"
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            elif y < self.border_size and (self.border_size < x < w - self.border_size):
                self.dragging = True
                self.drag_direction = "up"
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            elif x > w - self.border_size and (self.border_size < y < h - self.border_size):
                self.dragging = True
                self.drag_direction = "right"
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            elif y > h - self.border_size and (self.border_size < x < w - self.border_size):
                self.dragging = True
                self.drag_direction = "down"
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            else:
                self.oldPos = self.window().mapFromGlobal(event.globalPos())
                self.moving = True


    def mouseMoveEvent(self, event):
        if self.can_manage:
            x, y = event.pos().x(), event.pos().y()
            w, h = self.width(), self.height()

            if x < self.border_size and y < self.border_size:
                self.drag_direction = "left/up"
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            elif x < self.border_size and y > h - self.border_size:
                self.drag_direction = "left/down"
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            elif x > w - self.border_size and y < self.border_size:
                self.drag_direction = "right/up"
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            elif x > w - self.border_size and y > h - self.border_size:
                self.drag_direction = "right/down"
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            elif x < self.border_size and (self.border_size < y < h - self.border_size):
                self.drag_direction = "left"
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            elif y < self.border_size and (self.border_size < x < w - self.border_size):
                self.drag_direction = "up"
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            elif x > w - self.border_size and (self.border_size < y < h - self.border_size):
                self.drag_direction = "right"
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            elif y > h - self.border_size and (self.border_size < x < w - self.border_size):
                self.drag_direction = "down"
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            else:
                QApplication.restoreOverrideCursor()
                QApplication.setOverrideCursor(Qt.ArrowCursor)

            if self.moving:
                delta = self.window().mapFromGlobal(event.globalPos()) - self.oldPos
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.oldPos = self.window().mapFromGlobal(event.globalPos())
                self.update()


            if self.dragging:
                mouse_x, mouse_y = event.pos().x(), event.pos().y()
                pos_x, pos_y = self.pos().x(), self.pos().y()

                if self.drag_direction == "right/down":
                    self.resize(mouse_x, mouse_y)
                elif self.drag_direction == "left/up":
                    self.resize(self.width() - mouse_x, self.height() - mouse_y)
                    self.move(pos_x + mouse_x, pos_y + mouse_y)
                elif self.drag_direction == "right/up":
                    self.resize(mouse_x, self.height() - mouse_y)
                    self.move(pos_x, pos_y + mouse_y)
                elif self.drag_direction == "left/down":
                    self.resize(self.width() - mouse_x, mouse_y)
                    self.move(pos_x + mouse_x, pos_y)
                elif self.drag_direction == "up":
                    self.resize(self.width(), self.height() - mouse_y)
                    self.move(pos_x, pos_y + mouse_y)
                elif self.drag_direction == "right":
                    self.resize(mouse_x, self.height())
                elif self.drag_direction == "down":
                    self.resize(self.width(), mouse_y)
                elif self.drag_direction == "left":
                    self.resize(self.width() - mouse_x, self.height())
                    self.move(pos_x + mouse_x, pos_y)

    def mouseReleaseEvent(self, event):
        self.drag_direction = None
        self.dragging = False
        self.moving = False
        QApplication.restoreOverrideCursor()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        #Not ideal but restoreOverrideCursor() isnt super reliable
