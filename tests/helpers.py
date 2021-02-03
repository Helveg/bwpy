import os
import bwpy

def get_sample_path(sample):
    return os.path.join(os.path.dirname(__file__), "test_samples", sample)


def open_sample(sample, *args, **kwargs):
    return bwpy.File(get_sample_path(sample), *args, **kwargs)

def open_sample_copy(sample):
    return bwpy.File(get_sample_path(sample), mode='w', backing_store=False)
