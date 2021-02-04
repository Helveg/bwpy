import unittest
import numpy
import bwpy
from helpers import get_sample_path, open_sample, open_sample_copy


brw_sample = "truncated_brw.brw"
bxr_sample = "truncated_bxr.bxr"


class TestFileObjects(unittest.TestCase):
    def test_open_file(self):
        with bwpy.File(get_sample_path(brw_sample), "r") as file:
            pass

    def test_brw_type(self):
        with bwpy.File(get_sample_path(brw_sample), "r") as file:
            self.assertEqual("brw", file.type)

    def test_bxr_type(self):
        with bwpy.File(get_sample_path(bxr_sample), "r") as file:
            self.assertEqual("bxr", file.type)


class TestFileObjectProperties(unittest.TestCase):
    def test_description(self):
        with open_sample(brw_sample, "r") as f:
            descr = f.description
        self.assertIs(str, type(descr), "Description should be of type str.")
        with open_sample_copy(brw_sample) as f:
            f.description = "BRW-File Level3 - Hi, I'm Elfo"
            descr = f.description
        self.assertEqual(descr, "BRW-File Level3 - Hi, I'm Elfo")

    def test_description_prefix(self):
        with open_sample_copy(brw_sample) as f:
            with self.assertWarns(UserWarning):
                f.description = "Hi, I'm Elfo"
            descr = f.description
        self.assertEqual(descr, "BRW-File Level3 - Hi, I'm Elfo")

    def test_version(self):
        with open_sample(brw_sample, "r") as f:
            version = f.version
        self.assertEqual(numpy.int32, type(version))
        self.assertEqual(version, 320)

    def test_guid(self):
        with open_sample(brw_sample, "r") as f:
            guid = f.guid
        self.assertIs(str, type(guid), "GUID should be of type str.")
        self.assertEqual("cfef184e-a0ea-41af-976b-45dcec62d561", guid)
