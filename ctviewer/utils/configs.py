import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self.load_config()

    def load_config(self):
        """Load the .json configuration file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize with an empty structure or predefined defaults
            return {"default": {}, "user": {}}

    def save_user_config(self, user_config):
        """Save the updated user configuration."""
        self.config['user'] = user_config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def reset_user_config(self):
        """Reset user config to the default values."""
        self.config['user'] = self.config['default'].copy()
        self.save_user_config(self.config['user'])

    def get_user_config(self):
        """Get the current user configuration."""
        return self.config['user']