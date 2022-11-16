import h5py
import warnings
import numpy as np
from ._hdf_annotations import requires_write_access
from ._channels import Channel, ChannelGroup
import functools

__version__ = "0.0.1a0"


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
            self.__post_init__()
        if self.description.startswith("BXR"):
            self.__class__ = BXRFile
            self._type = "bxr"
            self.__post_init__()

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
        return self.get_recording_variable("SignalInversion")

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

    def convert(self, dv):
        step_v = self.signal_inversion * (
            (self.max_volt - self.min_volt) / 2**self.bit_depth
        )
        v_offset = self.signal_inversion * self.min_volt
        return dv * step_v + v_offset

    @property
    def version(self):
        return self.attrs["Version"]

    @property
    def guid(self):
        return self.attrs["GUID"].decode()


class _Slicer:
    def __init__(self, slice):
        self._slice = slice


class _TimeSlicer(_Slicer):
    def __getitem__(self, instruction):
        slice = self._slice._time_slice(instruction)
        return slice


class _ChannelSlicer(_Slicer):
    def __getitem__(self, instruction):
        slice = self._slice._channel_slice(instruction)
        return slice


class Variation:
    def __call__(self, data):
        return data + self.offset


def variation(slice, *args, **kwargs):
    slice.transformations.append(Variation(*args, **kwargs))
    return slice


class _Slice:
    def __init__(self, file, channels=None, time=None):
        self._file = file
        if channels is None:
            channels = file.channels[()].reshape(file.layout.shape)
        self._channels = channels
        if time is None:
            time = slice(None)
        self._time = time
        self._transformations = []
        self.bin_size = 100

    @property
    @functools.cache
    def t(self):
        return _TimeSlicer(self)

    @property
    @functools.cache
    def ch(self):
        return _ChannelSlicer(self)

    @property
    def channels(self):
        return self._channels

    @property
    def data(self):
        t_start, t_stop, t_step = self._time.indices(self._file.n_frames)
        time_slice = slice(
            t_start * self._file.n_channels,
            t_stop * self._file.n_channels,
            t_step * self._file.n_channels,
        )
        cols = self._file.layout.shape[1]
        mask = np.array(
            [(row - 1) * cols + (col - 1) for row, col in self.channels[()].ravel()]
        )

        if len(self._file.raw) < len(mask):
            raise ValueError(f"You recorded less than 1 value per channel.")

        start, stop, step = time_slice.indices(len(self._file.raw))
        time_ind = np.tile(mask, ((stop - start) // step, 1))
        for i, time_sample in enumerate(range(start, stop, step)):
            time_ind[i, :] += time_sample
        time_ind = time_ind.reshape(-1)
        data = np.empty(time_ind.shape)
        for i in range(0, len(time_ind), 1000):
            end_slice = i + 1000
            data[i:end_slice] = self._file.raw[time_ind[i:end_slice]]

        digital = data.reshape((len(mask), -1))
        analog = self._file.convert(digital)
        # Shape (-1, row, cols) because in the next line we'll swapaxes.
        # If we used directly shape (row,cols,-1) we would end up with data[:,:,0]:
        # [0,3,6]            [0,1,2]
        # [1,4,7] instead of [3,4,5]
        # [2,5,8]            [6,7,8]
        data = analog.reshape((-1, *self._file.layout.shape))
        data = np.flip(np.rot90(data.swapaxes(2, 0), -1), 1)

        for transformation in self._transformations:
            try:
                data = transformation(data, self, self._file)
            except Exception as e:
                raise TransformationError(
                    f"Error in transformation pipeline {self._transformations}"
                    f", with {transformation}: {e}"
                )
        return data

    def _time_slice(self, instruction):
        if isinstance(instruction, int):
            instruction = slice(instruction, instruction + 1, 1)
        if isinstance(instruction, slice):
            prev_start, prev_stop, prev_step = self._time.indices(self._file.n_frames)
            _len = (prev_stop - prev_start) // prev_step
            this_start, this_stop, this_step = instruction.indices(_len)
            start = prev_start + this_start * prev_step
            stop = prev_start + this_stop * prev_step
            step = this_step * prev_step
            # start: 1, end: 5, step: 1 --> Slice [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] into Slice [1, 2, 3, 4]
            # start: 0, end: 7, step: 2 --> Slice [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] into Slice [0, 2, 4, 6]
            # start: 5, end: -1, step: 4 --> Slice [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10] into Slice [5, 9]
            ret = self._copy_slice()
            ret._time = slice(start, stop, step)
            return ret

    def _channel_slice(self, instruction):
        ret = self._copy_slice()
        ret._channels = self._channels[instruction]
        return ret

    def _transform(self, transformation):
        ret = self._copy_slice()
        ret._transformations.append(transformation)
        return ret

    def _copy_slice(self):
        copied = _Slice(self._file, self._channels, self._time)
        copied._transformations = self._transformations.copy()
        return copied


class BRWFile(File, _Slice):
    def __post_init__(self):
        _Slice.__init__(self, self)

    def _get_descr_prefix(self):
        return "BRW-File Level3"

    @property
    def channels(self):
        return self["/3BRecInfo/3BMeaStreams/Raw/Chs"]

    @property
    def n_channels(self):
        return self.channels.shape[0]

    @property
    def layout(self):
        return self["/3BRecInfo/3BMeaChip/Layout"]

    @property
    def raw(self):
        return self["/3BData/Raw"]


class BXRFile(File):
    def __post_init__(self):
        pass

    @property
    def channel_groups(self):
        return self.get_channel_groups()

    def _get_descr_prefix(self):
        return "BXR-File Level2"

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


class TransformationError(Exception):
    pass


__all__ = ["File", "BRWFile", "BXRFile"]
