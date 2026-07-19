# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""Networking overview and plan-subnet wizard helpers."""

from __future__ import unicode_literals

import ipaddress

import frappe
from frappe import _

from it_management.it_management.utils.ipv4 import (
	design_from_network_and_prefix,
	ranges_overlap,
)

# Suggestion packs for the plan-subnet wizard (IPv4 only)
PURPOSE_PROFILES = {
	"Corporate": {
		"label": "Corporate",
		"description": "Trusted internal LAN for workstations and servers.",
		"preferred_prefix": 24,
		"growth_factor": 1.3,
		"vlan_hint": 10,
		"search_bases": ["10.0.0.0/16", "10.10.0.0/16", "172.16.0.0/16"],
		"notes": "Prefer RFC1918 private space; keep management hosts reachable.",
	},
	"Guest Wi-Fi": {
		"label": "Guest Wi-Fi",
		"description": "Isolated wireless access for visitors.",
		"preferred_prefix": 23,
		"growth_factor": 1.5,
		"vlan_hint": 40,
		"search_bases": ["10.40.0.0/16", "10.50.0.0/16", "192.168.40.0/16"],
		"notes": "Isolate from corporate; limited DHCP lease times recommended.",
	},
	"DMZ": {
		"label": "DMZ",
		"description": "Public-facing or semi-trusted services.",
		"preferred_prefix": 24,
		"growth_factor": 1.2,
		"vlan_hint": 30,
		"search_bases": ["10.30.0.0/16", "172.30.0.0/16"],
		"notes": "Tight firewall rules; minimal host count; no client DHCP pool by default.",
	},
	"Management": {
		"label": "Management",
		"description": "Out-of-band / infrastructure management network.",
		"preferred_prefix": 24,
		"growth_factor": 1.2,
		"vlan_hint": 99,
		"search_bases": ["10.99.0.0/16", "172.31.0.0/16"],
		"notes": "Restrict access to admins and controllers only.",
	},
	"IoT": {
		"label": "IoT",
		"description": "Sensors, printers, and other constrained devices.",
		"preferred_prefix": 22,
		"growth_factor": 1.4,
		"vlan_hint": 60,
		"search_bases": ["10.60.0.0/16", "10.70.0.0/16"],
		"notes": "Expect many small clients; segment from corporate data.",
	},
}


def _prefix_for_clients(expected_clients, growth_factor, preferred_prefix):
	"""Pick a prefix that fits expected clients with growth headroom."""
	try:
		clients = max(int(expected_clients or 0), 1)
	except (TypeError, ValueError):
		clients = 1
	needed = int(clients * float(growth_factor or 1.3)) + 2  # network + broadcast
	# usable hosts for prefix p is 2^(32-p) - 2 for p < 31
	for prefix in range(preferred_prefix, 8, -1):
		usable = (2 ** (32 - prefix)) - 2 if prefix < 31 else 2 ** (32 - prefix)
		if usable >= needed:
			return prefix
	return 16


def _landscape_ranges(landscape):
	rows = frappe.get_all(
		"ITM Subnet",
		filters={"itm_landscape": landscape, "network_address": ["!=", ""]},
		fields=["name", "cidr", "network_address", "prefix_length", "lifecycle_status"],
	)
	ranges = []
	for row in rows:
		try:
			design = design_from_network_and_prefix(row.network_address, row.prefix_length)
		except (ValueError, TypeError):
			continue
		ranges.append(
			{
				"name": row.name,
				"cidr": design["cidr"],
				"lifecycle_status": row.lifecycle_status,
				"network_int": design["network_int"],
				"broadcast_int": design["broadcast_int"],
			}
		)
	return ranges


def _find_free_block(landscape, prefix_length, search_bases):
	existing = _landscape_ranges(landscape)
	for base in search_bases:
		try:
			parent = ipaddress.ip_network(base, strict=False)
		except ValueError:
			continue
		if prefix_length < parent.prefixlen:
			continue
		for subnet in parent.subnets(new_prefix=prefix_length):
			start = int(subnet.network_address)
			end = int(subnet.broadcast_address)
			conflict = False
			for other in existing:
				if ranges_overlap(start, end, other["network_int"], other["broadcast_int"]):
					conflict = True
					break
			if not conflict:
				return design_from_network_and_prefix(str(subnet.network_address), prefix_length)
	# Fallback: try 10.x sequentially
	for second_octet in range(0, 256):
		try:
			design = design_from_network_and_prefix(f"10.{second_octet}.0.0", prefix_length)
		except (ValueError, TypeError):
			continue
		conflict = any(
			ranges_overlap(
				design["network_int"],
				design["broadcast_int"],
				other["network_int"],
				other["broadcast_int"],
			)
			for other in existing
		)
		if not conflict:
			return design
	frappe.throw(_("Could not find a free IPv4 block in this landscape."), title=_("No Free Space"))


def _subnet_utilization(subnet_name, usable_hosts):
	used = frappe.db.count("ITM IP Address", {"itm_subnet": subnet_name})
	usable = int(usable_hosts or 0)
	free = max(usable - used, 0)
	return {"used": used, "reserved": 0, "free": free, "usable": usable}


