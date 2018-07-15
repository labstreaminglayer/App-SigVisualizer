import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import random
import math
from math import *
import time
import numpy as np
from pylsl import StreamInlet, resolve_stream

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PySigVisualizer'
        self.left = 10
        self.top = 20
        self.width = 1800
        self.height = 1000
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
    xMargin = 100
    idx = 0
    increment = 1

    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_stream('name', 'ActiChamp-0')
    # streams = resolve_stream('name', 'BioSemi')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    samplingRate = int(streams[0].nominal_srate())
    channelCount = int(streams[0].channel_count())
    timeStampsBuffer = np.zeros(shape=(channelCount,samplingRate))
    dataBuffer = np.zeros(shape=(channelCount,samplingRate))
    scaling = 10

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(Qt.blue)
        self.yOffset = self.size().height() / self.channelCount / 2
        channelHeight = self.size().height() / self.channelCount

        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        chunk, timestamps = self.inlet.pull_chunk(max_samples=100)
        if timestamps:
            for c in range(len(timestamps)):
                self.idx = (self.idx + self.increment) % self.dataBuffer.shape[1]
                for m in range(self.channelCount):
                    self.dataBuffer[m, self.idx] = chunk[c][m] * self.scaling

        for m in range(self.channelCount):
            qp.drawText(10, m * channelHeight + self.yOffset, 'Channel {}'.format(m+1))

            for k in range(self.dataBuffer.shape[1]-1):
                qp.drawLine(k * 4 + self.xMargin, self.dataBuffer[m, k] + m * channelHeight + self.yOffset / 2, 
                (k+1)*4 + self.xMargin, self.dataBuffer[m, k+1] + m * channelHeight + self.yOffset / 2)

        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
