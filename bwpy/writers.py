import itertools, os
from .readers import SpikeReader


def _noop_writer(channel):
    return None


class GroupWriter:
    def __init__(self, bxr, group, path):
        self._bxr = bxr
        # self._channels = self._bxr.get_channels()
        self._group = group
        self._path = path
        self._channel_labels = [
            l.decode() for l in self._bxr["3BResults/3BInfo/ChIDs2Labels"][()]
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
