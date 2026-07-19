# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from it_management.it_management.utils.ipv4 import (
	design_from_network_and_prefix,
	ranges_overlap,
)

SUBNET_LIFECYCLE = ("Planned", "Implementing", "Running", "Storage", "Obsolete")


class ITMSubnet(Document):
	def validate(self):
		self._normalize_lifecycle()
		self._sync_from_lan()
		self._apply_address_design()
		self._warn_address_conflicts()
		self._warn_vlan_conflicts()

	def _normalize_lifecycle(self):
		if not self.lifecycle_status:
			self.lifecycle_status = "Implementing"
		elif self.lifecycle_status not in SUBNET_LIFECYCLE:
			frappe.throw(
				_("Invalid lifecycle status {0}.").format(self.lifecycle_status),
				title=_("Invalid Status"),
			)

	def _sync_from_lan(self):
		"""Landscape (and empty location) always follow the selected LAN."""
		if not self.itm_local_area_network:
			return

		lan = frappe.db.get_value(
			"ITM Local Area Network",
			self.itm_local_area_network,
			["itm_landscape", "itm_location"],
			as_dict=True,
		)
		if not lan:
			frappe.throw(
				_("Local Area Network {0} was not found.").format(self.itm_local_area_network),
				title=_("Invalid LAN"),
			)

		self.itm_landscape = lan.itm_landscape
		if not self.itm_location and lan.itm_location:
			self.itm_location = lan.itm_location

	def _apply_address_design(self):
		self._network_int = None
		self._broadcast_int = None
		try:
			design = design_from_network_and_prefix(self.network_address, self.prefix_length)
		except (ValueError, TypeError) as exc:
			frappe.throw(
				_("Invalid IPv4 network design: {0}").format(str(exc)),
				title=_("Invalid Subnet"),
			)

		self.network_address = design["network_address"]
		self.prefix_length = design["prefix_length"]
		self.subnet_mask = design["subnet_mask"]
		self.cidr = design["cidr"]
		self.first_usable = design["first_usable"]
		self.last_usable = design["last_usable"]
		self.broadcast = design["broadcast"]
		self.usable_hosts = design["usable_hosts"]
		self._network_int = design["network_int"]
		self._broadcast_int = design["broadcast_int"]

	def _warn_address_conflicts(self):
		if not self.itm_landscape or self._network_int is None:
			return

		others = frappe.get_all(
			"ITM Subnet",
			filters={
				"itm_landscape": self.itm_landscape,
				"name": ["!=", self.name or ""],
				"network_address": ["!=", ""],
			},
			fields=["name", "cidr", "network_address", "prefix_length", "lifecycle_status"],
		)

		messages = []
		strong = False
		for other in others:
			try:
				other_design = design_from_network_and_prefix(
					other.network_address, other.prefix_length
				)
			except (ValueError, TypeError):
				continue

			if not ranges_overlap(
				self._network_int,
				self._broadcast_int,
				other_design["network_int"],
				other_design["broadcast_int"],
			):
				continue

			exact = self.cidr == other_design["cidr"]
			involves_running = (
				self.lifecycle_status == "Running" or other.lifecycle_status == "Running"
			)
			if involves_running:
				strong = True

			if exact:
				template = _(
					"Duplicate CIDR {0} also used by {1} ({2})."
				)
			else:
				template = _(
					"Address range overlaps {0} on {1} ({2})."
				)
			messages.append(
				template.format(
					frappe.bold(other_design["cidr"]),
					frappe.bold(other.name),
					_(other.lifecycle_status or "Unknown"),
				)
			)

		if not messages:
			return

		title = (
			_("Running subnet address conflict")
			if strong
			else _("Subnet address conflict")
		)
		intro = (
			_("Warning: one or more conflicts involve a Running subnet. Save is still allowed.")
			if strong
			else _("Warning: overlapping or duplicate subnets in this landscape. Save is still allowed.")
		)
		frappe.msgprint(
			intro + "<br><br>" + "<br>".join(messages),
			title=title,
			indicator="red" if strong else "orange",
			alert=True,
		)

	def _warn_vlan_conflicts(self):
		if not self.itm_landscape or self.vlan_tag in (None, ""):
			return

		others = frappe.get_all(
			"ITM Subnet",
			filters={
				"itm_landscape": self.itm_landscape,
				"name": ["!=", self.name or ""],
				"vlan_tag": self.vlan_tag,
			},
			fields=["name", "cidr", "lifecycle_status", "vlan_tag"],
		)
		if not others:
			return

		strong = self.lifecycle_status == "Running" or any(
			row.lifecycle_status == "Running" for row in others
		)
		lines = [
			_("{0} ({1}) uses VLAN {2}.").format(
				frappe.bold(row.cidr or row.name),
				_(row.lifecycle_status or "Unknown"),
				row.vlan_tag,
			)
			for row in others
		]
		intro = (
			_("Warning: VLAN tag conflict involves a Running subnet. Save is still allowed.")
			if strong
			else _("Warning: VLAN tag already used in this landscape. Save is still allowed.")
		)
		frappe.msgprint(
			intro + "<br><br>" + "<br>".join(lines),
			title=_("Running VLAN conflict") if strong else _("VLAN conflict"),
			indicator="red" if strong else "orange",
			alert=True,
		)


@frappe.whitelist()
def calculate_address_design(network_address=None, prefix_length=None):
	"""
	Return derived IPv4 design fields for the Subnet form.

	Does not throw on invalid input so live form feedback can stay non-blocking.
	"""
	try:
		design = design_from_network_and_prefix(network_address, prefix_length)
	except (ValueError, TypeError) as exc:
		return {"ok": False, "error": str(exc)}

	design["ok"] = True
	return design
