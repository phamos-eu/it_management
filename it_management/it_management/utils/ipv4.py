# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""IPv4 helpers for ITM Subnet address design."""

from __future__ import unicode_literals

import ipaddress


def parse_cidr(value):
	"""
	Parse a CIDR string into a normalized IPv4Network.

	Returns None if value is empty; raises ValueError if invalid.
	"""
	if not value:
		return None
	return ipaddress.ip_network(str(value).strip(), strict=False)


def design_from_network_and_prefix(network_address, prefix_length):
	"""
	Build a normalized IPv4 design dict from network address + prefix.

	Raises ValueError on invalid input.
	"""
	if network_address in (None, ""):
		raise ValueError("Network address is required")
	if prefix_length in (None, ""):
		raise ValueError("Prefix length is required")

	prefix = int(prefix_length)
	if prefix < 0 or prefix > 32:
		raise ValueError("Prefix length must be between 0 and 32")

	network = ipaddress.ip_network(f"{str(network_address).strip()}/{prefix}", strict=False)
	return network_to_design(network)


def design_from_cidr(cidr):
	"""Build a normalized IPv4 design dict from a CIDR string."""
	network = parse_cidr(cidr)
	if network is None:
		raise ValueError("CIDR is required")
	return network_to_design(network)


def network_to_design(network):
	"""Convert an IPv4Network to the ITM Subnet design field values."""
	if network.version != 4:
		raise ValueError("Only IPv4 is supported")

	hosts = list(network.hosts())
	if network.prefixlen >= 31:
		# /31 and /32 have no classic usable host range
		first_usable = str(network.network_address)
		last_usable = str(network.broadcast_address)
		usable_hosts = int(network.num_addresses)
	else:
		first_usable = str(hosts[0])
		last_usable = str(hosts[-1])
		usable_hosts = len(hosts)

	return {
		"network_address": str(network.network_address),
		"prefix_length": network.prefixlen,
		"subnet_mask": str(network.netmask),
		"cidr": str(network),
		"first_usable": first_usable,
		"last_usable": last_usable,
		"broadcast": str(network.broadcast_address),
		"usable_hosts": usable_hosts,
		"network_int": int(network.network_address),
		"broadcast_int": int(network.broadcast_address),
	}


def ranges_overlap(a_start, a_end, b_start, b_end):
	"""Inclusive integer range overlap."""
	return a_start <= b_end and b_start <= a_end
