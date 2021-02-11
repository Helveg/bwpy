from .decoders import SpikeTimeDecoder, WaveFormDecoder


def _chunk_iter(dset, mult=1, decoder=None):
    if len(dset.shape) != 1:
        raise NotImplementedError("Future chunk iterator only implemented for 1D.")
    size = dset.size
    chunk_size = dset.chunks[0] * mult
    if decoder is None:
        for i in range(size // chunk_size):
            yield dset[(i * chunk_size) : ((i + 1) * chunk_size)]
        yield dset[((i + 1) * chunk_size) :]
    else:
        for i in range(size // chunk_size):
            yield decoder.decode(dset[(i * chunk_size) : ((i + 1) * chunk_size)])
        yield decoder.decode(dset[((i + 1) * chunk_size) :])


def _wave_iter(decoder, dset, wave_size):
    for chunk in _chunk_iter(dset, mult=wave_size):
        c_size = len(chunk)
        n_chunk_spikes = c_size // wave_size
        yield decoder.decode(chunk.reshape(n_chunk_spikes, wave_size))


_benchmark_chunks = None


class ChunkReader:
    """
    Reads BXR results in blocks equal in size to the chunks they are stored in.
    """

    def __init__(self, bxr, wave_decoder=None, time_decoder=None):
        self._bxr = bxr
        self._set_decoders(wave_decoder, time_decoder)

    def _set_decoders(self, wave_decoder, time_decoder):
        self._wave_decoder = WaveFormDecoder(
            self._bxr.min_volt,
            self._bxr.max_volt,
            self._bxr.bit_depth,
            self._bxr.signal_inversion,
        )
        self._time_decoder = SpikeTimeDecoder(self._bxr.sampling_rate)

    def read(self):
        _times = self._bxr.get_raw_times()
        _chids = self._bxr.get_raw_channels()
        _units = self._bxr.get_raw_units()
        _wave_forms = self._bxr.get_raw_waves()
        chunk_size = _chids.chunks
        chid_chunks = _chunk_iter(_chids)
        time_chunks = _chunk_iter(_times, decoder=self._time_decoder)
        unit_chunks = _chunk_iter(_units)
        wave_size = self._bxr.get_wave_size()
        # For each spike an entire waveform of `wave_size` should be loaded
        wave_chunks = _wave_iter(self._wave_decoder, _wave_forms, int(wave_size))
        i = 0
        for chunk in zip(time_chunks, wave_chunks, chid_chunks, unit_chunks):
            if _benchmark_chunks is not None and i >= _benchmark_chunks:
                break
            yield chunk
            i += 1

    def __len__(self):
        set = self._bxr.get_raw_times()
        return int(set.shape[0] / set.chunks[0])


class SpikeReader(ChunkReader):
    """
    Reads BXR results spike per spike.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self):
        for chunk_data in super().read():
            yield from zip(*chunk_data)

    def __len__(self):
        return int(self._bxr.get_raw_times().shape[0])
