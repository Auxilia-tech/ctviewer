# tests/test_main.py
import pytest
from PyQt6.QtWidgets import QApplication
from ctviewer.main import CtViewer
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

def test_ctviewer_initialization(qt_app):
    """
    Test if CtViewer initializes correctly.
    """
    viewer = CtViewer()
    assert viewer is not None
    assert viewer.mainWindow is not None

def test_main_window_show(qt_app, mocker):
    """
    Test if the main window show method is called correctly.
    """
    viewer = CtViewer()
    mock_show = mocker.patch.object(viewer.mainWindow, 'show')
    mock_renderer_show = mocker.patch.object(viewer.mainWindow.renderer, 'show')

    viewer.show()
    mock_show.assert_called_once()
    mock_renderer_show.assert_called_once()

def test_main_window_close(qt_app, mocker):
    """
    Test if the onClose method closes the main window and renderer correctly.
    """
    viewer = CtViewer()
    mock_main_close = mocker.patch.object(viewer.mainWindow, 'onClose')
    mock_renderer_close = mocker.patch.object(viewer.mainWindow.renderer, 'onClose')

    viewer.onClose()
    mock_main_close.assert_called_once()
    mock_renderer_close.assert_called_once()

def test_about_to_quit_signal(qt_app, mocker):
    """
    Test if the onClose method is connected to the QApplication aboutToQuit signal.
    """
    viewer = CtViewer()
    mock_on_close = mocker.patch.object(viewer, 'onClose')
    app = QApplication.instance()
    app.aboutToQuit.connect(viewer.onClose)
    app.aboutToQuit.emit()
    mock_on_close.assert_called_once()

def test_main_window_initialization_failure(qt_app, mocker):
    """
    Test how CtViewer handles an exception raised during MainWindow initialization.
    """
    mocker.patch('ctviewer.gui.main_window.MainWindow.__init__', side_effect=Exception("Initialization failed"))
    with pytest.raises(Exception, match="Initialization failed"):
        CtViewer()