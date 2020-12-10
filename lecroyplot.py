from PyQt5 import QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon

class FileBrowserWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file system view - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        idx = self.model.index(r'C:\Users\aspit\National Energy Technology Laboratory\MHD Lab - Documents\Data Share\MHD Lab\HVOF Booth')
        self.tree.setRootIndex(idx)
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.setWindowTitle("Dir View")
        self.tree.resize(640, 480)
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)
        

class MainWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        # self.setCentralWidget(self.graphWidget)

        hbox = QtWidgets.QHBoxLayout()

        self.fbwidget = FileBrowserWidget()

        self.fbwidget.tree.clicked.connect(self.on_treeView_clicked)

        hbox.addStretch(1)
        hbox.addWidget(self.fbwidget)
        hbox.addWidget(self.graphWidget)

        self.setLayout(hbox)

        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature = [30,32,34,32,33,31,29,32,35,45]

        self.graphWidget.plot(hour, temperature)
    
    def on_treeView_clicked(self, index):
        model = self.fbwidget.model

        # filename =  model.fileName(index)
        filepath = model.filePath(index)

        if os.path.splitext(filepath)[1] == '.trc':
            print(filepath)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setCentralWidget(MainWidget())

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()