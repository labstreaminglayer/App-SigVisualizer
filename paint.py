import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import random
from math import sin
import time

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PySigVisualizer'
        self.left = 10
        self.top = 20
        self.width = 1800
        self.height = 800
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        # Add paint widget and paint
        self.m = PaintWidget(self)
        self.m.move(0,0)
        self.m.resize(self.width,self.height)

        self.show()


class PaintWidget(QWidget):
    x = 0
    y = 0
    lastX = x
    lastY = y
    yOffset = 500
    xLimit = 5
    # xlist = list(range(500)*40)
    # ylist = [None] * 2000
    # for i in range(2000):
    #     ylist[i] = sin(xlist[i]) * 20

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(Qt.black)
        size = self.size()

        self.x = 0
        self.y = 0
        self.lastX = self.x
        self.lastY = self.y

        while self.x < self.xLimit:
            qp.drawLine(self.lastX, self.lastY + self.yOffset, self.x, self.y + self.yOffset)
            self.lastX = self.x
            self.lastY = self.y
            self.x = (self.x + 3)
            self.y = sin(self.x) * 50

        self.xLimit += 1
        if self.xLimit >= size.width():
            self.xLimit %= size.width()
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
