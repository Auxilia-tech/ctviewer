from vedo import Plotter
from vedo.pyplot import CornerHistogram
from vedo.colors import get_color
import vedo


class CustomPlotter(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, volume,
                 isovalue=None,
                 c=None,
                 alpha=1,
                 use_gpu=False,
                 delayed=False,
                 sliderpos=4,
                 **kwargs):

        super().__init__(**kwargs)
        # Iso seufer browser
        self.use_gpu = use_gpu
        self.c = c
        self.alpha = alpha
        self.isovalue = isovalue
        self.delayed = delayed
        self.sliderpos = sliderpos

        # Ray cast render
        self.alphaslider0 = 1
        self.alphaslider1 = 0.7
        self.alphaslider2 = 1

        self.properties = volume.properties
        img = volume.dataset
        if volume.dimensions()[2] < 3:
            vedo.logger.error("RayCastPlotter: not enough z slices.")
            raise RuntimeError

        self.smin, self.smax = img.GetScalarRange()
        self.x0alpha = self.smin + (self.smax - self.smin) * 0.25
        self.x1alpha = self.smin + (self.smax - self.smin) * 0.5
        self.x2alpha = self.smin + (self.smax - self.smin) * 1.0

        # Ncols = len(cmaps)
        self.csl = (0.9, 0.9, 0.9)
        if sum(get_color(self.renderer.GetBackground())) > 1.5:
            self.csl = (0.1, 0.1, 0.1)
        # alpha sliders
        # Create transfer mapping scalar value to opacity
        self.opacityTransferFunction = self.properties.GetScalarOpacity()
        self.setOTF()

        def sliderA0(widget, event):
            self.alphaslider0 = widget.GetRepresentation().GetValue()
            self.setOTF()
        self.w0 = self.add_slider(sliderA0, 0, 1, value=self.alphaslider0, pos=[
                                  (0.8, 0.1), (0.8, 0.26)], c=self.csl, show_value=0)

        def sliderA1(widget, event):
            self.alphaslider1 = widget.GetRepresentation().GetValue()
            self.setOTF()
        self.add_slider(sliderA1, 0, 1, value=self.alphaslider1, pos=[
                        (0.85, 0.1), (0.85, 0.26)], c=self.csl, show_value=0)

        def sliderA2(widget, event):
            self.alphaslider2 = widget.GetRepresentation().GetValue()
            self.setOTF()
        w2 = self.add_slider(sliderA2, 0, 1, value=self.alphaslider2, pos=[
                             (0.90, 0.1), (0.90, 0.26)], c=self.csl, show_value=0, title="Opacity levels")
        # w2.GetRepresentation().SetTitleHeight(0.014)
        # add histogram of scalar
        plot = CornerHistogram(volume, bins=25, logscale=1, c=(0.7, 0.7, 0.7), bg=(
            0.7, 0.7, 0.7), pos=(0.76, 0.065), lines=True, dots=False, nmax=3.1415e06)
        plot.GetPosition2Coordinate().SetValue(0.197, 0.20, 0)
        plot.GetXAxisActor2D().SetFontFactor(0.7)
        plot.GetProperty().SetOpacity(0.5)
        # iso val
        isovals = volume.properties.GetIsoSurfaceValues()
        isovals.SetValue(0, self.isovalue)
        scrange = volume.scalar_range()
        delta = scrange[1] - scrange[0]
        delta = scrange[1] - scrange[0]
        if not delta:
            return
        if self.isovalue is None:
            self.isovalue = delta / 3.0 + scrange[0]

        def slider_isovalue(widget, event):
            value = widget.GetRepresentation().GetValue()
            isovals.SetValue(0, value)

        self.add_slider(
            slider_isovalue,
            scrange[0] + 0.02 * delta,
            scrange[1] - 0.02 * delta,
            value=self.isovalue,
            pos=self.sliderpos,
            title="scalar value",
            show_value=True,
            delayed=self.delayed,
        )
        self.add([plot, volume])

    def setOTF(self):
        self.opacityTransferFunction.RemoveAllPoints()
        self.opacityTransferFunction.AddPoint(self.smin, 0.0)
        self.opacityTransferFunction.AddPoint(self.smin + (self.smax - self.smin) * 0.1, 0.0)
        self.opacityTransferFunction.AddPoint(self.x0alpha, self.alphaslider0)
        self.opacityTransferFunction.AddPoint(self.x1alpha, self.alphaslider1)
        self.opacityTransferFunction.AddPoint(self.x2alpha, self.alphaslider2)
