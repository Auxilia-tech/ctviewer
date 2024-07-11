import sys

from PyQt5 import QtWidgets, QtGui
from utils import Viewer, Renderer

class MainWindow(Viewer, Renderer):

    def __init__(self, parent=None):
        Viewer.__init__(self, parent)
        self.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose)
    app.setWindowIcon(QtGui.QIcon('icons/auxilia_tech_logo.jpeg'))
    window.show()
    sys.exit(app.exec_())
