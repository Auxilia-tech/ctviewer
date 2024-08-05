import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
import json
from ctviewer.utils import ConfigManager  # Replace with the correct import path

@pytest.fixture
def mock_config_file():
    return 'test_config.json'

@pytest.fixture
def config_manager(mock_config_file):
    with patch.object(Path, 'exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps({
             "default": {"key": "default_value"},
             "user": {"key": "user_value"}
         }))):
        return ConfigManager(config_file=mock_config_file)

def test_load_config(config_manager):
    assert config_manager.config == {
        "default": {"key": "default_value"},
        "user": {"key": "user_value"}
    }

def test_save_user_config(config_manager, mock_config_file):
    new_user_config = {"key": "new_user_value"}
    expected_output = json.dumps({
        "default": {"key": "default_value"},
        "user": new_user_config
    }, indent=4)
    
    with patch('builtins.open', mock_open()) as mocked_file:
        config_manager.save_user_config(new_user_config)
        # Check if the file was opened correctly
        mocked_file.assert_called_once_with(Path(mock_config_file), 'w')
        
        # Check if the correct content was written to the file
        handle = mocked_file()
        handle.write.assert_called()
        written_content = ''.join(call.args[0] for call in handle.write.mock_calls)
        assert written_content == expected_output



def test_reset_user_config(config_manager):
    with patch.object(ConfigManager, 'save_user_config') as mock_save_user_config:
        config_manager.reset_user_config()
        assert config_manager.config['user'] == {"key": "default_value"}
        mock_save_user_config.assert_called_once_with({"key": "default_value"})

def test_get_user_config(config_manager):
    user_config = config_manager.get_user_config()
    assert user_config == {"key": "user_value"}