import pytest
from unittest.mock import MagicMock
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering import IsoSurfer

@pytest.fixture
def mock_callbacks():
    """ Create a mock callbacks object """
    return MagicMock(spec=RendererCallbacks)

@pytest.fixture
def iso_surfer(temp_volume_data, mock_callbacks):
    """ Create an IsoSurfer instance for testing """
    return IsoSurfer(volume=temp_volume_data, isovalue=50, sliderpos=0, delayed=False, callbacks=mock_callbacks)

def test_initialization(iso_surfer, temp_volume_data, mock_callbacks):
    """
    Test if the IsoSurfer instance is initialized correctly.

    Args:
        iso_surfer (IsoSurfer): The IsoSurfer instance to test.
        temp_volume_data (VolumeData): The temporary volume data for testing.
        mock_callbacks (list): The list of mock callbacks for testing.

    Returns:
        None
    """
    assert iso_surfer.volume == temp_volume_data
    assert iso_surfer.isovalue == 50
    assert iso_surfer.sliderpos == 0
    assert iso_surfer.delayed is False
    assert iso_surfer.callbacks == mock_callbacks
    assert iso_surfer.on is False

def test_build(iso_surfer, mock_callbacks):
    """ Test if the build method adds a slider to the renderer """
    iso_surfer.build()
    assert mock_callbacks.add_slider.called
    args, kwargs = mock_callbacks.add_slider.call_args
    assert kwargs['value'] == 50
    assert kwargs['pos'] == 0
    assert kwargs['title'] == "scalar value"
    assert kwargs['delayed'] is False

def test_update_isovalue(iso_surfer):
    """ Test if the update_isovalue method updates the isovalue """
    iso_surfer.build()
    iso_surfer.update_isovalue(75)
    assert iso_surfer.isovalue == 75

def test_activate(iso_surfer):
    """ Test if the activate method activates the iso surfer """
    iso_surfer.build()
    iso_surfer.activate()
    assert iso_surfer.on is True
    iso_surfer.s0.on.assert_called_once()

def test_deactivate(iso_surfer):
    """ Test if the deactivate method deactivates the iso surfer """
    iso_surfer.build()
    iso_surfer.activate()
    iso_surfer.deactivate()
    assert iso_surfer.on is False
    iso_surfer.s0.off.assert_called_once()

def test_check_volume(iso_surfer):
    """ Test if the check_volume method checks if the volume is set """
    assert iso_surfer.check_volume() is True
    iso_surfer.volume = None
    assert iso_surfer.check_volume() is False
