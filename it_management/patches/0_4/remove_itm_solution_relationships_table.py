# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Remove Solution Relationships child table from ITM Solution.

ITM Solution Table remains — it is still used by ITM User Account.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Solution"):
		return

	# Drop relationship rows owned by ITM Solution only
	if frappe.db.table_exists("ITM Solution Table"):
		frappe.db.sql(
			"""
			DELETE FROM `tabITM Solution Table`
			WHERE parenttype = 'ITM Solution'
			"""
		)

	frappe.reload_doc("IT Management", "doctype", "itm_solution", force=True)

	frappe.db.delete(
		"DocField",
		{"parent": "ITM Solution", "fieldname": "itm_solution_table"},
	)

	frappe.clear_cache(doctype="ITM Solution")
	frappe.db.commit()
