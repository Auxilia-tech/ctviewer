from vedo import Volume

from .callbacks import RendererCallbacks

class IsoSurfer():
    """
    A class representing an isosurface renderer.

    Attributes:
        volume (Volume): The volume data to render.
        isovalue (float): The isovalue for the isosurface.
        sliderpos (int): The position of the slider.
        delayed (bool): Whether to delay the rendering.
        callbacks (RendererCallbacks): The callbacks for the renderer.
        on (bool): Whether the renderer is active.

    Methods:
        build(): Builds the isosurface renderer.
        update_isovalue(value): Updates the isovalue of the renderer.
        get_modules(): Returns the modules of the renderer.
        get_addons(): Returns the addons of the renderer.
        get_sliders(): Returns the sliders of the renderer.
        get_isovalue(): Returns the current isovalue of the renderer.
        activate(): Activates the renderer.
        deactivate(): Deactivates the renderer.
        is_active(): Checks if the renderer is active.
    """

    def __init__(self, volume:Volume, isovalue=None, sliderpos=0, delayed=True, callbacks:RendererCallbacks=None):
        self.volume = volume
        self.isovalue = isovalue
        self.sliderpos = sliderpos
        self.delayed = delayed
        self.callbacks = callbacks
        self.on = False

    def build(self):
        """Build the isosurface renderer for the current volume.

        The isosurface renderer is built using a slider to control the isovalue.
        Important : The mode should be set to 5 for isosurface rendering.

        """
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
        """Update the isovalue of the renderer.

        Args:
            value (float): The new isovalue.
        """
        self.isovalue = value
        self.s0.GetRepresentation().SetValue(value)
        self.volume.properties.GetIsoSurfaceValues().SetValue(0, value)

    def check_volume(self):
        """Check if the volume is valid."""
        if not hasattr(self.volume, "properties"): return False
        if self.volume.dimensions()[2] < 3: return False
        return True
    
    def get_modules(self):
        """Get the modules of the renderer."""
        return [self.s0]
    
    def get_addons(self):
        """Get the addons of the renderer (if any)."""
        return [self.s0]
    
    def get_sliders(self):
        """Get the sliders of the renderer."""
        return [self.s0]
    
    def get_isovalue(self):
        """Get the current isovalue of the renderer."""
        return self.isovalue
    
    def activate(self):
        """Activate the renderer."""
        if not self.check_volume(): return
        self.volume.mode(5)
        self.volume.alpha(1)
        if hasattr(self, "s0") and not self.on:
            for s in self.get_sliders():
                s.on()
        elif not hasattr(self, "s0"):
            self.build()
        self.on = True
    
    def deactivate(self):
        """Turn off the renderer and remove the addons."""
        if self.on:
            for s in self.get_sliders():
                s.off()
            self.on = False

    def is_active(self):
        """Check if the renderer is active."""
        return self.on