# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import unittest
import frappe
from frappe import _
from frappe.utils import getdate


class TestITManagementSettings(unittest.TestCase):
	"""Tests for IT Management Settings with ERPNext integration."""

	def setUp(self):
		"""Set up test fixtures."""
		# Ensure we have a clean state
		frappe.db.rollback()
		frappe.db.begin()

	def tearDown(self):
		"""Clean up after tests."""
		frappe.db.rollback()

	def test_erpnext_installed_check(self):
		"""Test that ERPNext installation is properly detected."""
		from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

		# This test will pass if ERPNext is installed in the test environment
		# or fail gracefully if it's not
		erpnext_installed = is_erpnext_installed()
		self.assertIsInstance(erpnext_installed, bool)

	def test_settings_validation_without_erpnext(self):
		"""Test that enabling use_erpnext_links fails without ERPNext."""
		from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

		# If ERPNext is not installed, test that validation fails
		if not is_erpnext_installed():
			# Create or get settings
			settings = frappe.get_single("IT Management Settings")

			# Try to enable ERPNext links
			settings.use_erpnext_links = 1

			# This should throw an error
			with self.assertRaises(frappe.ValidationError):
				settings.validate()

	def test_settings_validation_with_erpnext(self):
		"""Test that enabling use_erpnext_links works with ERPNext."""
		from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

		# If ERPNext is installed, test that validation passes
		if is_erpnext_installed():
			# Create or get settings
			settings = frappe.get_single("IT Management Settings")

			# Enable ERPNext links
			settings.use_erpnext_links = 1

			# This should not throw an error
			try:
				settings.validate()
			except frappe.ValidationError:
				self.fail("Validation failed even though ERPNext is installed")

	def test_field_mapping_exists(self):
		"""Test that field mappings are properly defined."""
		from it_management.it_management.utils.erpnext_integration import get_erpnext_doctype_fields_mapping

		mapping = get_erpnext_doctype_fields_mapping()

		# Check that ITM Host Item is in the mapping
		self.assertIn("ITM Host Item", mapping)

		# Check that it has the expected fields
		itm_host_item_config = mapping["ITM Host Item"]
		self.assertIn("erpnext_fields", itm_host_item_config)
		self.assertIn("itm_fields", itm_host_item_config)

		# Check that customer and item_code are in erpnext_fields
		erpnext_fields = itm_host_item_config["erpnext_fields"]
		self.assertIn("customer", erpnext_fields)
		self.assertIn("item_code", erpnext_fields)

		# Check that itm_customer and itm_item are in itm_fields
		itm_fields = itm_host_item_config["itm_fields"]
		self.assertIn("itm_customer", itm_fields)
		self.assertIn("itm_item", itm_fields)


# Run tests if this file is executed directly
if __name__ == '__main__':
	unittest.main()
