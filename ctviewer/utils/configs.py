import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class ConfigManager:
    """A class for managing configuration settings.

    This class provides methods for loading, saving, resetting, and retrieving
    configuration settings from a JSON file.

    Attributes:
        config_file (str): The path to the configuration file.
        config (dict): The loaded configuration settings.

    Methods:
        load_config: Load the configuration file.
        save_user_config: Save the updated user configuration.
        reset_user_config: Reset the user configuration to default values.
        get_user_config: Get the current user configuration.
    """

    def __init__(self, config_file=ROOT / 'config.json'):
        self.config_file = Path(config_file)
        self.config = self.load_config()

    def load_config(self):
        """Load the .json configuration file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # raise not found error here
            assert False, f"Config file not found: {self.config_file}"

    def save_user_config(self, user_config):
        """Save the updated user configuration.

        Args:
            user_config (dict): The updated user configuration settings.
        """
        self.config['user'] = user_config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def reset_user_config(self):
        """Reset user config to the default values."""
        self.config['user'] = self.config['default'].copy()
        self.save_user_config(self.config['user'])

    def get_user_config(self):
        """Get the current user configuration.

        Returns:
            dict: The current user configuration settings.
        """
        return self.config['user']