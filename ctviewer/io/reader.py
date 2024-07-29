from typing import Tuple
from vedo import Volume, np

from pydicos import dcsread

# create a new reader class
class Reader:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, path: str) -> Tuple[Volume, dict]:
        ext = "nii.gz" if path.endswith(".nii.gz") else path.split(".")[-1]
        self.properties = {"spacing": (1, 1, 1), "origin": (0, 0, 0), "is_tdr": False, "poses": [], "flag_poses": [], "labels": []}
        if ext == 'npy':
            data = np.load(path)
            vol = Volume(data)
        elif ext == 'nii.gz' or ext == 'mhd' or ext == 'dcm':
            vol = Volume(path)
            self.properties["spacing"] = vol.spacing()
            self.properties["origin"] = vol.origin()
        elif ext == 'dcs':
            data = dcsread(path).get_data()
            if isinstance(data, np.ndarray):
                vol = Volume(data)
            elif isinstance(data, dict):
                vol, self.properties = self.Read_TDR_data(data)
                vol = Volume(vol)
        return vol, self.properties
    
    def Read_TDR_data(self, metadata_dict: dict) -> Tuple[np.ndarray, dict]:
        """
        Read a TDR file and return the list of PTOs

        Returns:
        - bboxes: list of bounding boxes
        - labels: list of labels
        - masks: list of binary masks

        """
        PTOs = metadata_dict["PTOs"]
        max_dims = [0, 0, 0]
        self.properties["is_tdr"] = True
        

        for pto in PTOs:
            assert "Base" in pto and "Extent" in pto, "Base or Extent not found in PTO"
            base = [int(pto["Base"]["x"]), int(pto["Base"]["y"]), int(pto["Base"]["z"])]
            extent = [int(pto["Extent"]["x"]), int(pto["Extent"]["y"]), int(pto["Extent"]["z"])]
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
                base = [int(pto["Base"]["x"]), int(pto["Base"]["y"]), int(pto["Base"]["z"])]
                extent = [int(pto["Extent"]["x"]), int(pto["Extent"]["y"]), int(pto["Extent"]["z"])]
                mask[base[0]:base[0]+extent[0], base[1]:base[1]+extent[1], base[2]:base[2]+extent[2]] = pto["Bitmap"].astype(np.uint8)
        
        if mask.sum() == 0:
            print("Warning: No mask found in PTOs")
            mask[0, 0, 0] = 1  # add a dummy mask

        return mask, self.properties