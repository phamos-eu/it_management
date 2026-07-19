# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Move LAN↔Subnet from child table links to ITM Subnet.itm_local_area_network.

Also drops the ITM Subnet Table DocType after migrating.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Subnet"):
		return

	# Add link column on Subnet first; keep LAN child table until data is copied
	frappe.reload_doc("IT Management", "doctype", "itm_subnet", force=True)

	_migrate_child_table_links()

	# Drop child table field from LAN, then remove the child DocType
	frappe.reload_doc("IT Management", "doctype", "itm_local_area_network", force=True)
	_cleanup_orphan_lan_table_field()
	_delete_subnet_table_doctype()

	frappe.clear_cache(doctype="ITM Subnet")
	frappe.clear_cache(doctype="ITM Local Area Network")
	frappe.db.commit()


def _migrate_child_table_links():
	if not frappe.db.exists("DocType", "ITM Subnet Table"):
		return

	if not frappe.db.has_column("ITM Subnet", "itm_local_area_network"):
		return

	if not frappe.db.table_exists("ITM Subnet Table"):
		return

	rows = frappe.db.sql(
		"""
		SELECT parent AS lan, itm_subnet AS subnet
		FROM `tabITM Subnet Table`
		WHERE IFNULL(itm_subnet, '') != ''
		ORDER BY creation ASC
		""",
		as_dict=True,
	)

	seen = set()
	for row in rows:
		if row.subnet in seen:
			frappe.log(
				f"ITM Subnet {row.subnet} linked to multiple LANs; "
				f"keeping first assignment, skipping {row.lan}"
			)
			continue
		seen.add(row.subnet)

		if not frappe.db.exists("ITM Subnet", row.subnet):
			continue
		if not frappe.db.exists("ITM Local Area Network", row.lan):
			continue

		current = frappe.db.get_value("ITM Subnet", row.subnet, "itm_local_area_network")
		if current:
			continue

		lan_landscape = frappe.db.get_value(
			"ITM Local Area Network", row.lan, "itm_landscape"
		)
		values = {"itm_local_area_network": row.lan}
		if lan_landscape:
			values["itm_landscape"] = lan_landscape

		frappe.db.set_value(
			"ITM Subnet",
			row.subnet,
			values,
			update_modified=False,
		)


def _cleanup_orphan_lan_table_field():
	frappe.db.delete(
		"DocField",
		{"parent": "ITM Local Area Network", "fieldname": "itm_subnet_table"},
	)


def _delete_subnet_table_doctype():
	if not frappe.db.exists("DocType", "ITM Subnet Table"):
		return
	frappe.delete_doc("DocType", "ITM Subnet Table", force=1, ignore_permissions=True)
