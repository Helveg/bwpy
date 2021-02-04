import h5py
import warnings
import numpy as np
from ._hdf_annotations import requires_write_access
from ._channels import Channel, ChannelGroup

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
        prefix = self._get_descr_prefix()
        if not value.startswith(prefix):
            warnings.warn(
                f"File descriptions must start with '{prefix}'. "
                + f"Prepended '{prefix} - ' to the description.",
                stacklevel=2,
            )
            value = f"{prefix} - " + value
        utf8_type = h5py.string_dtype("utf-8", len(value))
        value = np.array(value.encode("utf-8"), dtype=utf8_type)
        self.attrs["Description"] = value

    def get_raw_user_info(self):
        return self["3BUserInfo"]

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
    @property
    def channel_groups(self):
        return self.get_channel_groups()

    def _get_descr_prefix(self):
        return "BXR-File Level2"

    def get_raw_channel_groups(self):
        return self.get_raw_user_info()["ChsGroups"]

    def get_channel_groups(self):
        return [ChannelGroup._from_bxr(self, data) for data in self.get_raw_channel_groups()]

    def get_channel_group_names(self):
        return self.get_raw_channel_groups()["Name"]

    def get_channel_group(self, group_id):
        groups = self.get_raw_channel_groups()
        try:
            # Try to cast to an int first so that field names can't be used as group names
            id = int(group_id)
            data = groups[id]
        except:
            for group in groups:
                if group["Name"] == group_id:
                    data = group
                    break
            else:
                raise KeyError(f"Channel group '{group_id}' does not exist.") from None
        return ChannelGroup._from_bxr(self, data)


__all__ = ["File", "BRWFile", "BXRFile"]
