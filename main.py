import sys

from PyQt5 import QtWidgets, QtGui

from utils import CustomPlotter, load_volume, load_mask
from utils import Ui_MainWindow


class MainWindow(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self, parent)
        self.setupUi(self)

        # Set OGB color map
        self.ogb_cmap = [int(2600), int(3600), int(5500)]
        self.alpha = [(0, 1), (self.ogb_cmap[0], 1), (self.ogb_cmap[1], 0.7), (self.ogb_cmap[2], 0.7)]

    def update_volume(self):
        if not self.first_load:
            load_volume(self.volume_path, self.first_load, self.vol)
        else:
            self.vol = load_volume(self.volume_path, self.first_load)

        # Apply color mapping
            self.ogb = [(0, [244, 102, 27]), (self.ogb_cmap[0], [244, 102, 27]), (self.ogb_cmap[1],
                                                                                  [0, 255, 0]), (self.ogb_cmap[2], [0, 0, 127])]
            self.vol.color(self.ogb)

            self.vol.alpha(self.alpha)
            self.plt = CustomPlotter(self.vol, bg='white', bg2='white', ogb=self.ogb, alpha=self.alpha, isovalue=1350,
                                     axes=7, qt_widget=self.vtkWidget1)
            self.plt.show(viewup="z")

        self.first_load = False
        self.plt.render()

    def update_mask(self):
        if len(self.mask_files) > 0:
            self.loaded_mask_id = 0 if self.loaded_mask_id is None else self.loaded_mask_id + 1
            if self.loaded_mask_id >= len(self.mask_files):
                self.remove_mask()
            elif self.loaded_mask is None:
                self.loaded_mask = load_mask(self.loaded_mask, self.mask_files, self.loaded_mask_id)
                self.plt.add(self.loaded_mask.color('red'))
            else:
                load_mask(self.loaded_mask, self.mask_files, self.loaded_mask_id)
            self.update_text_button_masks()
            self.plt.render()

    def remove_mask(self):
        self.plt.remove(self.loaded_mask)
        self.loaded_mask = None
        self.loaded_mask_id = None
        self.plt.render()

    def onClose(self):
        self.vtkWidget1.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose)
    app.setWindowIcon(QtGui.QIcon('icons/auxilia_tech_logo.jpeg'))
    window.show()
    sys.exit(app.exec_())
