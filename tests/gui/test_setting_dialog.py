import pytest
from PyQt6 import QtWidgets, QtCore
from pytestqt.plugin import QtBot
from ctviewer.gui import SettingDialog

@pytest.fixture(scope="module")
def app():
    app = QtWidgets.QApplication([])
    yield app

@pytest.fixture
def dialog(qtbot):
    dlg = SettingDialog()
    qtbot.addWidget(dlg)
    return dlg

def test_initialization(dialog):
    # Check initial values are correctly loaded from config
    config = dialog.get_user_config()
    assert dialog.windowTitle() == 'Settings'
    assert dialog.ogb_cmap1_edit.text() == str(config['ogb_cmap'][0])
    assert dialog.ogb_cmap2_edit.text() == str(config['ogb_cmap'][1])
    assert dialog.ogb_cmap3_edit.text() == str(config['ogb_cmap'][2])
    assert dialog.alpha1_edit.text() == str(config['alpha_weights'][0])
    assert dialog.alpha2_edit.text() == str(config['alpha_weights'][1])
    assert dialog.alpha3_edit.text() == str(config['alpha_weights'][2])

    # Check if all extensions are checked
    for i in range(dialog.exts_layout.count()):
        checkbox = dialog.exts_layout.itemAt(i).widget()
        assert checkbox.isChecked()

def test_update_settings(dialog, qtbot: QtBot):
    # Simulate user changes text fields
    dialog.alpha1_edit.setText('0.1')
    dialog.alpha2_edit.setText('0.2')
    dialog.alpha3_edit.setText('0.3')
    dialog.ogb_cmap1_edit.setText('10')
    dialog.ogb_cmap2_edit.setText('20')
    dialog.ogb_cmap3_edit.setText('30')
    # # Uncheck the first extension checkbox
    first_checkbox = dialog.exts_layout.itemAt(0).widget()
    qtbot.mouseClick(first_checkbox, QtCore.Qt.MouseButton.LeftButton)

    # Apply changes
    qtbot.mouseClick(dialog.okButton, QtCore.Qt.MouseButton.LeftButton)

    # Verify settings are updated
    updated_config = dialog.get_user_config()
    assert updated_config['ogb_cmap'] == [10, 20, 30]
    assert updated_config['alpha_weights'] == [0.1, 0.2, 0.3]
    # assert first_checkbox.text() not in updated_config['exts'] # TODO: To be added in the next PR

def test_reset_settings(dialog, qtbot):
    # Simulate user changes
    qtbot.keyClicks(dialog.ogb_cmap1_edit, '10')
    qtbot.keyClicks(dialog.alpha1_edit, '1.0')

    # Reset settings
    qtbot.mouseClick(dialog.resetButton, QtCore.Qt.MouseButton.LeftButton)

    # Verify settings are reset to default
    config = dialog.get_user_config()
    assert dialog.ogb_cmap1_edit.text() == str(config['ogb_cmap'][0])
    assert dialog.alpha1_edit.text() == str(config['alpha_weights'][0])

def test_getters(dialog):
    # Test getter methods
    config = dialog.get_user_config()
    assert dialog.get_colors() == config['colors']
    assert dialog.get_ogb_cmap() == config['ogb_cmap']
    assert dialog.get_alpha_weights() == config['alpha_weights']
    assert dialog.get_exts() == tuple(config['exts'])
    assert dialog.get_mask_classes() == config['mask_classes']
    assert dialog.get_user_config() == config
    assert dialog.get_config_manager() == dialog.config_manager
    assert dialog.get_ogb() == dialog.ogb
    assert dialog.get_alpha() == dialog.alpha
    assert dialog.get_current_config() == {
        'ogb': dialog.ogb,
        'alpha': dialog.alpha,
        'mask_classes': dialog.get_mask_classes()
    }
