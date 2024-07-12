import vedo
from vedo import addons, Volume, Plotter, Box, Flagpost, np, build_lut, Text3D
from vedo.pyplot import CornerHistogram
from vedo.colors import get_color
from vedo.utils import mag

import cc3d

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
        # self.mask_colors = [
        #     (val[0], val[1]) for val in mask_classes] if mask_classes is not None else "red"
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
        
    def add_flags(self, volume:Volume, reshape_factor=4, offset=(0, 0, 60)):
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
        self.bboxes = []
        volume.dilate((2*reshape_factor, 2*reshape_factor, 2*reshape_factor)).erode((reshape_factor, reshape_factor, reshape_factor))
        vol = volume.tonumpy()[::reshape_factor, ::reshape_factor, ::reshape_factor]
        labels_out, N = cc3d.connected_components(vol, connectivity=26, return_N=True)
        stats = cc3d.statistics(labels_out)
        print("Number of objects in the volume:", N)
        for centroid, bounding_boxe, each_label in zip(stats['centroids'][1:], stats['bounding_boxes'][1:], cc3d.each(labels_out, binary=True, in_place=True)):
            image = each_label[1]
            class_label = np.unique(image*vol)
            pos = np.array([bounding_boxe[0].start, bounding_boxe[0].stop, bounding_boxe[1].start, bounding_boxe[1].stop, bounding_boxe[2].start, bounding_boxe[2].stop])
            pos = pos*reshape_factor - reshape_factor
            box = Box(pos=pos, c="black", alpha=0.9).wireframe().lw(2).lighting("off")
            self.bboxes.append(box)
            # add the z length of the bounding box to the centroid
            centroid = centroid * reshape_factor - reshape_factor
            base = np.array([centroid[0], centroid[1], centroid[2]+((pos[-1]-pos[-2])/2)]).astype(int)
            fs = Flagpost(base=base, top=base + np.array(offset), txt=self.mask_flags.get(class_label[1]), s=0.7, c="gray", bc="k9", alpha=1, lw=3, font="SmartCouric")
            self.fss.append(fs)
        
        self.add([self.fss, self.bboxes])
        self.render()
    
    def remove_flags(self):
        self.remove(self.fss)
        self.remove(self.bboxes)
        self.render()
        
class Renderer:

    def load_volume(self):
        if not self.first_load:
            if self.ext == 'npy':
                self.vol._update(Volume(np.load(self.volume_path)).dataset)
            if self.ext == 'nii.gz' or self.ext == 'mhd' or self.ext == 'dcm':
                self.vol._update(Volume(self.volume_path).dataset)
            if self.ext == 'dcs':
                self.vol._update(Volume(self.load_dicos_ct()).dataset)
        else:
            if self.ext == 'npy':
                self.vol = Volume(np.load(self.volume_path))
            if self.ext == 'nii.gz' or self.ext == 'mhd' or self.ext == 'dcm':
                self.vol = Volume(self.volume_path)
            if self.ext == 'dcs':
                self.vol = Volume(self.load_dicos_ct())

    def load_mask(self):
        if self.mask_files is not None:
            if self.ext == 'npy':
                self.loaded_mask = Volume(np.load(self.mask_files[self.loaded_mask_id]))
            if self.ext == 'nii.gz' or self.ext == 'mhd' or self.ext == 'dcm':
                self.loaded_mask = Volume(self.mask_files[self.loaded_mask_id])
            if self.ext == 'dcs':
                self.loaded_mask = Volume(self.load_dicos_tdr())

        else:
            if self.ext == 'npy':
                self.loaded_mask._update(Volume(np.load(self.mask_files[self.loaded_mask_id])).dataset)
            if self.ext == 'nii.gz' or self.ext == 'mhd' or self.ext == 'dcm':
                self.loaded_mask._update(Volume(self.mask_files[self.loaded_mask_id]).dataset)
            if self.ext == 'dcs':
                self.loaded_mask._update(Volume(self.load_dicos_tdr()).dataset)
        
    def update_volume(self):
            self.load_volume()
            if self.first_load:
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
                self.load_mask()
                self.loaded_mask.alpha(self.plt.mask_alpha).mode(0).color("red")
                self.plt.add(self.loaded_mask)
                self.plt.add_flags(self.loaded_mask.copy(), reshape_factor=4, offset=(0, 0, 60))
            else:
                self.load_mask()
            self.update_text_button_masks()
            self.plt.render()

    def onClose(self):
        self.vtkWidget1.close()

    def load_dicos_ct(self):
        print ("Loading DICOM CT files from ", self.volume_path)

    def load_dicos_tdr(self):
        print ("Loading DICOS TDR files from ", self.mask_files[self.loaded_mask_id])

    def exportWebX3D(self):
        if self.volume_path is not None and self.loaded_mask is not None:
            # Prepare the mask for export
            plt = Plotter(size=(600, 600), bg='GhostWhite')
            mesh_mask = self.loaded_mask.isosurface().decimate(0.7).color('red').alpha(self.plt.mask_alpha)
            txt = Text3D("Auxilia Web CTViewer", font='Bongas', s=30, c='black', depth=0.05)
            plt.show(mesh_mask, self.plt.bboxes, self.plt.fss, txt, txt.box(padding=20), axes=1, viewup='z', zoom=1.2)
            plt.export('/tmp/tdr.x3d')
            plt.clear()
            plt.close()
        else:
            self.showPopup("Warning", "Export Error", "Please load both the volume and mask before exporting.")
