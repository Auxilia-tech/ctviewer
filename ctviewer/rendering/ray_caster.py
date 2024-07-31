from typing import Tuple

from vedo import Volume, pyplot

from .callbacks import RendererCallbacks

class RayCaster():
    """
    Generate a rendering window with ray casting for the input Volume.
    """
    def __init__(self, volume:Volume, ogb, alpha, callbacks:RendererCallbacks):
        """
        Initialize the ray caster with the input volume and callbacks object.

        Parameters
        ----------

        volume : Volume
            The input volume to be ray casted.
        ogb : list
            Oranges, greens, and blues for the opacity transfer function.
        alpha : float
            The alpha value for the volume.
        callbacks : RendererCallbacks
            The callbacks object to which the ray caster will be attached.
        """
        self.volume = volume
        self.ogb = ogb
        self.alpha = alpha
        self.callbacks = callbacks
        self.alphasliders_mode_0 = [0.1, 0.4, 1.0]
        self.alphasliders_mode_1 = [0.75, 0.75, 0.9]
        self.on = False
    
    def build(self, volume_mode):
        """
        Build the ray caster with the input volume.
        
        Parameters
        ----------

        volume_mode : int
            The mode of the volume rendering.
        """

        # Create transfer mapping scalar value to opacity
        self.opacityTransferFunction = self.volume.properties.GetScalarOpacity()
        
        self.update_mode(volume_mode)
        
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
        self.w0 = self.callbacks.add_slider(sliderA0, 0, 1, value=self.alphaslider0, pos=[
            (0.8, 0.1), (0.8, 0.26)], c=self.ogb[0][1], show_value=0)
        self.w1 = self.callbacks.add_slider(sliderA1, 0, 1, value=self.alphaslider1, pos=[
            (0.85, 0.1), (0.85, 0.26)], c=self.ogb[1][1], show_value=0)
        self.w2 = self.callbacks.add_slider(sliderA2, 0, 1, value=self.alphaslider2, pos=[
            (0.90, 0.1), (0.90, 0.26)], c=self.ogb[2][1], show_value=0, title="Opacity levels", title_size=0.7)
        
        for w in [self.w0, self.w1, self.w2]:
            w.GetSliderRepresentation().GetSliderProperty().SetOpacity(0.8)
            w.GetSliderRepresentation().GetTubeProperty().SetOpacity(0.2)
        
        # CornerHistogram -> vtki.new("XYPlotActor")
        self.hist = pyplot.CornerHistogram(self.volume, logscale=1, 
                                    c=(0.7, 0.7, 0.7), bg=(0.7, 0.7, 0.7), 
                                    pos=(0.76, 0.065), nmax=3.1415e06)
        self.hist.GetPosition2Coordinate().SetValue(0.197, 0.20, 0)
        self.hist.GetXAxisActor2D().SetFontFactor(0.7)
        self.hist.GetProperty().SetOpacity(0.5)
        self.setOTF()

    def setOTF(self):
        """Set the opacity transfer function."""
        self.opacityTransferFunction.RemoveAllPoints()
        self.smin, self.smax = self.volume.dataset.GetScalarRange()
        self.opacityTransferFunction.AddPoint(self.smin, 0.0)
        self.opacityTransferFunction.AddPoint(self.smin + (self.smax - self.smin) * 0.1, 0.0)
        self.opacityTransferFunction.AddPoint(self.ogb[0][0], self.alphaslider0)
        self.opacityTransferFunction.AddPoint(self.ogb[1][0], self.alphaslider1)
        self.opacityTransferFunction.AddPoint(self.ogb[2][0], self.alphaslider2)

    def update_mode(self, volume_mode:int):
        """
        Update the rendering mode of the volume.

        Parameters
        ----------

        volume_mode : int
            0, composite rendering
            1, maximum projection rendering
            2, minimum projection rendering
            3, average projection rendering
            4, additive mode
        """
        self.volume_mode = volume_mode
        self.volume.mode(volume_mode)
        self.volume.alpha(self.alpha)
        self.update_sliders()
        self.setOTF()

    def update_sliders(self, values:Tuple[float, float, float]=None):
        """Update the sliders of the ray caster."""
        if values:
            self.alphaslider0, self.alphaslider1, self.alphaslider2 = values
        else:
            self.alphaslider0, self.alphaslider1, self.alphaslider2 = self.alphasliders_mode_0 if self.volume_mode == 0 else self.alphasliders_mode_1
        if hasattr(self, 'w0'):
            self.w0.value, self.w1.value, self.w2.value = self.alphaslider0, self.alphaslider1, self.alphaslider2
        
        self.setOTF()

    def check_volume(self):
        """Check if the volume is valid."""
        # if the volume is valid, return True
        if not hasattr(self.volume, 'properties'): return False
        if self.volume.dimensions()[2] < 3: return False
        return True

    def get_modules(self):
        """Get the modules of the ray caster."""
        return [self.hist, self.w0, self.w1, self.w2]
    
    def get_addons(self):
        """Get the addons of the ray caster."""
        return [self.hist]
    
    def get_sliders(self):
        """
        Get the sliders of the ray caster.
        Used for activation and deactivation.
        """
        return [self.w0, self.w1, self.w2]
    
    def activate(self, volume_mode:int=1):
        """ 
        
        Activate the ray caster with the input volume.
        If the ray caster is already active, the sliders will be turned on again.

        Parameters
        ----------

        volume_mode : int
            See update_mode for details.
        """
        if not self.check_volume(): return
        if not hasattr(self, 'opacityTransferFunction') and not self.on:
            self.build(volume_mode)

        else:
            for m in self.get_sliders():
                m.on()

        self.update_mode(volume_mode)
        self.callbacks.add([self.get_addons()])
        self.on = True

    def deactivate(self):
        """ Deactivate the ray caster."""
        if self.on:
            for s in self.get_sliders():
                s.off()
        self.callbacks.remove(self.get_addons())
        self.update_sliders((0.0, 0.0, 0.0))
        self.on = False

    def is_active(self):
        """ Check if the ray caster is active."""
        return self.on