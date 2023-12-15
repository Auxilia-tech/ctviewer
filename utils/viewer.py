import os
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui

ROOT = Path(__file__).resolve().parents[2]

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Auxilia Viewer")
        MainWindow.resize(1700, 2300)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create tabs
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.gridLayout1 = QtWidgets.QGridLayout(self.tab1)
        self.vtkLayout1 = QtWidgets.QVBoxLayout(self.tab1)
        self.vtkLayout1.setObjectName("vtkLayout1")
        self.gridLayout1.addLayout(self.vtkLayout1, 0, 0, 1, 1)

        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")
        self.gridLayout2 = QtWidgets.QGridLayout(self.tab2)
        self.vtkLayout2 = QtWidgets.QVBoxLayout(self.tab2)
        self.vtkLayout2.setObjectName("vtkLayout2")
        self.gridLayout2.addLayout(self.vtkLayout2, 0, 0, 1, 1)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.addTab(self.tab1, "Ray Cast Plotter")
        self.tabWidget.addTab(self.tab2, "Iso surface Browser")

        # Horizontal layout
        self.hLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.hLayout.addWidget(self.tabWidget)

        # Add a QTreeView to the left side of the main window
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setObjectName("treeView of mhd files")
        self.treeView.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.treeView.setMaximumWidth(250)  # Set a maximum width for the tree view

        # Use a QVBoxLayout for the left side layout
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.treeView)

        # Add the left layout to the main layout
        self.hLayout.addLayout(left_layout)

        # Rest of code...
        self.fileSystemModel = QtWidgets.QFileSystemModel()
        self.treeView.setModel(self.fileSystemModel)
        self.data_path = '../datasets/' if os.path.exists('../datasets/') else str(ROOT)
        self.fileSystemModel.setRootPath(self.data_path)
        self.fileSystemModel.setNameFilters(['*.mhd'])
        self.fileSystemModel.setNameFilterDisables(False)
        self.treeView.setRootIndex(self.fileSystemModel.index(self.data_path))
        self.treeView.clicked.connect(self.treeItemClicked)

        # Init variables
        self.first_load = True
        self.volume_path = None

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.folder_menu = self.menubar.addMenu('Folder')
        open_folder_action = QtWidgets.QAction('Open', self)
        open_folder_action.triggered.connect(self.openFolderDialog)  # Connect the action to a function
        self.folder_menu.addAction(open_folder_action)
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setWindowTitle(_translate("Auxilia 3D viewer", "Auxilia 3D viewer", None))

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def openFolderDialog(self):
        options = QtWidgets.QFileDialog.Options()
        self.data_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select mhd data Folder", options=options)
        if self.data_path:
            print("Selected Folder:", self.data_path)
            self.mhd_files = [path for path in Path(self.data_path).rglob('*.' + 'mhd')]
            if len(self.mhd_files) > 0:
                # Update the file system model with the new root path
                self.fileSystemModel.setRootPath(self.data_path)
                self.treeView.setRootIndex(self.fileSystemModel.index(self.data_path))
            else:
                self.showEmptyFolderPopup()

    def showEmptyFolderPopup(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(f"No .mhd volumes in {self.data_path}")
        msg.setWindowTitle("Empty Folder Path")
        msg.exec_()

    def treeItemClicked(self, index):
        volume_path = self.fileSystemModel.filePath(index)
        if volume_path.endswith(".mhd"):
            self.volume_path = volume_path
            print("Selected Volume:", self.volume_path)
            self.update_volume()
