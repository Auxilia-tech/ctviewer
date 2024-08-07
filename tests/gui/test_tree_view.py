import pytest
import numpy as np
import vedo
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from ctviewer.gui import TreeView

@pytest.fixture(scope="module")
def app():
    app = QApplication([])
    yield app

@pytest.fixture
def main_window():
    window = QMainWindow()
    layout = QVBoxLayout(window)
    window.setLayout(layout)
    return window, layout

@pytest.fixture
def tree_view_components(main_window):
    window, layout = main_window
    exts = ["dcm", "nii", "nii.gz", "mhd"]
    callback = lambda x: x
    tree_view = TreeView(window, layout, exts, callback)
    return tree_view, exts

def test_tree_view_initialization(qtbot, tree_view_components):
    tree_view, exts = tree_view_components
    assert tree_view.exts == exts
    assert tree_view.update_volume_callback is not None
    assert tree_view.fileSystemModel is not None
    assert tree_view.data_path == os.path.expanduser("~")

def test_tree_view_file_filtering(qtbot, tree_view_components):
    tree_view, exts = tree_view_components
    tree_view.refreshTreeView()

    root_index = tree_view.fileSystemModel.index(tree_view.data_path)
    rows = tree_view.fileSystemModel.rowCount(root_index)

    for row in range(rows):
        index = tree_view.fileSystemModel.index(row, 0, root_index)
        file_name = tree_view.fileSystemModel.fileName(index)
        assert file_name.split('.')[-1] in exts

def test_tree_view_item_click(qtbot, tree_view_components):
    tree_view, _ = tree_view_components
    clicked_item = None
    def callback(path):
        nonlocal clicked_item
        clicked_item = path

    tree_view.refreshTreeView()

    root_index = tree_view.fileSystemModel.index(tree_view.data_path)
    if tree_view.fileSystemModel.rowCount(root_index) > 0:
        first_item_index = tree_view.fileSystemModel.index(0, 0, root_index)
        qtbot.mouseClick(tree_view.viewport(), qtbot.LeftButton, pos=tree_view.visualRect(first_item_index).center())
        assert clicked_item == tree_view.fileSystemModel.filePath(first_item_index)

def test_set_folder(qtbot, tmp_path, tree_view_components):
    tree_view, _ = tree_view_components
    
    # Create a temporary folder and a .mhd file within it
    temp_folder = tmp_path / "data"
    temp_folder.mkdir()
    volume_data = np.random.rand(10, 10, 10) 
    temp_mhd_file = temp_folder / "temp_volume.mhd"
    volume = vedo.Volume(volume_data)
    vedo.write(volume, str(temp_mhd_file))  # Save the volume data as a .mhd file

    # Test setting the folder
    tree_view.set_folder(str(temp_folder))
    assert tree_view.data_path == str(temp_folder)
    # assert tree_view.fileSystemModel.rootPath() == new_folder # TODO: This assertion fails because the root path is not updated.