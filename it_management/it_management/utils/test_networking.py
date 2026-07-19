# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import unittest

try:
	import frappe  # noqa: F401
except ImportError:
	frappe = None


@unittest.skipIf(frappe is None, "frappe not installed")
class TestNetworkingHelpers(unittest.TestCase):
	def test_purpose_profiles_complete(self):
		from it_management.it_management.utils.networking import PURPOSE_PROFILES

		expected = {"Corporate", "Guest Wi-Fi", "DMZ", "Management", "IoT"}
		self.assertEqual(set(PURPOSE_PROFILES), expected)
		for profile in PURPOSE_PROFILES.values():
			self.assertIn("preferred_prefix", profile)
			self.assertIn("search_bases", profile)
			self.assertIn("vlan_hint", profile)

	def test_prefix_grows_with_clients(self):
		from it_management.it_management.utils.networking import _prefix_for_clients

		small = _prefix_for_clients(20, 1.3, 24)
		large = _prefix_for_clients(400, 1.5, 23)
		self.assertGreaterEqual(small, large)


class TestPrefixHelperStandalone(unittest.TestCase):
	"""Mirror of _prefix_for_clients for environments without frappe."""

	def test_prefix_logic(self):
		def prefix_for_clients(expected_clients, growth_factor, preferred_prefix):
			clients = max(int(expected_clients or 0), 1)
			needed = int(clients * float(growth_factor or 1.3)) + 2
			for prefix in range(preferred_prefix, 8, -1):
				usable = (2 ** (32 - prefix)) - 2 if prefix < 31 else 2 ** (32 - prefix)
				if usable >= needed:
					return prefix
			return 16

		self.assertEqual(prefix_for_clients(20, 1.3, 24), 24)
		self.assertLessEqual(prefix_for_clients(400, 1.5, 23), 23)
