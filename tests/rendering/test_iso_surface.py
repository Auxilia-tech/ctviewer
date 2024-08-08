import pytest
from unittest.mock import MagicMock
from ctviewer.rendering.callbacks import RendererCallbacks
from ctviewer.rendering import IsoSurfer

@pytest.fixture
def mock_callbacks():
    return MagicMock(spec=RendererCallbacks)

@pytest.fixture
def iso_surfer(temp_volume_data, mock_callbacks):
    return IsoSurfer(volume=temp_volume_data, isovalue=50, sliderpos=0, delayed=False, callbacks=mock_callbacks)

def test_initialization(iso_surfer, temp_volume_data, mock_callbacks):
    assert iso_surfer.volume == temp_volume_data
    assert iso_surfer.isovalue == 50
    assert iso_surfer.sliderpos == 0
    assert iso_surfer.delayed is False
    assert iso_surfer.callbacks == mock_callbacks
    assert iso_surfer.on is False

def test_build(iso_surfer, mock_callbacks):
    iso_surfer.build()
    assert mock_callbacks.add_slider.called
    args, kwargs = mock_callbacks.add_slider.call_args
    assert kwargs['value'] == 50
    assert kwargs['pos'] == 0
    assert kwargs['title'] == "scalar value"
    assert kwargs['delayed'] is False

def test_update_isovalue(iso_surfer):
    iso_surfer.build()
    iso_surfer.update_isovalue(75)
    assert iso_surfer.isovalue == 75

def test_activate(iso_surfer):
    iso_surfer.build()
    iso_surfer.activate()
    assert iso_surfer.on is True
    iso_surfer.s0.on.assert_called_once()

def test_deactivate(iso_surfer):
    iso_surfer.build()
    iso_surfer.activate()
    iso_surfer.deactivate()
    assert iso_surfer.on is False
    iso_surfer.s0.off.assert_called_once()

def test_check_volume(iso_surfer):
    assert iso_surfer.check_volume() is True
    iso_surfer.volume = None
    assert iso_surfer.check_volume() is False
