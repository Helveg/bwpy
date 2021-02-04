import unittest
import numpy
import bwpy
from helpers import get_sample_path, open_sample, open_sample_copy, samples


class TestFileObjects(unittest.TestCase):
    def test_open_file(self):
        with bwpy.File(get_sample_path(samples.brw), "r") as file:
            pass

    def test_brw_type(self):
        with bwpy.File(get_sample_path(samples.brw), "r") as file:
            self.assertEqual("brw", file.type)

    def test_bxr_type(self):
        with bwpy.File(get_sample_path(samples.bxr), "r") as file:
            self.assertEqual("bxr", file.type)


class TestFileObjectProperties(unittest.TestCase):
    def test_description(self):
        with open_sample(samples.brw, "r") as f:
            descr = f.description
        self.assertIs(str, type(descr), "Description should be of type str.")
        with open_sample_copy(samples.brw) as f:
            f.description = "BRW-File Level3 - Hi, I'm Elfo"
            descr = f.description
        with open_sample_copy(samples.bxr) as f:
            f.description = "BXR-File Level2 - Hi, I'm Elfo"
            descr = f.description
        self.assertEqual(descr, "BXR-File Level2 - Hi, I'm Elfo")

    def test_description_prefix(self):
        with open_sample_copy(samples.brw) as f:
            with self.assertWarns(UserWarning):
                f.description = "Hi, I'm Elfo"
            descr = f.description
        self.assertEqual(descr, "BRW-File Level3 - Hi, I'm Elfo")

    def test_write_description(self):
        with open_sample(samples.brw, "r") as f:
            with self.assertRaises(RuntimeError):
                f.description = "Hi, I'm Elfo"

    def test_version(self):
        with open_sample(samples.brw, "r") as f:
            version = f.version
        self.assertEqual(numpy.int32, type(version))
        self.assertEqual(version, 320)

    def test_guid(self):
        with open_sample(samples.brw, "r") as f:
            guid = f.guid
        self.assertIs(str, type(guid), "GUID should be of type str.")
        self.assertEqual("cfef184e-a0ea-41af-976b-45dcec62d561", guid)

    def test_channel_groups_prop(self):
        with open_sample(samples.bxr, "r") as f:
            groups = f.channel_groups
            self.assertEqual(1, len(groups))
            self.assertIs(bwpy.ChannelGroup, type(groups[0]))


class TestRecordingInfo(unittest.TestCase):
    def test_raw_recording_info(self):
        with open_sample(samples.bxr, "r") as f:
            raw = f.get_raw_recording_info()
            self.assertIsNotNone(raw)

    def test_recording_vars(self):
        with open_sample(samples.bxr, "r") as f:
            vars = (
                "BitDepth",
                "ExperimentType",
                "MaxVolt",
                "MinVolt",
                "NRecFrames",
                "SamplingRate",
                "SignalInversion",
            )
            values = (12, 0, 4125.0, -4125.0, 8028300, 17855.5020, 1.0)
            props = (
                "bit_depth",
                "experiment_type",
                "max_volt",
                "min_volt",
                "n_frames",
                "sampling_rate",
                "signal_inversion",
                "duration",
            )
            prop_values = (12, 0, 4125.0, -4125.0, 8028300, 17855.5020, 1.0, 449.6261)
            for var, value in zip(vars, values):
                with self.subTest(recording_variable=var):
                    if type(value) is float:
                        self.assertAlmostEqual(
                            value, f.get_recording_variable(var), places=3
                        )
                    else:
                        self.assertEqual(value, f.get_recording_variable(var))
            for prop, value in zip(props, prop_values):
                with self.subTest(property=prop):
                    if type(value) is float:
                        self.assertAlmostEqual(value, getattr(f, prop), places=3)
                    else:
                        self.assertEqual(value, getattr(f, prop))

    def test_missing_recording_var(self):
        with open_sample(samples.bxr, "r") as f:
            with self.assertRaises(KeyError):
                f.get_recording_variable("ThisReallyShouldntExistInHere")


class TestUserInfo(unittest.TestCase):
    def test_raw_user_info(self):
        with open_sample(samples.bxr, "r") as f:
            raw = f.get_raw_user_info()
            self.assertIsNotNone(raw)


class TestResults(unittest.TestCase):
    def test_raw_results(self):
        with open_sample(samples.bxr, "r") as f:
            raw = f.get_raw_results()
            self.assertIsNotNone(raw)

    def test_raw_channel_events(self):
        with open_sample(samples.bxr, "r") as f:
            raw = f.get_raw_channel_events()
            self.assertIsNotNone(raw)
