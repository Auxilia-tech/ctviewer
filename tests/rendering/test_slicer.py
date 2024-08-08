import pytest
from unittest.mock import MagicMock
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering import Slicer

@pytest.fixture
def mock_callbacks():
    """ Create a mock callbacks object """
    mock = MagicMock(spec=RendererCallbacks)
    mock.background.return_value = [0, 0, 0]  # Simulate a dark background
    return mock

@pytest.fixture
def ogb():
    """ Create a mock opacity gradient base value """
    return [(100, 'orange'), (200, 'green'), (300, 'blue')]

@pytest.fixture
def slicer(temp_volume_data, ogb, mock_callbacks):
    """ Create a Slicer instance for testing"""
    return Slicer(volume=temp_volume_data, ogb=ogb, callbacks=mock_callbacks, clamp=True)

def test_initialization(slicer, temp_volume_data, ogb, mock_callbacks):
    """
    Test the initialization of the slicer object.

    Args:
        slicer: The slicer object to be tested.
        temp_volume_data: The temporary volume data used for testing.
        ogb: The ogb object used for testing.
        mock_callbacks: The mock callbacks used for testing.

    Returns:
        None
    """
    assert slicer.volume == temp_volume_data
    assert slicer.ogb == ogb
    assert slicer.callbacks == mock_callbacks
    assert slicer.clamp is True
    assert slicer.on is False

def test_build(slicer, mock_callbacks):
    """ Test the build method of the Slicer object. """
    slicer.build()
    assert mock_callbacks.add.called
    assert slicer.yslice is not None
    assert slicer.xslider is not None
    assert slicer.yslider is not None
    assert slicer.zslider is not None

def test_check_volume(slicer):
    """ Test the check_volume method of the Slicer object. """
    assert slicer.check_volume() is True
    assert slicer.volume is not None

def test_activate(slicer, mock_callbacks):
    """ Test the activate method of the Slicer object. """
    slicer.build()
    slicer.activate()
    assert slicer.on is True
    assert mock_callbacks.add.called

def test_deactivate(slicer, mock_callbacks):
    """ Test the deactivate method of the Slicer object. """
    slicer.build()
    slicer.activate()
    slicer.deactivate()
    assert slicer.on is False
    assert mock_callbacks.remove.called

def test_slider_functions(slicer, mock_callbacks):
    """ Test the slider functions of the Slicer object. """
    slicer.build()
    assert int(slicer.xslider.value) == 1
    assert int(slicer.yslider.value) == 1
    assert int(slicer.zslider.value) == 1
