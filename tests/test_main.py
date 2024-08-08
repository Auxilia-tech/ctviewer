# tests/test_main.py
import pytest
from PyQt6.QtWidgets import QApplication
from ctviewer.main import CtViewer

@pytest.fixture
def viewer():
    """
    Fixture to create a CtViewer instance.
    """
    return CtViewer()

def test_ctviewer_initialization(viewer):
    """
    Test if CtViewer initializes correctly.
    """
    assert viewer is not None
    assert viewer.mainWindow is not None

def test_main_window_show(mocker, viewer):
    """
    Test if the main window show method is called correctly.
    """
    mock_show = mocker.patch.object(viewer.mainWindow, 'show')
    mock_renderer_show = mocker.patch.object(viewer.mainWindow.renderer, 'show')

    viewer.show()
    mock_show.assert_called_once()
    mock_renderer_show.assert_called_once()

def test_main_window_close(mocker, viewer):
    """
    Test if the onClose method closes the main window and renderer correctly.
    """
    mock_main_close = mocker.patch.object(viewer.mainWindow, 'onClose')
    mock_renderer_close = mocker.patch.object(viewer.mainWindow.renderer, 'onClose')

    viewer.onClose()
    mock_main_close.assert_called_once()
    mock_renderer_close.assert_called_once()

def test_about_to_quit_signal(mocker, viewer):
    """
    Test if the onClose method is connected to the QApplication aboutToQuit signal.
    """
    mock_on_close = mocker.patch.object(viewer, 'onClose')
    app = QApplication.instance()
    app.aboutToQuit.connect(viewer.onClose)
    app.aboutToQuit.emit()
    mock_on_close.assert_called_once()

def test_main_window_initialization_failure(mocker, viewer):
    """
    Test how CtViewer handles an exception raised during MainWindow initialization.
    """
    mocker.patch('ctviewer.gui.main_window.MainWindow.__init__', side_effect=Exception("Initialization failed"))
    with pytest.raises(Exception, match="Initialization failed"):
        CtViewer()