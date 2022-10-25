import re
import abc
import functools
import numpy as np


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


class Variation(Transformer):
    def __call__(self, data, file):
        print("We are transforming our data using the", self.__class__.__name__)
        try:
            return np.amax(
                data.reshape((file.layout.shape[0], file.layout.shape[1], -1)), axis=2
            ) - np.amin(data, axis=2)
        except np.AxisError:
            return data


class Amplitude(Transformer):
    def __call__(self, data, file):
        print("We are transforming our data using the", self.__class__.__name__)
        print("input data:", data.shape)
        if data.ndim < 3:
            return data
        else:
            data = np.max(np.abs(data), axis=2)
            print("out data:", data.shape)
            return data


class Energy(Transformer):
    def __call__(self, data, file):
        print("We are transforming our data using the", self.__class__.__name__)
        try:
            return np.sum(
                np.square(data.reshape((file.layout.shape[0], file.layout.shape[1], -1))),
                axis=2,
            )
        except np.AxisError:
            return data
