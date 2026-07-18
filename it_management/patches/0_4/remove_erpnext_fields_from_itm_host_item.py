# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Migrate ITM Host Item ERPNext Link fields off the DocType JSON.

Runs as a pre_model_sync patch (default patches.txt format) so it executes
BEFORE DocType sync. That lets us preserve valued columns as Data Custom Fields
before JSON sync would drop them.

After migration:
- Fresh schema has no customer / item_code standard fields
- Settings toggle creates Link Custom Fields via sync_erpnext_custom_fields()

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	from it_management.it_management.utils.erpnext_integration import (
		migrate_managed_erpnext_standard_fields,
		sync_erpnext_custom_fields,
	)

	if not frappe.db.exists("DocType", "ITM Host Item"):
		frappe.log("ITM Host Item DocType not found, skipping patch")
		return

	for line in migrate_managed_erpnext_standard_fields(doctypes=["ITM Host Item"]):
		frappe.log("ERPNext field migration: {0}".format(line))

	for line in sync_erpnext_custom_fields(doctypes=["ITM Host Item"]):
		frappe.log("ERPNext custom field sync: {0}".format(line))

	frappe.db.commit()
	frappe.clear_cache(doctype="ITM Host Item")
