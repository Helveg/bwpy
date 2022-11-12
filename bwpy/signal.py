import re
import abc
import functools
import numpy as np
import numpy.lib.stride_tricks as np_tricks
from scipy.signal import find_peaks


__all__ = []


def _transformer_factory(cls):
    @functools.wraps(cls)
    def transformer_factory(slice, bin_size, *args, **kwargs):
        return slice._transform(cls(*args, **kwargs), bin_size)

    return transformer_factory


class Transformer(abc.ABC):
    def __init_subclass__(cls, operator=None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        name = operator or re.sub("([a-z0-9])([A-Z])", r"\1_\2", cls.__name__).lower()
        globals()[name] = _transformer_factory(cls)
        __all__.append(name)

    def _apply_window(self, data, bin_size):
        rows = data.shape[0]
        cols = data.shape[1]
        window_shape = (rows, cols, bin_size)
        # sliding window returns more complex shape like (num_windows, 1, 1, rows, cols, bin_size)
        # with the reshape we get rid of the unnecessary complexity (1, 1)
        return np_tricks.sliding_window_view(data, window_shape).reshape(
            -1, rows, cols, bin_size
        )

    @abc.abstractmethod
    def __call__(self, data, file, bin_size):
        pass


class Variation(Transformer):
    def __call__(self, data, file, bin_size):
        print("calling ", self.__class__.__name__)
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, bin_size)
            return np.max(np.abs(windows), axis=3) - np.min(np.abs(windows), axis=3)


class Amplitude(Transformer):
    def __call__(self, data, file, bin_size):
        print("calling ", self.__class__.__name__)
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, bin_size)
            return np.max(np.abs(windows), axis=3)


class Energy(Transformer):
    def __call__(self, data, file, bin_size):
        print("calling ", self.__class__.__name__)
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, bin_size)
            return np.sum(np.square(windows), axis=3)


class Raw(Transformer):
    def __call__(self, data, file, bin_size):
        print("calling ", self.__class__.__name__)
        return np.moveaxis(data, 2, 0)


class DetectArtifacts(Transformer):
    def __call__(self, data, file, bin_size):
        n_channels = file.layout.shape[0] * file.layout.shape[1]
        artifacts = []
        out_bounds = data > 170

        for i in range(len(data)):
            if np.count_nonzero(out_bounds[i]) / n_channels > 0.8:
                artifacts.append(i)
        return artifacts
