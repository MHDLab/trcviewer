from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout, QSplitter
from PyQt5.QtGui import QIcon

from readTrc import readTrc
import pprint 

class FileBrowserWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):        
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        idx = self.model.index(r'C:\Users\aspit\National Energy Technology Laboratory\MHD Lab - Documents\Data Share\MHD Lab\HVOF Booth')
        self.tree.setRootIndex(idx)
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.hideColumn(2)
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)
        
class MainWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fbwidget = FileBrowserWidget()
        self.fbwidget.tree.clicked.connect(self.on_treeView_clicked)
        self.textbrowser = QtWidgets.QTextBrowser()
        fb_layout = QtWidgets.QVBoxLayout()
        fb_layout.addWidget(self.fbwidget)
        fb_layout.addWidget(self.textbrowser)
        fb_widget = QtWidgets.QWidget()
        fb_widget.setLayout(fb_layout)

        self.graphWidget = pg.PlotWidget()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(fb_widget)
        splitter.addWidget(self.graphWidget)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter)

        self.setLayout(hbox)
        self.trc = readTrc.Trc()
    
    def on_treeView_clicked(self, index):
        model = self.fbwidget.model
        filepath = model.filePath(index)

        if os.path.splitext(filepath)[1] == '.trc':
            datX, datY, d = self.trc.open(filepath)
            self.graphWidget.clear()
            self.graphWidget.plot(datX, datY)
            self.textbrowser.setText(pprint.pformat(d, indent=2))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Lecroy Viewer')

        self.setCentralWidget(MainWidget())

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()