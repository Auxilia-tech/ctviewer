from vedo import Image
from .callbacks import RendererCallbacks

class ImageViewer():
    def __init__(self, image:Image, callbacks:RendererCallbacks):
        self.image = image
        self.title = 'Image Viewer'
        self.callbacks = callbacks
        self.on = False

    def activate(self):
        # self.image.enhance()#.cmap("jet")
        self.callbacks.add(self.image)
        self.callbacks.reset_camera()
        self.on = True

    def deactivate(self):
        self.callbacks.remove(self.image)
        self.on = False

    def is_active(self):
        return self.on