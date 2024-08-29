from typing import List

import vedo
from vedo import Volume, np

from . import RendererCallbacks

class Slicer():
    """
    Generate a rendering window with slicing planes for the input Volume.
    """

    def __init__(self, volume:Volume, ogb:List, callbacks:RendererCallbacks, clamp:bool=True):
        """
        Initialize the slicer with the input volume and callbacks object.

        Parameters
        ----------
        volume : Volume
            The input volume to be sliced.
        ogb : list
            Oranges, greens, and blues for the opacity transfer function.
        callbacks : RendererCallbacks
            The callbacks object to which the slicer will be attached.
        clamp : bool, optional
            Whether to clamp the scalar range to reduce the effect of tails in color mapping.
        """

        self.volume = volume
        self.callbacks = callbacks
        self.clamp = clamp
        self.ogb = ogb # Oranges, greens, and blues for the opacity transfer function
        self.cx, self.cy, self.cz = "dr", "dg", "db" # colors for the sliders
        self.la, self.ld = 0.7, 0.3  # Ambient, Diffuse
        # Build vtkLookupTable object that can be fed into cmap() method.
        self.slider_cmap = vedo.build_lut(ogb, vmin=1024, vmax=16384, below_color='white',
                                     above_color='blue', nan_color='black', interpolate=1)
        self.on = False

    def build(self):
        """ Build the slicer with the input volume. Mode 1 by default. """
        self.dims = self.volume.dimensions()
        self.data = self.volume.pointdata[0]
        self.rmin, self.rmax = self.volume.scalar_range()

        if np.sum(self.callbacks.background()) < 1.5:
            self.cx, self.cy, self.cz = "lr", "lg", "lb"
        self.box = self.volume.box().alpha(0.2)
        self.callbacks.add(self.box)

        if self.clamp:
            hdata, edg = np.histogram(self.data, bins=20)
            logdata = np.log(hdata + 1)
            # mean of the logscale plot
            meanlog = np.sum(np.multiply(edg[:-1], logdata)) / np.sum(logdata)
            self.rmax = min(self.rmax, meanlog + (meanlog - self.rmin) * 0.9)
            self.rmin = max(self.rmin, meanlog - (self.rmax - meanlog) * 0.9)
        self.cmap_slicer = self.slider_cmap
        self.current_i = None
        self.current_j = int(self.dims[1] / 1.5)
        self.current_k = None
        self.xslice = None
        self.yslice = None
        self.zslice = None
        self.yslice = self.volume.yslice(
            self.current_j).lighting("", self.la, self.ld, 0)
        self.yslice.name = "YSlice"
        self.yslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
        self.callbacks.add(self.yslice)

        def slider_function_x(widget, event):
            i = int(self.xslider.value)
            if i == self.current_i:
                return
            self.current_i = i
            self.xslice = self.volume.xslice(i).lighting("", self.la, self.ld, 0)
            self.xslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.xslice.name = "XSlice"
            self.callbacks.remove("XSlice")  # Removes the old one
            if 0 < i < self.dims[0]:
                self.callbacks.add(self.xslice)
            self.callbacks.render()

        def slider_function_y(widget, event):
            j = int(self.yslider.value)
            if j == self.current_j:
                return
            self.current_j = j
            self.yslice = self.volume.yslice(
                j).lighting("", self.la, self.ld, 0)
            self.yslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.yslice.name = "YSlice"
            self.callbacks.remove("YSlice")
            if 0 < j < self.dims[1]:
                self.callbacks.add(self.yslice)
            self.callbacks.render()

        def slider_function_z(widget, event):
            k = int(self.zslider.value)
            if k == self.current_k:
                return
            self.current_k = k
            self.zslice = self.volume.zslice(
                k).lighting("", self.la, self.ld, 0)
            self.zslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.zslice.name = "ZSlice"
            self.callbacks.remove("ZSlice")
            if 0 < k < self.dims[2]:
                self.callbacks.add(self.zslice)
            self.callbacks.render()
        # 3d sliders attached to the axes bounds
        bs = self.box.bounds()
        self.xslider = self.callbacks.add_slider3d(
            slider_function_x,
            pos1=(bs[0], bs[2], bs[4]),
            pos2=(bs[1], bs[2], bs[4]),
            xmin=0,
            xmax=self.dims[0],
            t=self.box.diagonal_size() / vedo.mag(self.box.xbounds()) * 0.6,
            c=self.cx,
            show_value=False,
        )
        self.xslider.name = "3Dxslider"
        self.yslider = self.callbacks.add_slider3d(
            slider_function_y,
            pos1=(bs[1], bs[2], bs[4]),
            pos2=(bs[1], bs[3], bs[4]),
            xmin=0,
            xmax=self.dims[1],
            value=int(self.dims[1] / 1.5),
            t=self.box.diagonal_size() / vedo.mag(self.box.ybounds()) * 0.6,
            c=self.cy,
            show_value=False,
        )
        self.zslider = self.callbacks.add_slider3d(
            slider_function_z,
            pos1=(bs[0], bs[2], bs[4]),
            pos2=(bs[0], bs[2], bs[5]),
            xmin=0,
            xmax=self.dims[2],
            value=self.dims[2],
            t=self.box.diagonal_size() / vedo.mag(self.box.zbounds()) * 0.6,
            c=self.cz,
            show_value=False,
        )
    
    def check_volume(self):
        """Check if the volume is valid."""
        if not hasattr(self.volume, "properties"): return False
        if self.volume.dimensions()[2] < 3: return False
        return True
    
    def get_modules(self):
        """ Get the slicer modules. """
        return [self.yslider, self.xslider, self.zslider]
    
    def get_addons(self):
        """ Get the slicer addons. """
        return [self.xslice, self.yslice, self.zslice, self.box]
    
    def get_sliders(self):
        """ 
        Get the slicer sliders. 
        Used for activation and deactivation.
        """
        return [self.yslider, self.xslider, self.zslider]
    
    def is_active(self):
        """ Check if the slicer is active. """
        return self.on
    
    def activate(self, clamp=True):
        """
        Activate the slicer with the input volume.
        If the slicer is already active, the sliders will be turned on again.
        If clamp is set to True, the scalar range will be clamped to reduce the effect of tails in color mapping.

        Parameters
        ----------
        clamp : bool, optional
            Whether to clamp the scalar range to reduce the effect of tails in color
            mapping. Default is True
        """
        if not self.check_volume(): return
        self.volume.mode(1)
        self.clamp = clamp if clamp is not None else self.clamp
        if hasattr(self, "yslider") and not self.on:
            for s in self.get_sliders():
                s.on()
            self.callbacks.add(self.get_addons())
        elif not hasattr(self, "yslider"):
            self.build()
        self.on = True

    def deactivate(self):
        """ Deactivate the slicer. """
        for s in self.get_sliders():
            s.off()
        self.callbacks.remove(self.get_addons())
        self.on = False