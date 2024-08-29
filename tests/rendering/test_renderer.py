from unittest.mock import patch
import vedo
from ctviewer.io import Reader
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering.ray_caster import RayCaster
from ctviewer.rendering.iso_surfer import IsoSurfer
from ctviewer.rendering.slicer import Slicer

def test_initialization(mock_renderer, ogb, alpha):
    """ Test the initialization of the Renderer class. """
    assert mock_renderer.ogb == ogb
    assert mock_renderer.alpha == alpha
    assert isinstance(mock_renderer.reader, Reader)
    assert isinstance(mock_renderer.callbacks, RendererCallbacks)
    assert isinstance(mock_renderer.ray_caster, RayCaster)
    assert isinstance(mock_renderer.iso_surfer, IsoSurfer)
    assert isinstance(mock_renderer.slicer, Slicer)

def test_ray_cast_mode(mock_renderer):
    "Test the ray_cast_mode method of the Renderer class. """
    mock_renderer.ray_cast_mode(volume_mode=1)
    assert mock_renderer.ray_caster.is_active()

def test_iso_surface_mode(mock_renderer):
    "Test the iso_surface_mode method of the Renderer class. """
    mock_renderer.iso_surface_mode()
    assert mock_renderer.iso_surfer.is_active()

def test_slider_mode(mock_renderer):
    "Test the slider_mode method of the Renderer class. """
    mock_renderer.slider_mode()
    assert mock_renderer.slicer.is_active()

def test_quit_current_mode(mock_renderer):
    """ Test the quit_current_mode method of the Renderer class. """
    mock_renderer.ray_cast_mode(volume_mode=1)
    mock_renderer.quit_current_mode()
    mock_renderer.ray_caster.deactivate.assert_called_once()

def test_update_volume(mock_renderer, mock_reader, mock_volume, temp_mhd_path, temp_mask_path):
    """
    Test the update_volume method of the Renderer class.

    This function tests the behavior of the update_volume method of the Renderer class.
    It verifies that the method correctly updates the volume and mask based on the provided file paths.

    Args:
        mock_renderer: A mock instance of the Renderer class.
        mock_reader: A mock instance of the Reader class.
        mock_volume: A mock instance of the Volume class.
        temp_mhd_path: The path to a temporary MHD file.
        temp_mask_path: The path to a temporary mask file.

    Returns:
        None
    """
    # Test with a regular volume
    with patch.object(mock_reader, '__call__', return_value=(mock_volume, {"is_mask": False})), \
         patch.object(mock_renderer.volume, '_update') as mock_update_volume, \
         patch.object(mock_renderer, 'add_flags') as mock_add_flags, \
         patch.object(mock_renderer, 'ray_cast_mode') as mock_ray_cast_mode:

        mock_renderer.update_volume(temp_mhd_path)
        # mock_update_volume.assert_called_once_with(mock_volume.dataset)
        mock_add_flags.assert_not_called()

    # Test with a mask tdr file
    with patch.object(mock_reader, '__call__', return_value=(mock_volume, {"is_mask": True})), \
         patch.object(mock_renderer.mask_, '_update') as mock_update_mask, \
         patch.object(mock_renderer, 'add_flags') as mock_add_flags:

        mock_renderer.update_volume(temp_mask_path)
        # mock_update_mask.assert_called_once_with(mock_volume.dataset)
        mock_add_flags.assert_called_once()


def test_clean_view(mock_renderer):
    """ Test the clean_view method of the Renderer class. """
    mock_renderer.clean_view()
    assert mock_renderer.bboxes == []
    assert mock_renderer.fss == []
    i = mock_renderer.renderers.index(mock_renderer.renderer)
    assert mock_renderer.axes_instances[i] is None

def test_delete_mask(mock_renderer):
    """ Test the delete_mask method of the Renderer class. """
    mock_renderer.delete_mask()
    assert mock_renderer.bboxes == []
    assert mock_renderer.fss == []
    # TODO add check for mask

