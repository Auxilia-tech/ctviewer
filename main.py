import sys

from PyQt5 import QtWidgets, QtGui

from utils import CustomPlotter, load_volume, load_mask
from utils import Ui_MainWindow


class MainWindow(Ui_MainWindow):

    def __init__(self, parent=None):
        Ui_MainWindow.__init__(self, parent)
        self.setupUi(self)

    def update_volume(self):
        if not self.first_load:
            load_volume(self.volume_path, self.first_load, self.vol, ext=self.ext)
        else:
            self.vol = load_volume(self.volume_path, self.first_load, ext=self.ext)

            # Apply color mapping from user settings
            self.vol.color(self.ogb)

            self.vol.alpha(self.alpha)
            self.plt = CustomPlotter(self.vol, bg='white', bg2='white', ogb=self.ogb, alpha=self.alpha, isovalue=1350,
                                     axes=8, qt_widget=self.vtkWidget1, mask_classes=self.mask_classes)
            self.plt.show(viewup="z")

        self.first_load = False
        self.plt.render()

    def update_mask(self):
        if len(self.mask_files) > 0:
            self.loaded_mask_id = 0 if self.loaded_mask_id is None else self.loaded_mask_id + 1
            if self.loaded_mask_id >= len(self.mask_files):
                self.plt.remove_mask(self)
            elif self.loaded_mask is None:
                self.loaded_mask = load_mask(self.loaded_mask, self.mask_files, self.loaded_mask_id, ext=self.ext)
                self.loaded_mask.color("red").mode(0)
                self.plt.add(self.loaded_mask)
                self.plt.add_flags(self.loaded_mask)
            else:
                load_mask(self.loaded_mask, self.mask_files, self.loaded_mask_id, ext=self.ext)
            self.update_text_button_masks()
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
