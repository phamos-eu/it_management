# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""Ensure Networking Overview page and Networking child workspace exist."""

import frappe

PAGE_NAME = "it-networking-overview"


def execute():
	_ensure_page()
	frappe.reload_doc("IT Management", "workspace", "networking", force=True)
	frappe.reload_doc("IT Management", "workspace", "it_management", force=True)
	frappe.clear_cache()
	frappe.db.commit()


def _ensure_page():
	page_values = {
		"page_name": PAGE_NAME,
		"title": "Networking Overview",
		"module": "IT Management",
		"standard": "Yes",
	}

	if frappe.db.exists("Page", PAGE_NAME):
		page = frappe.get_doc("Page", PAGE_NAME)
		changed = False
		for fieldname, value in page_values.items():
			if page.get(fieldname) != value:
				page.set(fieldname, value)
				changed = True
		if not page.roles:
			page.append("roles", {"role": "System Manager"})
			page.append("roles", {"role": "Desk User"})
			page.append("roles", {"role": "Support Team"})
			changed = True
		if changed:
			page.flags.ignore_validate = True
			page.save(ignore_permissions=True)
		return

	page = frappe.get_doc(
		{
			"doctype": "Page",
			**page_values,
			"roles": [
				{"role": "System Manager"},
				{"role": "Desk User"},
				{"role": "Support Team"},
			],
		}
	)
	page.flags.ignore_validate = True
	page.insert(ignore_permissions=True)
