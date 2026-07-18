# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Rename ITM Host Item status value Obsolet → Obsolete.

Keeps the existing status set (Implementing, Running, Issue, Storage, Obsolete)
and only corrects the English spelling on ITM Host Item. Existing records with
status "Obsolet" are updated so they remain valid after the Select options change.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Host Item"):
		return

	if not frappe.db.has_column("ITM Host Item", "status"):
		return

	count = frappe.db.count("ITM Host Item", {"status": "Obsolet"})
	if not count:
		frappe.log("ITM Host Item: no Obsolet status values to rename")
		return

	frappe.db.sql(
		"""
		UPDATE `tabITM Host Item`
		SET `status` = 'Obsolete'
		WHERE `status` = 'Obsolet'
		"""
	)
	frappe.log(
		"ITM Host Item: renamed status Obsolet → Obsolete on {0} record(s)".format(count)
	)
	frappe.db.commit()
