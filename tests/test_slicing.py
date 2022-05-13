import pathlib
from sre_constants import SRE_FLAG_UNICODE
import h5py
import unittest
import numpy
import bwpy
import numpy as np

path = pathlib.Path(__file__).parent

class TestFileObjects(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.file = bwpy.File(f"{path}/test_samples/100frames.brw", "r")
    
    def tearDown(self) -> None:
        super().tearDown()
        self.file.close()
    
    def test_file_integrity(self):
        self.assertEqual(self.file.data[()].shape, (self.file.n_channels, self.file.n_frames))
        
    def test_basic_slicing(self):
        self.assertEqual(self.file.raw.size, self.file.data.size)
        print("get unsliced slice passed")
        self.assertEqual((self.file.n_channels, 1), self.file.t[1].data.shape)
        print("get channel slice passed")
        self.assertEqual((1, self.file.n_frames), self.file.ch[1, 1].data.shape)
        print("get time slice passed")

    def test_concatenate_slicing(self):
        self.assertEqual((60 * 60, 90), self.file.t[:90].ch[0:60, 0:60].data.shape)
        new_slice = self.file.t[:90].ch[:60, :60]
        print("2 slices concat passed")
        self.assertEqual((40 * 50, 70), new_slice.t[10:80].ch[:40, 10:].data.shape)
        new_slice_2 = new_slice.t[10:80].ch[:40, :50]
        print("4 slices concat passed")
        self.assertEqual((1 * 50, 1), new_slice_2.t[65].ch[30, :].data.shape)
        new_slice_3 = new_slice_2.t[65].ch[30, :]
        print("6 slices concat passed")
        self.assertEqual((1 * 50, 1), new_slice_3.t[:].ch[:].data.shape)
        print("8 slices concat passed")

    def test_slicing_out_of_range_index(self):
        self.assertEqual((64 * 2, 100), self.file.t[:150].ch[:850, -2:88880].data.shape)

    def test_empty_slice(self):
        empty_slice = bwpy.File(f"{path}/test_samples/empty.brw", "r")

        self.assertEqual((4096, 0), empty_slice.t[:150].ch[:850, :].data.shape)
