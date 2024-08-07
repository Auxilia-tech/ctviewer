from typing import List

import pytest
import numpy as np
import vedo
from vedo import Volume
from pyDICOS import CT, DcsLongString, Filename, ErrorLog

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

def create_temp_dcs_file(volume_data:List[np.ndarray], temp_dcs_file:str):
    CTObject = CT(
            CT.OBJECT_OF_INSPECTION_TYPE.enumTypeBaggage,
            CT.OOI_IMAGE_CHARACTERISTICS.enumHighEnergy,
            CT.IMAGE_FLAVOR.enumVolume,
            CT.PHOTOMETRIC_INTERPRETATION.enumMonochrome2,
        )

    CTObject.SetImageAcquisitionDuration(5.2)
    DCS = DcsLongString("HIGH ENERGY SCAN")
    CTObject.SetScanDescription(DCS)

    CTObject.SetNumberOfSections(len(volume_data))

    for n, array in enumerate(volume_data):
        assert array.ndim == 3, "Data must be 3D"
        assert array.dtype == np.uint16, "Data must be uint16"

        section = CTObject.GetSectionByIndex(n)
        volume = section.GetPixelData()
        volume.set_data(volume, array)

    _err = ErrorLog()
    if not CTObject.Write(
        Filename(str(temp_dcs_file)), _err, CT.TRANSFER_SYNTAX.enumLittleEndianExplicit
    ):
        raise RuntimeError(
        f"Failed to write DICOS file: {str(temp_dcs_file)}\n{_err.GetErrorLog().Get()}"
    )

def test_read_npy(reader, tmp_path):
    # Create a temporary .npy file
    temp_npy_file = tmp_path / "temp_volume.npy"
    volume_data = np.random.rand(10, 10, 10)
    np.save(temp_npy_file, volume_data)
    
    # Test reading the .npy file
    volume, properties = reader(str(temp_npy_file))
    assert isinstance(volume, Volume)
    assert np.array_equal(volume.tonumpy(), volume_data)
    assert properties == reader.properties
    assert properties["spacing"] == (1, 1, 1)
    assert properties["origin"] == (0, 0, 0)
    assert properties["is_mask"] == False

def test_read_mhd(reader, tmp_path):
    # Create a temporary .mhd file
    temp_nii_gz_file = tmp_path / "temp_volume.mhd"
    volume_data = Volume(np.random.rand(10, 10, 10))
    vedo.write(volume_data, str(temp_nii_gz_file))
    
    # Test reading the .mhd file
    volume, properties = reader(str(temp_nii_gz_file))
    assert isinstance(volume, Volume)
    assert np.array_equal(volume.tonumpy(), volume_data.tonumpy())
    assert properties == reader.properties
    assert properties["is_mask"] == False

def test_read_dcs(reader, tmp_path):
    # Create a temporary .dcs file
    temp_dcs_file = tmp_path / "temp_volume.dcs"
    volume_data = np.random.rand(10, 10, 10).astype(np.uint16)
    create_temp_dcs_file([volume_data], str(temp_dcs_file))
    
    # Test reading a .dcs file
    volume, properties = reader(str(temp_dcs_file))
    assert isinstance(volume, Volume)
    assert properties["is_mask"] == False
    assert np.array_equal(volume.tonumpy(), volume_data)

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
