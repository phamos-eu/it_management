# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Migrate all ITM-* DocType ERPNext Link fields to settings-driven Custom Fields.

Covers every ITM DocType that linked to Customer / Item / Supplier (including
ITM Solution, ITM Trip, ITM User Account, child tables, etc.).

Pre_model_sync (default patches.txt): preserve valued columns as Data Custom
Fields before DocType JSON sync would drop them, then apply the current
IT Management Settings toggle.

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	from it_management.it_management.utils.erpnext_integration import (
		migrate_managed_erpnext_standard_fields,
		sync_erpnext_custom_fields,
	)

	for line in migrate_managed_erpnext_standard_fields():
		frappe.log("ITM ERPNext field migration: {0}".format(line))

	for line in sync_erpnext_custom_fields():
		frappe.log("ITM ERPNext custom field sync: {0}".format(line))

	frappe.db.commit()
