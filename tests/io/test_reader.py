import pytest
import numpy as np
from vedo import Volume
from ctviewer.io import Reader

@pytest.fixture
def reader():
    return Reader()

def test_initialization(reader):
    # Check initial properties
    assert reader.properties == {
        "spacing": (1, 1, 1),
        "origin": (0, 0, 0),
        "is_mask": False,
        "poses": [],
        "flag_poses": [],
        "labels": []
    }

def test_read_npy(reader):
    # Test reading a .npy file
    volume, properties = reader("../datasets/ts_image_74_0000.npy")
    assert isinstance(volume, Volume)
    assert properties == reader.properties
    assert properties["spacing"] == (1, 1, 1)
    assert properties["origin"] == (0, 0, 0)
    assert properties["is_mask"] == False

def test_read_nii_gz(reader):
    # Test reading a .nii.gz file
    volume, properties = reader("../datasets/ts_image_74_0000.nii.gz")
    assert isinstance(volume, Volume)
    assert properties == reader.properties
    assert properties["is_mask"] == False

def test_read_dcs(reader):
    # Test reading a .dcs file
    volume, properties = reader("../datasets/ts_Mask_680_0000.dcs")
    assert isinstance(volume, Volume)
    assert properties["is_mask"] == True
    assert len(properties["poses"]) > 0
    assert len(properties["labels"]) > 0
    assert properties["is_mask"] == True

def test_read_tdr_data(reader):
    # Test the internal method Read_TDR_data if needed
    metadata_dict = {
        "PTOs": [
            {
                "Base": {"x": 0, "y": 0, "z": 0},
                "Extent": {"x": 5, "y": 5, "z": 5},
                "Bitmap": np.ones((5, 5, 5)),
                "Assessment": {"description": "Test"}
            }
        ]
    }
    mask = reader.Read_TDR_data(metadata_dict)
    assert mask.shape == (5, 5, 5)
    assert mask.sum() > 0
    assert reader.properties["is_mask"] == True
    assert reader.properties["labels"] == ["Test"]

def test_reset_properties(reader):
    # Modify properties and reset
    reader.properties["spacing"] = (2, 2, 2)
    reader.reset_properties()
    assert reader.properties == {
        "spacing": (1, 1, 1),
        "origin": (0, 0, 0),
        "is_mask": False,
        "poses": [],
        "flag_poses": [],
        "labels": []
    }
