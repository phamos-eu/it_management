# Copyright (c) 2026, IT-Geräte und IT-Lösungen wie Server, Rechner, Netzwerke und E-Mailserver sowie auch Backups, and contributors
# For license information, please see license.txt

"""IPv4 helpers for ITM Subnet address design."""

from __future__ import unicode_literals

import ipaddress
import re


_OCTET_PARTS_RE = re.compile(r"^\s*([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)\s*$")


def explain_ipv4_address_error(network_address):
	"""
	Return a user-facing explanation for an invalid IPv4 address, or None if OK.

	Guides on octet ranges (0–255) and dotted-quad shape.
	"""
	if network_address in (None, ""):
		return "Network address is required"

	raw = str(network_address).strip()
	match = _OCTET_PARTS_RE.match(raw)
	if not match:
		return (
			f"'{raw}' is not a valid IPv4 address. "
			"Use four numbers separated by dots, e.g. 192.168.0.0. "
			"Each number (octet) must be between 0 and 255."
		)

	bad = []
	for index, part in enumerate(match.groups(), start=1):
		try:
			value = int(part)
		except ValueError:
			bad.append(f"octet {index} ('{part}') is not a number")
			continue
		# Leading zeros like 00 are ok for int(); reject out of range
		if value < 0 or value > 255:
			bad.append(
				f"octet {index} is {value}, but each octet must be between 0 and 255"
			)

	if bad:
		return (
			f"'{raw}' is not a valid IPv4 address: "
			+ "; ".join(bad)
			+ ". Example of a valid network address: 192.168.0.0."
		)

	return None


def is_complete_ipv4_address(network_address):
	"""True when the value has four numeric dotted parts (may still be out of range)."""
	if network_address in (None, ""):
		return False
	return bool(_OCTET_PARTS_RE.match(str(network_address).strip()))


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
	address_error = explain_ipv4_address_error(network_address)
	if address_error:
		raise ValueError(address_error)

	if prefix_length in (None, ""):
		raise ValueError("Prefix length is required (0–32)")

	try:
		prefix = int(prefix_length)
	except (TypeError, ValueError):
		raise ValueError("Prefix length must be a whole number between 0 and 32")

	if prefix < 0 or prefix > 32:
		raise ValueError("Prefix length must be between 0 and 32")

	try:
		network = ipaddress.ip_network(
			f"{str(network_address).strip()}/{prefix}", strict=False
		)
	except ValueError as exc:
		raise ValueError(
			f"Could not build an IPv4 network from '{network_address}/{prefix}': {exc}. "
			"Use a dotted IPv4 address (octets 0–255) and a prefix from 0 to 32."
		) from exc

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


def parse_ipv4_host(value):
	"""
	Parse a host IPv4 address.

	Raises ValueError with a user-facing message when invalid.
	"""
	address_error = explain_ipv4_address_error(value)
	if address_error:
		# explain_ipv4_address_error says "Network address" for empty — rephrase for hosts
		if value in (None, ""):
			raise ValueError("IP address is required")
		raise ValueError(address_error.replace("network address", "IP address", 1))

	try:
		host = ipaddress.ip_address(str(value).strip())
	except ValueError as exc:
		raise ValueError(
			"'{0}' is not a valid IPv4 address. "
			"Use four numbers separated by dots, e.g. 192.168.1.10.".format(str(value).strip())
		) from exc

	if host.version != 4:
		raise ValueError("Only IPv4 addresses are supported")

	return host


def explain_ip_not_in_subnet(ip_address, network_address, prefix_length):
	"""
	Return a user-facing error if the host IP cannot be used in the subnet.

	Returns None when the IP is a usable host address in the subnet.
	Network and broadcast addresses are rejected for prefixes shorter than /31.
	"""
	try:
		host = parse_ipv4_host(ip_address)
	except ValueError as exc:
		return str(exc)

	try:
		design = design_from_network_and_prefix(network_address, prefix_length)
	except ValueError as exc:
		return "Linked subnet is invalid: {0}".format(str(exc))

	network = ipaddress.ip_network(design["cidr"], strict=False)
	if host not in network:
		return (
			"IP address {0} is outside subnet {1}. "
			"Usable host range is {2} – {3}."
		).format(
			host,
			design["cidr"],
			design["first_usable"],
			design["last_usable"],
		)

	# /31 and /32 treat both addresses as usable
	if network.prefixlen >= 31:
		return None

	if host == network.network_address:
		return (
			"IP address {0} is the network address of {1} and cannot be assigned to a host. "
			"Use an address from {2} to {3}."
		).format(host, design["cidr"], design["first_usable"], design["last_usable"])

	if host == network.broadcast_address:
		return (
			"IP address {0} is the broadcast address of {1} and cannot be assigned to a host. "
			"Use an address from {2} to {3}."
		).format(host, design["cidr"], design["first_usable"], design["last_usable"])

	return None


def assert_ip_in_subnet(ip_address, network_address, prefix_length):
	"""Raise ValueError when the host IP is not usable in the subnet."""
	message = explain_ip_not_in_subnet(ip_address, network_address, prefix_length)
	if message:
		raise ValueError(message)
	return True
