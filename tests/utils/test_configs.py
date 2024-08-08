# tests/test_config_manager.py
import pytest
import json
from unittest.mock import patch, mock_open
from pathlib import Path
from ctviewer.utils.configs import ConfigManager

@pytest.fixture
def temp_config_file_path(tmp_path: Path):
    """ 
    Create a temporary config file for testing

    Args:
        tmp_path (Path): Temporary directory path

    Returns:
        str: Temporary config file path
    """
    config_file_path = tmp_path / "config.json"
    config_file_path.write_text(json.dumps({
        "default": {"key": "default_value"},
        "user": {"key": "user_value"}
    }))
    return str(config_file_path)

@pytest.fixture
def config_manager(temp_config_file_path):
    """ Create a ConfigManager instance for testing """
    return ConfigManager(temp_config_file_path)

def test_load_config(config_manager: ConfigManager):
    """ Test if the config is loaded correctly """
    assert config_manager.config == {
        "default": {"key": "default_value"},
        "user": {"key": "user_value"}
    }

def test_save_user_config(config_manager: ConfigManager, temp_config_file_path: str):
    """ Test if the user config is saved correctly """
    new_user_config = {"key": "new_user_value"}
    expected_output = json.dumps({
        "default": {"key": "default_value"},
        "user": new_user_config
    }, indent=4)
    
    with patch('builtins.open', mock_open()) as mocked_file:
        config_manager.save_user_config(new_user_config)
        mocked_file.assert_called_once_with(Path(temp_config_file_path), 'w')
        handle = mocked_file()
        handle.write.assert_called()
        written_content = ''.join(call.args[0] for call in handle.write.mock_calls)
        assert written_content == expected_output

def test_reset_user_config(config_manager: ConfigManager):
    """ Test if the user config is reset correctly """
    with patch.object(config_manager, 'save_user_config') as mock_save_user_config:
        config_manager.reset_user_config()
        assert config_manager.config['user'] == {"key": "default_value"}
        mock_save_user_config.assert_called_once_with({"key": "default_value"})

def test_get_user_config(config_manager: ConfigManager):
    """ Test if the user config is retrieved correctly """
    user_config = config_manager.get_user_config()
    assert user_config == {"key": "user_value"}