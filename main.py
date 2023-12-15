import sys
import gc
from PyQt5 import QtWidgets, Qt, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Volume

from utils.renderer import CustomIsosurfaceBrowser, CustomRayCastPlotter
from utils.viewer import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.vtkWidget1 = QVTKRenderWindowInteractor(self)
        self.vtkLayout1.addWidget(self.vtkWidget1)

        self.mode_button = QtWidgets.QPushButton("Mode")
        self.mode_button.setToolTip("Change volume Mode")
        self.mode_button.clicked.connect(self.onClick_mode)
        self.mode_button.setFixedSize(100, 60)
        self.vtkLayout1.addWidget(self.mode_button)

        self.vtkWidget2 = QVTKRenderWindowInteractor(self)
        self.vtkLayout2.addWidget(self.vtkWidget2)

    def update_volume(self):
        if not self.first_load:
            # Clear the plotter and close it to release the memory
            self.plt1.clear()
            self.plt2.clear()
            gc.collect()
            print('gc.collect()')
            self.vol1._update(self.volume_path)
            self.vol2._update(self.volume_path)
        else:
            self.vol1 = Volume(self.volume_path)
            self.vol2 = self.vol1.copy()
            # Apply shifting
            volume_array = self.vol1.tonumpy()
            add_value = 600
            orange_value = 2600
            green_value = 3600
            blue_value = 5500
            # volume_array[(volume_array <= 1200)] = 0
            volume_array[(volume_array >= 1200)] += add_value

            self.vol1.modified()
            # Apply color mapping
            self.vol1.color([(orange_value + add_value, (244, 102, 27)), (green_value + add_value, (0, 255, 0)),
                            (blue_value + add_value, (0, 0, 127))])
            self.vol1.alpha([(orange_value, 1), (green_value + add_value, 0.7), (blue_value + add_value, 0.7)])
            self.plt1 = CustomRayCastPlotter(self.vol1.mode(1), bg='white', bg2='white',
                                             axes=7, qt_widget=self.vtkWidget1)

            # self.id2 = self.plt1.add_callback("key press", self.onKeypress)
            self.plt2 = CustomIsosurfaceBrowser(self.vol2, use_gpu=True, isovalue=1350, qt_widget=self.vtkWidget2)
            self.plt1.show(viewup="z")
            self.plt2.show(axes=7, bg2='lb')
            self.first_load = False

    @Qt.pyqtSlot()
    def onClick_mode(self):
        if self.volume_path is not None:
            s = self.vol1.mode()
            snew = (s + 1) % 2
            self.vol1.mode(snew)
            self.plt1.render()
            if snew == 0:
                self.plt1.w0.value = 0.01
            else:
                self.plt1.w0.value = 1
            self.plt1.setOTF()
            self.plt1.bum.status(snew)

    def onClose(self):
        self.vtkWidget1.close()

    def onKeypress(self, evt):
        print("You have pressed key:", evt.keypress)
        if evt.keypress == 'q':
            sys.exit(0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose)
    app.setWindowIcon(QtGui.QIcon('icons/auxilia_tech_logo.jpeg'))
    window.show()
    sys.exit(app.exec_())
