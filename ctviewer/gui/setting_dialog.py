from PyQt6 import QtWidgets

from ctviewer.utils import ConfigManager

class SettingDialog(QtWidgets.QDialog):
    """
    A dialog window for managing settings in the CT Viewer application.

    Attributes:
        colors (list): The list of colors.
        ogb_cmap (list): The list of ogb_cmap values.
        alpha_weights (list): The list of alpha weights.
        exts (list): The list of extensions.
        mask_classes (list): The list of mask classes.
        user_config (dict): The user configuration settings.
        config_manager (ConfigManager): The configuration manager.

    Methods:
        setup(): Set up the settings dialog.
        updateSettings(): Update the user settings based on the dialog input.
        reset_settings(): Reset the settings to their default values.
        get_colors(): Get the list of colors.
        get_ogb_cmap(): Get the list of ogb_cmap values.
        get_alpha_weights(): Get the list of alpha weights.
        get_exts(): Get the list of extensions.
        get_mask_classes(): Get the list of mask classes.
        get_user_config(): Get the user configuration settings.
        get_config_manager(): Get the configuration manager.
        get_ogb(): Get the ogb values.
        get_alpha(): Get the alpha values.
    """

    def __init__(self, parent=None):
        """
        Initialize the settings dialog.

        Args:
            parent (QWidget): The parent widget.
        """
        super(SettingDialog, self).__init__(parent)

        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 300, 200)
        self.layout_ = QtWidgets.QVBoxLayout(self)
        
        # Set up the settings dialog
        self.config_manager = ConfigManager()
        self.user_config = self.config_manager.get_user_config()

        # Load current user settings or defaults if not set
        colors = self.user_config.get('colors')
        ogb_cmap = self.user_config.get('ogb_cmap')
        alpha_weights = self.user_config.get('alpha_weights')
        exts = self.user_config.get('exts', ['dcs', 'dcm', 'nii.gz', "mhd"])

        self.ogb_cmap1_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap1_edit.setText(str(ogb_cmap[0]))
        self.layout_.addWidget(self.ogb_cmap1_edit)

        self.ogb_cmap2_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap2_edit.setText(str(ogb_cmap[1]))
        self.layout_.addWidget(self.ogb_cmap2_edit)

        self.ogb_cmap3_edit = QtWidgets.QLineEdit(self)
        self.ogb_cmap3_edit.setText(str(ogb_cmap[2]))
        self.layout_.addWidget(self.ogb_cmap3_edit)

        self.alpha1_edit = QtWidgets.QLineEdit(self)
        self.alpha1_edit.setText(str(alpha_weights[0]))
        self.layout_.addWidget(self.alpha1_edit)

        self.alpha2_edit = QtWidgets.QLineEdit(self)
        self.alpha2_edit.setText(str(alpha_weights[1]))
        self.layout_.addWidget(self.alpha2_edit)

        self.alpha3_edit = QtWidgets.QLineEdit(self)
        self.alpha3_edit.setText(str(alpha_weights[2]))
        self.layout_.addWidget(self.alpha3_edit)

        # add a checkbox list for extenstions that can be loaded and save them in self to be used in updateSettings
        # Add a vertival layout for the checkboxes
        self.exts_layout = QtWidgets.QVBoxLayout()
        for ext in exts:
            checkbox = QtWidgets.QCheckBox(ext, self)
            checkbox.setChecked(True)
            self.exts_layout.addWidget(checkbox)
        self.layout_.addLayout(self.exts_layout)

        self.resetButton = QtWidgets.QPushButton('Reset', self)
        self.resetButton.clicked.connect(self.reset_settings)
        self.layout_.addWidget(self.resetButton)

        self.okButton = QtWidgets.QPushButton('Apply', self)
        self.okButton.clicked.connect(lambda: self.updateSettings())
        self.layout_.addWidget(self.okButton)

        # Update the user settings
        self.ogb = [(ogb_cmap[0], colors[0]), (ogb_cmap[1],
                                                 colors[1]), (ogb_cmap[2], colors[2])]
        self.alpha = [(0, 1), (ogb_cmap[0], alpha_weights[0]),
                        (ogb_cmap[1], alpha_weights[1]), (ogb_cmap[2], alpha_weights[2])]

    def updateSettings(self):
        """
        Update the user settings based on the dialog input.
        """
        self.user_config['ogb_cmap'] = [
            int(self.ogb_cmap1_edit.text()),
            int(self.ogb_cmap2_edit.text()),
            int(self.ogb_cmap3_edit.text())
        ]
        self.user_config['alpha_weights'] = [
            float(self.alpha1_edit.text()),
            float(self.alpha2_edit.text()),
            float(self.alpha3_edit.text())
        ]
        # get the extensions that are checked in the exts_layout
        self.user_config['exts'] = [self.exts_layout.itemAt(i).widget().text() for i in range(self.exts_layout.count()) if self.exts_layout.itemAt(i).widget().isChecked()]

        # Get the value of the user settings
        ogb_cmap = self.user_config['ogb_cmap']
        alpha_weights = self.user_config['alpha_weights']
        colors = self.user_config['colors']
        self.config_manager.save_user_config(self.user_config)
        # Update the user settings
        self.ogb = [(ogb_cmap[0], colors[0]), (ogb_cmap[1],
                                                 colors[1]), (ogb_cmap[2], colors[2])]
        self.alpha = [(0, 1), (ogb_cmap[0], alpha_weights[0]),
                        (ogb_cmap[1], alpha_weights[1]), (ogb_cmap[2], alpha_weights[2])]
        self.close()

    def reset_settings(self):
        """
        Reset the settings to their default values.
        """
        self.config_manager.reset_user_config()
        self.user_config = self.config_manager.get_user_config()

        # Load current user settings or defaults if not set
        ogb_cmap = self.user_config.get('ogb_cmap')
        alpha_weights = self.user_config.get('alpha_weights')

        # Update the panel settings
        self.ogb_cmap1_edit.setText(str(ogb_cmap[0]))
        self.ogb_cmap2_edit.setText(str(ogb_cmap[1]))
        self.ogb_cmap3_edit.setText(str(ogb_cmap[2]))
        self.alpha1_edit.setText(str(alpha_weights[0]))
        self.alpha2_edit.setText(str(alpha_weights[1]))
        self.alpha3_edit.setText(str(alpha_weights[2]))
        self.exts_layout = QtWidgets.QVBoxLayout()
        for ext in self.user_config.get('exts'):
            checkbox = QtWidgets.QCheckBox(ext, self)
            checkbox.setChecked(True)
            self.exts_layout.addWidget(checkbox)
        
    def get_colors(self) -> list:
        """
        Get the list of colors.

        Returns:
            list: The list of colors.
        """
        return self.user_config.get('colors')
    
    def get_ogb_cmap(self) -> list:
        """
        Get the list of ogb_cmap values.

        Returns:
            list: The list of ogb_cmap values.
        """
        return self.user_config.get('ogb_cmap')
    
    def get_alpha_weights(self) -> list:
        """
        Get the list of alpha weights.

        Returns:
            list: The list of alpha weights.
        """
        return self.user_config.get('alpha_weights')
    
    def get_exts(self) -> tuple:
        """
        Get the tupe of extensions.

        Returns:
            tupe: The tupe of extensions.
        """
        return tuple(self.user_config.get('exts'))
    
    def get_mask_classes(self) -> list:
        """
        Get the list of mask classes.

        Returns:
            list: The list of mask classes.
        """
        return self.user_config.get('mask_classes')
    
    def get_user_config(self) -> dict:
        """
        Get the user configuration settings.

        Returns:
            dict: The user configuration settings.
        """
        return self.user_config
    
    def get_config_manager(self) -> ConfigManager:
        """
        Get the configuration manager.

        Returns:
            ConfigManager: The configuration manager.
        """
        return self.config_manager
    
    def get_ogb(self) -> list:
        """
        Return the ogb values.

        Returns:
            list: The ogb values.
        """
        return self.ogb
    
    def get_alpha(self) -> list:
        """
        Return the alpha values.

        Returns:
            list: The alpha values.
        """
        return self.alpha
    
    def get_current_config(self) -> dict:
        """
        Get the current configuration settings.

        Returns:
            dict: The current configuration settings.
        """
        return {
            'ogb': self.ogb,
            'alpha': self.alpha,
            'mask_classes': self.get_mask_classes(),
        }