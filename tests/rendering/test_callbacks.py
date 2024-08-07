import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_renderer():
    return MagicMock()

def test_initialization(mock_callbacks, mock_renderer):
    assert mock_callbacks.renderer == mock_renderer

def test_add(mock_callbacks, mock_renderer):
    obj = "test_object"
    mock_callbacks.add(obj)
    mock_renderer.add.assert_called_once_with(obj)

def test_background(mock_callbacks, mock_renderer):
    mock_renderer.background.return_value = "background_color"
    assert mock_callbacks.background() == "background_color"
    mock_renderer.background.assert_called_once()

def test_render(mock_callbacks, mock_renderer):
    mock_callbacks.render()
    mock_renderer.render.assert_called_once()

def test_add_slider(mock_callbacks, mock_renderer):
    mock_callbacks.add_slider(0, 1, 0.5, title="Slider")
    mock_renderer.add_slider.assert_called_once_with(0, 1, 0.5, title="Slider")

def test_add_slider3d(mock_callbacks, mock_renderer):
    mock_callbacks.add_slider3d(0, 1, 0.5, title="3D Slider")
    mock_renderer.add_slider3d.assert_called_once_with(0, 1, 0.5, title="3D Slider")

def test_remove(mock_callbacks, mock_renderer):
    name = "object_name"
    mock_callbacks.remove(name)
    mock_renderer.remove.assert_called_once_with(name)

def test_clear(mock_callbacks, mock_renderer):
    mock_callbacks.clear()
    mock_renderer.clear.assert_called_once()
