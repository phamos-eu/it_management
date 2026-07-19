# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Migrate ITM Subnet from free-text CIDR (`subnet`) to designed IPv4 fields.

Also sets lifecycle_status default and DocType title/autoname metadata.
"""

import frappe

from it_management.it_management.utils.ipv4 import design_from_cidr, design_from_network_and_prefix


def execute():
	if not frappe.db.exists("DocType", "ITM Subnet"):
		return

	legacy_rows = []
	if frappe.db.has_column("ITM Subnet", "subnet"):
		legacy_rows = frappe.db.sql(
			"""
			SELECT name, subnet, itm_landscape
			FROM `tabITM Subnet`
			WHERE IFNULL(subnet, '') != ''
			""",
			as_dict=True,
		)

	frappe.reload_doc("IT Management", "doctype", "itm_subnet", force=True)

	if frappe.db.has_column("ITM Subnet", "lifecycle_status"):
		frappe.db.sql(
			"""
			UPDATE `tabITM Subnet`
			SET `lifecycle_status` = 'Implementing'
			WHERE IFNULL(`lifecycle_status`, '') = ''
			"""
		)

	for row in legacy_rows:
		if not frappe.db.has_column("ITM Subnet", "network_address"):
			break
		if frappe.db.get_value("ITM Subnet", row.name, "cidr"):
			continue
		try:
			design = design_from_cidr(row.subnet)
		except (ValueError, TypeError):
			frappe.log(f"ITM Subnet {row.name}: could not parse legacy CIDR {row.subnet!r}")
			continue

		frappe.db.set_value(
			"ITM Subnet",
			row.name,
			{
				"network_address": design["network_address"],
				"prefix_length": design["prefix_length"],
				"subnet_mask": design["subnet_mask"],
				"cidr": design["cidr"],
				"first_usable": design["first_usable"],
				"last_usable": design["last_usable"],
				"broadcast": design["broadcast"],
				"usable_hosts": design["usable_hosts"],
				"lifecycle_status": "Implementing",
			},
			update_modified=False,
		)

	# Fill derived fields for rows that already have network/prefix but empty cidr
	if frappe.db.has_column("ITM Subnet", "network_address"):
		pending = frappe.db.sql(
			"""
			SELECT name, network_address, prefix_length
			FROM `tabITM Subnet`
			WHERE IFNULL(network_address, '') != ''
				AND IFNULL(cidr, '') = ''
			""",
			as_dict=True,
		)
		for row in pending:
			try:
				design = design_from_network_and_prefix(row.network_address, row.prefix_length)
			except (ValueError, TypeError):
				continue
			frappe.db.set_value(
				"ITM Subnet",
				row.name,
				{
					"network_address": design["network_address"],
					"prefix_length": design["prefix_length"],
					"subnet_mask": design["subnet_mask"],
					"cidr": design["cidr"],
					"first_usable": design["first_usable"],
					"last_usable": design["last_usable"],
					"broadcast": design["broadcast"],
					"usable_hosts": design["usable_hosts"],
				},
				update_modified=False,
			)

	frappe.db.set_value(
		"DocType",
		"ITM Subnet",
		{
			"autoname": "hash",
			"title_field": "cidr",
			"allow_rename": 0,
			"show_title_field_in_link": 1,
		},
		update_modified=False,
	)

	frappe.db.delete("DocField", {"parent": "ITM Subnet", "fieldname": "subnet"})
	frappe.clear_cache(doctype="ITM Subnet")
	frappe.db.commit()
