import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PyQt5 import QtCore
from PyQt5 import QtWidgets

class TreeView(QTreeView):
    def __init__(self, centralwidget:QWidget, left_layout:QVBoxLayout, exts:list, update_volume_callback:callable):
        """
        A custom QTreeView widget for displaying a file system view with specific file extensions.

        Args:
            centralwidget (QWidget): The parent widget to which the TreeView will be added.
            left_layout (QVBoxLayout): The layout in which the TreeView will be placed.
            exts (list): A list of file extensions to filter the file system view.
            update_volume_callback (callable): A callback function to be called when a tree item is clicked.

        """
        super().__init__(centralwidget)
        self.exts = exts
        self.update_volume_callback = update_volume_callback
        self.setObjectName(f"TreeView of {exts} volume files")
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.setMaximumWidth(300)
        self.fileSystemModel = QtWidgets.QFileSystemModel()
        self.setModel(self.fileSystemModel)
        self.clicked.connect(self.treeItemClicked)
        left_layout.addWidget(self)
        self.data_path = '../datasets/' if os.path.exists('../datasets/') else str(os.path.dirname(os.path.realpath(__file__))) + '/datasets/'
        self.refreshTreeView()
    
    def refreshTreeView(self):
        """Refresh the file system view based on the current directory and file extension."""
        self.fileSystemModel.setRootPath(self.data_path)
        self.fileSystemModel.setNameFilters([f"*.{ext}" for ext in self.exts])
        self.fileSystemModel.setNameFilterDisables(False)
        self.setRootIndex(self.fileSystemModel.index(self.data_path))
        self.dataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def treeItemClicked(self, index:QtCore.QModelIndex):
        """
        Handle the tree item clicked event.

        Args:
            index (QModelIndex): The index of the clicked tree item.

        """
        volume_path = self.fileSystemModel.filePath(index)
        self.update_volume_callback(volume_path)
        self.refreshTreeView()

    def set_folder(self, folder:str):
        """
        Set the data path to a new folder and refresh the file system view.

        Args:
            folder (str): The path to the new folder.

        """
        self.data_path = folder
        self.refreshTreeView()