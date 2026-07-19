# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import unittest

from it_management.it_management.utils.ipv4 import (
	design_from_cidr,
	design_from_network_and_prefix,
	ranges_overlap,
)


class TestIPv4Design(unittest.TestCase):
	def test_normalizes_network_address(self):
		design = design_from_network_and_prefix("10.40.1.0", 23)
		self.assertEqual(design["network_address"], "10.40.0.0")
		self.assertEqual(design["subnet_mask"], "255.255.254.0")
		self.assertEqual(design["cidr"], "10.40.0.0/23")
		self.assertEqual(design["usable_hosts"], 510)

	def test_slash_24(self):
		design = design_from_cidr("192.168.1.10/24")
		self.assertEqual(design["network_address"], "192.168.1.0")
		self.assertEqual(design["first_usable"], "192.168.1.1")
		self.assertEqual(design["last_usable"], "192.168.1.254")
		self.assertEqual(design["broadcast"], "192.168.1.255")

	def test_overlap_detection(self):
		a = design_from_cidr("10.40.0.0/23")
		b = design_from_cidr("10.40.1.0/24")
		c = design_from_cidr("10.50.0.0/24")
		self.assertTrue(
			ranges_overlap(a["network_int"], a["broadcast_int"], b["network_int"], b["broadcast_int"])
		)
		self.assertFalse(
			ranges_overlap(a["network_int"], a["broadcast_int"], c["network_int"], c["broadcast_int"])
		)
