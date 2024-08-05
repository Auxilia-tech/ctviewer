import pytest
from unittest.mock import MagicMock
from ctviewer.io import Reader
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering import RayCaster

@pytest.fixture
def mock_callbacks():
    return MagicMock(spec=RendererCallbacks)

@pytest.fixture
def nii_gz_volume():
    reader = Reader()
    volume, properties = reader("../datasets/ts_image_74_0000.nii.gz")  # Path to the test file
    return volume

@pytest.fixture
def ogb():
    return [(100, 'orange'), (200, 'green'), (300, 'blue')]

@pytest.fixture
def alpha():
    return 0.5

@pytest.fixture
def ray_caster(nii_gz_volume, ogb, alpha, mock_callbacks):
    return RayCaster(volume=nii_gz_volume, ogb=ogb, alpha=alpha, callbacks=mock_callbacks)

def test_initialization(ray_caster, nii_gz_volume, ogb, alpha, mock_callbacks):
    assert ray_caster.volume == nii_gz_volume
    assert ray_caster.ogb == ogb
    assert ray_caster.alpha == alpha
    assert ray_caster.callbacks == mock_callbacks
    assert ray_caster.on is False

def test_build(ray_caster, mock_callbacks):
    ray_caster.build(volume_mode=0)
    assert mock_callbacks.add_slider.called
    assert len(ray_caster.get_sliders()) == 3
    assert ray_caster.hist is not None

def test_setOTF(ray_caster):
    ray_caster.build(volume_mode=0)
    ray_caster.setOTF()
    otf = ray_caster.opacityTransferFunction
    assert otf.GetSize() > 0

def test_update_mode(ray_caster):
    ray_caster.build(volume_mode=0)
    ray_caster.update_mode(volume_mode=1)
    assert ray_caster.volume_mode == 1

def test_update_sliders(ray_caster):
    ray_caster.build(volume_mode=0)
    ray_caster.update_sliders((0.2, 0.4, 0.6))
    assert ray_caster.alphaslider0 == 0.2
    assert ray_caster.alphaslider1 == 0.4
    assert ray_caster.alphaslider2 == 0.6

def test_activate(ray_caster):
    ray_caster.build(volume_mode=0)
    ray_caster.activate(volume_mode=1)
    assert ray_caster.on is True

def test_deactivate(ray_caster):
    ray_caster.build(volume_mode=0)
    ray_caster.activate(volume_mode=1)
    ray_caster.deactivate()
    assert ray_caster.on is False

def test_check_volume(ray_caster):
    assert ray_caster.check_volume() is True
