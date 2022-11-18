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

    def _apply_window(self, data, bin_size):
        rows = data.shape[1]
        cols = data.shape[2]
        window_shape = (bin_size, rows, cols)
        # sliding window returns more complex shape like (num_windows, 1, 1, rows, cols, bin_size)
        # with the reshape we get rid of the unnecessary complexity (1, 1)
        return np_tricks.sliding_window_view(data, window_shape).reshape(
            -1, bin_size, rows, cols
        )

    @abc.abstractmethod
    def __call__(self, data, file):
        pass


class Variation(Transformer):
    def __init__(self, bin_size):
        self.bin_size = bin_size

    def __call__(self, data, slice, file):
        print("calling ", self.__class__.__name__)
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, self.bin_size)
            return np.max(np.abs(windows), axis=1) - np.min(np.abs(windows), axis=1)


class Amplitude(Transformer):
    def __init__(self, bin_size):
        self.bin_size = bin_size

    def __call__(self, data, slice, file):
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, self.bin_size)
            return np.max(np.abs(windows), axis=1)


class Energy(Transformer):
    def __init__(self, bin_size):
        self.bin_size = bin_size

    def __call__(self, data, slice, file):
        if data.ndim < 3:
            return data
        else:
            windows = self._apply_window(data, self.bin_size)
            return np.sum(np.square(windows), axis=1)


class Raw(Transformer):
    def __call__(self, data, slice, file):
        return np.moveaxis(data, 2, 0)


class Noop(Transformer):
    """Noop that doesn't transform the data at all."""
    def __call__(self, data, slice, file):
        return data


class DetectArtifacts(Transformer):
    def __call__(self, data, slice, file):
        if data.ndim < 3:
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

        bin_size = self.ms_to_idx(file, 100)
        mea_viewer.MEAViewer().build_view(
            file, data=masked_data, view_method="no_method", bin_size=bin_size
        ).show()

        if self.callable:
            return self.callable(self.data, mask)
        else:
            return masked_data

    def ms_to_idx(self, file, delay_ms):
        return int(delay_ms * file.sampling_rate * 1000)
