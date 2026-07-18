# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Normalize ITM Host Item status values after Select options cleanup.

- Renames Obsolet → Obsolete (spelling fix)
- Sets blank/NULL status → Implementing (empty option removed; default is Implementing)

Keeps the status set: Implementing, Running, Issue, Storage, Obsolete.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Host Item"):
		return

	if not frappe.db.has_column("ITM Host Item", "status"):
		return

	obsolet_count = frappe.db.count("ITM Host Item", {"status": "Obsolet"})
	if obsolet_count:
		frappe.db.sql(
			"""
			UPDATE `tabITM Host Item`
			SET `status` = 'Obsolete'
			WHERE `status` = 'Obsolet'
			"""
		)
		frappe.log(
			"ITM Host Item: renamed status Obsolet → Obsolete on {0} record(s)".format(
				obsolet_count
			)
		)
	else:
		frappe.log("ITM Host Item: no Obsolet status values to rename")

	# Empty string or NULL (blank Select option removed)
	blank_count = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabITM Host Item`
		WHERE IFNULL(`status`, '') = ''
		"""
	)[0][0]
	if blank_count:
		frappe.db.sql(
			"""
			UPDATE `tabITM Host Item`
			SET `status` = 'Implementing'
			WHERE IFNULL(`status`, '') = ''
			"""
		)
		frappe.log(
			"ITM Host Item: set blank status → Implementing on {0} record(s)".format(
				blank_count
			)
		)
	else:
		frappe.log("ITM Host Item: no blank status values to set")

	frappe.db.commit()
