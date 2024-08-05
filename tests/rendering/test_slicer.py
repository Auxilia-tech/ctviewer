import pytest
from unittest.mock import MagicMock
from vedo import Volume
from ctviewer.io import Reader
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering import Slicer  # Replace with the correct import path

@pytest.fixture
def mock_callbacks():
    mock = MagicMock(spec=RendererCallbacks)
    # Set the return value for the background method
    mock.background.return_value = [0, 0, 0]  # Simulate a dark background
    return mock

@pytest.fixture
def nii_gz_volume():
    reader = Reader()
    volume, properties = reader("../datasets/ts_image_74_0000.nii.gz")  # Path to the test file
    return volume

@pytest.fixture
def ogb():
    return [(100, 'orange'), (200, 'green'), (300, 'blue')]

@pytest.fixture
def slicer(nii_gz_volume, ogb, mock_callbacks):
    return Slicer(volume=nii_gz_volume, ogb=ogb, callbacks=mock_callbacks, clamp=True)

def test_initialization(slicer, nii_gz_volume, ogb, mock_callbacks):
    assert slicer.volume == nii_gz_volume
    assert slicer.ogb == ogb
    assert slicer.callbacks == mock_callbacks
    assert slicer.clamp is True
    assert slicer.on is False

def test_build(slicer, mock_callbacks):
    slicer.build()
    assert mock_callbacks.add.called
    assert slicer.yslice is not None
    assert slicer.xslider is not None
    assert slicer.yslider is not None
    assert slicer.zslider is not None

def test_check_volume(slicer):
    assert slicer.check_volume() is True

def test_activate(slicer, mock_callbacks):
    slicer.build()
    slicer.activate()
    assert slicer.on is True

def test_deactivate(slicer, mock_callbacks):
    slicer.build()
    slicer.activate()
    slicer.deactivate()
    assert slicer.on is False
    assert mock_callbacks.remove.called

def test_slider_functions(slicer, mock_callbacks):
    slicer.build()
    # Verify that the slicer correctly updates its state
    assert int(slicer.xslider.value) == 1 # TODO - Update the expected value
    assert int(slicer.yslider.value) == 1 # TODO - Update the expected value
    assert int(slicer.zslider.value) == 1 # TODO - Update the expected value
