# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Default location_type / is_group on existing ITM Location rows.

Existing locations become Site (group) so the new hierarchy can be built under them.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Location"):
		return

	if not frappe.db.has_column("ITM Location", "location_type"):
		return

	frappe.db.sql(
		"""
		UPDATE `tabITM Location`
		SET `location_type` = 'Site'
		WHERE IFNULL(`location_type`, '') = ''
		"""
	)

	if frappe.db.has_column("ITM Location", "is_group"):
		frappe.db.sql(
			"""
			UPDATE `tabITM Location`
			SET `is_group` = 1
			WHERE `location_type` IN ('Site', 'Building', 'Floor')
			"""
		)
		frappe.db.sql(
			"""
			UPDATE `tabITM Location`
			SET `is_group` = 0
			WHERE `location_type` = 'Room'
			"""
		)

	frappe.log("ITM Location: applied location_type/is_group defaults")
	frappe.db.commit()
