import abc


class Decoder(abc.ABC):
    @abc.abstractmethod
    def decode(self):
        pass


class WaveFormDecoder(Decoder):
    """
    Decodes sampled waveforms to potentials based on sampling parameters.
    """

    def __init__(self, min_volt, max_volt, bit_depth, inversion=False):
        super().__init__()
        self.min_volt = min_volt
        self.max_volt = max_volt
        self.bit_depth = bit_depth
        self.inversion = inversion

    @property
    def voltage_step(self):
        return (self.max_volt - self.min_volt) / self.q_level

    @property
    def q_level(self):
        return 2 ** self.bit_depth

    def decode(self, signal):
        if self.inversion:
            signal = np.negative(signal)

        return (signal - self.q_level / 2) * self.voltage_step


class SpikeTimeDecoder(Decoder):
    """
    Decodes timesteps to time based on the sampling rate.
    """

    def __init__(self, sampling_rate):
        super().__init__()
        self._sampling_rate = sampling_rate

    def decode(self, times):
        return times / self._sampling_rate
