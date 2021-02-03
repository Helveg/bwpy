import h5py
import warnings
import numpy as np
from ._hdf_annotations import requires_write_access

__version__ = "0.0.1a0"

class File(h5py.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def description(self):
        return self.attrs["Description"].decode()

    @description.setter
    @requires_write_access
    def description(self, value):
        if not value.startswith("BRW-File Level3"):
            warnings.warn("File descriptions must start with 'BRW-File Level3'. Added 'BRW-File Level3 - ' to the description.", stacklevel=2)
        utf8_type = h5py.string_dtype('utf-8', len(value))
        value = np.array(value.encode("utf-8"), dtype=utf8_type)
        self.attrs["Description"] = value

    def get_channels(self):
        return self.keys()

__all__ = ["File"]
