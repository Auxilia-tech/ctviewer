import sys

from PyQt5 import QtWidgets, QtGui

from ctviewer.gui.main_window import MainWindow

class CtViewer():
    def __init__(self):
        self.mainWindow = MainWindow()

    def show(self):
        self.mainWindow.show()
        self.mainWindow.renderer.show()

    def onClose(self):
        self.mainWindow.renderer.onClose()
        self.mainWindow.onClose()
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CtViewer()
    app.aboutToQuit.connect(window.onClose)
    app.setWindowIcon(QtGui.QIcon('icons/auxilia_tech_logo.jpeg'))
    window.show()
    sys.exit(app.exec_())
