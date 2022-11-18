from . import mea_viewer
import re
import abc
import functools
import numpy as np
import numpy.lib.stride_tricks as np_tricks


__all__ = []


def _transformer_factory(cls):
    @functools.wraps(cls)
    def transformer_factory(slice, *args, **kwargs):
        return slice._transform(cls(*args, **kwargs))

    return transformer_factory


class Transformer(abc.ABC):
    def __init_subclass__(cls, operator=None, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        name = operator or re.sub("([a-z0-9])([A-Z])", r"\1_\2", cls.__name__).lower()
        globals()[name] = _transformer_factory(cls)
        __all__.append(name)

    @abc.abstractmethod
    def __call__(self, data, file):
        pass


class WindowedTransformer(Transformer):
    def get_signal_window(self, data, window_size):
        rows = data.shape[1]
        cols = data.shape[2]
        window_shape = (window_size, rows, cols)
        # sliding window returns more complex shape like (num_windows, 1, 1, rows, cols, window_size)
        # with the reshape we get rid of the unnecessary complexity (1, 1)
        return np_tricks.sliding_window_view(data, window_shape).reshape(
            -1, window_size, rows, cols
        )


class Variation(WindowedTransformer):
    def __init__(self, window_size):
        self.window_size = window_size

    def __call__(self, data, slice, file):
        # If data have only 2 dimensions windowing is not necessary
        if data.ndim == 2:
            return data
        else:
            windows = self.get_signal_window(data, self.window_size)
            return np.max(np.abs(windows), axis=1) - np.min(np.abs(windows), axis=1)


class Amplitude(WindowedTransformer):
    def __init__(self, window_size):
        self.window_size = window_size

    def __call__(self, data, slice, file):
        # If data have only 2 dimensions windowing is not necessary
        if data.ndim == 2:
            return data
        else:
            windows = self.get_signal_window(data, self.window_size)
            return np.max(np.abs(windows), axis=1)


class Energy(WindowedTransformer):
    def __init__(self, window_size):
        self.window_size = window_size

    def __call__(self, data, slice, file):
        if data.ndim == 2:
            return data
        else:
            windows = self.get_signal_window(data, self.window_size)
            return np.sum(np.square(windows), axis=1)


class NoMethod(Transformer):
    def __call__(self, data, slice, file):
        return np.moveaxis(data, 2, 0)


class Noop(Transformer):
    """Noop that doesn't transform the data at all."""

    def __call__(self, data, slice, file):
        return data


class DetectArtifacts(WindowedTransformer):
    def __call__(self, data, slice, file):
        # If data have only 2 dimensions windowing is not necessary
        if data.ndim == 2:
            return data
        else:
            up_limit = file.convert(file.max_volt) * 0.98
            out_bounds = data > up_limit
            mask = np.sum(out_bounds, axis=(1, 2)) > 80
            return mask


class Shutter(Transformer):
    def __init__(self, data, delay_ms, callable=None):
        self.delay_ms = delay_ms
        self.data = data
        self.callable = callable

    def __call__(self, mask, slice, file):
        if mask.ndim > 1:
            raise ValueError("mask must be a 1dim array.")

        delay = self.ms_to_idx(file, self.delay_ms)
        for i in range(len(mask) - 1, 0, -1):
            if mask[i]:
                mask[i : i + delay] = 1
        masked_data = self.data[mask]

        window_size = self.ms_to_idx(file, 100)
        mea_viewer.MEAViewer().build_view(
            file, data=masked_data, view_method="no_method", window_size=window_size
        ).show()

        if self.callable:
            return self.callable(self.data, mask)
        else:
            return masked_data

    def ms_to_idx(self, file, delay_ms):
        return int(delay_ms * file.sampling_rate * 1000)
