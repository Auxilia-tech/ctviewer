import vedo
from vedo import Volume, Plotter, Box, Text3D, Flagpost, np, addons

import cc3d

from ctviewer.io.reader import Reader
from ctviewer.rendering.ray_cast import RayCaster
from ctviewer.rendering.iso_surface import IsoSurfer
from ctviewer.rendering.slicer import Slicer
from ctviewer.rendering.callbacks import RendererCallbacks


class Renderer(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, 
                 isovalue=None,
                 ogb=None,
                 alpha=1,
                 delayed=False,
                 sliderpos=4,
                 mask_classes=None,
                 **kwargs):

        super().__init__(**kwargs)

        self.ogb, self.alpha = ogb, alpha
        self.mask_classes = mask_classes

        self.mask_alpha = [val[2] for val in mask_classes] if mask_classes is not None else 0.5
        self.mask_flags = {val[0]: val[3] for val in mask_classes} if mask_classes is not None else None

        self.volume = Volume(np.zeros((1, 1, 1))).color(self.ogb).alpha(self.alpha).origin((0, 0, 0))
        self.mask_ = Volume(np.zeros((1, 1, 1))).color("red").alpha(self.mask_alpha).origin((0, 0, 0))

        self.add([self.volume, self.mask_])

        # init variables
        self.first_load = True
        self.bboxes, self.fss, self.tdr_poses = [], [], []

        # Create a reader object
        self.reader = Reader()
        self.callbacks = RendererCallbacks(self)
        self.ray_caster = RayCaster(self.volume, self.ogb, self.alpha, self.callbacks)
        self.iso_surfer = IsoSurfer(self.volume, isovalue, sliderpos, delayed, self.callbacks)
        self.slicer = Slicer(self.volume, self.ogb, self.callbacks)

    def ray_cast_mode(self, volume_mode=1):
        if self.ray_caster.is_active():
            self.ray_caster.update_mode(volume_mode)
            self.render()
        else:
            self.quit_current_mode()
            self.ray_caster.activate(volume_mode)
            self.add([self.ray_caster.get_addons()])
            self.refresh_axes()
            self.render()

    def iso_surface_mode(self):
        if self.iso_surfer.is_active():
            return
        self.quit_current_mode()
        self.iso_surfer.activate()
        self.render()

    def slider_mode(self, clamp=True):
        """
        Initialize a 3d slider with the given parameters.
        """
        if self.slicer.is_active():
            return
        self.quit_current_mode()
        self.slicer.activate(clamp)
        self.render()

    def quit_current_mode(self):
        if self.ray_caster.is_active():
            self.ray_caster.deactivate()
        elif self.iso_surfer.is_active():
            self.iso_surfer.deactivate()
        elif self.slicer.is_active():
            self.slicer.deactivate()
        self.render()

    def clean_view(self):
        self.quit_current_mode()
        self.volume._update(Volume(np.zeros((1, 1, 1))).dataset)
        self.mask_._update(Volume(np.zeros((1, 1, 1))).dataset)
        self.remove_flags()
        self.delete_current_axes()
        self.render()

    def switch_axes(self):
        self.delete_current_axes()
        if self.axes == 13:
            self.axes = 0
        else:
            self.axes += 1
        self.add_axes(self.axes)
        self.render()
    
    def add_axes(self, axes=0):
        bns = self.renderer.ComputeVisiblePropBounds()
        addons.add_global_axes(axtype=(axes) % 15, c=None, bounds=bns)
    
    def delete_current_axes(self):
        i = self.renderers.index(self.renderer)
        try:
            self.axes_instances[i].EnabledOff()
            self.axes_instances[i].SetInteractor(None)
        except AttributeError:
            try:
                self.remove(self.axes_instances[i])
            except:
                print("Cannot remove axes", [self.axes_instances[i]])
                return
        self.axes_instances[i] = None

    def refresh_axes(self):
        self.delete_current_axes()
        self.add_axes(self.axes)
        self.render()
        
    def change_background(self, bg, bg2):
        self.renderer.SetBackground(vedo.get_color(bg))
        self.renderer.SetBackground2(vedo.get_color(bg2))
        self.render()
        
    def add_flags_from_volume(self, volume:Volume, reshape_factor=4, offset=(0, 0, 60)):
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

    def add_flags_from_tdr(self, offset=(0, 0, 60)):
        """
        Add flags from a TDR file
        
        Parameters
        ----------
        bboxes : list
            The list of bounding boxes
        labels : list
            The list of labels
        offset : tuple
            The offset to apply to the flags
        
        """
        self.fss = []
        self.bboxes = []
        for pos, flag_pos, label in zip(self.volume_properties["poses"], self.volume_properties["flag_poses"], self.volume_properties["labels"]):
            self.bboxes.append(Box(pos=pos, c="black", alpha=0.9).wireframe().lw(2).lighting("off"))
            fs = Flagpost(base=flag_pos, top=flag_pos + np.array(offset), txt=label, s=0.7, c="gray", bc="k9", alpha=1, lw=3, font="SmartCouric")
            self.fss.append(fs)
        
        self.add([self.fss, self.bboxes])
        self.render()

    def add_flags(self):
        if self.ext_mask != 'dcs':
            self.add_flags_from_volume(self.mask_.copy(), reshape_factor=4, offset=(0, 0, 60))
            
    def remove_flags(self):
        if len(self.fss) > 0:
            self.remove(self.fss)
            self.remove(self.bboxes)
            self.render()

    def update_volume(self, volume_path):
        vol, self.volume_properties = self.reader(volume_path)
        if self.volume_properties["is_tdr"]:
            self.mask_._update(vol.dataset).alpha([0]+[1]*15) # Background is transparent (TODO 15 is the number of classes)
            self.add_flags_from_tdr()
        else:
            self.volume._update(vol.dataset)
        if self.ray_caster.is_active() or self.iso_surfer.is_active() or self.slicer.is_active():
            self.refresh_axes()
        else:
            self.ray_cast_mode(1)
            self.show(viewup='z')
        self.render()

    def exportWeb(self):
        plt = Plotter(size=(600, 600), bg='GhostWhite')
        mask = self.mask_.clone()
        mask_array = mask.tonumpy().astype(np.uint8)
        mask_array[mask_array > 0] = 1
        mask.modified()
        mesh_mask = mask.isosurface().decimate(0.5).color("red").alpha(1)
        txt = Text3D("Auxilia Web CTViewer", font='Bongas', s=30, c='black', depth=0.05)
        plt.show(mesh_mask, self.bboxes, self.fss, txt, txt.box(padding=20), axes=1, viewup='z', zoom=1.2)
        plt.export('tdr.x3d')

    def onClose(self):
        self.quit_current_mode()
        self.remove_flags()
        self.remove(self.volume)
        self.remove(self.mask_)
        self.close()