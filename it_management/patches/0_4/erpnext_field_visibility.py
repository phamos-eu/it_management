# -*- coding: utf-8 -*-
# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Patch to validate ERPNext integration settings.
This ensures that the 'Use ERPNext Link Fields' setting is not enabled
when ERPNext is not installed.
"""

from __future__ import unicode_literals, print_function
import frappe


def execute():
	"""Execute the patch."""
	from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

	# Log that we're running the patch
	frappe.log("Running ERPNext field visibility patch...")

	# Check if ERPNext is installed
	erpnext_installed = is_erpnext_installed()
	frappe.log("ERPNext installed: {0}".format(erpnext_installed))

	# Get settings and validate
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
			frappe.log("Setting disabled successfully.")
		else:
			frappe.log("Settings are valid. No changes needed.")
	except Exception:
		frappe.log("Error getting settings")

	frappe.log("ERPNext field visibility patch completed.")
