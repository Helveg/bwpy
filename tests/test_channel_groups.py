import unittest
import numpy
import bwpy
from helpers import get_sample_path, open_sample, open_sample_copy, samples


class TestChannelGroups(unittest.TestCase):
    def test_channel_group_names(self):
        with open_sample(samples.bxr, "r") as f:
            names = f.get_channel_group_names()
            self.assertEqual(["Group 1"], names)

    def test_get_channel_groups(self):
        with open_sample(samples.bxr, "r") as f:
            groups = f.get_channel_groups()
            self.assertEqual("Group 1", groups[0]._name)
            self.assertEqual(1, len(groups))

    def test_get_channel_group(self):
        with open_sample(samples.bxr, "r") as f:
            group = f.get_channel_group(0)
            self.assertEqual("Group 1", group.name)
            self.assertRaises(KeyError, f.get_channel_group, 5)
            group = f.get_channel_group("Group 1")
            self.assertRaises(KeyError, f.get_channel_group, "Group 2")
            self.assertEqual(183, len(group.channels))
