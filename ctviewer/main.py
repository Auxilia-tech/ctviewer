import sys

from PyQt6 import QtWidgets

from ctviewer import MainWindow

class CtViewer():
    """
    The CtViewer class represents a viewer for CT scans.

    Attributes:
        mainWindow (MainWindow): The main window of the viewer.

    Methods:
        show(): Shows the main window and the renderer.
        onClose(): Closes the renderer and the main window.
    """

    def __init__(self):
        """
        Initializes a new instance of the class.
        """
        self.mainWindow = MainWindow()

    def show(self):
        """
        Shows the main window and the renderer.
        """
        self.mainWindow.show()
        self.mainWindow.renderer.show()

    def onClose(self):
        """
        Closes the renderer and the main window.
        """
        self.mainWindow.renderer.onClose()
        self.mainWindow.onClose()
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CtViewer()
    app.aboutToQuit.connect(window.onClose)
    window.show()
    sys.exit(app.exec())
