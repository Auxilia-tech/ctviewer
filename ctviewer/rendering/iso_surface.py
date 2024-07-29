from vedo import Volume
from ctviewer.rendering.callbacks import RendererCallbacks

class IsoSurfer():
    def __init__(self, volume:Volume, isovalue=None, sliderpos=0, delayed=True, callbacks:RendererCallbacks=None):
        self.volume = volume
        self.isovalue = isovalue
        self.sliderpos = sliderpos
        self.delayed = delayed
        self.callbacks = callbacks
        self.on = False

    def build(self):
        self.volume.mode(5)
        self.volume.alpha(1)
        isovals = self.volume.properties.GetIsoSurfaceValues()
        if self.isovalue is None:
            self.isovalue = delta / 3.0 + scrange[0]
        isovals.SetValue(0, self.isovalue)
        scrange = self.volume.scalar_range()
        delta = scrange[1] - scrange[0]
        delta = scrange[1] - scrange[0]
        if not delta:
            return

        def slider_isovalue(widget, event):
            value = widget.GetRepresentation().GetValue()
            isovals.SetValue(0, value)

        self.s0 = self.callbacks.add_slider(
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

    def update_isovalue(self, value):
        self.isovalue = value
        self.s0.GetRepresentation().SetValue(value)
        self.volume.properties.GetIsoSurfaceValues().SetValue(0, value)
    
    def get_modules(self):
        return [self.s0]
    
    def get_addons(self):
        return [self.s0]
    
    def get_sliders(self):
        return [self.s0]
    
    def get_isovalue(self):
        return self.isovalue
    
    def activate(self):
        if hasattr(self, "s0") and not self.on:
            for s in self.get_sliders():
                s.on()
        elif not hasattr(self, "s0"):
            self.build()
    
    def deactivate(self):
        if self.on:
            for s in self.get_sliders():
                s.off()
            self.on = False

    def is_active(self):
        return self.on