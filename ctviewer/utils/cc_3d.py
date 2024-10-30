from vedo import Volume, np
import cc3d

def connected_components_3d(volume:Volume, connectivity=26, reshape_factor:float=4):
    """
    Compute connected components in 3D image.
    
    Parameters
    ----------
    volume : Volume
        The input volume to be processed.
    connectivity : int, optional
        The connectivity of the connected components.
        Only 4,8 (2D) and 26, 18, and 6 (3D) are allowed
    reshape_factor : float, optional
        The factor to reshape the volume.
    
    Returns
    -------
    volume_properties : dict
        The dictionary containing the properties of the connected components.
            - poses : list
                The list of poses to create the bounding boxes.
            - flag_poses : list
                The list of center of the upper face of the bounding boxes.
                Used to create the 3D flags.
            - labels : list 
                The list of class labels of the connected components
    """
    volume_properties = {"spacing": (1, 1, 1), "origin": (0, 0, 0), "is_proj": False, "is_mask": True, "poses": [], "flag_poses": [], "labels": []}
    volume.dilate((2*reshape_factor, 2*reshape_factor, 2*reshape_factor)).erode((reshape_factor, reshape_factor, reshape_factor))
    vol = volume.tonumpy()[::reshape_factor, ::reshape_factor, ::reshape_factor]
    labels_out, N = cc3d.connected_components(vol, connectivity=connectivity, return_N=True)
    stats = cc3d.statistics(labels_out)
    print("Number of objects in the volume:", N)
    for centroid, bounding_boxe, each_label in zip(stats['centroids'][1:], stats['bounding_boxes'][1:], cc3d.each(labels_out, binary=True, in_place=True)):
        image = each_label[1]
        class_label = np.unique(image*vol)
        volume_properties["labels"].append(class_label[1])
        pos = np.array([bounding_boxe[0].start, bounding_boxe[0].stop, bounding_boxe[1].start, bounding_boxe[1].stop, bounding_boxe[2].start, bounding_boxe[2].stop])
        pos = pos*reshape_factor - reshape_factor
        volume_properties["poses"].append(pos)
        # add the z length of the bounding box to the centroid
        centroid = centroid * reshape_factor - reshape_factor
        base = np.array([centroid[0], centroid[1], centroid[2]+((pos[-1]-pos[-2])/2)]).astype(int)
        volume_properties["flag_poses"].append(base)
    
    return volume_properties
    