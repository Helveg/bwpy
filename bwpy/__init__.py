import h5py
import warnings
import numpy as np
from ._hdf_annotations import requires_write_access

__version__ = "0.0.1a0"

class File(h5py.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._establish_type()

    @property
    def type(self):
        if hasattr(self, "_type"):
            return self._type
        self._establish_type()
        if hasattr(self, "_type"):
            return self._type
        else:
            return None

    def _establish_type(self):
        if "3BData" in self:
            self.__class__ = BRWFile
            self._type = "brw"
        if "3BResults" in self:
            self.__class__ = BXRFile
            self._type = "bxr"

    @property
    def description(self):
        return self.attrs["Description"].decode()

    @description.setter
    @requires_write_access
    def description(self, value):
        if not value.startswith("BRW-File Level3"):
            warnings.warn(
                "File descriptions must start with 'BRW-File Level3'. Prepended 'BRW-File Level3 - ' to the description.",
                stacklevel=2,
            )
            value = "BRW-File Level3 - " + value
        utf8_type = h5py.string_dtype("utf-8", len(value))
        value = np.array(value.encode("utf-8"), dtype=utf8_type)
        self.attrs["Description"] = value

    @property
    def version(self):
        return self.attrs["Version"]

    @property
    def guid(self):
        return self.attrs["GUID"].decode()


class BRWFile(File):
    def _get_descr_prefix(self):
        return "BRW-File Level3"


class BXRFile(File):
    def _get_descr_prefix(self):
        return "BXR-File Level2"


__all__ = ["File", "BRWFile", "BXRFile"]
