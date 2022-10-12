import pathlib
import unittest
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
        self.assertEqual(
            self.file.data[()].shape, (self.file.n_channels, self.file.n_frames)
        )

    def test_basic_slicing(self):
        self.assertEqual(
            self.file.raw.size, self.file.data.size, "get unsliced slice failed"
        )
        self.assertEqual(
            True,
            np.allclose(
                self.file.t[0].data.reshape(-1),
                self.file.convert(self.file.raw[: self.file.n_channels]),
            ),
            "get time slice failed",
        )
        self.assertEqual(
            (self.file.n_channels, 1), self.file.t[1].data.shape, "get time slice failed"
        )
        self.assertEqual(
            True,
            np.allclose(
                self.file.ch[0, 0].data.reshape(-1),
                self.file.convert(self.file.raw[:: self.file.n_channels]),
            ),
            "get channel slice failed",
        )
        self.assertEqual(
            (1, self.file.n_frames),
            self.file.ch[1, 1].data.shape,
            "get channel slice failed",
        )

    def test_concatenate_slicing(self):
        self.assertEqual(
            (60 * 60, 90),
            self.file.t[:90].ch[0:60, 0:60].data.shape,
            "2 slices concat failed",
        )
        new_slice = self.file.t[:90].ch[:60, :60]
        self.assertEqual(
            (40 * 50, 70),
            new_slice.t[10:80].ch[:40, 10:].data.shape,
            "4 slices concat failed",
        )
        new_slice_2 = new_slice.t[10:80].ch[:40, :50]
        self.assertEqual(
            (1 * 50, 1), new_slice_2.t[65].ch[30, :].data.shape, "6 slices concat failed"
        )
        new_slice_3 = new_slice_2.t[65].ch[30, :]
        self.assertEqual(
            (1 * 50, 1), new_slice_3.t[:].ch[:].data.shape, "8 slices concat failed"
        )

    def test_slicing_out_of_range_index(self):
        self.assertEqual(
            (64 * 2, 100),
            self.file.t[:150].ch[:850, -2:88880].data.shape,
            "slicing out of range index failed",
        )

    def test_empty_slice(self):
        empty_slice = bwpy.File(f"{path}/test_samples/empty.brw", "r")
        with self.assertRaises(ValueError, "It should throw a ValueError") as context:
            empty_slice.t[:150].ch[:850, :].data
