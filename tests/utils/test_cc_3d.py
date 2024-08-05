import pytest
from ctviewer.io import Reader  # Replace with the actual import path
from ctviewer.utils import connected_components_3d  # Replace with the actual import path

@pytest.fixture
def volume():
    reader = Reader()
    volume, properties = reader("../datasets/ts_Mask_74_0000.nii.gz")  # Path to the test file
    return volume

def test_connected_components_3d(volume):
    volume_properties = connected_components_3d(volume, connectivity=26, reshape_factor=4)
    print("Volume Properties:", volume_properties)

    # Assertions can be added based on expected results, e.g.,
    assert volume_properties["is_mask"] is True
    assert "poses" in volume_properties
    assert "flag_poses" in volume_properties
    assert "labels" in volume_properties

    # For example, check if at least one component is found
    assert len(volume_properties["poses"]) > 0
    assert len(volume_properties["flag_poses"]) > 0
    assert len(volume_properties["labels"]) > 0
