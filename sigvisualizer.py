import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStatusBar,
                             QTreeWidgetItem)

from ui_sigvisualizer import Ui_MainWindow


class SigVisualizer(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Real Time Signal Visualizer')
        self.ui.treeWidget.setHeaderLabel('Streams')
        self.setWindowIcon(QIcon('sigvisualizer.ico'))

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.ui.toggleButton.setIcon(QIcon("icons/chevron_left.svg"))
        self.ui.toggleButton.setIconSize(QSize(30, 30))

        self.ui.toggleButton.clicked.connect(self.toggle_panel)
        self.ui.updateButton.clicked.connect(
            self.ui.widget.dataTr.update_streams)
        self.ui.widget.dataTr.updateStreamNames.connect(
            self.update_metadata_widget)
        self.panelHidden = False

    def update_metadata_widget(self, metadata, default_idx):
        for k in range(len(metadata)):
            item = QTreeWidgetItem(self.ui.treeWidget)
            item.setText(0, metadata[k]["name"])

            for m in range(metadata[k]["ch_count"]):
                channel_item = QTreeWidgetItem(item)
                channel_item.setText(0, 'Channel {}'.format(m+1))
                channel_item.setCheckState(0, Qt.Checked)

            item.setExpanded(True if k == default_idx else False)
            self.ui.treeWidget.addTopLevelItem(item)

        self.ui.treeWidget.setAnimated(True)
        self.statusBar.showMessage(
            "Sampling rate: {}Hz".format(metadata[default_idx]["srate"]))

    def toggle_panel(self):
        if self.panelHidden:
            self.panelHidden = False
            self.ui.treeWidget.show()
            self.ui.updateButton.show()
            self.ui.toggleButton.setIcon(QIcon("icons/chevron_left.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30))
        else:
            self.panelHidden = True
            self.ui.treeWidget.hide()
            self.ui.updateButton.hide()
            self.ui.toggleButton.setIcon(QIcon("icons/chevron_right.svg"))
            self.ui.toggleButton.setIconSize(QSize(30, 30))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SigVisualizer()
    window.show()
    sys.exit(app.exec_())
