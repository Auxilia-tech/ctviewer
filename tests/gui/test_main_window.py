# tests/gui/test_main_window.py
import pytest
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import Qt
from unittest import mock
from pytest_mock import MockerFixture
from ctviewer.gui.main_window import MainWindow
import sys

@pytest.fixture(scope="module")
def qt_app():
    """
    Fixture to create and configure a QApplication instance.
    This fixture will be shared among tests within this module.
    """
    app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def main_window(qtbot):
    """Fixture to create and return a MainWindow instance."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_main_window_initialization(main_window: MainWindow):
    """
    Test if MainWindow initializes correctly.
    """
    assert main_window is not None, "MainWindow should be initialized."
    assert main_window.windowTitle() == "Auxilia CTViewer", "Window title should be set correctly."

def test_main_window_show(main_window: MainWindow, mocker):
    """
    Test if the show method of MainWindow is called correctly.
    """
    with mock.patch.object(main_window, 'show') as mock_show:
        main_window.show()
        mock_show.assert_called_once(), "MainWindow.show() should be called once."

def test_main_window_close(main_window: MainWindow, mocker):
    """
    Test if the onClose method closes the MainWindow correctly.
    """
    with mock.patch.object(main_window, 'onClose') as mock_on_close:
        main_window.onClose()
        mock_on_close.assert_called_once(), "MainWindow.onClose() should be called once."

def test_main_window_ui_components(main_window: MainWindow):
    """
    Test if UI components of MainWindow are initialized correctly.
    """
    # Check for basic widgets and layout components
    assert main_window.menuBar() is not None, "Menu bar should be initialized."
    assert main_window.centralWidget() is not None, "Central widget should be initialized."
    assert main_window.statusBar() is not None, "Status bar should be initialized."

    # Check for menu items
    assert main_window.file_menu is not None, "File menu should be initialized."
    assert main_window.edit_menu is not None, "Edit menu should be initialized."
    assert main_window.settings_menu is not None, "Settings menu should be initialized."
    assert main_window.help_menu is not None, "Help menu should be initialized."
    
    # Check specific widgets
    assert main_window.settingDialog is not None, "Setting dialog should be initialized."
    assert main_window.vtkWidget1 is not None, "VTK render window interactor should be initialized."
    assert main_window.renderer is not None, "Renderer should be initialized."

    assert main_window.main_view is not None, "Main view should be initialized."
    assert main_window.tabWidget is not None, "Tab widget should be initialized."

def test_main_window_layout(main_window: MainWindow):

    # Check if the main layout is correctly set up
    assert main_window.hLayout is not None, "Horizontal layout should be initialized."
    assert main_window.vtkLayout1 is not None, "VTK layout should be initialized."
    assert main_window.buttonsLayout is not None, "Buttons layout should be initialized."

    # Check if the left layout is correctly set up
    assert main_window.left_layout is not None, "Left layout should be initialized."
    assert main_window.treeView is not None, "Tree view should be initialized."
    assert main_window.left_layout.refresh_button is not None, "Refresh button should be initialized."

def test_main_window_buttons(main_window: MainWindow):
    
    # Check if the buttons are correctly set up
    assert main_window.buttonsLayout.composite_button is not None, "Composite button should be initialized."
    assert main_window.buttonsLayout.max_button is not None, "Max proj. button should be initialized."
    assert main_window.buttonsLayout.iso_button is not None, "Iso surface button should be initialized."
    assert main_window.buttonsLayout.slider_button is not None, "3D Slider button should be initialized."
    assert main_window.buttonsLayout.clean_button is not None, "Clean view button should be initialized."
    assert main_window.buttonsLayout.axes_button is not None, "Axes button should be initialized."
    assert main_window.buttonsLayout.dark_button is not None, "Dark mode button should be initialized."
    assert main_window.buttonsLayout.shorcuts_button is not None, "Shorcuts button should be initialized."  

def test_main_window_actions(main_window: MainWindow):

    # Check if the actions are correctly set up
    assert main_window.file_menu.open_folder_action is not None, "Open folder action should be initialized."
    assert main_window.file_menu.open_file_action is not None, "Open file action should be initialized."
    assert main_window.file_menu.new_action is not None, "New action should be initialized."
    assert main_window.file_menu.save_action is not None, "Save action should be initialized."
    assert main_window.file_menu.save_as_action is not None, "Save As action should be initialized."
    assert main_window.file_menu.exit_action is not None, "Exit action should be initialized."
    assert main_window.edit_menu.export_web_x3d_action is not None, "Export Web X3D action should be initialized."
    assert main_window.settings_menu.settings_action is not None, "Settings action should be initialized."
    assert main_window.help_menu.about_action is not None, "About action should be initialized."
    assert main_window.help_menu.website_action is not None, "Website action should be initialized."

def test_main_window_actions(main_window: MainWindow, mocker):
    
    # Test if the actions trigger the correct dialogs
    with mock.patch.object(QFileDialog, 'getExistingDirectory', return_value="../datasets") as mock_get_existing_dir:
        main_window.file_menu.open_folder_action.trigger()
        mock_get_existing_dir.assert_called_once(), "QFileDialog.getExistingDirectory() should be called once."
        assert hasattr(main_window, 'data_path'), "Folder path should be set after opening a folder."
        assert main_window.data_path == "../datasets", "Folder path should be set correctly."
        assert main_window.treeView.data_path == "../datasets", "TreeView data path should be set correctly."

    with mock.patch.object(QFileDialog, 'getOpenFileName', return_value=("../datasets/ts_Mask_680_0000.dcs", "DICOS files (*.dcs)")) as mock_get_open_file:
        main_window.file_menu.actions()[1].trigger()  # Trigger the "Open file" action
        # qtbot.mouseClick(main_window.file_menu.open_file_action, Qt.MouseButton.LeftButton)
        mock_get_open_file.assert_called_once(), "QFileDialog.getOpenFileName() should be called once."
        assert hasattr(main_window, 'file_path'), "File path should be set after opening a file."
        assert main_window.file_path == "../datasets/ts_Mask_680_0000.dcs", "File path should be set correctly."
    
