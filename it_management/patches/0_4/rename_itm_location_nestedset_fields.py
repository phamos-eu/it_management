# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Align ITM Location NestedSet field names with Frappe tree conventions.

Tree view posts parent as parent_<scrub(doctype)> → parent_itm_location.
NestedSet tracks moves via old_parent.
"""

import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	if not frappe.db.exists("DocType", "ITM Location"):
		return

	frappe.reload_doc("IT Management", "doctype", "itm_location", force=True)

	if frappe.db.has_column("ITM Location", "itm_parent_location") and not frappe.db.has_column(
		"ITM Location", "parent_itm_location"
	):
		rename_field("ITM Location", "itm_parent_location", "parent_itm_location")

	if frappe.db.has_column("ITM Location", "itm_old_parent") and not frappe.db.has_column(
		"ITM Location", "old_parent"
	):
		rename_field("ITM Location", "itm_old_parent", "old_parent")

	# Keep NestedSet parent field pointer in sync on the DocType row
	frappe.db.set_value(
		"DocType",
		"ITM Location",
		{
			"nsm_parent_field": "parent_itm_location",
			"title_field": "itm_location_name",
		},
		update_modified=False,
	)

	frappe.clear_cache(doctype="ITM Location")
	frappe.db.commit()
