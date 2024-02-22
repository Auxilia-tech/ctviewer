import os
from pathlib import Path
from PyQt5 import QtCore, QtWidgets, Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import glob
import sys

ROOT = Path(__file__).resolve().parents[2]
EXT = 'mhd'

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
        MainWindow.resize(1920, 1080)

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
        self.treeView.setObjectName(f"treeView of {EXT} volume files")
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
        self.fileSystemModel.setNameFilters([f'*volume*.{EXT}'])
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

        # Create a Help or About menu
        self.help_menu = self.menubar.addMenu('Help')

        # Add an About action
        self.about_action = QtWidgets.QAction('About', self)
        self.about_action.triggered.connect(self.openAboutDialog)
        self.help_menu.addAction(self.about_action)

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

        self.slice_button = QtWidgets.QPushButton("3D Slider")
        self.slice_button.setToolTip("Cut the volume in 2D slices")
        self.slice_button.clicked.connect(self.onClick_slice)
        self.slice_button.setFixedSize(100, 60)

        self.masks_button = QtWidgets.QPushButton("Masks")
        self.masks_button.setToolTip("Load masks detected by the X-ray machine")
        self.masks_button.clicked.connect(self.onClick_masks)
        self.masks_button.setFixedSize(100, 60)

        self.clean_button = QtWidgets.QPushButton("Clean")
        self.clean_button.setToolTip("Delete loaded masks and volume")
        self.clean_button.clicked.connect(self.onClick_clean)
        self.clean_button.setFixedSize(100, 60)

        # Ajouter les boutons au layout horizontal
        self.buttonsLayout.addWidget(self.mode0_button)
        self.buttonsLayout.addWidget(self.mode1_button)
        self.buttonsLayout.addWidget(self.iso_button)
        self.buttonsLayout.addWidget(self.slice_button)
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
        self.data_path = QtWidgets.QFileDialog.getExistingDirectory(self, f"Select {EXT} data Folder", options=options)
        if self.data_path:
            print("Selected Folder:", self.data_path)
            self.volume_files = [path for path in Path(self.data_path).rglob('*.' + EXT)]
            if len(self.volume_files) > 0:
                # Update the file system model with the new root path
                self.fileSystemModel.setRootPath(self.data_path)
                self.treeView.setRootIndex(self.fileSystemModel.index(self.data_path))
            else:
                self.showEmptyFolderPopup()

    def showEmptyFolderPopup(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(f"No .{EXT} volumes in {self.data_path}")
        msg.setWindowTitle("Empty Folder Path")
        msg.exec_()

    def treeItemClicked(self, index):
        volume_path = self.fileSystemModel.filePath(index)
        if volume_path.endswith(f".{EXT}"):
            self.volume_path = volume_path
            print("Selected Volume:", self.volume_path)
            if self.loaded_mask is not None:
                self.remove_mask()
            self.update_volume()
            search_pattern = os.path.join(os.path.dirname(self.volume_path), f'*labelMask.{EXT}')
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
            if self.vol.mode() == 5:
                self.plt.quit_iso_surface()
                self.plt.init_ray_cast(0)
            elif self.plt.slice_mode == True:
                self.plt.quit_3d_slider()
                self.plt.init_ray_cast(0)
            else:
                self.vol.mode(0)
            self.plt.w0.value = 0.1
            self.plt.alphaslider0 = 0.1
            self.plt.w1.value = 0.7
            self.plt.alphaslider1 = 0.7
            self.plt.w2.value = 1
            self.plt.alphaslider2 = 1
            self.plt.render()
            self.plt.setOTF()

    @Qt.pyqtSlot()
    def onClick_mode_1(self):
        if self.volume_path is not None:
            if self.vol.mode() == 5:
                self.plt.quit_iso_surface()
                self.plt.init_ray_cast(1)
            elif self.plt.slice_mode == True:
                self.plt.quit_3d_slider()
                self.plt.init_ray_cast(1)
            else:
                self.vol.mode(1)
            self.plt.w0.value = 1
            self.plt.alphaslider0 = 1
            self.plt.w1.value = 0.7
            self.plt.alphaslider1 = 0.7
            self.plt.w2.value = 1
            self.plt.alphaslider2 = 1
            self.plt.render()
            self.plt.setOTF()

    @Qt.pyqtSlot()
    def onClick_iso(self):
        if self.volume_path is not None:
            if self.plt.slice_mode == True:
                self.plt.quit_3d_slider()
                self.plt.init_iso_surface()
            elif self.vol.mode() != 5:
                self.plt.quit_ray_cast()
                self.plt.init_iso_surface()
            else:
                self.vol.mode(5)
            self.plt.render()

    @Qt.pyqtSlot()
    def onClick_slice(self):
        if self.volume_path is not None and self.plt.slice_mode != True:
            if self.vol.mode() == 5:
                self.plt.quit_iso_surface()
            elif self.vol.mode() == 0 or self.vol.mode() == 1:
                self.plt.quit_ray_cast()
            self.plt.init_3d_slider()
            self.plt.w0.value = 0
            self.plt.alphaslider0 = 0
            self.plt.w1.value = 0
            self.plt.alphaslider1 = 0
            self.plt.w2.value = 0
            self.plt.alphaslider2 = 0
            self.plt.setOTF()
            self.plt.render()

    @Qt.pyqtSlot()
    def onClick_masks(self):
        if self.volume_path is not None:
            self.update_mask()

    @Qt.pyqtSlot()
    def onClick_clean(self):
        if self.volume_path is not None:
            self.remove_mask()
            self.update_text_button_masks()
            if self.plt.slice_mode != True:
                if self.vol.mode() == 5:
                    self.plt.quit_iso_surface()
                elif self.vol.mode() == 0 or self.vol.mode() == 1:
                    self.plt.quit_ray_cast()
            else:
                self.plt.quit_3d_slider()
            self.plt.remove(self.vol)
            self.volume_path = None
            self.first_load = True
            self.plt.clear(deep=True)
            self.plt.setOTF()
            self.plt.render()

    @Qt.pyqtSlot()
    def onClick_axes(self):
        if self.volume_path is not None:
            i = self.plt.renderers.index(self.plt.renderer)
            try:
                self.plt.axes_instances[i].EnabledOff()
                self.plt.axes_instances[i].SetInteractor(None)
            except AttributeError:
                try:
                    self.plt.remove(self.plt.axes_instances[i])
                except:
                    print("Cannot remove axes", [self.plt.axes_instances[i]])
                    return
            if self.plt.axes == 13:
                    self.plt.axes = 0
            else:
                self.plt.axes += 1
            axes_count_text = f"Axes\n[ {self.plt.axes} / {14} ]"
            self.axes_button.setText(axes_count_text)
            self.plt.axes_instances[i] = None
            self.plt.axes_render()
            self.plt.render()
    
    @Qt.pyqtSlot()
    def onClick_apparence(self):
        if self.volume_path is not None:
            if self.apparence_button.text() == "Light mode":
                self.plt.change_background('white', 'white')
                self.apparence_button.setText(f"Dark mode")
            else:
                self.plt.change_background('black', 'blackboard')
                self.apparence_button.setText(f"Light mode")
            self.plt.render()
    
    def onClick_shorcuts(self):
        msg = (
                "    i     : print info about the last clicked object     \n"
                "    I     : print color of the pixel under the mouse     \n"
                "    Y     : show the pipeline for this object as a graph \n"
                "    <- -> : use arrows to reduce/increase opacity        \n"
                "    x     : toggle mesh visibility                       \n"
                "    w     : toggle wireframe/surface style               \n"
                "    l     : toggle surface edges visibility              \n"
                "    p/P   : hide surface faces and show only points      \n"
                "    1-3   : cycle surface color (2=light, 3=dark)        \n"
                "    4     : cycle color map (press shift-4 to go back)   \n"
                "    5-6   : cycle point-cell arrays (shift to go back)   \n"
                "    7-8   : cycle background and gradient color          \n"
                "    09+-  : cycle axes styles (on keypad, or press +/-)  \n"
                "    k     : cycle available lighting styles              \n"
                "    K     : toggle shading as flat or phong              \n"
                "    A     : toggle anti-aliasing                         \n"
                "    D     : toggle depth-peeling (for transparencies)    \n"
                "    U     : toggle perspective/parallel projection       \n"
                "    o/O   : toggle extra light to scene and rotate it    \n"
                "    a     : toggle interaction to Actor Mode             \n"
                "    n     : toggle surface normals                       \n"
                "    r     : reset camera position                        \n"
                "    R     : reset camera to the closest orthogonal view  \n"
                "    .     : fly camera to the last clicked point         \n"
                "    C     : print the current camera parameters state    \n"
                "    X     : invoke a cutter widget tool                  \n"
                "    S     : save a screenshot of the current scene       \n"
                "    E/F   : export 3D scene to numpy file or X3D         \n"
                "    q     : return control to python script              \n"
                "    Esc   : abort execution and exit python kernel         "
            )
        QtWidgets.QMessageBox.about(self, "Keybord shorcuts", msg)

    def openAboutDialog(self):
        about_text = """
Viewer Version 1.1

This application is designed and developed by AUXILIA-TECH for efficient and effective 3D visualization of X-ray security data. It offers a range of features designed to help professionals gain insights and make informed decisions.

Copyright © 2023 AUXILIA. All rights reserved.

For more information or to provide feedback, please contact us at auxilia-tech.com
        """
        QtWidgets.QMessageBox.about(self, "About Viewer", about_text)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.config_manager = ConfigManager()
        self.user_config = self.config_manager.get_user_config()

        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 300, 200)
        self.layout = QtWidgets.QVBoxLayout(self)

        # Load current user settings or defaults if not set
        colors = self.user_config.get('colors')
        ogb_cmap = self.user_config.get('ogb_cmap')
        alpha_weights = self.user_config.get('alpha_weights')
        ext = self.user_config.get('ext', 'mhd')
        mask_classes = self.user_config.get('mask_classes')

        self.ogb_cmap1_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap1_edit.setText(str(ogb_cmap[0]))
        self.layout.addWidget(self.ogb_cmap1_edit)

        self.ogb_cmap2_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap2_edit.setText(str(ogb_cmap[1]))
        self.layout.addWidget(self.ogb_cmap2_edit)

        self.ogb_cmap3_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap3_edit.setText(str(ogb_cmap[2]))
        self.layout.addWidget(self.ogb_cmap3_edit)

        self.alpha1_edit = QtWidgets.QLineEdit(self)
        self.alpha1_edit.setText(str(alpha_weights[0]))
        self.layout.addWidget(self.alpha1_edit)

        self.alpha2_edit = QtWidgets.QLineEdit(self)
        self.alpha2_edit.setText(str(alpha_weights[1]))
        self.layout.addWidget(self.alpha2_edit)

        self.alpha3_edit = QtWidgets.QLineEdit(self)
        self.alpha3_edit.setText(str(alpha_weights[2]))
        self.layout.addWidget(self.alpha3_edit)

        self.ext_edit = QtWidgets.QLineEdit(self)
        self.ext_edit.setText(str(ext))
        self.layout.addWidget(self.ext_edit)

        self.resetButton = QtWidgets.QPushButton('Reset', self)
        self.resetButton.clicked.connect(self.reset_settings)
        self.layout.addWidget(self.resetButton)

        self.okButton = QtWidgets.QPushButton('Apply', self)
        self.okButton.clicked.connect(lambda: self.updateSettings(parent))
        self.layout.addWidget(self.okButton)

        # Update the user settings
        parent.colors = colors
        parent.ogb_cmap = ogb_cmap
        parent.ogb = [(ogb_cmap[0], colors[0]), (ogb_cmap[1],
                                                 colors[1]), (ogb_cmap[2], colors[2])]
        parent.alpha = [(0, 1), (ogb_cmap[0], alpha_weights[0]),
                        (ogb_cmap[1], alpha_weights[1]), (ogb_cmap[2], alpha_weights[2])]
        parent.ext = ext
        parent.mask_classes = mask_classes

    def updateSettings(self, parent):
        # Update the user settings based on the dialog input
        self.user_config['ogb_cmap'] = [
            int(self.ogb_cmap1_edit.text()),
            int(self.ogb_cmap2_edit.text()),
            int(self.ogb_cmap3_edit.text())
        ]
        self.user_config['alpha_weights'] = [
            float(self.alpha1_edit.text()),
            float(self.alpha2_edit.text()),
            float(self.alpha3_edit.text())
        ]
        self.user_config['ext'] = str(self.ext_edit.text())

        # Get the value of the user settings
        ogb_cmap = self.user_config['ogb_cmap']
        alpha_weights = self.user_config['alpha_weights']
        colors = self.user_config['colors']
        ext = self.user_config['ext']

        # Update the volume color and alpha settings
        if parent.volume_path is not None:
            parent.vol.color([(ogb_cmap[0], colors[0]), (ogb_cmap[1], colors[1]),
                              (ogb_cmap[2], colors[2])])
            parent.vol.alpha([(ogb_cmap[0], alpha_weights[0]), (ogb_cmap[1],
                             alpha_weights[1]), (ogb_cmap[2], alpha_weights[2])])
            parent.ext = ext
            parent.plt.setOTF()
            parent.plt.render()
        self.config_manager.save_user_config(self.user_config)
        parent.refreshTreeView()
        self.close()

    def reset_settings(self):
        self.config_manager.reset_user_config()
        self.user_config = self.config_manager.get_user_config()

        # Load current user settings or defaults if not set
        ogb_cmap = self.user_config.get('ogb_cmap')
        alpha_weights = self.user_config.get('alpha_weights')
        ext = self.user_config.get('ext')

        # Update the panel settings
        self.ogb_cmap1_edit.setText(str(ogb_cmap[0]))
        self.ogb_cmap2_edit.setText(str(ogb_cmap[1]))
        self.ogb_cmap3_edit.setText(str(ogb_cmap[2]))
        self.alpha1_edit.setText(str(alpha_weights[0]))
        self.alpha2_edit.setText(str(alpha_weights[1]))
        self.alpha3_edit.setText(str(alpha_weights[2]))
        self.ext_edit.setText(str(ext))


class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self.load_config()

    def load_config(self):
        """Load the .json configuration file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize with an empty structure or predefined defaults
            return {"default": {}, "user": {}}

    def save_user_config(self, user_config):
        """Save the updated user configuration."""
        self.config['user'] = user_config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def reset_user_config(self):
        """Reset user config to the default values."""
        self.config['user'] = self.config['default'].copy()
        self.save_user_config(self.config['user'])

    def get_user_config(self):
        """Get the current user configuration."""
        return self.config['user']
