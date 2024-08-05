import pytest
from unittest.mock import MagicMock, patch
import vedo
from vedo import Volume, addons
from ctviewer.io import Reader
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering.ray_caster import RayCaster
from ctviewer.rendering.iso_surfer import IsoSurfer
from ctviewer.rendering.slicer import Slicer
from ctviewer.rendering import Renderer
from ctviewer.utils import ConfigManager

@pytest.fixture
def mock_callbacks():
    return MagicMock(spec=RendererCallbacks)

@pytest.fixture
def mock_reader():
    return Reader()

@pytest.fixture
def mock_volume():
    return MagicMock(spec=Volume)

@pytest.fixture
def ogb():
    return [(100, 'orange'), (200, 'green'), (300, 'blue')]

@pytest.fixture
def alpha():
    return [0.5, 0.5, 0.5]

@pytest.fixture
def mock_ray_caster():
    return MagicMock(spec=RayCaster)

@pytest.fixture
def mock_iso_surfer():
    return MagicMock(spec=IsoSurfer)

@pytest.fixture
def mock_slicer():
    return MagicMock(spec=Slicer)

@pytest.fixture
def mask_classes():
    config_manager = ConfigManager()
    user_config = config_manager.get_user_config()
    return user_config["mask_classes"]

@pytest.fixture
def renderer(ogb, alpha, mock_callbacks, mock_reader, mock_ray_caster, mock_iso_surfer, mock_slicer, mask_classes):
    renderer = Renderer(ogb=ogb, alpha=alpha, isovalue=0.5, sliderpos=4, mask_classes=mask_classes)
    renderer.reader = mock_reader
    renderer.callbacks = mock_callbacks
    renderer.ray_caster = mock_ray_caster
    renderer.iso_surfer = mock_iso_surfer
    renderer.slicer = mock_slicer
    return renderer

def test_initialization(renderer, ogb, alpha):
    assert renderer.ogb == ogb
    assert renderer.alpha == alpha
    assert isinstance(renderer.reader, Reader)
    assert isinstance(renderer.callbacks, RendererCallbacks)
    assert isinstance(renderer.ray_caster, RayCaster)
    assert isinstance(renderer.iso_surfer, IsoSurfer)
    assert isinstance(renderer.slicer, Slicer)

def test_ray_cast_mode(renderer):
    renderer.ray_cast_mode(volume_mode=1)
    assert renderer.ray_caster.is_active()

def test_iso_surface_mode(renderer):
    renderer.iso_surface_mode()
    assert renderer.iso_surfer.is_active()

def test_slider_mode(renderer):
    renderer.slider_mode()
    assert renderer.slicer.is_active()

def test_quit_current_mode(renderer):
    renderer.ray_cast_mode(volume_mode=1)
    renderer.quit_current_mode()
    renderer.ray_caster.deactivate.assert_called_once()

def test_update_volume(renderer, mock_reader, mock_volume):
    # Test with a regular volume
    with patch.object(mock_reader, '__call__', return_value=(mock_volume, {"is_mask": False})), \
         patch.object(renderer.volume, '_update') as mock_update_volume, \
         patch.object(renderer, 'add_flags') as mock_add_flags, \
         patch.object(renderer, 'ray_cast_mode') as mock_ray_cast_mode:

        renderer.update_volume("../datasets/ts_image_74_0000.nii.gz")
        # mock_update_volume.assert_called_once_with(mock_volume.dataset)
        mock_add_flags.assert_not_called()

    # Test with a mask volume
    with patch.object(mock_reader, '__call__', return_value=(mock_volume, {"is_mask": True})), \
         patch.object(renderer.mask_, '_update') as mock_update_mask, \
         patch.object(renderer, 'add_flags') as mock_add_flags:

        renderer.update_volume("../datasets/ts_Mask_680_0000.dcs")
        # mock_update_mask.assert_called_once_with(mock_volume.dataset)
        mock_add_flags.assert_called_once()


def test_clean_view(renderer):
    renderer.clean_view()
    assert renderer.bboxes == []
    assert renderer.fss == []
    i = renderer.renderers.index(renderer.renderer)
    assert renderer.axes_instances[i] is None

def test_delete_mask(renderer):
    renderer.delete_mask()
    assert renderer.bboxes == []
    assert renderer.fss == []
    # TODO add check for mask

def test_switch_axes(renderer):
    with patch.object(renderer, 'add_axes', wraps=renderer.add_axes) as mock_add_axes:
        renderer.axes = 13
        renderer.switch_axes()
        assert renderer.axes == 0
        mock_add_axes.assert_called_once_with(renderer.axes)

        renderer.switch_axes()
        assert renderer.axes == 1
        mock_add_axes.assert_called_with(renderer.axes)


def test_add_axes(renderer):
    with patch('vedo.addons.add_global_axes') as mock_add_global_axes:
        renderer.add_axes(4)
        assert renderer.axes == 4
        mock_add_global_axes.assert_called_once()

def test_delete_current_axes(renderer):
    renderer.delete_current_axes()
    i = renderer.renderers.index(renderer.renderer)
    assert renderer.axes_instances[i] is None

def test_refresh_axes(renderer):
    with patch.object(renderer, 'delete_current_axes') as mock_delete_current_axes, \
         patch.object(renderer, 'add_axes') as mock_add_axes:
        renderer.refresh_axes()
        mock_delete_current_axes.assert_called_once()
        mock_add_axes.assert_called_once_with(renderer.axes)

def test_change_background(renderer):
    with patch.object(renderer.renderer, 'SetBackground') as mock_set_background, \
         patch.object(renderer.renderer, 'SetBackground2') as mock_set_background2:
        renderer.change_background('red', 'blue')
        mock_set_background.assert_called_once_with(vedo.get_color('red'))
        mock_set_background2.assert_called_once_with(vedo.get_color('blue'))

def test_add_flags(renderer):
    volume_properties = {
        "poses": [(0, 0, 0), (1, 1, 1)],
        "flag_poses": [(0, 0, 0), (1, 1, 1)],
        "labels": ["Label1", "Label2"]
    }
    renderer.add_flags(volume_properties)
    assert len(renderer.fss) == 2
    assert len(renderer.bboxes) == 2

def test_remove_flags(renderer):
    with patch.object(renderer, 'remove') as mock_remove:
        renderer.remove_flags()
        mock_remove.assert_called_once_with([renderer.fss, renderer.bboxes])
        assert renderer.fss == []
        assert renderer.bboxes == []

def test_exportWeb(renderer):
    # with patch('vedo.Plotter.show'), patch('vedo.Plotter.export') as mock_export:
    #     renderer.exportWeb()
    #     mock_export.assert_called_once()
    pass # TODO

def test_onClose(renderer):
    with patch.object(renderer, 'quit_current_mode') as mock_quit_current_mode, \
         patch.object(renderer, 'remove_flags') as mock_remove_flags, \
         patch.object(renderer, 'remove') as mock_remove, \
         patch.object(renderer, 'close') as mock_close:
        renderer.onClose()
        mock_quit_current_mode.assert_called_once()
        mock_remove_flags.assert_called_once()
        mock_remove.assert_any_call(renderer.volume)
        mock_remove.assert_any_call(renderer.mask_)
        mock_close.assert_called_once()


