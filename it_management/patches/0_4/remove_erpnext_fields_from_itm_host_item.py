# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Remove ERPNext Link fields from ITM Host Item and ITM Solution DocTypes.

These fields (customer, item_code, supplier) should only be added as Custom Fields when:
1. ERPNext is installed
2. The "Use ERPNext Link Fields" setting is enabled in IT Management Settings

This ensures the DocTypes don't reference non-existent DocTypes when ERPNext is not installed,
preventing errors like: "Field customer is referring to non-existing doctype Customer."

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	"""Remove ERPNext fields from ITM Host Item and ITM Solution DocTypes."""
	from it_management.it_management.utils.erpnext_integration import (
		is_erpnext_installed,
		create_custom_field,
	)

	# Define which DocTypes and fields to process
	doctypes_to_fix = {
		"ITM Host Item": {
			"fields_to_remove": ["customer", "item_code"],
			"custom_fields": [
				{"fieldname": "customer", "label": "Customer", "options": "Customer"},
				{"fieldname": "item_code", "label": "Item", "options": "Item"}
			]
		},
		"ITM Solution": {
			"fields_to_remove": ["customer", "supplier"],
			"custom_fields": [
				{"fieldname": "customer", "label": "Customer", "options": "Customer"},
				{"fieldname": "supplier", "label": "Supplier", "options": "Supplier"}
			]
		}
	}

	for doctype, config in doctypes_to_fix.items():
		# Check if the DocType exists
		if not frappe.db.exists("DocType", doctype):
			frappe.log(f"{doctype} DocType not found, skipping")
			continue

		# Get the DocType
		doc = frappe.get_doc("DocType", doctype)

		# Remove fields from field_order
		new_field_order = [
			f for f in doc.field_order 
			if f not in config["fields_to_remove"]
		]

		if new_field_order != doc.field_order:
			doc.field_order = new_field_order

		# Remove fields from fields list
		new_fields = [
			f for f in doc.fields 
			if f.fieldname not in config["fields_to_remove"]
		]

		if len(new_fields) != len(doc.fields):
			doc.fields = new_fields

		# Save the DocType
		doc.save(ignore_permissions=True)
		frappe.db.commit()
		frappe.clear_cache(doctype=doctype)

		frappe.log(f"Removed ERPNext fields from {doctype} DocType")

	# Now add them as Custom Fields if ERPNext is installed and setting is enabled
	if is_erpnext_installed():
		try:
			settings = frappe.get_single("IT Management Settings")
			use_erpnext = settings.use_erpnext_links if settings else False
		except Exception:
			use_erpnext = False

		if use_erpnext:
			for doctype, config in doctypes_to_fix.items():
				for field_info in config["custom_fields"]:
					create_custom_field(
						doctype,
						field_info["fieldname"],
						"Link",
						options=field_info["options"],
						label=field_info["label"]
					)

			frappe.db.commit()
			frappe.log("Added ERPNext fields as Custom Fields (ERPNext is installed and enabled)")
		else:
			frappe.log("ERPNext is installed but not enabled in settings. Fields not added as Custom Fields.")
	else:
		frappe.log("ERPNext is not installed. ERPNext fields not added as Custom Fields.")
