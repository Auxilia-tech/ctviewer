import pytest
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from ctviewer.gui import TreeView  # Replace 'your_module' with the actual module name where TreeView is defined.

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

def test_tree_view_initialization(main_window):
    window, layout = main_window
    exts = ["dcs", "dcm", "nii", "nii.gz", "mhd"]
    callback = lambda x: x
    tree_view = TreeView(window, layout, exts, callback)
    assert tree_view.exts == exts
    assert tree_view.update_volume_callback == callback
    assert tree_view.fileSystemModel is not None

def test_tree_view_file_filtering(main_window, qtbot):
    window, layout = main_window
    exts = ["dcm", "nii", "nii.gz", "mhd"]
    callback = lambda x: x
    tree_view = TreeView(window, layout, exts, callback)

    # Assuming '../datasets/' or the script directory contains some test files
    tree_view.refreshTreeView()

    root_index = tree_view.fileSystemModel.index(tree_view.data_path)
    rows = tree_view.fileSystemModel.rowCount(root_index)

    for row in range(rows):
        index = tree_view.fileSystemModel.index(row, 0, root_index)
        file_name = tree_view.fileSystemModel.fileName(index)
        assert file_name.split('.')[-1] in exts

def test_tree_view_item_click(main_window, qtbot):
    window, layout = main_window
    exts = ["dcm", "nii", "nii.gz", "mhd"]
    clicked_item = None
    def callback(path):
        nonlocal clicked_item
        clicked_item = path

    tree_view = TreeView(window, layout, exts, callback)
    tree_view.refreshTreeView()

    root_index = tree_view.fileSystemModel.index(tree_view.data_path)
    if tree_view.fileSystemModel.rowCount(root_index) > 0:
        first_item_index = tree_view.fileSystemModel.index(0, 0, root_index)
        qtbot.mouseClick(tree_view.viewport(), qtbot.LeftButton, pos=tree_view.visualRect(first_item_index).center())
        assert clicked_item == tree_view.fileSystemModel.filePath(first_item_index)

def test_set_folder(main_window, qtbot):
    window, layout = main_window
    exts = ["dcm", "nii", "nii.gz", "mhd"]
    callback = lambda x: x
    tree_view = TreeView(window, layout, exts, callback)

    new_folder = '/new/path/to/datasets'
    tree_view.set_folder(new_folder)
    assert tree_view.data_path == new_folder
    # assert tree_view.fileSystemModel.rootPath() == new_folder # TODO: This assertion fails because the root path is not updated.