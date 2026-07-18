# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Set deployment = Physical on existing ITM Host Items after the field is introduced.

New hosts default to Physical; this patch fills blank/NULL values for older rows.
"""

import frappe


def execute():
	if not frappe.db.exists("DocType", "ITM Host Item"):
		return

	if not frappe.db.has_column("ITM Host Item", "deployment"):
		return

	count = frappe.db.sql(
		"""
		SELECT COUNT(*) FROM `tabITM Host Item`
		WHERE IFNULL(`deployment`, '') = ''
		"""
	)[0][0]
	if not count:
		frappe.log("ITM Host Item: no blank deployment values to set")
		return

	frappe.db.sql(
		"""
		UPDATE `tabITM Host Item`
		SET `deployment` = 'Physical'
		WHERE IFNULL(`deployment`, '') = ''
		"""
	)
	frappe.log(
		"ITM Host Item: set deployment → Physical on {0} record(s)".format(count)
	)
	frappe.db.commit()
