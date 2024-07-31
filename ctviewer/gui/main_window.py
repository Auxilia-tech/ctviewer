from pathlib import Path

from PyQt5 import QtCore, QtWidgets, Qt, QtGui
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from ctviewer.rendering import Renderer
from .setting_dialog import SettingDialog
from .tree_view import TreeView
from ctviewer.utils import SHORCUTS_TEXT, ABOUT_TEXT

ROOT = Path(__file__).resolve().parents[2]

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class MainWindow(QtWidgets.QMainWindow):
    """
    The main window of the CTViewer application.

    This class represents the main window of the CTViewer application. It contains various widgets and functionality
    to display and interact with CT scan data.

    """

    def __init__(self):
        """ Initialize the main window of the CTViewer application. """
        super(MainWindow, self).__init__()

        self.setObjectName("Auxilia CTViewer")
        self.setWindowTitle(_translate("Auxilia CTViewer", "Auxilia CTViewer", None))
        self.setWindowIcon(QtGui.QIcon(str(ROOT / "icons" / "logo.png"))  )
        QtCore.QMetaObject.connectSlotsByName(self)
        self.resize(1920, 1080)

        # Create a settings dialog
        self.settingDialog = SettingDialog(self)
        self.vtkWidget1 = QVTKRenderWindowInteractor(self)
        user_config = self.settingDialog.get_current_config()
        
        # Create a renderer
        self.renderer = Renderer(**user_config, qt_widget=self.vtkWidget1, isovalue=1350, bg='white', bg2='white', axes=8)

        # Create a central widget
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)

        # Create main view
        self.main_view = QtWidgets.QWidget()
        self.main_view.setObjectName("Main View")

        # Create a vertical layout for the main view
        self.vtkLayout1 = QtWidgets.QVBoxLayout(self.main_view)
        self.vtkLayout1.setObjectName("vtkLayout1")
        self.vtkLayout1.addWidget(self.vtkWidget1)
        
        # Create a tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.addTab(self.main_view, "Main View")

        # Horizontal layout
        self.hLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.hLayout.addWidget(self.tabWidget)

        # Create a vertical layout for the left side of the main window
        self.left_layout = QtWidgets.QVBoxLayout()

        # Add a QTreeView to the left side of the main window
        self.treeView = TreeView(self.centralwidget, self.left_layout, self.settingDialog.get_exts(), self.renderer.update_volume)
        self.add_Push_button("Refresh", "Refresh the tree view", self.treeView.refreshTreeView, self.left_layout, size=(270, 60))
    
        self.hLayout.addLayout(self.left_layout)

        # Create a menu bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.setMenuBar(self.menubar)

        # Add a menu "File"
        self.file_menu = self.menubar.addMenu('File')
        self.add_Action_button("Open folder", self.openFolderDialog, self.file_menu)
        self.add_Action_button("Open file", self.openFileDialog, self.file_menu)
        self.add_Action_button("New", self.newFile, self.file_menu)
        self.add_Action_button("Save", self.saveFile, self.file_menu)
        self.add_Action_button("Save As...", self.saveAsFile, self.file_menu)
        self.add_Action_button("Exit", self.onClose(), self.file_menu)

        # Add a menu "Edit"
        self.edit_menu = self.menubar.addMenu('Edit')
        self.add_Action_button("Export Web X3D", self.OnClick_exportWebX3D, self.edit_menu)

        # Add a menu "Settings"
        self.settings_menu = self.menubar.addMenu('Settings')
        self.add_Action_button("Settings", self.settingDialog.show, self.settings_menu)

        # Add a menu "Help"
        self.help_menu = self.menubar.addMenu('Help')
        self.add_Action_button("About", self.openAboutDialog, self.help_menu)
        self.add_Action_button("Website", self.openWebsite, self.help_menu)

        # Create a status bar
        self.setStatusBar(QtWidgets.QStatusBar(self))

        # Créer un layout horizontal pour les boutons
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        # Ajustez l'espace entre les boutons ici
        self.buttonsLayout.setSpacing(10)

        # Add a button to export the 3D scene to X3D
        self.add_Push_button("Composite", "Change volume Mode to Composite", lambda: self.renderer.ray_cast_mode(0), self.buttonsLayout)
        self.add_Push_button("Max proj.", "Change volume Mode to max proj.", lambda: self.renderer.ray_cast_mode(1), self.buttonsLayout)
        self.add_Push_button("Iso surface", "Change volume Mode to Iso surface Browser", self.renderer.iso_surface_mode, self.buttonsLayout)
        self.add_Push_button("3D Slider", "Cut the volume in 2D slices", self.renderer.slider_mode, self.buttonsLayout)
        self.add_Push_button("Clean view", "Delete loaded masks and volume", self.renderer.clean_view, self.buttonsLayout)
        self.add_Push_button(f"Axes\n[ {8} / {14} ]", "Change axes mode", self.onClick_axes, self.buttonsLayout)
        self.add_Push_button(f"Dark mode", "Change apparence mode", self.onClick_apparence, self.buttonsLayout)
        self.add_Push_button(f"Shorcuts", "Show keyboard shorcuts", self.onClick_shorcuts, self.buttonsLayout)

        self.buttonsLayout.addStretch()
        self.vtkLayout1.addLayout(self.buttonsLayout)

    def add_Push_button(self, text:str, tooltip:str, callback_func, layout:QtWidgets.QLayout, size=(100, 60)):

        button = QtWidgets.QPushButton(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback_func)
        button.setFixedSize(*size)
        layout.addWidget(button)
        button_name = "axes_button" if "Axes" in text else text.split()[0].lower() + "_button"
        setattr(self, button_name, button)
            
    
    def add_Action_button(self, action_name:str, callback_func, menu:QtWidgets.QMenu):
        action = QtWidgets.QAction(action_name, self)
        action.triggered.connect(callback_func)
        menu.addAction(action)
        
    # Définitions des méthodes pour les actions (à implémenter)
    def newFile(self):
        """ Create a new scene """
        pass

    def saveFile(self):
        """ Save the current scene to a file """
        pass

    def saveAsFile(self):
        """ Save the current scene to a file """
        pass

    def openFolderDialog(self):
        options = QtWidgets.QFileDialog.Options()
        exts = self.settingDialog.get_exts()
        self.data_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, f"Select {exts} data Folder", options=options)
        if hasattr(self, 'data_path') and self.data_path:
            self.volume_files = [path for ext in exts for path in Path(self.data_path).rglob('*.' + ext)]
            if len(self.volume_files) > 0:
                self.treeView.set_folder(self.data_path)
            else:
                self.showPopup("Warning", "Empty Folder Path", f"No .{exts} volumes in {self.data_path}")
    
    def openFileDialog(self):
        options = QtWidgets.QFileDialog.Options()
        exts = self.settingDialog.get_exts() # 'nii', 'nii.gz', 'mha', 'mhd'
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open volume or mask file", "", f"Volume Files (*.{' *.'.join(exts)})", options=options)
        if file_path:
            self.renderer.update_volume(file_path)
            self.treeView.refreshTreeView()
        
    def showPopup(self, type, title, message):
        msg = QtWidgets.QMessageBox()
        icon_type = getattr(QtWidgets.QMessageBox, type)
        msg.setIcon(icon_type)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec_()

    @Qt.pyqtSlot()
    def onClick_axes(self):
        self.renderer.switch_axes()
        axes_count_text = f"Axes\n[ {self.renderer.axes} / {14} ]"
        self.axes_button.setText(axes_count_text)
    
    @Qt.pyqtSlot()
    def onClick_apparence(self):
        if self.dark_button.text() == "Light mode":
            self.renderer.change_background('white', 'white')
            self.dark_button.setText(f"Dark mode")
        else:
            self.renderer.change_background('black', 'blackboard')
            self.dark_button.setText(f"Light mode")

    @Qt.pyqtSlot()
    def OnClick_exportWebX3D(self):
        if len(self.renderer.bboxes) > 0:
            self.renderer.exportWeb()
            self.showPopup("Information", "Export Success", "The volume and mask have been exported to export/tdr.x3d")
        else:
            self.showPopup("Warning", "Export Error", "No mask found. Please upload a TDR file first.")

    def onClose(self):
        # self.vtkWidget1.close()
        self.renderer.onClose()
        self.close()
    
    def onClick_shorcuts(self):
        QtWidgets.QMessageBox.about(self, "Keybord shorcuts", SHORCUTS_TEXT)

    def openAboutDialog(self):
        QtWidgets.QMessageBox.about(self, "About Viewer", ABOUT_TEXT)

    def openWebsite(self):
        url = QtCore.QUrl("https://auxilia-tech.com")
        QtGui.QDesktopServices.openUrl(url)
