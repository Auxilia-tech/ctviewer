from typing import Tuple, List, Dict

import vedo
from vedo import Volume, Image, Plotter, Box, Text3D, Flagpost, np, addons

from ctviewer.io import Reader
from .callbacks import RendererCallbacks
from .ray_caster import RayCaster
from .iso_surfer import IsoSurfer
from .image_viewer import ImageViewer
from .slicer import Slicer


class Renderer(Plotter):
    """
    Generate Volume rendering using ray casting.
    """

    def __init__(self, ogb:List[int], alpha:List[Tuple[int]], isovalue:bool=None, 
                 delayed:bool=False, sliderpos:int=4, mask_classes:List[Tuple[int, str, int, str]]=None, **kwargs):
        """ 
        Initialize the renderer with the given parameters.
        
        Parameters
        ----------
        isovalue : float
            The isovalue to use for the iso surface
        ogb : list
            The list of colors to use for the volume rendering
        alpha : float
            The alpha value to use for the volume rendering
        delayed : bool
            Delay the slider update on mouse release.
        sliderpos : int
            The position of the slider
        mask_classes : list
            The list of classes and their flags, alpha values, and colors names to use for the mask 
        """

        super().__init__(**kwargs)
        """ Initialize the renderer with the given parameters. """

        self.ogb, self.alpha, self.mask_classes = ogb, alpha, mask_classes

        self.mask_alpha = [val[2] for val in mask_classes] if mask_classes is not None else 0.5
        self.mask_flags = {val[0]: val[3] for val in mask_classes} if mask_classes is not None else None

        self.volume = Volume(np.zeros((1, 1, 1))).color(self.ogb).alpha(self.alpha).origin((0, 0, 0))
        self.mask_ = Volume(np.zeros((1, 1, 1))).color("red").alpha([0]+[1]*(len(self.mask_classes)-1)).origin((0, 0, 0))
        self.image = Image(np.zeros((1, 1)), channels=1).enhance().cmap("hot")

        self.add([self.volume, self.mask_])

        # init variables
        self.bboxes, self.fss, self.tdr_poses = [], [], []

        # Create a reader object
        self.reader = Reader()
        self.callbacks = RendererCallbacks(self)
        self.ray_caster = RayCaster(self.volume, self.ogb, self.alpha, self.callbacks)
        self.iso_surfer = IsoSurfer(self.volume, isovalue, sliderpos, delayed, self.callbacks)
        self.slicer = Slicer(self.volume, self.ogb, self.callbacks)
        self.image_viewer = ImageViewer(self.image, self.callbacks)

    def ray_cast_mode(self, volume_mode:int=1):
        """
        Initialize a ray cast with the given parameters.

        Parameters
        ----------
        volume_mode : int
            0, composite rendering
            1, maximum projection rendering
            2, minimum projection rendering
            3, average projection rendering
            4, additive mode
        """
        if self.ray_caster.is_active():
            self.ray_caster.update_mode(volume_mode)
            self.render()
        else:
            self.quit_current_mode()
            self.ray_caster.activate(volume_mode)
            if self.ray_caster.is_active(): # if the ray caster was built successfully
                self.refresh_axes()
            self.render()

    def iso_surface_mode(self):
        """ 
        Initialize an iso surface with the given parameters.
        """
        if self.iso_surfer.is_active():
            return
        self.quit_current_mode()
        self.iso_surfer.activate()
        self.render()

    def slider_mode(self, clamp:bool=True):
        """
        Initialize a 3d slider with the given parameters.
        """
        if self.slicer.is_active():
            return
        self.quit_current_mode()
        self.ray_caster.update_sliders((0, 0, 0)) # Hide the volume
        self.slicer.activate(clamp)
        self.render()
    
    def image_viewer_mode(self):
        """
        Initialize an image viewer with the given parameters.
        """
        if self.image_viewer.is_active():
            return
        self.quit_current_mode()
        self.image_viewer.activate()
        self.render()

    def quit_current_mode(self):
        """
        Quit the current mode.
        """
        if self.ray_caster.is_active():
            self.ray_caster.deactivate()
        elif self.iso_surfer.is_active():
            self.iso_surfer.deactivate()
        elif self.slicer.is_active():
            self.slicer.deactivate()
        elif self.image_viewer.is_active():
            self.image_viewer.deactivate()
        self.render()

    def clean_view(self):
        """
        Delete the loaded masks, volume, flags, bounding boxes and axes.
        """
        self.quit_current_mode()
        self.remove_flags()
        self.mask_._update(Volume(np.zeros((1, 1, 1))).dataset)
        self.volume._update(Volume(np.zeros((1, 1, 1))).dataset)
        self.delete_current_axes()
        self.render()
    
    def delete_mask(self):
        """
        Delete the loaded mask.
        """
        self.remove_flags()
        self.mask_._update(Volume(np.zeros((1, 1, 1))).dataset)
        if not self.ray_caster.is_active() and not self.iso_surfer.is_active() and not self.slicer.is_active() and not self.image_viewer.is_active():
            self.delete_current_axes()
        self.render()

    def switch_axes(self):
        """
        Switch between different axes.
        """
        self.delete_current_axes()
        if self.axes == 13:
            self.axes = 0
        else:
            self.axes += 1
        self.add_axes(self.axes)
        self.render()
    
    def add_axes(self, axes: int=8):
        """
        Add axes to the plot.
        
        Parameters
        ----------
        axes : int
            The axes to add to the plot
        """
        self.axes = axes if axes is not None else 8
        bns = self.renderer.ComputeVisiblePropBounds()
        addons.add_global_axes(axtype=(self.axes) % 15, c=None, bounds=bns)
    
    def delete_current_axes(self):
        """
        Delete the current axes.
        """
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
        """
        Delete the current axes and add new axes.
        """
        self.delete_current_axes()
        self.add_axes(self.axes)
        self.render()
        
    def change_background(self, bg, bg2):
        """
        Change the background of the plot.

        Parameters
        ----------
        bg : Could be a string, rgb tuple, hex string or int
            The first background
        bg2 : Could be a string, rgb tuple, hex string or int
            The second background  

        Example:
            - `RGB    = (255, 255, 255)` corresponds to white
            - `rgb    = (1,1,1)` is again white
            - `hex    = #FFFF00` is yellow
            - `string = 'white'`
            - `string = 'w'` is white nickname
            - `string = 'dr'` is darkred
            - `string = 'red4'` is a shade of red
            - `int    =  7` picks color nr. 7 in a predefined color list
            - `int    = -7` picks color nr. 7 in a different predefined list

        """
        self.renderer.SetBackground(vedo.get_color(bg))
        self.renderer.SetBackground2(vedo.get_color(bg2))
        self.render()

    def add_flags(self, volume_properties:Dict, offset:Tuple[int]=(0, 0, 60)):
        """
        Read the flags from a TDR file and add them to the plot.
        
        Parameters
        ----------
        volume_properties : dict
            Contains poses, flag_poses, and labels
        offset : tuple
            The offset to apply to the flags
        
        """
        self.fss = []
        self.bboxes = []
        for pos, flag_pos, label in zip(volume_properties["poses"], volume_properties["flag_poses"], volume_properties["labels"]):
            self.bboxes.append(Box(pos=pos, c="black", alpha=0.9).wireframe().lw(2).lighting("off"))
            label = label if isinstance(label, str) else self.mask_flags.get(label)
            fs = Flagpost(base=flag_pos, top=flag_pos + np.array(offset), txt=label, s=0.7, c="gray", bc="k9", alpha=1, lw=3, font="SmartCouric")
            self.fss.append(fs)
        
        self.add([self.fss, self.bboxes])
        self.render()
            
    def remove_flags(self):
        """
        Remove the flags from the current plot.
        """
        self.remove([self.fss, self.bboxes])
        self.fss, self.bboxes = [], []
        self.render()

    def update_volume(self, volume_path):
        """
        Update the volume with the given path when the user selects a new volume.
        
        Parameters
        ----------
        volume_path : str
            The path to the new volume
        """
        self.reader.reset_properties()
        vol, volume_properties = self.reader(volume_path)
        if volume_properties["is_proj"]:
            self.image._update(vol.dataset)
            self.clean_view()
            self.image_viewer_mode()
        else:
            self.image_viewer.deactivate()
        if volume_properties["is_mask"]:
            self.remove_flags()
            self.mask_._update(vol.dataset).alpha([0]+[1]*(len(self.mask_classes)-1)) # keep the background transparent
            self.add_flags(volume_properties)
            if not self.ray_caster.is_active() and not self.iso_surfer.is_active() and not self.slicer.is_active():
                self.show(viewup='z')
        else:
            self.volume._update(vol.dataset)
        if not self.ray_caster.is_active() and not self.iso_surfer.is_active() and not self.slicer.is_active() and not self.image_viewer.is_active():
            self.ray_cast_mode(1)
            self.show(viewup='z')
        self.refresh_axes()
        self.render()
    
    def update_user_config(self, user_config:Dict):
        """
        Update the user configuration with the given parameters.
        
        Parameters
        ----------
        user_config : dict
            The user configuration to update
        """
        self.ogb, self.alpha = user_config['ogb'], user_config['alpha']
        self.mask_alpha = [val[2] for val in user_config['mask_classes']]
        self.mask_flags = {val[0]: val[3] for val in user_config['mask_classes']}
        self.volume.color(self.ogb).alpha(self.alpha)
        self.mask_.color("red").alpha([0]+self.mask_alpha[1:])
        if hasattr(self.ray_caster, 'opacityTransferFunction'):
            self.ray_caster.setOTF()
        self.render()

    def exportWeb(self):
        """
        Export the current plot to a web format (x3d).
        
        Generates
            3D plot of the current volume and mask with the flags and bounding boxes.
            HTML file with the code to display the 3D plot (Link to a JS library).
        """
        plt = Plotter(size=(600, 600), bg='GhostWhite')
        mask = self.mask_.clone()
        mask_array = mask.tonumpy().astype(np.uint8)
        mask_array[mask_array > 0] = 1
        mask.modified()
        mesh_mask = mask.isosurface().decimate(0.5).color("red").alpha(1)
        txt = Text3D("Auxilia Web CTViewer", font='Bongas', s=30, c='black', depth=0.05)
        plt.show(mesh_mask, self.bboxes, self.fss, txt, txt.box(padding=20), axes=1, viewup='z', zoom=1.2)
        import os
        if not os.path.exists('export'):
            os.makedirs('export')
        plt.export('export/tdr.x3d')

    def onClose(self):
        """
        Close the current plot.
        """
        self.quit_current_mode()
        self.remove_flags()
        self.remove(self.volume)
        self.remove(self.mask_)
        self.close()