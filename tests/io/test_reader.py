import pytest
import numpy as np
import vedo
from vedo import Volume

def test_initialization(mock_reader):
    """ Test the initialization of the Reader object. """
    assert mock_reader.properties == {
        "spacing": (1, 1, 1),
        "origin": (0, 0, 0),
        "is_mask": False,
        "poses": [],
        "flag_poses": [],
        "labels": []
    }

def test_read_npy(mock_reader, temp_npy_path, volume_data):
    """ Test reading the .npy file """
    volume, properties = mock_reader(temp_npy_path)
    assert isinstance(volume, Volume)
    assert np.array_equal(volume.tonumpy(), volume_data)
    assert properties == mock_reader.properties
    assert properties["spacing"] == (1, 1, 1)
    assert properties["origin"] == (0, 0, 0)
    assert properties["is_mask"] == False

def test_read_mhd(mock_reader, temp_mhd_path, volume_data):
    """ Test reading the .mhd file """
    # Test reading the .mhd file
    volume, properties = mock_reader(temp_mhd_path)
    assert isinstance(volume, Volume)
    assert np.array_equal(volume.tonumpy(), volume_data)
    assert properties == mock_reader.properties
    assert properties["is_mask"] == False

def test_read_dcs(mock_reader, temp_dcs_file_path, volume_data):
    """ Test reading the .dcm file """
    volume, properties = mock_reader(temp_dcs_file_path)
    assert isinstance(volume, Volume)
    assert properties["is_mask"] == False
    assert np.array_equal(volume.tonumpy(), volume_data)

def test_read_mask(mock_reader, temp_tdr_file_path, mask_data):
    """ Test reading the mask file """
    volume, properties = mock_reader(temp_tdr_file_path)
    assert isinstance(volume, Volume)
    assert properties["is_mask"] == True
    assert properties["labels"] == ["Label1", "Label2"]
    # Check if the mask has the same number of non-zero elements as the mask data
    assert len(np.nonzero(volume.tonumpy())[0]) == len(np.nonzero(mask_data)[0])

def test_read_tdr_data(mock_reader):
    """" Test the internal method Read_TDR_data if needed """
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
    mask = mock_reader.Read_TDR_data(metadata_dict)
    assert mask.shape == (5, 5, 5)
    assert mask.sum() > 0
    assert mock_reader.properties["is_mask"] == True
    assert mock_reader.properties["labels"] == ["Test"]

def test_reset_properties(mock_reader):
    """ Test the reset_properties method of the Reader class """
    mock_reader.properties["spacing"] = (2, 2, 2)
    mock_reader.reset_properties()
    assert mock_reader.properties == {
        "spacing": (1, 1, 1),
        "origin": (0, 0, 0),
        "is_mask": False,
        "poses": [],
        "flag_poses": [],
        "labels": []
    }
