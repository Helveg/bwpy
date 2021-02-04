import bwpy
import time
import atexit
import psutil, shutil
import gc, os, sys
import numpy as np

from bwpy.writers import GroupWriter
import bwpy.readers


def path(*p):
    return os.path.join(os.path.dirname(__file__), *p)


sample_path = path("../tests/test_samples/full_sample.bxr")
_process = psutil.Process(os.getpid())

atexit.register(shutil.rmtree, path("out_bwpy"))

for chunks in np.logspace(1, 4, 100):
    gc.collect()
    chunks = int(chunks)
    bwpy.readers._benchmark_chunks = chunks
    _start_time = time.time()
    with bwpy.File(sample_path, "r") as file:
        group = file.get_channel_group("Group 1")
        writer = GroupWriter(file, group, path("out_bwpy"))
        writer.to_txt()
    print(chunks, time.time() - _start_time, _process.memory_info().rss)
