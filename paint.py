import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import random
from math import sin

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt paint - pythonspot.com'
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


    # def __init__(self):
    x1 = 10
    x2 = 10
    y1 = 1
    y2 = 1
    xlist = list(range(1000))
    ylist = [None]*1000
    for i in range(1000):
        ylist[i] = sin(xlist[i])
    x = 0
    y = 0

    def paintEvent(self, event):
        qp = QPainter(self)

        qp.setPen(Qt.black)

    
    #   for i in range(1024):
    #   while True:
        self.x2 += 1
        # self.y2 += 2
#   x = random.randint(1, size.width()-1)
#   y = random.randint(1, size.height()-1)
#   qp.drawPoint(x, y)
        # qp.drawLine(self.x1, self.y1, self.x2, sin(self.x2) * 100)
        # self.x1 = self.x2
        # self.y1 = sin(self.x2) * 100
        for i in range(self.x):
            qp.drawLine(self.xlist[i] * 10, 200, self.xlist[i+1] * 10, self.ylist[i+1]*100 + 200)
        self.x += 1
        self.y += 1
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
