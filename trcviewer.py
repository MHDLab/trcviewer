
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import pandas as pd

#TODO: Improve imports and make consistent
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QTreeView, QWidget, QVBoxLayout, QSplitter, QMenuBar, QMenu, QAction, QFileDialog, QTableWidget, QTableWidgetItem, QLabel
from PyQt5 import QtGui

from readTrc import readTrc

BASE_DIR = r'C:\Users\aspit\National Energy Technology Laboratory\MHD Lab - Documents\Data Share\MHD Lab'

#https://stackoverflow.com/questions/47357578/how-do-i-collect-rows-from-qitemselection
def selected_rows(selection):
    indexes = []
    for index in selection.indexes():
        if index.column() == 0:
            indexes.append(index)
    return indexes

if not os.path.exists(BASE_DIR):
    print('Could not find default base directory')
    BASE_DIR = ''
class FileBrowserWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):        
        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        idx = self.model.index(BASE_DIR)
        self.tree.setRootIndex(idx)
        
        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        
        self.tree.hideColumn(2)
        self.tree.header().resizeSection(0,200)
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)      
class Plotter(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)    

        vbox = QtWidgets.QVBoxLayout()

        self.radiobutton = QtWidgets.QRadioButton()
        radio_formlayout = QtWidgets.QFormLayout()
        radio_formlayout.addRow('Smooth' , self.radiobutton)

        self.spinBox_smoothamount= QtWidgets.QSpinBox()
        self.spinBox_smoothamount.setMinimum(1)
        self.spinBox_smoothamount.setMaximum(1000)
        spinbox_formlayout = QtWidgets.QFormLayout()
        spinbox_formlayout.addRow('Smooth Amount', self.spinBox_smoothamount)
        
        controls = QtWidgets.QHBoxLayout()
        controls.addLayout(radio_formlayout)
        controls.addLayout(spinbox_formlayout)

        vbox.addLayout(controls)

        styles = {'color': '#FFF', 'font-size':'12pt'}

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel('left', 'Amplitude (V)', **styles)
        self.graphWidget.setLabel('bottom', 'Time (s)', **styles)
        vbox.addWidget(self.graphWidget)
        
        self.setLayout(vbox)

class TableView(QTableWidget):
    #https://pythonbasics.org/pyqt-table/
    def __init__(self, *args):
        QTableWidget.__init__(self, *args)
        self.setHorizontalHeaderLabels(['Value'])
 
    def setData(self, data): 
        self.setRowCount(len(data))

        verHeaders = []
        for n, key in enumerate(sorted(data.keys())):
            verHeaders.append(key)
            newitem = QTableWidgetItem(data[key])
            self.setItem(n, 0, newitem)
        self.setVerticalHeaderLabels(verHeaders)
    
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

class MainWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fbwidget = FileBrowserWidget()
        self.fbwidget.tree.selectionModel().selectionChanged.connect(self.on_treeView_clicked)
        self.metadata_browser = TableView(1,1)

        fullpath_layout = QtWidgets.QHBoxLayout()
        fullpath_layout.addWidget(QLabel('Selected Path'))
        self.current_selected_path = QtWidgets.QLineEdit()
        fullpath_layout.addWidget(self.current_selected_path)

        relpath_layout = QtWidgets.QHBoxLayout()
        relpath_layout.addWidget(QLabel('Relative Path'))
        self.current_selected_relpath = QtWidgets.QLineEdit()
        relpath_layout.addWidget(self.current_selected_relpath)



        fb_layout = QtWidgets.QVBoxLayout()
        fb_layout.addWidget(QLabel('File Browser'))
        fb_layout.addLayout(fullpath_layout)
        fb_layout.addLayout(relpath_layout)
        fb_layout.addWidget(self.fbwidget)
        fb_layout.addWidget(QLabel('File Metadata'))
        fb_layout.addWidget(self.metadata_browser)
        fb_widget = QtWidgets.QWidget()
        fb_widget.setLayout(fb_layout)

        self.plotter = Plotter()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(fb_widget)
        splitter.addWidget(self.plotter)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(splitter)

        self.setLayout(hbox)
        self.trc = readTrc.Trc()

        self.series = None

        self.plotter.spinBox_smoothamount.valueChanged.connect(self.update_plot)
        self.plotter.radiobutton.clicked.connect(self.update_plot)
    
    def on_treeView_clicked(self, selected, deselected):

        #See function definition. Selection model is needed to allow for change when navigating by keyboard. 
        index = selected_rows(selected)[0]

        model = self.fbwidget.model
        filepath = model.filePath(index)

        self.current_selected_path.setText(filepath)

        root_dir = self.fbwidget.model.filePath(self.fbwidget.tree.rootIndex())
        rel_path = os.path.relpath(filepath, root_dir)
        self.current_selected_relpath.setText(rel_path)

        if os.path.splitext(filepath)[1] == '.trc':
            datX, datY, d = self.trc.open(filepath)

            self.series = pd.Series(datY, index=datX)

            d_str = {key: str(d[key]) for key in d.keys()}
            self.metadata_browser.setData(d_str)
            self.metadata_browser.show()
            self.update_plot()

    def update_plot(self):
        if self.series is not None:
            if self.plotter.radiobutton.isChecked():
                rolling_amount = self.plotter.spinBox_smoothamount.value()
                s = self.series.rolling(rolling_amount).mean()
            else:
                s = self.series

            self.plotter.graphWidget.clear()
            self.plotter.graphWidget.plot(s.index, s.values)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon(r'resources\icon.ico'))
        self.setWindowTitle('trc File Viewer')

        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)

        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        self.open_base_folderAction = QAction("&Open Base Folder", self)
        fileMenu.addAction(self.open_base_folderAction)

        self.open_base_folderAction.triggered.connect(self.update_base_folder)

        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    def update_base_folder(self):

        fb = self.main_widget.fbwidget

        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        idx = fb.model.index(folder)
        fb.tree.setRootIndex(idx)

def main():
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()