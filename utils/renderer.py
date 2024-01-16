from vedo import Plotter, np, build_lut
from vedo.pyplot import CornerHistogram
from vedo.colors import get_color
from vedo.utils import mag
import vedo


class CustomPlotter(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, volume,
                 isovalue=None,
                 ogb=None,
                 alpha=1,
                 delayed=False,
                 sliderpos=4,
                 **kwargs):

        super().__init__(**kwargs)

        # 3D slider
        self.volume = volume
        self.cx, self.cy, self.cz = "dr", "dg", "db"
        self.la, self.ld = 0.7, 0.3  # ambient, diffuse
        self.slice_mode = False
        self.slider_cmap = build_lut(ogb,
                                     vmin=1200,
                                     vmax=16000,
                                     below_color='white',
                                     above_color='blue',
                                     nan_color='black',
                                     interpolate=False,
                                     )

        # Iso seufer browser
        self.alpha = alpha
        self.isovalue = isovalue
        self.delayed = delayed
        self.sliderpos = sliderpos

        # Ray cast render
        self.ogb = ogb
        self.alphaslider0 = 1
        self.alphaslider1 = 0.7
        self.alphaslider2 = 1

        self.csl = (0.9, 0.9, 0.9)
        if sum(get_color(self.renderer.GetBackground())) > 1.5:
            self.csl = (0.1, 0.1, 0.1)

        self.add([self.volume])
        self.init_ray_cast()

    def init_ray_cast(self, mode=1):
        self.volume.mode(mode)
        self.volume.alpha(self.alpha)
        # Create transfer mapping scalar value to opacity
        self.properties = self.volume.properties
        self.opacityTransferFunction = self.properties.GetScalarOpacity()
        img = self.volume.dataset
        if self.volume.dimensions()[2] < 3:
            vedo.logger.error("RayCastPlotter: not enough z slices.")
            raise RuntimeError
        self.smin, self.smax = img.GetScalarRange()
        self.x0alpha = self.smin + (self.smax - self.smin) * 0.25
        self.x1alpha = self.smin + (self.smax - self.smin) * 0.5
        self.x2alpha = self.smin + (self.smax - self.smin) * 1.0
        self.setOTF()

        def sliderA0(widget, event):
            self.alphaslider0 = widget.GetRepresentation().GetValue()
            self.setOTF()

        def sliderA1(widget, event):
            self.alphaslider1 = widget.GetRepresentation().GetValue()
            self.setOTF()

        def sliderA2(widget, event):
            self.alphaslider2 = widget.GetRepresentation().GetValue()
            self.setOTF()
        # alpha sliders
        self.w0 = self.add_slider(sliderA0, 0, 1, value=self.alphaslider0, pos=[
            (0.8, 0.1), (0.8, 0.26)], c=self.csl, show_value=0)
        self.w1 = self.add_slider(sliderA1, 0, 1, value=self.alphaslider1, pos=[
            (0.85, 0.1), (0.85, 0.26)], c=self.csl, show_value=0)
        self.w2 = self.add_slider(sliderA2, 0, 1, value=self.alphaslider2, pos=[
            (0.90, 0.1), (0.90, 0.26)], c=self.csl, show_value=0, title="Opacity levels")
        # add histogram of scalar
        self.plot = CornerHistogram(self.volume, bins=25, logscale=1, c=(0.7, 0.7, 0.7), bg=(
            0.7, 0.7, 0.7), pos=(0.76, 0.065), lines=True, dots=False, nmax=3.1415e06)
        self.plot.GetPosition2Coordinate().SetValue(0.197, 0.20, 0)
        self.plot.GetXAxisActor2D().SetFontFactor(0.7)
        self.plot.GetProperty().SetOpacity(0.5)
        self.add([self.plot])
        self.setOTF()
        self.render()

    def quit_ray_cast(self):
        self.w0.off()
        self.w1.off()
        self.w2.off()
        self.remove(self.plot)
        self.opacityTransferFunction.RemoveAllPoints()
        self.render()

    def init_iso_surface(self):
        self.volume.mode(5)
        self.volume.alpha(1)
        isovals = self.volume.properties.GetIsoSurfaceValues()
        isovals.SetValue(0, self.isovalue)
        scrange = self.volume.scalar_range()
        delta = scrange[1] - scrange[0]
        delta = scrange[1] - scrange[0]
        if not delta:
            return
        if self.isovalue is None:
            self.isovalue = delta / 3.0 + scrange[0]

        def slider_isovalue(widget, event):
            value = widget.GetRepresentation().GetValue()
            isovals.SetValue(0, value)

        self.s0 = self.add_slider(
            slider_isovalue,
            scrange[0] + 0.02 * delta,
            scrange[1] - 0.02 * delta,
            value=self.isovalue,
            pos=self.sliderpos,
            title="scalar value",
            show_value=True,
            delayed=self.delayed,
        )
        self.s0.name = "s0"
        self.render()

    def quit_iso_surface(self):
        self.s0.off()
        self.render()

    def init_3d_slider(self, clamp=False):
        """
        Initialize a 3d slider with the given parameters.
        """
        self.volume.mode(1)
        self.dims = self.volume.dimensions()
        self.data = self.volume.pointdata[0]
        self.rmin, self.rmax = self.volume.scalar_range()

        if np.sum(self.renderer.GetBackground()) < 1.5:
            self.cx, self.cy, self.cz = "lr", "lg", "lb"
        self.box = self.volume.box().alpha(0.2)
        self.add(self.box)

        if clamp:
            hdata, edg = np.histogram(self.data, bins=50)
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
        self.yslice = self.volume.yslice(self.current_j).lighting("", self.la, self.ld, 0)
        self.yslice.name = "YSlice"
        self.yslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
        self.add(self.yslice)

        def slider_function_x(widget, event):
            i = int(self.xslider.value)
            if i == self.current_i:
                return
            self.current_i = i
            self.xslice = self.volume.xslice(i).lighting("", self.la, self.ld, 0)
            self.xslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.xslice.name = "XSlice"
            self.remove("XSlice")  # removes the old one
            if 0 < i < self.dims[0]:
                self.add(self.xslice)
            self.render()

        def slider_function_y(widget, event):
            j = int(self.yslider.value)
            if j == self.current_j:
                return
            self.current_j = j
            self.yslice = self.volume.yslice(j).lighting("", self.la, self.ld, 0)
            self.yslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.yslice.name = "YSlice"
            self.remove("YSlice")
            if 0 < j < self.dims[1]:
                self.add(self.yslice)
            self.render()

        def slider_function_z(widget, event):
            k = int(self.zslider.value)
            if k == self.current_k:
                return
            self.current_k = k
            self.zslice = self.volume.zslice(k).lighting("", self.la, self.ld, 0)
            self.zslice.cmap(self.cmap_slicer, vmin=self.rmin, vmax=self.rmax)
            self.zslice.name = "ZSlice"
            self.remove("ZSlice")
            if 0 < k < self.dims[2]:
                self.add(self.zslice)
            self.render()
        # 3d sliders attached to the axes bounds
        bs = self.box.bounds()
        self.xslider = self.add_slider3d(
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
        self.yslider = self.add_slider3d(
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
        self.zslider = self.add_slider3d(
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
        self.slice_mode = True
        self.render()

    def quit_3d_slider(self):
        self.yslider.off()
        self.xslider.off()
        self.zslider.off()
        self.remove("ZSlice")
        self.remove("YSlice")
        self.remove("XSlice")
        self.remove(self.box)
        self.render()
        self.slice_mode = False

    def setOTF(self):
        if self.volume.mode() == 5:
            self.opacityTransferFunction.RemoveAllPoints()
        else:
            self.opacityTransferFunction.RemoveAllPoints()
            self.opacityTransferFunction.AddPoint(self.smin, 0.0)
            self.opacityTransferFunction.AddPoint(self.smin + (self.smax - self.smin) * 0.1, 0.0)
            self.opacityTransferFunction.AddPoint(self.x0alpha, self.alphaslider0)
            self.opacityTransferFunction.AddPoint(self.x1alpha, self.alphaslider1)
            self.opacityTransferFunction.AddPoint(self.x2alpha, self.alphaslider2)
