# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

"""Custom fields on Address that power Map View + geocoding."""

from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


ADDRESS_GEO_CUSTOM_FIELDS = {
	"Address": [
		{
			"fieldname": "itm_map_section",
			"fieldtype": "Section Break",
			"label": "Map Location",
			"insert_after": "disabled",
			"collapsible": 1,
		},
		{
			"fieldname": "latitude",
			"fieldtype": "Float",
			"label": "Latitude",
			"insert_after": "itm_map_section",
			"precision": "9",
		},
		{
			"fieldname": "longitude",
			"fieldtype": "Float",
			"label": "Longitude",
			"insert_after": "latitude",
			"precision": "9",
		},
		{
			"fieldname": "column_break_itm_map",
			"fieldtype": "Column Break",
			"insert_after": "longitude",
		},
		{
			"fieldname": "itm_manual_coordinates",
			"fieldtype": "Check",
			"label": "Manual Coordinates",
			"insert_after": "column_break_itm_map",
			"description": "If checked, auto-geocoding will not overwrite latitude/longitude.",
			"default": "0",
		},
		{
			"fieldname": "itm_geocode_hash",
			"fieldtype": "Data",
			"label": "Geocode Hash",
			"insert_after": "itm_manual_coordinates",
			"read_only": 1,
			"hidden": 1,
			"no_copy": 1,
		},
	]
}


def ensure_address_geo_fields():
	"""Create Address custom fields required for Map View (idempotent)."""
	create_custom_fields(ADDRESS_GEO_CUSTOM_FIELDS, update=True)
	frappe.clear_cache(doctype="Address")


def remove_address_geo_fields():
	"""Remove Address geo custom fields (used on app uninstall)."""
	for field in ADDRESS_GEO_CUSTOM_FIELDS["Address"]:
		fieldname = field["fieldname"]
		custom_field_name = "Address-{0}".format(fieldname)
		if frappe.db.exists("Custom Field", custom_field_name):
			frappe.delete_doc("Custom Field", custom_field_name, force=1, ignore_permissions=True)
