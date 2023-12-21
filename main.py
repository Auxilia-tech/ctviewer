import sys

from PyQt5 import QtWidgets, QtGui
from vedo import Volume

from utils.renderer import CustomPlotter
from utils.viewer import Ui_MainWindow


class MainWindow(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self, parent)
        self.setupUi(self)

        # Set OGB color map
        self.ogb_cmap = [int(2600), int(3600), int(5500)]

    def update_volume(self):
        if not self.first_load:
            self.vol._update(Volume(self.volume_path).dataset)
        else:
            self.vol = Volume(self.volume_path)

        # Apply color mapping
            self.vol.color([(self.ogb_cmap[0], (244, 102, 27)), (self.ogb_cmap[1], (0, 255, 0)),
                            (self.ogb_cmap[2], (0, 0, 127))])
            self.vol.alpha([(self.ogb_cmap[0], 1), (self.ogb_cmap[1], 0.7), (self.ogb_cmap[2], 0.7)])
            self.plt = CustomPlotter(self.vol.mode(1), bg='white', bg2='white', use_gpu=True, isovalue=1350,
                                     axes=7, qt_widget=self.vtkWidget1)
            self.plt.show(viewup="z")

        self.first_load = False
        self.plt.render()
        self.plt.setOTF()

    def update_mask(self):
        if len(self.mask_files) > 0:
            self.loaded_mask_id = 0 if self.loaded_mask_id is None else self.loaded_mask_id + 1
            if self.loaded_mask_id >= len(self.mask_files):
                self.remove_mask()
            elif self.loaded_mask is None:
                self.loaded_mask = Volume(self.mask_files[self.loaded_mask_id]).origin((0,0,0))
                self.plt.add(self.loaded_mask.color('red'))
            else:
                self.loaded_mask._update(Volume(self.mask_files[self.loaded_mask_id]).dataset)
            self.update_text_button_masks()
            self.plt.render()
            self.plt.setOTF()

    def set_mode(self, mode):
        self.vol.mode(mode)
        if mode == 5:
            self.vol.alpha(1)
        self.plt.render()
        self.plt.w0.value = 0.1 if mode == 0 else 1
        self.plt.alphaslider0 = 0.1 if mode == 0 else 1
        self.plt.setOTF()

    def remove_mask(self):
        self.plt.remove(self.loaded_mask)
        self.loaded_mask = None
        self.loaded_mask_id = None
        self.plt.render()
        self.plt.setOTF()

    def onClose(self):
        self.vtkWidget1.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose)
    app.setWindowIcon(QtGui.QIcon('icons/auxilia_tech_logo.jpeg'))
    window.show()
    sys.exit(app.exec_())
