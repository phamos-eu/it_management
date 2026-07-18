# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Prevent form-load failures when ERPNext is not installed.

Root cause (Frappe v15): FormMeta.add_search_fields() calls get_meta() on every
Link field's options. Fields that still point at Customer/Item/Supplier throw:

	Field customer is referring to non-existing doctype Customer.

depends_on / hidden do not skip that check. This patch neutralizes those Link
options via Property Setters when ERPNext is absent (and restores them when it
is present).

Compatible with Frappe v15 and v16.
"""

import frappe


def execute():
	from it_management.it_management.utils.erpnext_integration import (
		is_erpnext_installed,
		sync_erpnext_link_fields,
	)

	frappe.log(
		"Syncing ERPNext Link fields (ERPNext installed: {0})".format(
			is_erpnext_installed()
		)
	)
	changed = sync_erpnext_link_fields()
	if changed:
		frappe.db.commit()
		for entry in changed:
			frappe.log("ERPNext Link field sync: {0}".format(entry))
	else:
		frappe.log("ERPNext Link field sync: no changes needed")
