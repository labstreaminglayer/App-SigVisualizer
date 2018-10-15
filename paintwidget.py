from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QPainter, QPen
from PyQt5.QtWidgets import QWidget
from pylsl import StreamInlet, resolve_streams, cf_string
import math


class DataThread(QThread):
    updateStreamNames = pyqtSignal(list, int)
    sendSignalChunk = pyqtSignal(int, list)

    def __init__(self, parent):
        super().__init__(parent)
        self.chunksPerScreen = 50
        self.streams = []
        self.chunk_idx = 0
        self.seconds_per_screen = 2
        self.metadata = []
        self.srate = None
        self.chunkSize = None
        self.downSampling = None
        self.downSamplingFactor = None
        self.downSamplingBuffer = None
        self.inlet = None
        self.sig_strm_idx = None

    def update_streams(self):
        if not self.streams:
            self.streams = resolve_streams(wait_time=1.0)
            self.sig_strm_idx = -1
            for k, stream in enumerate(self.streams):
                self.metadata.append({
                    "name": stream.name(),
                    "ch_count": stream.channel_count(),
                    "ch_format": stream.channel_format(),
                    "srate": stream.nominal_srate()
                })
                if self.sig_strm_idx == -1 and stream.channel_format() not in ["String", cf_string]:
                    self.sig_strm_idx = k

            if self.sig_strm_idx != -1:
                sig_stream = self.streams[self.sig_strm_idx]
                self.srate = int(sig_stream.nominal_srate())
                self.downSampling = False if self.srate <= 1000 else True
                self.chunkSize = round(self.srate / self.chunksPerScreen * self.seconds_per_screen)

                if self.downSampling:
                    self.downSamplingFactor = round(self.srate / 1000)
                    self.downSamplingBuffer = [[0 for m in range(int(sig_stream.channel_count()))]
                                               for n in range(round(self.chunkSize/self.downSamplingFactor))]

                self.inlet = StreamInlet(sig_stream)
                self.updateStreamNames.emit(self.metadata, self.sig_strm_idx)
                self.start()

    def run(self):
        if self.streams:
            while True:
                chunk, timestamps = self.inlet.pull_chunk(max_samples=self.chunkSize, timeout=1)
                if timestamps:

                    if self.downSampling:
                        for k in range(int(self.streams[self.sig_strm_idx].channel_count())):
                            for m in range(round(self.chunkSize/self.downSamplingFactor)):
                                end_idx = min((m+1) * self.downSamplingFactor, len(chunk))
                                buf = [chunk[n][k] for n in range(m * self.downSamplingFactor, end_idx)]
                                self.downSamplingBuffer[m][k] = sum(buf) / len(buf)
                        self.sendSignalChunk.emit(self.chunk_idx, self.downSamplingBuffer)
                    else:
                        self.sendSignalChunk.emit(self.chunk_idx, chunk)

                    if self.chunk_idx < self.chunksPerScreen:
                        self.chunk_idx += 1
                    else:
                        self.chunk_idx = 0


class PaintWidget(QWidget):

    def __init__(self, widget):
        super().__init__()
        self.idx = 0
        self.channelHeight = 0
        self.interval = 0
        self.dataBuffer = []
        self.lastY = []
        self.scaling = []
        self.mean = []

        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.dataTr = DataThread(self)
        self.dataTr.sendSignalChunk.connect(self.get_data_chunk)

    def get_data_chunk(self, chunk_idx, buffer):
        if not self.mean:
            self.mean = [0 for k in range(len(buffer[0]))]
            self.scaling = [0 for k in range(len(buffer[0]))]
        self.dataBuffer = buffer

        self.idx = chunk_idx
        self.update(self.idx * (self.width() / self.dataTr.chunksPerScreen) - self.interval,
                    0,
                    self.width() / self.dataTr.chunksPerScreen,
                    self.height())

    def paintEvent(self, event):
        if self.dataBuffer:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.blue))

            self.channelHeight = self.height() / len(self.dataBuffer[0])
            self.interval = self.width() / self.dataTr.chunksPerScreen / len(self.dataBuffer)

            # ======================================================================================================
            # Calculate Trend and Scaling
            # ======================================================================================================
            if self.idx == 0 or not self.mean:
                for k in range(len(self.dataBuffer[0])):
                    column = [row[k] for row in self.dataBuffer]
                    self.mean[k] = sum(column) / len(column)

                    for m in range(len(column)):
                        column[m] -= self.mean[k]

                    self.scaling[k] = self.channelHeight * 0.7 / (max(column) - min(column) + 0.0000000000001)

            # ======================================================================================================
            # Trend Removal and Scaling
            # ======================================================================================================
            for k in range(len(self.dataBuffer[0])):
                for m in range(len(self.dataBuffer)):
                    self.dataBuffer[m][k] -= self.mean[k]
                    self.dataBuffer[m][k] *= self.scaling[k]

            # ======================================================================================================
            # Plot
            # ======================================================================================================
            for k in range(len(self.dataBuffer[0])):
                if self.lastY:
                    if not math.isnan(self.lastY[k]) and not math.isnan(self.dataBuffer[0][k]):
                        painter.drawLine(self.idx * (self.width() / self.dataTr.chunksPerScreen) - self.interval,
                                         -self.lastY[k] + (k + 0.5) * self.channelHeight,
                                         self.idx * (self.width() / self.dataTr.chunksPerScreen),
                                         -self.dataBuffer[0][k] + (k + 0.5) * self.channelHeight)

                for m in range(len(self.dataBuffer) - 1):
                    if not math.isnan(self.dataBuffer[m][k]) and not math.isnan(self.dataBuffer[m+1][k]):
                        painter.drawLine(m * self.interval + self.idx * (self.width() / self.dataTr.chunksPerScreen),
                                         -self.dataBuffer[m][k] + (k + 0.5) * self.channelHeight,
                                         (m + 1)*self.interval + self.idx*(self.width() / self.dataTr.chunksPerScreen),
                                         -self.dataBuffer[m+1][k] + (k + 0.5) * self.channelHeight)

            self.lastY = self.dataBuffer[-1]
