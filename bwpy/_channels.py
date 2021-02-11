from ._hdf_annotations import requires_bxr


class Channel:
    def __init__(self, file, id=None, /, row=None, col=None):
        self._file = file
        if id is not None:
            self._id = id
        else:
            cols = self._file.get_channel_columns()
            self._id = (row - 1) * cols + (col - 1)

    @property
    def id(self):
        return self._id

    @property
    def row(self):
        cols = self._file.get_channel_columns()
        return (self._id // cols) + 1

    @property
    def col(self):
        cols = self._file.get_channel_columns()
        return (self._id % cols) + 1

    @property
    def spike_times(self):
        return self.get_spike_times()

    @property
    def waveforms(self):
        return self.get_waveforms()

    @requires_bxr("_file")
    def get_spike_times(self):
        return self._file.get_raw_demux_channel(self.id)["SpikeTimes"][()]

    @requires_bxr("_file")
    def get_waveforms(self):
        return self._file.get_raw_demux_channel(self.id)["WaveForms"][()]

    @classmethod
    def _from_channelgrouplist(cls, file, file_list):
        return [cls(file, row=data[0], col=data[1]) for data in file_list]


class ChannelGroup:
    def __init__(self, name, channels, units, color=None, visible=True):
        self._name = name
        self._channels = channels
        self._units = units
        self._color = color
        self._visible = visible

    @property
    def name(self):
        return self._name

    @property
    def channels(self):
        return self._channels.copy()

    @property
    def units(self):
        return self._units.copy()

    @property
    def color(self):
        return self._color

    @property
    def visible(self):
        return self._visible

    @classmethod
    def _from_bxr(cls, bxr, bxr_data):
        channels = Channel._from_channelgrouplist(bxr, bxr_data["Chs"])
        color = _color_tuple(bxr_data["Color"])
        return cls(
            bxr_data["Name"],
            channels,
            bxr_data["Units"],
            color,
            bool(bxr_data["IsVisible"]),
        )


def _color_tuple(data):
    return tuple(data[t] for t in ("Red", "Green", "Blue", "Alpha"))
