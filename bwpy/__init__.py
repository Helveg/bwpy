import h5py
import warnings
import numpy as np
from ._hdf_annotations import requires_write_access
from ._channels import Channel, ChannelGroup
from .writers import ChannelDemultiplexer

__version__ = "0.1a0"


class File(h5py.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._establish_type()

    @property
    def type(self):
        if hasattr(self, "_type"):
            return self._type
        else:  # pragma: nocover
            # The type is established in `__init__`, unless the user is writing a new
            # file which is currently not supported. But just in case they then manage to
            # write a correct file we can re-check whenever the type is used anywhere.
            self._establish_type()
            if hasattr(self, "_type"):
                return self._type
            else:
                return None

    def _establish_type(self):
        if self.description.startswith("BRW"):
            self.__class__ = BRWFile
            self._type = "brw"
        if self.description.startswith("BXR"):
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

    @property
    def bit_depth(self):
        return self.get_recording_variable("BitDepth")

    @property
    def experiment_type(self):
        return self.get_recording_variable("ExperimentType")

    @property
    def max_volt(self):
        return self.get_recording_variable("MaxVolt")

    @property
    def min_volt(self):
        return self.get_recording_variable("MinVolt")

    @property
    def n_frames(self):
        return self.get_recording_variable("NRecFrames")

    @property
    def sampling_rate(self):
        return self.get_recording_variable("SamplingRate")

    @property
    def duration(self):
        return self.n_frames / self.sampling_rate

    @property
    def signal_inversion(self):
        return self.get_recording_variable("SignalInversion") == -1

    def get_recording_variable(self, var):
        rec_info = self.get_raw_recording_info()
        rec_vars = rec_info["3BRecVars"]
        if var not in rec_vars:
            raise KeyError(f"Recording variable '{var}' not found.")
        return rec_vars[var][0]

    def get_raw_recording_info(self):
        return self["3BRecInfo"]

    def get_raw_user_info(self):
        return self["3BUserInfo"]

    def get_raw_mea_chip(self):
        return self.get_raw_recording_info()["3BMeaChip"]

    @property
    def version(self):
        return self.attrs["Version"]

    @property
    def guid(self):
        return self.attrs["GUID"].decode()

    @requires_write_access
    def demux(self, *args, progress=False, **kwargs):
        if progress:

            def print_progress(w, p):
                print(p.current, "out of", p.total, end="\r")

            l = kwargs.get("listeners", [])
            l.append(print_progress)
            kwargs["listeners"] = l

        dm = ChannelDemultiplexer(self, *args, **kwargs)
        dm.demux()


class BRWFile(File):
    def _get_descr_prefix(self):
        return "BRW-File Level3"


class BXRFile(File):
    @property
    def channel_groups(self):
        return self.get_channel_groups()

    @property
    def channels(self):
        return self.get_channels()

    def _get_descr_prefix(self):
        return "BXR-File Level2"

    def get_raw_results(self):
        return self["3BResults"]

    def get_raw_result_info(self):
        return self.get_raw_results()["3BInfo"]

    def get_raw_channel_events(self):
        return self.get_raw_results()["3BChEvents"]

    def get_raw_channel_groups(self):
        return self.get_raw_user_info()["ChsGroups"]

    def get_channel_groups(self):
        groups = self.get_raw_channel_groups()
        return [ChannelGroup._from_bxr(self, data) for data in groups]

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

    def get_channel_columns(self):
        mea_chip = self.get_raw_mea_chip()
        return mea_chip["NCols"][0]

    def get_channel_rows(self):
        mea_chip = self.get_raw_mea_chip()
        return mea_chip["NRows"][0]

    def get_channel_ids(self):
        mea_chip = self.get_raw_mea_chip()
        rows = mea_chip["NRows"][0]
        cols = mea_chip["NCols"][0]
        return range(rows * cols)

    def get_channels(self):
        return [self.get_channel(id) for id in self.get_channel_ids()]

    def get_channel(self, id):
        return Channel(self, id)

    def get_raw_demux_channels(self):
        if "DemuxedChannels" not in self:
            raise MissingDemuxError("Data has not been demultiplexed yet. Use `.demux`")
        return self["DemuxedChannels"]

    def get_raw_demux_channel(self, id):
        channels = self.get_raw_demux_channels()
        id = str(int(float(id)))
        if id not in channels:
            raise MissingDemuxError(f"Channel {id} is not demultiplexed yet.")
        return channels[id]

    def get_raw_times(self):
        return self.get_raw_channel_events()["SpikeTimes"]

    def get_raw_waves(self):
        return self.get_raw_channel_events()["SpikeForms"]

    def get_raw_units(self):
        return self.get_raw_channel_events()["SpikeUnits"]

    def get_raw_channels(self):
        return self.get_raw_channel_events()["SpikeChIDs"]

    def get_wave_chunk_shape(self):
        return (self.get_chunk_size(), self.get_wave_size())

    def get_chunk_size(self):
        return self.get_raw_units().chunks[0]

    def get_wave_size(self):
        return len(self.get_raw_waves()) / len(self.get_raw_units())


__all__ = ["File", "BRWFile", "BXRFile"]
