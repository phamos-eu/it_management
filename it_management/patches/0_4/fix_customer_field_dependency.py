# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Fix the depends_on condition for customer and item_code fields in ITM Host Item.
	The current condition 'eval:doc.use_erpnext_links || !doc.use_erpnext_links' is a tautology (always true).
	This causes these fields to always be visible, even when ERPNext is not installed.
	
	This patch updates the depends_on to hide these fields by default when ERPNext is not installed.
	
	Compatible with Frappe v15 and v16.
	"""
	from it_management.it_management.utils.erpnext_integration import is_erpnext_installed

	# Check if ERPNext is installed
	erpnext_installed = is_erpnext_installed()

	# Check if the DocType exists
	if not frappe.db.exists("DocType", "ITM Host Item"):
		frappe.log("ITM Host Item DocType not found, skipping patch")
		return

	# Get the DocType
	doc = frappe.get_doc("DocType", "ITM Host Item")

	# Fields to fix: customer, item_code (ERPNext fields)
	fields_to_fix = ["customer", "item_code"]

	for fieldname in fields_to_fix:
		# Find the field
		field = None
		for f in doc.fields:
			if f.fieldname == fieldname:
				field = f
				break

		if not field:
			frappe.log(f"Field '{fieldname}' not found in ITM Host Item, skipping")
			continue

		# Only fix if ERPNext is not installed
		if not erpnext_installed:
			old_depends_on = field.depends_on
			new_depends_on = "eval:False"

			if old_depends_on == new_depends_on:
				frappe.log(f"Field '{fieldname}' depends_on is already '{new_depends_on}', skipping")
				continue

			field.depends_on = new_depends_on
			frappe.log(f"Updated ITM Host Item '{fieldname}' field depends_on from '{old_depends_on}' to '{new_depends_on}'")

	# Save if any changes were made
	if any(f.depends_on == "eval:False" for f in doc.fields if f.fieldname in fields_to_fix):
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		frappe.log("ITM Host Item DocType updated successfully")
	else:
		frappe.log("No changes needed for ITM Host Item DocType")
