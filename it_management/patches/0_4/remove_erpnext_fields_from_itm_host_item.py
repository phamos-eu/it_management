# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Remove ERPNext Link fields from ITM Host Item DocType.

These fields (customer, item_code) should only be added as Custom Fields when:
1. ERPNext is installed
2. The "Use ERPNext Link Fields" setting is enabled in IT Management Settings

This ensures the DocType doesn't reference non-existent DocTypes when ERPNext is not installed,
preventing the error: "Field customer is referring to non-existing doctype Customer."

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	"""Remove customer and item_code fields from ITM Host Item DocType."""
	from it_management.it_management.utils.erpnext_integration import (
		is_erpnext_installed,
		create_custom_field,
	)

	# Check if the DocType exists
	if not frappe.db.exists("DocType", "ITM Host Item"):
		frappe.log("ITM Host Item DocType not found, skipping patch")
		return

	# Get the DocType
	doc = frappe.get_doc("DocType", "ITM Host Item")

	# ERPNext fields to remove
	erpnext_fields_to_remove = ["customer", "item_code"]

	# Remove ERPNext fields from field_order
	new_field_order = [f for f in doc.field_order if f not in erpnext_fields_to_remove]

	if new_field_order != doc.field_order:
		doc.field_order = new_field_order

	# Remove ERPNext fields from fields list
	new_fields = [f for f in doc.fields if f.fieldname not in erpnext_fields_to_remove]

	if len(new_fields) != len(doc.fields):
		doc.fields = new_fields

	# Save the DocType
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.clear_cache(doctype="ITM Host Item")

	frappe.log("Removed ERPNext fields (customer, item_code) from ITM Host Item DocType")

	# Now add them as Custom Fields if ERPNext is installed and setting is enabled
	if is_erpnext_installed():
		try:
			settings = frappe.get_single("IT Management Settings")
			use_erpnext = settings.use_erpnext_links if settings else False
		except Exception:
			use_erpnext = False

		if use_erpnext:
			# Add customer field as Custom Field
			create_custom_field(
				"ITM Host Item",
				"customer",
				"Link",
				options="Customer",
				label="Customer"
			)

			# Add item_code field as Custom Field
			create_custom_field(
				"ITM Host Item",
				"item_code",
				"Link",
				options="Item",
				label="Item"
			)

			frappe.db.commit()
			frappe.log("Added ERPNext fields (customer, item_code) as Custom Fields")
		else:
			frappe.log("ERPNext is installed but not enabled in settings. Fields not added as Custom Fields.")
	else:
		frappe.log("ERPNext is not installed. ERPNext fields not added as Custom Fields.")
