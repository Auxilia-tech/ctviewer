from typing import Tuple, List

from vedo import Volume, Image, np
from pydicos import dcsread

from ctviewer.utils import connected_components_3d

# create a new reader class
class Reader:
    """
    A class for reading and processing medical image data.

    Attributes:
    - properties: A dictionary containing various properties of the volume.

    """

    def __init__(self):
        """
        Initializes the reader with default properties.

        """
        self.properties = {"spacing": (1, 1, 1), "origin": (0, 0, 0), "is_proj": False, "is_mask": False, "poses": [], "flag_poses": [], "labels": []}

    def __call__(self, path: str) -> Tuple[Volume, dict]:
        """
        Reads the volume data from the specified path and returns the volume and properties.

        Args:
        - path: A string representing the path to the volume file.

        Returns:
        - volume: An instance of the Volume class representing the volume data.
        - properties: A dictionary containing various properties of the volume.

        """
        ext = "nii.gz" if path.endswith(".nii.gz") else path.split(".")[-1]
        if ext == 'npy':
            data = np.load(path)
            volume = Volume(data)
            smin, smax = volume.dataset.GetScalarRange()
            if smin == 0 and smax < 100: # check if the volume is a mask.
                self.properties = connected_components_3d(volume, connectivity = 26, reshape_factor = 4)
        elif ext == 'nii.gz' or ext == 'mhd' or ext == 'dcm':
            volume = Volume(path)
            smin, smax = volume.dataset.GetScalarRange()
            if smin == 0 and smax < 100: # check if the volume is a mask.
                self.properties = connected_components_3d(volume, connectivity = 26, reshape_factor = 4)
            else:
                self.properties["spacing"] = volume.spacing()
                self.properties["origin"] = volume.origin()
        elif ext == 'dcs':
            ct = dcsread(path)
            data = ct.get_data()
            if isinstance(data, np.ndarray):
                volume = Volume(data)
            elif isinstance(data, List):
                if data[0].shape[0] == 1: # check if the volume is a projection
                    self.properties["is_proj"] = True
                    volume = Image(data[0][0]/ np.max(data[0][0]) * 255, channels=1)
                else:
                    volume = Volume(data[0])
                    if ct.GetDeviceManufacturer().Get() == "Analogic":
                        volume = volume.threshold(above=0, below=350, replace=0).operation("+", 1300)
            elif isinstance(data, dict):
                volume = self.Read_TDR_data(data) 
                volume = Volume(volume)
            else:
                raise ValueError("Invalid data type")
        return volume, self.properties
    
    def Read_TDR_data(self, metadata_dict: dict) -> np.ndarray:
        """
        Reads a TDR file and returns the list of PTOs.

        Args:
        - metadata_dict: A dictionary containing the metadata of the TDR file.

        Returns:
        - mask: An ndarray representing the binary mask.
        - properties: A dictionary containing various properties of the mask.

        """
        PTOs = metadata_dict["PTOs"]
        max_dims = [0, 0, 0]
        self.properties["is_mask"] = True

        for pto in PTOs:
            assert "Base" in pto and "Extent" in pto, "Base or Extent not found in PTO"
            base = [int(pto["Base"]["z"]), int(pto["Base"]["y"]), int(pto["Base"]["x"])]
            extent = [int(pto["Extent"]["z"]), int(pto["Extent"]["y"]), int(pto["Extent"]["x"])]
            pos =  [base[0], base[0] + extent[0], base[1], base[1] + extent[1], base[2], base[2] + extent[2]]
            max_dims = [max(max_dims[0], pos[1]), max(max_dims[1], pos[3]), max(max_dims[2], pos[5])]
            self.properties["poses"].append(np.array(pos))
            self.properties["flag_poses"].append(np.array([base[0] + extent[0]//2, base[1] + extent[1]//2, base[2] + extent[2]]))
            if "Assessment" in pto and "description" in pto["Assessment"]:
                self.properties["labels"].append(str(pto["Assessment"]["description"]))
            else:
                self.properties["labels"].append("Threat")

        mask = np.zeros(max_dims, dtype=np.uint8)
        for pto in PTOs:
            assert "Base" in pto and "Extent" in pto, "Base or Extent not found in PTO"
            if "Bitmap" in pto and len(pto["Bitmap"].shape) > 0:
                base = [int(pto["Base"]["z"]), int(pto["Base"]["y"]), int(pto["Base"]["x"])]
                extent = [int(pto["Extent"]["z"]), int(pto["Extent"]["y"]), int(pto["Extent"]["x"])]
                temp_mask = mask[base[0]:base[0]+extent[0], base[1]:base[1]+extent[1], base[2]:base[2]+extent[2]]
                temp_mask = np.logical_or(temp_mask, pto["Bitmap"].astype(np.uint8))
                mask[base[0]:base[0] + extent[0], base[1]:base[1] + extent[1], base[2]:base[2] + extent[2]] = temp_mask
        
        if mask.sum() == 0:
            print("Warning: No mask found in PTOs")
            mask = np.zeros((1, 1, 1), dtype=np.uint8)

        return mask
        
    def reset_properties(self):
        """ Reset the properties to default values. """
        self.__init__()