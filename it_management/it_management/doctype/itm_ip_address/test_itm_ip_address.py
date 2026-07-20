# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase

from it_management.it_management.doctype.itm_ip_address.itm_ip_address import (
	validate_ip_for_subnet,
)
from it_management.it_management.utils.ipv4 import (
	assert_ip_in_subnet,
	explain_ip_not_in_subnet,
	parse_ipv4_host,
)


class TestIPv4HostInSubnet(unittest.TestCase):
	def test_parse_host(self):
		self.assertEqual(str(parse_ipv4_host(" 192.168.1.10 ")), "192.168.1.10")

	def test_host_inside_slash_24(self):
		self.assertIsNone(explain_ip_not_in_subnet("192.168.1.10", "192.168.1.0", 24))
		assert_ip_in_subnet("192.168.1.10", "192.168.1.0", 24)

	def test_host_outside_subnet(self):
		message = explain_ip_not_in_subnet("10.0.0.5", "192.168.1.0", 24)
		self.assertIsNotNone(message)
		self.assertIn("outside subnet", message)
		self.assertIn("192.168.1.0/24", message)
		with self.assertRaises(ValueError):
			assert_ip_in_subnet("10.0.0.5", "192.168.1.0", 24)

	def test_rejects_network_and_broadcast(self):
		network_msg = explain_ip_not_in_subnet("192.168.1.0", "192.168.1.0", 24)
		self.assertIn("network address", network_msg)

		broadcast_msg = explain_ip_not_in_subnet("192.168.1.255", "192.168.1.0", 24)
		self.assertIn("broadcast address", broadcast_msg)

	def test_allows_slash_31_endpoints(self):
		self.assertIsNone(explain_ip_not_in_subnet("10.0.0.0", "10.0.0.0", 31))
		self.assertIsNone(explain_ip_not_in_subnet("10.0.0.1", "10.0.0.0", 31))

	def test_invalid_ip_message(self):
		message = explain_ip_not_in_subnet("192.300.1.1", "192.168.1.0", 24)
		self.assertIn("0 and 255", message)


class TestITMIPAddressValidation(FrappeTestCase):
	def setUp(self):
		super().setUp()
		suffix = frappe.generate_hash(length=6)
		self.landscape = frappe.get_doc(
			{"doctype": "ITM Landscape", "title": "ITM IP Test Landscape {0}".format(suffix)}
		).insert(ignore_permissions=True)
		self.lan = frappe.get_doc(
			{
				"doctype": "ITM Local Area Network",
				"title": "ITM IP Test LAN {0}".format(suffix),
				"itm_landscape": self.landscape.name,
			}
		).insert(ignore_permissions=True)
		self.subnet = frappe.get_doc(
			{
				"doctype": "ITM Subnet",
				"network_address": "10.55.0.0",
				"prefix_length": 24,
				"itm_local_area_network": self.lan.name,
				"lifecycle_status": "Implementing",
			}
		).insert(ignore_permissions=True)

		self.addCleanup(lambda: frappe.delete_doc("ITM Subnet", self.subnet.name, force=1))
		self.addCleanup(lambda: frappe.delete_doc("ITM Local Area Network", self.lan.name, force=1))
		self.addCleanup(lambda: frappe.delete_doc("ITM Landscape", self.landscape.name, force=1))

	def test_rejects_ip_outside_subnet(self):
		doc = frappe.get_doc(
			{
				"doctype": "ITM IP Address",
				"ip_address": "192.168.9.9",
				"itm_subnet": self.subnet.name,
			}
		)
		with self.assertRaises(frappe.ValidationError) as ctx:
			doc.insert(ignore_permissions=True)
		self.assertIn("outside subnet", str(ctx.exception))

	def test_rejects_network_address(self):
		doc = frappe.get_doc(
			{
				"doctype": "ITM IP Address",
				"ip_address": "10.55.0.0",
				"itm_subnet": self.subnet.name,
			}
		)
		with self.assertRaises(frappe.ValidationError) as ctx:
			doc.insert(ignore_permissions=True)
		self.assertIn("network address", str(ctx.exception).lower())

	def test_rejects_broadcast_address(self):
		doc = frappe.get_doc(
			{
				"doctype": "ITM IP Address",
				"ip_address": "10.55.0.255",
				"itm_subnet": self.subnet.name,
			}
		)
		with self.assertRaises(frappe.ValidationError) as ctx:
			doc.insert(ignore_permissions=True)
		self.assertIn("broadcast address", str(ctx.exception).lower())

	def test_accepts_usable_host(self):
		doc = frappe.get_doc(
			{
				"doctype": "ITM IP Address",
				"ip_address": "10.55.0.42",
				"itm_subnet": self.subnet.name,
			}
		)
		doc.insert(ignore_permissions=True)
		self.addCleanup(lambda: frappe.delete_doc("ITM IP Address", doc.name, force=1))
		self.assertEqual(doc.ip_address, "10.55.0.42")

	def test_whitelist_validate_helper(self):
		ok = validate_ip_for_subnet("10.55.0.10", self.subnet.name)
		self.assertTrue(ok["ok"])

		bad = validate_ip_for_subnet("8.8.8.8", self.subnet.name)
		self.assertFalse(bad["ok"])
		self.assertIn("outside subnet", bad["message"])
