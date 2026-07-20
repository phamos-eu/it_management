# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from it_management.it_management.utils.ipv4 import (
	assert_ip_in_subnet,
	explain_ip_not_in_subnet,
	parse_ipv4_host,
)


class ITMIPAddress(Document):
	def validate(self):
		self._normalize_ip_address()
		self._validate_ip_against_subnet()

	def _normalize_ip_address(self):
		if not self.ip_address:
			frappe.throw(_("IP Address is required."), title=_("Invalid IP Address"))

		try:
			host = parse_ipv4_host(self.ip_address)
		except ValueError as exc:
			frappe.throw(str(exc), title=_("Invalid IP Address"))

		# Store the canonical dotted-quad form
		self.ip_address = str(host)

	def _validate_ip_against_subnet(self):
		if not self.itm_subnet:
			frappe.throw(_("Subnet is required."), title=_("Invalid Subnet"))

		subnet = frappe.db.get_value(
			"ITM Subnet",
			self.itm_subnet,
			["name", "network_address", "prefix_length", "cidr", "first_usable", "last_usable"],
			as_dict=True,
		)
		if not subnet:
			frappe.throw(
				_("Subnet {0} was not found.").format(self.itm_subnet),
				title=_("Invalid Subnet"),
			)

		try:
			assert_ip_in_subnet(
				self.ip_address, subnet.network_address, subnet.prefix_length
			)
		except ValueError as exc:
			frappe.throw(str(exc), title=_("IP Not in Subnet"))


@frappe.whitelist()
def validate_ip_for_subnet(ip_address=None, itm_subnet=None):
	"""
	Live form check: can this IP be used on the selected ITM Subnet?

	Returns {ok, message, cidr, first_usable, last_usable} and does not throw
	on membership errors so the form can show feedback while typing.
	"""
	result = {
		"ok": False,
		"message": "",
		"cidr": None,
		"first_usable": None,
		"last_usable": None,
		"normalized_ip": None,
	}

	if not ip_address:
		result["message"] = _("Enter an IP address.")
		return result

	try:
		host = parse_ipv4_host(ip_address)
	except ValueError as exc:
		result["message"] = str(exc)
		return result

	result["normalized_ip"] = str(host)

	if not itm_subnet:
		result["message"] = _("Select a subnet to check whether this IP can be used.")
		return result

	subnet = frappe.db.get_value(
		"ITM Subnet",
		itm_subnet,
		["name", "network_address", "prefix_length", "cidr", "first_usable", "last_usable"],
		as_dict=True,
	)
	if not subnet:
		result["message"] = _("Subnet {0} was not found.").format(itm_subnet)
		return result

	result["cidr"] = subnet.cidr
	result["first_usable"] = subnet.first_usable
	result["last_usable"] = subnet.last_usable

	message = explain_ip_not_in_subnet(
		str(host), subnet.network_address, subnet.prefix_length
	)
	if message:
		result["message"] = message
		return result

	result["ok"] = True
	result["message"] = _("IP address {0} can be used in subnet {1}.").format(
		str(host), subnet.cidr or subnet.name
	)
	return result
