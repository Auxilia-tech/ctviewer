import vedo
from vedo import addons, Volume, Plotter, Flagpost, np, build_lut
from vedo.pyplot import CornerHistogram
from vedo.colors import get_color
from vedo.utils import mag

from scipy.ndimage import label

class CustomPlotter(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, 
                 volume,
                 isovalue=None,
                 ogb=None,
                 alpha=1,
                 delayed=False,
                 sliderpos=4,
                 mask_classes=None,
                 **kwargs):

        super().__init__(**kwargs)

        # 3D slider
        self.volume = volume
        self.ogb = ogb
        self.mask_classes = mask_classes
        self.mask_colors = [
            (val[0], val[1]) for val in mask_classes] if mask_classes is not None else "red"
        self.mask_alpha = [val[2]
                           for val in mask_classes] if mask_classes is not None else 0.5
        # Create dictionary to store the mask classes and their flags from config file
        self.mask_flags = {val[0]: val[3] for val in mask_classes} if mask_classes is not None else None
        self.cx, self.cy, self.cz = "dr", "dg", "db"
        self.la, self.ld = 0.7, 0.3  # ambient, diffuse
        self.slice_mode = False
        self.slider_cmap = build_lut(ogb,
                                     vmin=1024,
                                     vmax=16384,
                                     below_color='white',
                                     above_color='blue',
                                     nan_color='black',
                                     interpolate=1,
                                     )

        # Iso seufer browser
        self.alpha = alpha
        self.isovalue = isovalue
        self.delayed = delayed
        self.sliderpos = sliderpos
        self.s0 = None

        # Ray cast render
        self.ogb = ogb
        self.alphaslider0 = 0.55
        self.alphaslider1 = 0.75
        self.alphaslider2 = 0.9

        self.csl = (0.9, 0.9, 0.9)
        if sum(get_color(self.renderer.GetBackground())) > 1.5:
            self.csl = (0.1, 0.1, 0.1)

        self.yslider = None

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
        self.x0alpha = self.ogb[0][0] # self.smin + (self.smax - self.smin) * 0.25
        self.x1alpha = self.ogb[1][0] # self.smin + (self.smax - self.smin) * 0.5
        self.x2alpha = self.ogb[2][0] # self.smin + (self.smax - self.smin) * 1.0
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
            (0.8, 0.1), (0.8, 0.26)], c=self.ogb[0][1], show_value=0)
        self.w1 = self.add_slider(sliderA1, 0, 1, value=self.alphaslider1, pos=[
            (0.85, 0.1), (0.85, 0.26)], c=self.ogb[1][1], show_value=0)
        self.w2 = self.add_slider(sliderA2, 0, 1, value=self.alphaslider2, pos=[
            (0.90, 0.1), (0.90, 0.26)], c=self.ogb[2][1], show_value=0, title="Opacity levels", title_size=0.7)
        
        for w in [self.w0, self.w1, self.w2]:
            w.GetSliderRepresentation().GetSliderProperty().SetOpacity(0.8)
            w.GetSliderRepresentation().GetTubeProperty().SetOpacity(0.2)
        
        # add histogram of scalar
        self.plot = CornerHistogram(self.volume, bins=20, logscale=1, c=(0.7, 0.7, 0.7), bg=(
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
        if self.s0 is not None:
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
            hdata, edg = np.histogram(self.data, bins=20)
            logdata = np.log(hdata + 1)
            # mean  of the logscale plot
            meanlog = np.sum(np.multiply(edg[:-1], logdata)) / np.sum(logdata)
            self.rmax = min(self.rmax, meanlog + (meanlog - self.rmin) * 0.9)
            self.rmin = max(self.rmin, meanlog - (self.rmax - meanlog) * 0.9)
            print(
                f"scalar range clamped to range: ( {(self.rmin, 3)} {(self.rmax, 3)} ")
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
        self.add(self.yslice)

        def slider_function_x(widget, event):
            i = int(self.xslider.value)
            if i == self.current_i:
                return
            self.current_i = i
            self.xslice = self.volume.xslice(
                i).lighting("", self.la, self.ld, 0)
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
            self.yslice = self.volume.yslice(
                j).lighting("", self.la, self.ld, 0)
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
            self.zslice = self.volume.zslice(
                k).lighting("", self.la, self.ld, 0)
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
        if self.yslider is not None:
            self.yslider.off()
            self.xslider.off()
            self.zslider.off()
            self.remove("ZSlice")
            self.remove("YSlice")
            self.remove("XSlice")
            self.remove(self.box)
        self.slice_mode = False
        self.render()

    def setOTF(self):
        self.opacityTransferFunction.RemoveAllPoints()
        if self.volume.mode() != 5:
            self.opacityTransferFunction.RemoveAllPoints()
            self.opacityTransferFunction.AddPoint(self.smin, 0.0)
            self.opacityTransferFunction.AddPoint(
                self.smin + (self.smax - self.smin) * 0.1, 0.0)
            self.opacityTransferFunction.AddPoint(
                self.x0alpha, self.alphaslider0)
            self.opacityTransferFunction.AddPoint(
                self.x1alpha, self.alphaslider1)
            self.opacityTransferFunction.AddPoint(
                self.x2alpha, self.alphaslider2)

    def axes_render(self):
            bns = self.renderer.ComputeVisiblePropBounds()
            addons.add_global_axes(axtype=(self.axes) % 15, c=None, bounds=bns)
            self.render()

    def add_legend(self, loaded_mask: Volume):
        loaded_mask.add_scalarbar3d(categories=self.mask_classes,
                                    title='Mask Legend', 
                                    title_size=2.5,
                                    label_size=3)
        loaded_mask.scalarbar.use_bounds(True)
        loaded_mask.scalarbar = loaded_mask.scalarbar.clone2d("center-right", size=0.3)
        
    def change_background(self, bg, bg2):
        self.renderer.SetBackground(vedo.get_color(bg))
        self.renderer.SetBackground2(vedo.get_color(bg2))
        self.render()
        
    def remove_mask(self, parent=None):
        self.remove(parent.loaded_mask)
        parent.loaded_mask = None
        parent.loaded_mask_id = None
        self.remove_flags()
        self.render()
        
    def add_flags(self, volume:Volume, reshape_factor=3, offset=(0, 0, 60)):
        """
        Get the classes and their flags
        
        Parameters
        ----------
        volume : np.ndarray
            The volume to process
        reshape_factor : int
            The factor to reshape the volume by

        Returns
        -------
        dict
            A dictionary containing the classes and their flags
            
        """
        self.fss = []
        
        vol = volume.copy().tonumpy()[::reshape_factor, ::reshape_factor, ::reshape_factor]
        vol[:] = Volume(vol).dilate((2*reshape_factor, 2*reshape_factor, 2*reshape_factor)).erode((reshape_factor, reshape_factor, reshape_factor)).tonumpy()
        
        # Iterate over each class present in the volume
        for class_label in np.unique(vol):
            if class_label == 0:  # Assuming 0 is the background class and should be ignored
                continue
                
            # Create a binary mask for the current class
            class_mask = (vol == class_label)
            
            # Identify connected components/objects for the class
            labeled_array, num_features = label(class_mask, structure=np.ones((3, 3, 3)))
            
            for object_label in range(1, num_features + 1):
                # Find the bounding box for each object
                object_mask = (labeled_array == object_label)
                object_positions = np.argwhere(object_mask)
                
                highest_point = object_positions[object_positions[:, 2].argmax()].astype(int)*reshape_factor-reshape_factor
                
                fs = Flagpost(base=highest_point, top=np.array(highest_point) + np.array(offset), txt=self.mask_flags.get(class_label), s=0.7, c="gray", bc="k9", alpha=1, lw=3, font="SmartCouric")
                self.fss.append(fs)
        
        self.add(self.fss)
        self.render()
    
    def remove_flags(self):
        self.remove(self.fss)
        self.render()
        


def load_volume(volume_path: str, first_load: bool, volume: Volume = None, ext: str = 'nii.gz'):
    """
    Load volume from path.
    """
    if not first_load:
        volume._update(Volume(np.load(volume_path)).dataset) if ext == 'npy' else volume._update(
            Volume(volume_path).dataset)
    else:
        return Volume(np.load(volume_path), spacing=(1.00000, 1.00000, 0.96200)) if ext == 'npy' else Volume(volume_path)


def load_mask(loaded_mask: Volume, mask_files, loaded_mask_id, ext: str = 'nii.gz'):
    """
    Load mask from path.
    """
    if loaded_mask is None:
        return Volume(np.load(mask_files[loaded_mask_id])if ext == 'npy' else mask_files[loaded_mask_id]).origin((0, 0, 0))
    else:
        loaded_mask._update(Volume(np.load(
            mask_files[loaded_mask_id])if ext == 'npy' else mask_files[loaded_mask_id]).dataset)
