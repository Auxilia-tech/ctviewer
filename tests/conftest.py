import pytest
import numpy as np
import vedo
from vedo import Volume
from unittest.mock import MagicMock, patch

from pyDICOS import CT, DcsLongString, Filename, ErrorLog
from pydicos import CTLoader

from ctviewer.rendering import RendererCallbacks, IsoSurfer, RayCaster, Slicer, Renderer
from ctviewer.utils import ConfigManager
from ctviewer.io import Reader

@pytest.fixture
def mock_reader():
    return Reader()

@pytest.fixture
def volume_data():
    temp_volume = np.zeros((50, 50, 50)).astype(np.uint16)
    temp_volume[5:45, 5:45, 5:45] = 1000
    return temp_volume

@pytest.fixture
def mask_data():
    temp_volume = np.zeros((50, 50, 50)).astype(np.uint8)
    temp_volume[5:10, 5:10, 5:10] = 1
    temp_volume[40:49, 40:49, 40:49] = 2
    return temp_volume

@pytest.fixture
def temp_npy_path(tmp_path, volume_data):
    np.save(str(tmp_path / "temp_volume.npy"), volume_data)
    return str(tmp_path / "temp_volume.npy")

@pytest.fixture
def temp_mhd_path(tmp_path, volume_data):
    vedo.write(vedo.Volume(volume_data), str(tmp_path / "temp_volume.mhd"))
    return str(tmp_path / "temp_volume.mhd")
    
@pytest.fixture
def temp_mask_path(tmp_path, mask_data):
    vedo.write(vedo.Volume(mask_data), str(tmp_path / "temp_mask.mhd"))
    return str(tmp_path / "temp_mask.mhd")

@pytest.fixture
def temp_mask_data(temp_mask_path, mock_reader):
    return mock_reader(temp_mask_path)[0]

@pytest.fixture
def temp_volume_data(temp_mhd_path, mock_reader):
    return mock_reader(temp_mhd_path)[0]

@pytest.fixture
def mock_callbacks():
    return MagicMock(spec=RendererCallbacks)

@pytest.fixture
def mock_volume():
    return MagicMock(spec=Volume)

@pytest.fixture
def ogb():
    return [(100, 'orange'), (200, 'green'), (300, 'blue')]

@pytest.fixture
def alpha():
    return [0.5, 0.5, 0.5]

@pytest.fixture
def mock_ray_caster():
    return MagicMock(spec=RayCaster)

@pytest.fixture
def mock_iso_surfer():
    return MagicMock(spec=IsoSurfer)

@pytest.fixture
def mock_slicer():
    return MagicMock(spec=Slicer)

@pytest.fixture
def mock_renderer(ogb, alpha, mock_callbacks, mock_reader, mock_ray_caster, mock_iso_surfer, mock_slicer, mask_classes):
    with patch('vedo.show', MagicMock()):
        renderer = Renderer(ogb=ogb, alpha=alpha, isovalue=0.5, sliderpos=4, mask_classes=mask_classes)
        renderer.reader = mock_reader
        renderer.callbacks = mock_callbacks
        renderer.ray_caster = mock_ray_caster
        renderer.iso_surfer = mock_iso_surfer
        renderer.slicer = mock_slicer
        return renderer

@pytest.fixture
def mask_classes():
    config_manager = ConfigManager()
    user_config = config_manager.get_user_config()
    return user_config["mask_classes"]

@pytest.fixture
def temp_dcs_file_path(tmp_path, volume_data):
    temp_dcs_file = tmp_path / "temp_volume.dcs"
    CTObject = CT(
            CT.OBJECT_OF_INSPECTION_TYPE.enumTypeBaggage,
            CT.OOI_IMAGE_CHARACTERISTICS.enumHighEnergy,
            CT.IMAGE_FLAVOR.enumVolume,
            CT.PHOTOMETRIC_INTERPRETATION.enumMonochrome2,
        )

    CTObject.SetImageAcquisitionDuration(5.2)
    DCS = DcsLongString("HIGH ENERGY SCAN")
    CTObject.SetScanDescription(DCS)

    CTObject.SetNumberOfSections(len([volume_data]))

    for n, array in enumerate([volume_data]):
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
    return str(temp_dcs_file)

@pytest.fixture
def temp_tdr_file_path(tmp_path, temp_dcs_file_path, mask_data):
    temp_tdr_file = tmp_path / "temp_tdr.dcs"
    loader = CTLoader(temp_dcs_file_path)
    detection_boxes = [
        # {"label": "Label1", "point1": (5, 5, 5), "point2": (10, 10, 10), "confidence": 0.5, "mask": mask_data[5:10, 5:10, 5:10].astype(np.bool_).astype(np.uint8)},
        # {"label": "Label2", "point1": (40, 40, 40), "point2": (45, 45, 45), "confidence": 0.5, "mask": mask_data[40:45, 40:45, 40:45].astype(np.bool_).astype(np.uint8)}
        {"label": "Label1", "point1": (5, 5, 5), "point2": (10, 10, 10), "confidence": 0.5, "mask": None},
        {"label": "Label2", "point1": (40, 40, 40), "point2": (45, 45, 45), "confidence": 0.5, "mask": None}
        ]
    tdr = loader.generate_tdr(detection_boxes)
    tdr.SetImageScaleRepresentation(1)
    tdr.write(str(temp_tdr_file))
    return str(temp_tdr_file)