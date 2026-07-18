# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Migrate ERPNext Link fields off ITM Host Item and ITM Solution DocTypes.

Aligned with the Host Item + Solution scope from PR discussions: these fields
must not ship as standard Links (FormMeta fails without ERPNext). They are
managed as Custom Fields when ERPNext is installed and
"Use ERPNext Link Fields" is enabled.

Data-safe (pre_model_sync):
- valued Link columns → Data Custom Fields (same fieldname)
- empty Link columns → removed
- then sync_erpnext_custom_fields() applies the settings toggle

Further ITM-* DocTypes are covered by migrate_itm_erpnext_link_fields.

Compatible with Frappe v15 and v16.
"""

import frappe

# Same DocTypes/fields as the Host Item + Solution alignment target
_HOST_ITEM_AND_SOLUTION = ("ITM Host Item", "ITM Solution")


def execute():
	from it_management.it_management.utils.erpnext_integration import (
		migrate_managed_erpnext_standard_fields,
		sync_erpnext_custom_fields,
	)

	for line in migrate_managed_erpnext_standard_fields(doctypes=list(_HOST_ITEM_AND_SOLUTION)):
		frappe.log("ERPNext field migration: {0}".format(line))

	for line in sync_erpnext_custom_fields(doctypes=list(_HOST_ITEM_AND_SOLUTION)):
		frappe.log("ERPNext custom field sync: {0}".format(line))

	frappe.db.commit()
	for doctype in _HOST_ITEM_AND_SOLUTION:
		if frappe.db.exists("DocType", doctype):
			frappe.clear_cache(doctype=doctype)
