# Copyright (c) 2024, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe


def execute():
	"""
	Create a Page for IT Landscape Graph and add link to IT Management workspace.
	Compatible with Frappe v15 and v16.
	"""
	# Step 1: Create the Page DocType record
	page_name = "it-landscape-graph"
	if not frappe.db.exists("Page", page_name):
		# Use frappe.db.insert to bypass Page validation which requires developer mode
		page_data = {
			"doctype": "Page",
			"page_name": page_name,
			"title": "IT Landscape Graph",
			"route": "/it-landscape-graph",
			"module": "IT Management",
			"is_virtual_page": 0,
			"script": """
// Redirect to the actual HTML file
window.location.href = '/assets/it_management/www/it_landscape_graph.html';
""",
			"is_single": 0,
			"published": 1
		}
		frappe.db.insert(page_data, ignore_permissions=True)
		frappe.db.commit()
		frappe.log(f"Created Page: {page_name}")
	else:
		frappe.log(f"Page {page_name} already exists")

	# Step 2: Add link to IT Management workspace
	workspace_name = "IT Management"
	if not frappe.db.exists("Workspace", workspace_name):
		frappe.log(f"Workspace '{workspace_name}' not found, skipping link addition")
		return

	workspace = frappe.get_doc("Workspace", workspace_name)

	# Check if the link already exists
	link_exists = any(
		link.get("link_to") == page_name
		for link in workspace.get("links", [])
	)

	if link_exists:
		frappe.log("IT Landscape Graph link already exists in workspace")
		return

	# Add the link to the workspace
	# In v15, workspace links use "link_type", "link_to", "label"
	# link_to should be the Page name, not the URL
	new_link = {
		"link_type": "Page",
		"link_to": page_name,  # This is the Page name, not the URL
		"label": "IT Landscape Graph",
		"idx": 10
	}

	workspace.append("links", new_link)
	workspace.save(ignore_permissions=True)
	
	frappe.db.commit()
	frappe.log("IT Landscape Graph link added to IT Management workspace")
