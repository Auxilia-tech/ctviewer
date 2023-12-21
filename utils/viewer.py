import os
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import glob
import sys

ROOT = Path(__file__).resolve().parents[2]

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_MainWindow(QtWidgets.QMainWindow):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Auxilia Viewer")
        MainWindow.resize(1700, 2300)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create main view
        self.main_view = QtWidgets.QWidget()
        self.main_view.setObjectName("Main View")
        self.gridLayout1 = QtWidgets.QGridLayout(self.main_view)
        self.vtkLayout1 = QtWidgets.QVBoxLayout(self.main_view)
        self.vtkLayout1.setObjectName("vtkLayout1")
        self.gridLayout1.addLayout(self.vtkLayout1, 0, 0, 1, 1)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.addTab(self.main_view, "main view")

        # Horizontal layout
        self.hLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.hLayout.addWidget(self.tabWidget)

        # Add a QTreeView to the left side of the main window
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setObjectName("treeView of mhd volume files")
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
        self.fileSystemModel.setNameFilters(['*volume*.mhd'])
        self.fileSystemModel.setNameFilterDisables(False)
        self.treeView.setRootIndex(self.fileSystemModel.index(self.data_path))
        self.treeView.clicked.connect(self.treeItemClicked)

        # Init variables
        self.first_load = True
        self.volume_path = None
        self.mask_files = []
        self.loaded_mask = None
        self.loaded_mask_id = None

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.file_menu = self.menubar.addMenu('File')

        # Action pour ouvrir un dossier
        open_folder_action = QtWidgets.QAction('Open folder', self)
        open_folder_action.triggered.connect(self.openFolderDialog)
        self.file_menu.addAction(open_folder_action)

        # Action pour créer un nouveau projet/fichier
        new_action = QtWidgets.QAction('New', self)
        new_action.triggered.connect(self.newFile)  # Vous devrez définir la méthode newFile
        self.file_menu.addAction(new_action)

        # Action pour ouvrir un fichier
        open_action = QtWidgets.QAction('Open', self)
        open_action.triggered.connect(self.openFile)  # Vous devrez définir la méthode openFile
        self.file_menu.addAction(open_action)

        # Action pour enregistrer
        save_action = QtWidgets.QAction('Save', self)
        save_action.triggered.connect(self.saveFile)  # Vous devrez définir la méthode saveFile
        self.file_menu.addAction(save_action)

        # Action pour enregistrer sous
        save_as_action = QtWidgets.QAction('Save As...', self)
        save_as_action.triggered.connect(self.saveAsFile)  # Vous devrez définir la méthode saveAsFile
        self.file_menu.addAction(save_as_action)

        # Action pour quitter l'application
        exit_as_action = QtWidgets.QAction('Exit', self)
        exit_as_action.triggered.connect(self.exitApp)  # Vous devrez définir la méthode saveAsFile
        self.file_menu.addAction(exit_as_action)

        # Ajouter un menu "Settings"
        self.settings_menu = self.menubar.addMenu('Settings')
        settings_action = QtWidgets.QAction('Settings', self)
        settings_action.triggered.connect(self.openSettingsDialog)
        self.settings_menu.addAction(settings_action)

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setWindowTitle(_translate("Auxilia 3D viewer", "Auxilia 3D viewer", None))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.vtkWidget1 = QVTKRenderWindowInteractor(self)
        self.vtkLayout1.addWidget(self.vtkWidget1)
        # Créer un layout horizontal pour les boutons
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setSpacing(10)  # Ajustez l'espace entre les boutons ici
        # Mode buttons
        self.mode0_button = QtWidgets.QPushButton("Composite")
        self.mode0_button.setToolTip("Change volume Mode to Composite")
        self.mode0_button.clicked.connect(self.onClick_mode_0)
        self.mode0_button.setFixedSize(100, 60)

        self.mode1_button = QtWidgets.QPushButton("Max proj.")
        self.mode1_button.setToolTip("Change volume Mode to max proj.")
        self.mode1_button.clicked.connect(self.onClick_mode_1)
        self.mode1_button.setFixedSize(100, 60)

        self.iso_button = QtWidgets.QPushButton("Iso surface")
        self.iso_button.setToolTip("Change volume Mode to Iso surface Browser")
        self.iso_button.clicked.connect(self.onClick_iso)
        self.iso_button.setFixedSize(100, 60)

        self.masks_button = QtWidgets.QPushButton("Masks")
        self.masks_button.setToolTip("Load masks detected by the X-ray machine")
        self.masks_button.clicked.connect(self.onClick_masks)
        self.masks_button.setFixedSize(100, 60)

        # Ajouter les boutons au layout horizontal
        self.buttonsLayout.addWidget(self.mode0_button)
        self.buttonsLayout.addWidget(self.mode1_button)
        self.buttonsLayout.addWidget(self.iso_button)
        self.buttonsLayout.addWidget(self.masks_button)

        # Ajouter un stretch pour aligner les boutons à gauche
        self.buttonsLayout.addStretch()
        # Ajouter le layout horizontal au layout principal
        self.vtkLayout1.addLayout(self.buttonsLayout)

    # Définitions des méthodes pour les actions (à implémenter)
    def newFile(self):
        pass

    def openFile(self):
        pass

    def saveFile(self):
        pass

    def saveAsFile(self):
        pass

    def exitApp(self):
        print("Exit App")
        sys.exit(0)

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
            if self.loaded_mask is not None:
                self.remove_mask()
            self.update_volume()
            search_pattern = os.path.join(os.path.dirname(self.volume_path), '*labelMask.mhd')
            self.mask_files = glob.glob(search_pattern)
            print(f"{len(self.mask_files)} masks found")
            self.update_color_button_masks()
            self.update_text_button_masks()

    # Méthode pour ouvrir la fenêtre de réglages
    def openSettingsDialog(self):
        self.settingsDialog = SettingsDialog(self)
        self.settingsDialog.show()

    def update_color_button_masks(self):
        new_style = f"{self.masks_button.styleSheet()} background-color: {'red' if len(self.mask_files) > 0 else 'green'};"
        self.masks_button.setStyleSheet(new_style)

    def update_text_button_masks(self):
        if len(self.mask_files) == 0:
            mask_count_text = f"Masks"
        elif self.loaded_mask_id is None:
            mask_count_text = f"Masks\n[ 0 / {len(self.mask_files)} ]"
        else:
            mask_count_text = f"Masks\n[ {self.loaded_mask_id + 1} / {len(self.mask_files)} ]"
        self.masks_button.setText(mask_count_text)

    @Qt.pyqtSlot()
    def onClick_mode_0(self):
        if self.volume_path is not None:
            self.set_mode(0)

    @Qt.pyqtSlot()
    def onClick_mode_1(self):
        if self.volume_path is not None:
            self.set_mode(1)

    @Qt.pyqtSlot()
    def onClick_iso(self):
        if self.volume_path is not None:
            self.set_mode(5)

    @Qt.pyqtSlot()
    def onClick_masks(self):
        if self.volume_path is not None:
            self.update_mask()


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 300, 200)

        self.layout = QtWidgets.QVBoxLayout(self)

        # Ajouter des champs pour les réglages
        self.variable1_edit = QtWidgets.QLineEdit(self)
        self.variable1_edit.setText(str(parent.ogb_cmap[0]))  # Utiliser la valeur actuelle
        self.layout.addWidget(self.variable1_edit)

        self.variable2_edit = QtWidgets.QLineEdit(self)
        self.variable2_edit.setText(str(parent.ogb_cmap[1]))  # Utiliser la valeur actuelle
        self.layout.addWidget(self.variable2_edit)

        self.variable3_edit = QtWidgets.QLineEdit(self)
        self.variable3_edit.setText(str(parent.ogb_cmap[2]))  # Utiliser la valeur actuelle
        self.layout.addWidget(self.variable3_edit)

        # Ajouter un bouton OK
        self.okButton = QtWidgets.QPushButton('OK', self)
        self.okButton.clicked.connect(lambda: self.updateSettings(parent))
        self.layout.addWidget(self.okButton)

    # Méthode pour mettre à jour les réglages
    def updateSettings(self, parent):
        parent.ogb_cmap[0] = int(self.variable1_edit.text())
        parent.ogb_cmap[1] = int(self.variable2_edit.text())
        parent.ogb_cmap[2] = int(self.variable3_edit.text())
        parent.vol.color([(parent.ogb_cmap[0], (244, 102, 27)), (parent.ogb_cmap[1], (0, 255, 0)),
                          (parent.ogb_cmap[2], (0, 0, 127))])
        parent.vol.alpha([(parent.ogb_cmap[0], 1), (parent.ogb_cmap[1], 0.7), (parent.ogb_cmap[2], 0.7)])
        parent.plt.setOTF()
        parent.plt.render()
        self.close()
