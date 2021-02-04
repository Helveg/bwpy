import unittest
import numpy
import bwpy
from helpers import get_sample_path, open_sample, open_sample_copy, samples


class TestChannelGroups(unittest.TestCase):
    def test_channel_group_names(self):
        with open_sample(samples.bxr, "r") as f:
            names = f.get_channel_group_names()
            self.assertEqual(["Group 1"], names)
