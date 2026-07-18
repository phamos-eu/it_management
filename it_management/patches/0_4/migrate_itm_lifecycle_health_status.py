# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Replace blended ITM status with lifecycle_status + health_status.

ITM Host Item / ITM Solution:
- Copy legacy status → lifecycle_status / health_status
- Issue → lifecycle Running, health Critical
- Obsolet → lifecycle Obsolete, health Unknown
- Drop orphaned status column when present

ITM Software Instance:
- Fill blank lifecycle_status / health_status with defaults

Then refresh ITM Solution health from Running host members.
"""

import frappe

from it_management.it_management.utils.status import (
	map_legacy_status,
	update_solution_health,
)


def execute():
	_migrate_legacy_status_doctype("ITM Host Item")
	_migrate_legacy_status_doctype("ITM Solution")
	_ensure_software_instance_defaults()
	_refresh_all_solution_health()
	frappe.db.commit()


def _migrate_legacy_status_doctype(doctype):
	if not frappe.db.exists("DocType", doctype):
		return

	if not frappe.db.has_column(doctype, "lifecycle_status"):
		return

	if frappe.db.has_column(doctype, "status"):
		rows = frappe.db.sql(
			"""
			SELECT `name`, `status`
			FROM `tab{doctype}`
			""".format(doctype=doctype),
			as_dict=True,
		)
		for row in rows:
			lifecycle, health = map_legacy_status(row.get("status"))
			values = {"lifecycle_status": lifecycle}
			if frappe.db.has_column(doctype, "health_status"):
				values["health_status"] = health
			frappe.db.set_value(doctype, row.name, values, update_modified=False)

		frappe.db.sql(
			"ALTER TABLE `tab{doctype}` DROP COLUMN `status`".format(doctype=doctype)
		)
		frappe.log(
			"{0}: migrated status → lifecycle_status/health_status ({1} row(s))".format(
				doctype, len(rows)
			)
		)
	else:
		# Fresh column set: ensure defaults on blank values
		_fill_blank_lifecycle_health(doctype)
		frappe.log("{0}: no legacy status column; defaults applied if needed".format(doctype))


def _fill_blank_lifecycle_health(doctype):
	if frappe.db.has_column(doctype, "lifecycle_status"):
		frappe.db.sql(
			"""
			UPDATE `tab{doctype}`
			SET `lifecycle_status` = 'Implementing'
			WHERE IFNULL(`lifecycle_status`, '') = ''
			""".format(doctype=doctype)
		)
	if frappe.db.has_column(doctype, "health_status"):
		frappe.db.sql(
			"""
			UPDATE `tab{doctype}`
			SET `health_status` = 'Unknown'
			WHERE IFNULL(`health_status`, '') = ''
			""".format(doctype=doctype)
		)


def _ensure_software_instance_defaults():
	doctype = "ITM Software Instance"
	if not frappe.db.exists("DocType", doctype):
		return
	if not frappe.db.has_column(doctype, "lifecycle_status"):
		return
	_fill_blank_lifecycle_health(doctype)
	frappe.log("ITM Software Instance: applied lifecycle/health defaults where blank")


def _refresh_all_solution_health():
	if not frappe.db.exists("DocType", "ITM Solution"):
		return
	if not frappe.db.has_column("ITM Solution", "health_status"):
		return

	for name in frappe.get_all("ITM Solution", pluck="name"):
		update_solution_health(name, update_modified=False)

	frappe.log("ITM Solution: refreshed derived health_status")
