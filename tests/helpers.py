import os
import bwpy

class Samples:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

samples = Samples(brw="truncated_brw.brw", bxr="truncated_bxr.bxr")

def get_sample_path(sample):
    return os.path.join(os.path.dirname(__file__), "test_samples", sample)


def open_sample(sample, *args, **kwargs):
    return bwpy.File(get_sample_path(sample), *args, **kwargs)


def open_sample_copy(sample):
    return bwpy.File(
        get_sample_path(sample), mode="a", driver="core", backing_store=False
    )
