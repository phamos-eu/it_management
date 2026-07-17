# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Add IT Landscape Graph link to the IT Management workspace sidebar.
	Compatible with Frappe v15 and v16.
	"""
	# Check if the workspace exists
	workspace_name = "IT Management"
	if not frappe.db.exists("Workspace", workspace_name):
		frappe.log(f"Workspace '{workspace_name}' not found, skipping link addition")
		return

	workspace = frappe.get_doc("Workspace", workspace_name)

	# Check if the link already exists
	link_exists = any(
		link.get("link_to") == "/app/it-landscape-graph"
		for link in workspace.get("links", [])
	)

	if link_exists:
		frappe.log("IT Landscape Graph link already exists in workspace")
		return

	# Add the link to the workspace
	# In v15, workspace links use "link_type", "link_to", "label"
	new_link = {
		"link_type": "Page",
		"link_to": "/app/it-landscape-graph",
		"label": "IT Landscape Graph",
		"idx": 10  # Position in the sidebar
	}

	# In v15, we append directly to the links list
	workspace.append("links", new_link)
	workspace.save(ignore_permissions=True)
	
	frappe.db.commit()
	frappe.log("IT Landscape Graph link added to IT Management workspace")
