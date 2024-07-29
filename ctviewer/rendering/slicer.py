from vedo import Volume, np, mag, build_lut
from ctviewer.rendering.callbacks import RendererCallbacks

class Slicer():
    def __init__(self, volume:Volume, ogb, callbacks:RendererCallbacks):
        self.volume = volume
        self.cx, self.cy, self.cz = "dr", "dg", "db" # colors for the sliders
        self.la, self.ld = 0.7, 0.3  # ambient, diffuse
        self.clamp = True
        self.slider_cmap = build_lut(ogb, vmin=1024, vmax=16384, below_color='white',
                                     above_color='blue', nan_color='black', interpolate=1)
        self.callbacks = callbacks
        self.on = False

    def build(self):
        self.volume.mode(1)
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
            # mean  of the logscale plot
            meanlog = np.sum(np.multiply(edg[:-1], logdata)) / np.sum(logdata)
            self.rmax = min(self.rmax, meanlog + (meanlog - self.rmin) * 0.9)
            self.rmin = max(self.rmin, meanlog - (self.rmax - meanlog) * 0.9)
            print(f"scalar range clamped to range: ( {(self.rmin, 3)} {(self.rmax, 3)} ")
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
            self.callbacks.remove("XSlice")  # removes the old one
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
            t=self.box.diagonal_size() / mag(self.box.xbounds()) * 0.6,
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
            t=self.box.diagonal_size() / mag(self.box.ybounds()) * 0.6,
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
            t=self.box.diagonal_size() / mag(self.box.zbounds()) * 0.6,
            c=self.cz,
            show_value=False,
        )
    
    def get_modules(self):
        return [self.yslider, self.xslider, self.zslider]
    
    def get_addons(self):
        return ["ZSlice", "YSlice", "XSlice", self.box]
    
    def get_sliders(self):
        return [self.yslider, self.xslider, self.zslider]
    
    def is_active(self):
        return self.on
    
    def activate(self, clamp=True):
        self.clamp = clamp if clamp is not None else self.clamp
        if hasattr(self, "yslider") and not self.on:
            for s in self.get_sliders():
                s.on()
        elif not hasattr(self, "yslider"):
            self.build()
        self.on = True

    def deactivate(self):
        for s in self.get_sliders():
            s.off()
        self.callbacks.remove(self.get_addons())
        self.on = False