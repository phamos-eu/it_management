# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe


PAGE_NAME = "it-landscape-graph"
WORKSPACE_NAME = "IT Management"


def execute():
	"""
	Ensure the IT Landscape Graph Desk Page exists and is linked in the
	IT Management workspace.

	Page assets live at:
	it_management/page/it_landscape_graph/it_landscape_graph.js
	Compatible with Frappe v15 and v16.
	"""
	_ensure_page()
	_ensure_workspace_link()


def _ensure_page():
	"""Create or repair the Page document used by Desk routing."""
	page_values = {
		"page_name": PAGE_NAME,
		"title": "IT Landscape Graph",
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
			changed = True

		if changed:
			# Page.validate() requires developer mode for new pages; keep
			# ignore_validate for safe updates during migrate as well.
			page.flags.ignore_validate = True
			page.save(ignore_permissions=True)
			frappe.db.commit()
			frappe.log(f"Updated Page: {PAGE_NAME}")
		else:
			frappe.log(f"Page {PAGE_NAME} already up to date")
		return

	page = frappe.get_doc(
		{
			"doctype": "Page",
			**page_values,
			"roles": [
				{"role": "System Manager"},
				{"role": "Desk User"},
			],
		}
	)
	# Skip Page.validate() developer-mode check during migrate
	page.flags.ignore_validate = True
	page.insert(ignore_permissions=True)
	frappe.db.commit()
	frappe.log(f"Created Page: {PAGE_NAME}")


def _ensure_workspace_link():
	"""Add a workspace link to the Desk Page if missing."""
	if not frappe.db.exists("Workspace", WORKSPACE_NAME):
		frappe.log(f"Workspace '{WORKSPACE_NAME}' not found, skipping link addition")
		return

	workspace = frappe.get_doc("Workspace", WORKSPACE_NAME)
	link_exists = any(
		link.get("link_to") == PAGE_NAME and link.get("link_type") == "Page"
		for link in workspace.get("links", [])
	)

	if link_exists:
		frappe.log("IT Landscape Graph link already exists in workspace")
		return

	workspace.append(
		"links",
		{
			"type": "Link",
			"link_type": "Page",
			"link_to": PAGE_NAME,
			"label": "IT Landscape Graph",
		},
	)
	workspace.save(ignore_permissions=True)
	frappe.db.commit()
	frappe.log("IT Landscape Graph link added to IT Management workspace")
