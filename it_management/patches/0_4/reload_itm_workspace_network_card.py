# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Ensure the IT Management workspace shows the Network card.

The networking DocTypes were added with Card Break links, but the workspace
`content` JSON only rendered the Configuration card, so Network stayed hidden.
"""

import json

import frappe


WORKSPACE = "IT Management"

NETWORK_LINKS = [
	"ITM Local Area Network",
	"ITM Subnet",
	"ITM IP Address",
	"ITM Network Interface Controller",
	"ITM Socket",
	"ITM Host Domain",
]


def execute():
	try:
		frappe.reload_doc("it_management", "workspace", "it_management", force=True)
	except Exception:
		frappe.log("Could not reload workspace doc from files; updating DB row")

	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	doc = frappe.get_doc("Workspace", WORKSPACE)
	_ensure_network_card_break(doc)
	_ensure_network_links(doc)
	_ensure_network_card_in_content(doc)
	doc.save(ignore_permissions=True)
	frappe.clear_cache()
	frappe.log("IT Management workspace: Network card ensured")


def _ensure_network_card_break(doc):
	for row in doc.links or []:
		if row.type == "Card Break" and row.label == "Network":
			row.link_count = len(NETWORK_LINKS)
			return

	doc.append(
		"links",
		{
			"type": "Card Break",
			"label": "Network",
			"link_type": "DocType",
			"link_count": len(NETWORK_LINKS),
			"hidden": 0,
		},
	)


def _ensure_network_links(doc):
	existing = {
		row.link_to
		for row in (doc.links or [])
		if row.type == "Link" and row.link_to
	}
	for name in NETWORK_LINKS:
		if name in existing:
			continue
		doc.append(
			"links",
			{
				"type": "Link",
				"label": name,
				"link_type": "DocType",
				"link_to": name,
				"hidden": 0,
			},
		)


def _ensure_network_card_in_content(doc):
	try:
		blocks = json.loads(doc.content or "[]")
	except (TypeError, ValueError):
		blocks = []

	has_network_card = any(
		block.get("type") == "card"
		and (block.get("data") or {}).get("card_name") == "Network"
		for block in blocks
	)
	if has_network_card:
		return

	blocks.append(
		{
			"id": "itmNetCard1",
			"type": "card",
			"data": {"card_name": "Network", "col": 4},
		}
	)
	doc.content = json.dumps(blocks)
