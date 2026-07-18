# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""Lifecycle and Health status helpers for ITM DocTypes."""

from __future__ import unicode_literals

import frappe

LIFECYCLE_OPTIONS = ("Implementing", "Running", "Storage", "Obsolete")
LIFECYCLE_OPTIONS_SOFTWARE_INSTANCE = LIFECYCLE_OPTIONS + ("Uninstalled",)
HEALTH_OPTIONS = ("Healthy", "Warning", "Critical", "Unknown")

HEALTH_RANK = {
	"Critical": 3,
	"Warning": 2,
	"Unknown": 1,
	"Healthy": 0,
}

# Host lifecycle values that cascade to Software Instances
CASCADE_LIFECYCLE = {
	"Storage": "Storage",
	"Obsolete": "Obsolete",
}

# Software Instance lifecycle values that must not be overwritten by cascade
CASCADE_SKIP_SI = frozenset(("Obsolete", "Uninstalled"))


def map_legacy_status(old_status):
	"""Map legacy blended status → (lifecycle_status, health_status)."""
	if not old_status:
		return "Implementing", "Unknown"

	if old_status == "Issue":
		return "Running", "Critical"

	if old_status in ("Obsolet", "Obsolete"):
		return "Obsolete", "Unknown"

	if old_status in LIFECYCLE_OPTIONS:
		return old_status, "Unknown"

	return "Implementing", "Unknown"


def worst_health(health_values):
	"""Return the worst health among values; Unknown if empty."""
	if not health_values:
		return "Unknown"

	worst = "Healthy"
	worst_rank = -1
	for value in health_values:
		rank = HEALTH_RANK.get(value, HEALTH_RANK["Unknown"])
		if rank > worst_rank:
			worst = value if value in HEALTH_RANK else "Unknown"
			worst_rank = rank
	return worst


def compute_solution_health(solution_name):
	"""
	Derive Solution health from linked Host Items with Lifecycle Running.

	Worst wins: Critical > Warning > Unknown > Healthy.
	No Running hosts → Unknown.
	"""
	if not solution_name:
		return "Unknown"

	rows = frappe.db.sql(
		"""
		SELECT h.health_status
		FROM `tabITM Host Item` h
		INNER JOIN `tabITM Host Item Solution Table` t
			ON t.parent = h.name
			AND t.parenttype = 'ITM Host Item'
		WHERE t.itm_solution = %s
			AND h.lifecycle_status = 'Running'
		""",
		solution_name,
		as_dict=True,
	)
	if not rows:
		return "Unknown"

	return worst_health([row.get("health_status") or "Unknown" for row in rows])


def update_solution_health(solution_name, update_modified=False):
	"""Set ITM Solution.health_status from linked Running hosts."""
	if not solution_name or not frappe.db.exists("ITM Solution", solution_name):
		return

	if not frappe.db.has_column("ITM Solution", "health_status"):
		return

	new_health = compute_solution_health(solution_name)
	current = frappe.db.get_value("ITM Solution", solution_name, "health_status")
	if current == new_health:
		return

	frappe.db.set_value(
		"ITM Solution",
		solution_name,
		"health_status",
		new_health,
		update_modified=update_modified,
	)


def cascade_host_lifecycle_to_software_instances(host_name, lifecycle_status):
	"""
	Cascade host Storage/Obsolete to linked Software Instances.

	Skips instances already Obsolete or Uninstalled.
	"""
	target = CASCADE_LIFECYCLE.get(lifecycle_status)
	if not target or not host_name:
		return

	if not frappe.db.has_column("ITM Software Instance", "lifecycle_status"):
		return

	instances = frappe.get_all(
		"ITM Software Instance",
		filters={"itm_host_item": host_name},
		fields=["name", "lifecycle_status"],
	)
	for row in instances:
		if row.lifecycle_status in CASCADE_SKIP_SI:
			continue
		if row.lifecycle_status == target:
			continue
		frappe.db.set_value(
			"ITM Software Instance",
			row.name,
			"lifecycle_status",
			target,
			update_modified=False,
		)


def solutions_linked_to_host(host_doc):
	"""Return solution names linked on a Host Item (current and previous save)."""
	solutions = set()
	for row in host_doc.get("itm_host_item_solution_table") or []:
		if row.itm_solution:
			solutions.add(row.itm_solution)

	before = host_doc.get_doc_before_save()
	if before:
		for row in before.get("itm_host_item_solution_table") or []:
			if row.itm_solution:
				solutions.add(row.itm_solution)

	return solutions
