import pytest
from ctviewer.rendering import RayCaster

@pytest.fixture
def ray_caster(temp_volume_data, ogb, alpha, mock_callbacks):
    """ Create a RayCaster instance for testing """
    return RayCaster(volume=temp_volume_data, ogb=ogb, alpha=alpha, callbacks=mock_callbacks)

def test_initialization(ray_caster, temp_volume_data, ogb, alpha, mock_callbacks):
    """
    Test the initialization of the RayCaster object.

    Args:
        ray_caster (RayCaster): The RayCaster object to be tested.
        temp_volume_data (VolumeData): The temporary volume data object.
        ogb (float): The opacity gradient base value.
        alpha (float): The alpha value.
        mock_callbacks (list): The list of mock callbacks.

    Returns:
        None
    """
    assert ray_caster.volume == temp_volume_data
    assert ray_caster.ogb == ogb
    assert ray_caster.alpha == alpha
    assert ray_caster.callbacks == mock_callbacks
    assert ray_caster.on is False

def test_build(ray_caster, mock_callbacks):
    """ Test the build method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    assert mock_callbacks.add_slider.called
    assert len(ray_caster.get_sliders()) == 3
    assert ray_caster.hist is not None

def test_setOTF(ray_caster):
    """ Test the setOTF method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    ray_caster.setOTF()
    otf = ray_caster.opacityTransferFunction
    assert otf.GetSize() > 0

def test_update_mode(ray_caster):
    """ Test the update_mode method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    ray_caster.update_mode(volume_mode=1)
    assert ray_caster.volume_mode == 1

def test_update_sliders(ray_caster):
    """ Test the update_sliders method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    ray_caster.update_sliders((0.2, 0.4, 0.6))
    assert ray_caster.alphaslider0 == 0.2
    assert ray_caster.alphaslider1 == 0.4
    assert ray_caster.alphaslider2 == 0.6

def test_activate(ray_caster):
    """ Test the activate method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    ray_caster.activate(volume_mode=1)
    assert ray_caster.on is True

def test_deactivate(ray_caster):
    """ Test the deactivate method of the RayCaster object. """
    ray_caster.build(volume_mode=0)
    ray_caster.activate(volume_mode=1)
    ray_caster.deactivate()
    assert ray_caster.on is False

def test_check_volume(ray_caster):
    """ Test the check_volume method of the RayCaster object. """
    assert ray_caster.check_volume() is True
