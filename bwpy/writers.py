import itertools, os, numpy as np, abc
from .readers import ChunkReader, SpikeReader


class WriteProgress:
    def __init__(self, current, total):
        self.current = current
        self.total = total


class Demultiplexer(abc.ABC):
    def __init__(self, bxr, listeners=None):
        self._bxr = bxr
        self._listeners = listeners if listeners is not None else []

    @abc.abstractmethod
    def demux(self):
        pass


class ChannelDemultiplexer(Demultiplexer):
    def demux(self):
        reader = ChunkReader(self._bxr)
        wave_size = reader._bxr.get_wave_size()
        chunk_size = reader._bxr.get_chunk_size() >> 4
        shape = (chunk_size, wave_size)
        channels = self._require_channels(shape)
        i = 0
        total = len(reader)
        self._emit_progress(i, total)
        for time_chunk, waveform_chunk, channel_chunk, unit_chunk in reader.read():
            uchannels = np.unique(channel_chunk, axis=0)
            for uc in uchannels:
                channel_mask = channel_chunk == uc
                channel = channels[uc]
                channel_units = unit_chunk[channel_mask]
                spikes = time_chunk[channel_mask]
                waves = waveform_chunk[channel_mask]
                self._append(channel, "SpikeTimes", spikes)
                self._append(channel, "WaveForms", waves)
            i += 1
            self._emit_progress(i, total)

    def _require_channels(self, shape):
        root = self._bxr.require_group("DemuxedChannels")
        return [
            self._require_channel(root, channel.id, shape)
            for channel in self._bxr.channels
        ]

    def _require_channel(self, group, channel_id, shape):
        id = str(int(float(channel_id)))
        channel = group.require_group(id)
        if "SpikeTimes" not in channel:
            ds = channel.create_dataset(
                "SpikeTimes",
                shape=(0,),
                chunks=(shape[0],),
                maxshape=(None,),
                dtype=float,
            )
        if "WaveForms" not in channel:
            ds = channel.create_dataset(
                "WaveForms",
                shape=(0, shape[1]),
                chunks=shape,
                maxshape=(None, shape[1]),
                dtype=float,
            )
        return channel

    def _append(self, group, name, data):
        ds = group[name]
        ol = len(ds)
        l = ol + len(data)
        ds.resize(l, axis=0)
        ds[ol:] = data

    def _emit_progress(self, current, total):
        p = WriteProgress(current, total)
        for l in self._listeners:
            l(self, p)


def _noop_writer(channel):
    return None


class GroupWriter:
    def __init__(self, bxr, group, path):
        self._bxr = bxr
        # self._channels = self._bxr.get_channels()
        self._group = group
        self._path = path
        self._channel_labels = [
            l.decode() for l in self._bxr.get_raw_result_info()["ChIDs2Labels"][()]
        ]

    def get_resource_path(self, channel, unit, suffix=""):
        if suffix:
            suffix = "_" + suffix
        channel_label = self._channel_labels[channel]
        return os.path.join(self._path, f"{channel_label}_unit_{unit}{suffix}.txt")

    def to_txt(self):
        os.makedirs(self._path, exist_ok=True)
        units = self._group.units
        _writers = self._get_channel_writers(units)
        unit_map = {unit: resources for unit, resources, _ in _writers}
        reader = SpikeReader(self._bxr)
        for spike_time, waveform, channel_id, unit in reader.read():
            writers = unit_map.get(unit, _noop_writer)(channel_id)
            if writers is None:
                continue
            writers[0].write(f"{spike_time:.18e} ")
            writers[1].write(" ".join(f"{w:.18e}" for w in waveform) + "\n")

        self._close_writers(_writers)

    def _get_channel_writers(self, units):
        return [self._get_channel_writer(unit) for unit in units]

    def _get_channel_writer(self, unit):
        channels = {}

        def _get_channel_resources(channel):
            resources = channels.get(channel, None)
            if resources is None:
                resources = (
                    open(self.get_resource_path(channel, unit), "w"),
                    open(self.get_resource_path(channel, unit, "waves"), "w"),
                )
                channels[channel] = resources
            return resources

        return unit, _get_channel_resources, channels

    def _close_writers(self, writers):
        for resources in itertools.chain(*(w[2].values() for w in writers)):
            resources[0].close()
            resources[1].close()
