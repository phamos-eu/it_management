# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Patch to initialize ERPNext field visibility based on settings.
This ensures that when the patch is run, all doctypes with ERPNext fields
are properly configured based on whether ERPNext is installed and the
IT Management Settings.
"""

from __future__ import unicode_literals, print_function
import frappe


def execute():
	"""Execute the patch."""
	from it_management.it_management.utils.erpnext_integration import (
		is_erpnext_installed,
		sync_all_erpnext_fields
	)

	# Log that we're running the patch
	frappe.log("Running ERPNext field visibility patch...")

	# Check if ERPNext is installed
	erpnext_installed = is_erpnext_installed()
	frappe.log("ERPNext installed: {0}".format(erpnext_installed))

	# Sync all doctypes
	sync_all_erpnext_fields()

	# Get settings and log them
	try:
		settings = frappe.get_single("IT Management Settings")
		use_erpnext = settings.use_erpnext_links if settings else True
		frappe.log("Use ERPNext Links setting: {0}".format(use_erpnext))

		# If ERPNext is not installed but the setting is enabled, disable it
		if not erpnext_installed and use_erpnext:
			frappe.log("ERPNext not installed but setting is enabled. Disabling...")
			settings.use_erpnext_links = 0
			settings.save()
			frappe.db.commit()
	except Exception as e:
		frappe.log("Error getting settings: {0}".format(e))

	frappe.log("ERPNext field visibility patch completed.")
