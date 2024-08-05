import pytest
from unittest.mock import MagicMock
from ctviewer.rendering.callbacks import RendererCallbacks

@pytest.fixture
def mock_renderer():
    return MagicMock()

@pytest.fixture
def renderer_callbacks(mock_renderer):
    return RendererCallbacks(mock_renderer)

def test_initialization(renderer_callbacks, mock_renderer):
    assert renderer_callbacks.renderer == mock_renderer

def test_add(renderer_callbacks, mock_renderer):
    obj = "test_object"
    renderer_callbacks.add(obj)
    mock_renderer.add.assert_called_once_with(obj)

def test_background(renderer_callbacks, mock_renderer):
    mock_renderer.background.return_value = "background_color"
    assert renderer_callbacks.background() == "background_color"
    mock_renderer.background.assert_called_once()

def test_render(renderer_callbacks, mock_renderer):
    renderer_callbacks.render()
    mock_renderer.render.assert_called_once()

def test_add_slider(renderer_callbacks, mock_renderer):
    renderer_callbacks.add_slider(0, 1, 0.5, title="Slider")
    mock_renderer.add_slider.assert_called_once_with(0, 1, 0.5, title="Slider")

def test_add_slider3d(renderer_callbacks, mock_renderer):
    renderer_callbacks.add_slider3d(0, 1, 0.5, title="3D Slider")
    mock_renderer.add_slider3d.assert_called_once_with(0, 1, 0.5, title="3D Slider")

def test_remove(renderer_callbacks, mock_renderer):
    name = "object_name"
    renderer_callbacks.remove(name)
    mock_renderer.remove.assert_called_once_with(name)

def test_clear(renderer_callbacks, mock_renderer):
    renderer_callbacks.clear()
    mock_renderer.clear.assert_called_once()
