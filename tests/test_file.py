import unittest
import bwpy
from helpers import get_sample_path, open_sample, open_sample_copy


class TestFileObjects(unittest.TestCase):
    def test_open_file(self):
        with bwpy.File(get_sample_path("truncated_brw.brw"), "r") as file:
            pass


class TestFileObjectProperties(unittest.TestCase):
    def test_description(self):
        with open_sample("truncated_brw.brw", "r") as f:
            descr = f.description
