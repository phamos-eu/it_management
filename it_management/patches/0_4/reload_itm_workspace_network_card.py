# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""
Ensure the IT Management workspace shows a Networking section.

Adds a Networking header, short description, and card with the ITM
networking DocTypes (LAN, Subnet, IP, NIC, Socket, Host Domain).
"""

import json

import frappe


WORKSPACE = "IT Management"
CARD_LABEL = "Networking"

NETWORK_LINKS = [
	"ITM Local Area Network",
	"ITM Subnet",
	"ITM IP Address",
	"ITM Network Interface Controller",
	"ITM Socket",
	"ITM Host Domain",
]

NETWORKING_SECTION_BLOCKS = [
	{
		"id": "itmNetHdr1",
		"type": "header",
		"data": {"text": '<span class="h5">Networking</span>', "col": 12},
	},
	{
		"id": "itmNetPara1",
		"type": "paragraph",
		"data": {
			"text": (
				"Manage local area networks, subnets, IP addresses, network "
				"interfaces, wall sockets, and host domains for each ITM Landscape."
			),
			"col": 12,
		},
	},
	{
		"id": "itmNetCard1",
		"type": "card",
		"data": {"card_name": CARD_LABEL, "col": 4},
	},
]


def execute():
	try:
		frappe.reload_doc("it_management", "workspace", "it_management", force=True)
	except Exception:
		frappe.log("Could not reload workspace doc from files; updating DB row")

	if not frappe.db.exists("Workspace", WORKSPACE):
		return

	doc = frappe.get_doc("Workspace", WORKSPACE)
	_ensure_networking_card_break(doc)
	_ensure_network_links(doc)
	_ensure_networking_section_in_content(doc)
	doc.save(ignore_permissions=True)
	frappe.clear_cache()
	frappe.log("IT Management workspace: Networking section ensured")


def _ensure_networking_card_break(doc):
	for row in doc.links or []:
		if row.type == "Card Break" and row.label in ("Network", "Networking"):
			row.label = CARD_LABEL
			row.link_count = len(NETWORK_LINKS)
			return

	doc.append(
		"links",
		{
			"type": "Card Break",
			"label": CARD_LABEL,
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


def _ensure_networking_section_in_content(doc):
	try:
		blocks = json.loads(doc.content or "[]")
	except (TypeError, ValueError):
		blocks = []

	# Drop older Network-only card so we can insert the full section once
	blocks = [
		block
		for block in blocks
		if not (
			block.get("type") == "card"
			and (block.get("data") or {}).get("card_name") in ("Network", "Networking")
		)
		and block.get("id") not in ("itmNetHdr1", "itmNetPara1", "itmNetCard1")
	]

	# Ensure Configuration has a section header for consistency
	has_config_header = any(block.get("id") == "itmCfgHdr1" for block in blocks)
	if not has_config_header:
		for idx, block in enumerate(blocks):
			if (
				block.get("type") == "card"
				and (block.get("data") or {}).get("card_name") == "Configuration"
			):
				blocks.insert(
					idx,
					{
						"id": "itmCfgHdr1",
						"type": "header",
						"data": {
							"text": '<span class="h5">Configuration</span>',
							"col": 12,
						},
					},
				)
				break

	blocks.extend(NETWORKING_SECTION_BLOCKS)
	doc.content = json.dumps(blocks)
