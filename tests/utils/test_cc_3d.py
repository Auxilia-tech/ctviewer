from ctviewer.utils import connected_components_3d

def test_connected_components_3d(temp_mask_data):
    """ Test the connected_components_3d function. """
    volume_properties = connected_components_3d(temp_mask_data, connectivity=26, reshape_factor=4)
    print("Volume Properties:", volume_properties)

    # Assertions can be added based on expected results, e.g.,
    assert volume_properties["is_mask"] is True
    assert "poses" in volume_properties
    assert "flag_poses" in volume_properties
    assert "labels" in volume_properties

    # Check if there 2 connected components
    assert len(volume_properties["poses"]) == 2
    assert len(volume_properties["flag_poses"]) == 2
    assert len(volume_properties["labels"]) == 2
    assert volume_properties["labels"][0] == 1
    assert volume_properties["labels"][1] == 2