def test_switch_axes(mock_renderer):
    """ Test the switch_axes method of the Renderer class. """
    with patch.object(mock_renderer, 'add_axes', wraps=mock_renderer.add_axes) as mock_add_axes:
        mock_renderer.axes = 13
        mock_renderer.switch_axes()
        assert mock_renderer.axes == 0
        mock_add_axes.assert_called_once_with(mock_renderer.axes)

        mock_renderer.switch_axes()
        assert mock_renderer.axes == 1
        mock_add_axes.assert_called_with(mock_renderer.axes)


def test_add_axes(mock_renderer):
    """ Test the add_axes method of the Renderer class. """
    with patch('vedo.addons.add_global_axes') as mock_add_global_axes:
        mock_renderer.add_axes(4)
        assert mock_renderer.axes == 4
        mock_add_global_axes.assert_called_once()

def test_delete_current_axes(mock_renderer):
    """ Test the delete_current_axes method of the Renderer class. """
    mock_renderer.delete_current_axes()
    i = mock_renderer.renderers.index(mock_renderer.renderer)
    assert mock_renderer.axes_instances[i] is None

def test_refresh_axes(mock_renderer):
    """ Test the refresh_axes method of the Renderer class. """
    with patch.object(mock_renderer, 'delete_current_axes') as mock_delete_current_axes, \
         patch.object(mock_renderer, 'add_axes') as mock_add_axes:
        mock_renderer.refresh_axes()
        mock_delete_current_axes.assert_called_once()
        mock_add_axes.assert_called_once_with(mock_renderer.axes)

def test_change_background(mock_renderer):
    """ Test the change_background method of the Renderer class. """
    with patch.object(mock_renderer.renderer, 'SetBackground') as mock_set_background, \
         patch.object(mock_renderer.renderer, 'SetBackground2') as mock_set_background2:
        mock_renderer.change_background('red', 'blue')
        mock_set_background.assert_called_once_with(vedo.get_color('red'))
        mock_set_background2.assert_called_once_with(vedo.get_color('blue'))

def test_add_flags(mock_renderer):
    """ Test the add_flags method of the Renderer class. """
    volume_properties = {
        "poses": [(0, 0, 0), (1, 1, 1)],
        "flag_poses": [(0, 0, 0), (1, 1, 1)],
        "labels": ["Label1", "Label2"]
    }
    mock_renderer.add_flags(volume_properties)
    assert len(mock_renderer.fss) == 2
    assert len(mock_renderer.bboxes) == 2

def test_remove_flags(mock_renderer):
    """ Test the remove_flags method of the Renderer class. """
    with patch.object(mock_renderer, 'remove') as mock_remove:
        mock_renderer.remove_flags()
        mock_remove.assert_called_once_with([mock_renderer.fss, mock_renderer.bboxes])
        assert mock_renderer.fss == []
        assert mock_renderer.bboxes == []

def test_exportWeb(mock_renderer):
    """ Test the exportWeb method of the Renderer class. """
    # with patch('vedo.Plotter.show'), patch('vedo.Plotter.export') as mock_export:
    #     mock_renderer.exportWeb()
    #     mock_export.assert_called_once()
    pass # TODO

def test_onClose(mock_renderer):
    """ Test the onClose method of the Renderer class. """
    with patch.object(mock_renderer, 'quit_current_mode') as mock_quit_current_mode, \
         patch.object(mock_renderer, 'remove_flags') as mock_remove_flags, \
         patch.object(mock_renderer, 'remove') as mock_remove, \
         patch.object(mock_renderer, 'close') as mock_close:
        mock_renderer.onClose()
        mock_quit_current_mode.assert_called_once()
        mock_remove_flags.assert_called_once()
        mock_remove.assert_any_call(mock_renderer.volume)
        mock_remove.assert_any_call(mock_renderer.mask_)
        mock_close.assert_called_once()

