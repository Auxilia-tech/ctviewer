import pytest
from ctviewer.rendering.callbacks import RendererCallbacks

@pytest.fixture
def renderer_callbacks(mock_object):
    """ Create a RendererCallbacks instance for testing """
    return RendererCallbacks(mock_object)

def test_initialization(renderer_callbacks, mock_object):
    """ Test if the RendererCallbacks instance is initialized correctly """
    assert renderer_callbacks.renderer == mock_object

def test_add(renderer_callbacks, mock_object):
    """ Test if the add method adds an object to the renderer """
    obj = "test_object"
    renderer_callbacks.add(obj)
    mock_object.add.assert_called_once_with(obj)

def test_background(renderer_callbacks, mock_object):
    """ Test if the background method returns the background color """
    mock_object.background.return_value = "background_color"
    assert renderer_callbacks.background() == "background_color"
    mock_object.background.assert_called_once()

def test_render(renderer_callbacks, mock_object):
    """ Test if the render method renders the scene """
    renderer_callbacks.render()
    mock_object.render.assert_called_once()

def test_add_slider(renderer_callbacks, mock_object):
    """ Test if the add_slider method adds a slider to the renderer """
    renderer_callbacks.add_slider(0, 1, 0.5, title="Slider")
    mock_object.add_slider.assert_called_once_with(0, 1, 0.5, title="Slider")

def test_add_slider3d(renderer_callbacks, mock_object):
    renderer_callbacks.add_slider3d(0, 1, 0.5, title="3D Slider")
    mock_object.add_slider3d.assert_called_once_with(0, 1, 0.5, title="3D Slider")

def test_remove(renderer_callbacks, mock_object):
    """ Test if the remove method removes an object from the renderer """
    name = "object_name"
    renderer_callbacks.remove(name)
    mock_object.remove.assert_called_once_with(name)

def test_clear(renderer_callbacks, mock_object):
    """ Test if the clear method clears the renderer """
    renderer_callbacks.clear()
    mock_object.clear.assert_called_once()
