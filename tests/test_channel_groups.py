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


class TestChannelGroupProperties(unittest.TestCase):
    def test_name_property(self):
        with open_sample(samples.bxr, "r") as f:
            group = f.get_channel_group(0)
            self.assertEqual("Group 1", group.name)

    def test_channels_property(self):
        with open_sample(samples.bxr, "r") as f:
            channels = f.get_channel_group(0).channels
            self.assertEqual(183, len(channels))
            self.assertIs(bwpy.Channel, type(channels[0]))

    def test_channels_property_mutation(self):
        with open_sample(samples.bxr, "r") as f:
            group = f.get_channel_group(0)
            channels = group.channels
            channels.append("trash")
            self.assertEqual(183, len(group.channels))

    def test_visible_property(self):
        with open_sample(samples.bxr, "r") as f:
            group = f.get_channel_group(0)
            self.assertIs(True, group.visible)

    def test_color_property(self):
        with open_sample(samples.bxr, "r") as f:
            group = f.get_channel_group(0)
            self.assertIs(tuple, type(group.color))
            self.assertEqual(4, len(group.color))