@frappe.whitelist()
def get_purpose_profiles():
	"""Return wizard suggestion packs."""
	return [
		{
			"name": key,
			"label": _(profile["label"]),
			"description": _(profile["description"]),
			"preferred_prefix": profile["preferred_prefix"],
			"vlan_hint": profile["vlan_hint"],
			"notes": _(profile["notes"]),
		}
		for key, profile in PURPOSE_PROFILES.items()
	]


@frappe.whitelist()
def get_networking_overview(itm_landscape=None):
	"""LAN-centric utilization tree for the Networking overview page."""
	if not itm_landscape:
		frappe.throw(_("Landscape is required."), title=_("Missing Landscape"))

	lans = frappe.get_all(
		"ITM Local Area Network",
		filters={"itm_landscape": itm_landscape},
		fields=["name", "title", "itm_location", "note"],
		order_by="title asc",
	)

	result = []
	for lan in lans:
		subnets = frappe.get_all(
			"ITM Subnet",
			filters={"itm_local_area_network": lan.name},
			fields=[
				"name",
				"cidr",
				"network_address",
				"prefix_length",
				"usable_hosts",
				"lifecycle_status",
				"vlan_tag",
			],
			order_by="cidr asc",
		)
		subnet_rows = []
		for subnet in subnets:
			util = _subnet_utilization(subnet.name, subnet.usable_hosts)
			subnet_rows.append(
				{
					"name": subnet.name,
					"cidr": subnet.cidr,
					"lifecycle_status": subnet.lifecycle_status,
					"vlan_tag": subnet.vlan_tag,
					**util,
				}
			)
		result.append(
			{
				"name": lan.name,
				"title": lan.title or lan.name,
				"itm_location": lan.itm_location,
				"note": lan.note,
				"subnets": subnet_rows,
			}
		)
	return {"itm_landscape": itm_landscape, "lans": result}


@frappe.whitelist()
def suggest_subnet_design(
	itm_landscape=None,
	purpose_profile=None,
	expected_clients=None,
	prefix_length=None,
):
	"""Suggest a free IPv4 design for the wizard address step."""
	if not itm_landscape:
		frappe.throw(_("Landscape is required."), title=_("Missing Landscape"))

	profile = PURPOSE_PROFILES.get(purpose_profile) or PURPOSE_PROFILES["Corporate"]
	if prefix_length in (None, ""):
		prefix_length = _prefix_for_clients(
			expected_clients, profile["growth_factor"], profile["preferred_prefix"]
		)
	else:
		prefix_length = int(prefix_length)

	design = _find_free_block(itm_landscape, prefix_length, profile["search_bases"])
	conflicts = []
	for other in _landscape_ranges(itm_landscape):
		if ranges_overlap(
			design["network_int"],
			design["broadcast_int"],
			other["network_int"],
			other["broadcast_int"],
		):
			conflicts.append(other)

	return {
		"purpose_profile": purpose_profile or "Corporate",
		"profile_notes": _(profile["notes"]),
		"vlan_hint": profile["vlan_hint"],
		"design": {k: v for k, v in design.items() if not k.endswith("_int")},
		"conflicts": conflicts,
	}


@frappe.whitelist()
def quick_create_host_item(title=None, itm_landscape=None, itm_location=None):
	"""Minimal Host Item create for wizard infra step."""
	if not title:
		frappe.throw(_("Host title is required."), title=_("Missing Title"))
	if not itm_landscape:
		frappe.throw(_("Landscape is required."), title=_("Missing Landscape"))

	doc = frappe.get_doc(
		{
			"doctype": "ITM Host Item",
			"title": title,
			"itm_landscape": itm_landscape,
			"itm_location": itm_location,
			"lifecycle_status": "Implementing",
			"health_status": "Unknown",
			"deployment": "Physical",
		}
	)
	doc.insert()
	return {"name": doc.name, "title": doc.title}


@frappe.whitelist()
def create_subnet_from_wizard(values=None):
	"""Create an ITM Subnet (Implementing) from wizard review payload."""
	if isinstance(values, str):
		values = frappe.parse_json(values)
	values = frappe._dict(values or {})

	required = ("itm_local_area_network", "network_address", "prefix_length")
	for key in required:
		if not values.get(key):
			frappe.throw(_("{0} is required.").format(key), title=_("Missing Value"))

	lan = frappe.db.get_value(
		"ITM Local Area Network",
		values.itm_local_area_network,
		["name", "itm_landscape", "itm_location"],
		as_dict=True,
	)
	if not lan:
		frappe.throw(_("Local Area Network was not found."), title=_("Invalid LAN"))

	doc = frappe.get_doc(
		{
			"doctype": "ITM Subnet",
			"network_address": values.network_address,
			"prefix_length": values.prefix_length,
			"itm_local_area_network": lan.name,
			"itm_landscape": lan.itm_landscape,
			"itm_location": values.get("itm_location") or lan.itm_location,
			"lifecycle_status": values.get("lifecycle_status") or "Implementing",
			"vlan_tag": values.get("vlan_tag"),
			"gateway": values.get("gateway"),
			"dhcp": values.get("dhcp"),
			"dns_1": values.get("dns_1"),
			"dns_2": values.get("dns_2"),
			"ntp_1": values.get("ntp_1"),
			"ntp_2": values.get("ntp_2"),
			"note": values.get("note"),
			"wireless": values.get("wireless"),
		}
	)
	doc.insert()
	return {"name": doc.name, "cidr": doc.cidr, "lifecycle_status": doc.lifecycle_status}
