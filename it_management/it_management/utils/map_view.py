# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

"""Map View helpers for DocTypes that link to Address."""

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils.data import flt

# DocType → Link fieldname pointing to Address
ADDRESS_LINK_FIELDS = {
	"ITM Location": "itm_location_address",
	"Location": "address",
	"ITM Trip": "destination",
	"Trip": "destination",
	"IT Service Report": "destination",
}


def create_point_feature(name, latitude, longitude, title=None, address=None):
	"""Build a GeoJSON Point Feature for Map View markers."""
	properties = {"name": name}
	if title:
		properties["title"] = title
	if address:
		properties["address"] = address

	return {
		"type": "Feature",
		"properties": properties,
		"geometry": {
			"type": "Point",
			# GeoJSON order is longitude, latitude
			"coordinates": [flt(longitude), flt(latitude)],
		},
	}


def _get_address_coords(address_name):
	"""Return (lat, lng, address_name) for a linked Address, or None."""
	if not address_name:
		return None

	if not frappe.db.has_column("Address", "latitude"):
		return None

	row = frappe.db.get_value(
		"Address",
		address_name,
		["name", "latitude", "longitude", "address_title"],
		as_dict=True,
	)
	if not row:
		return None

	lat = flt(row.latitude)
	lng = flt(row.longitude)
	if not (lat or lng):
		return None

	return lat, lng, row.name


def resolve_itm_location_address(location_name):
	"""
	Resolve the best Address for an ITM Location.

	Site/Building use their own address; Floor/Room walk up to a parent
	Site or Building that has an address.
	"""
	current = location_name
	seen = set()

	while current and current not in seen:
		seen.add(current)
		row = frappe.db.get_value(
			"ITM Location",
			current,
			["name", "itm_location_address", "itm_parent_location", "location_type"],
			as_dict=True,
		)
		if not row:
			break

		if row.itm_location_address:
			return row.itm_location_address

		current = row.itm_parent_location

	return None


def resolve_address_for_doc(doctype, doc):
	"""Return Address name for a document, including ITM Location inheritance."""
	if doctype == "ITM Location":
		direct = doc.get(ADDRESS_LINK_FIELDS["ITM Location"])
		if direct:
			return direct
		return resolve_itm_location_address(doc.name)

	fieldname = ADDRESS_LINK_FIELDS.get(doctype)
	if not fieldname:
		return None
	return doc.get(fieldname)


@frappe.whitelist()
def get_coords(doctype, filters=None, type=None):
	"""
	Return a GeoJSON FeatureCollection for Map View.

	Used via frappe.listview_settings[doctype].get_coords_method for DocTypes
	that store location as a Link to Address (with latitude/longitude).
	"""
	if not frappe.has_permission(doctype):
		frappe.throw(_("Not Permitted"), frappe.PermissionError)

	# Address itself uses core coordinate fields
	if doctype == "Address":
		from frappe.geo.utils import get_coords as core_get_coords

		return core_get_coords(doctype, filters, "coordinates")

	address_field = ADDRESS_LINK_FIELDS.get(doctype)
	if not address_field:
		frappe.throw(
			_("No Address link mapping configured for {0}").format(doctype),
			title=_("Map View"),
		)

	from frappe.desk.reportview import get_filters_cond

	conditions = get_filters_cond(doctype, filters, [], with_match_conditions=True)
	# get_filters_cond returns " and ..." or ""
	where_sql = conditions[4:] if conditions else "1=1"

	# Fetch enough fields to resolve addresses
	if doctype == "ITM Location":
		fields = "name, itm_location_name as title, itm_location_address, itm_parent_location, location_type"
	elif doctype == "Location":
		fields = "name, title, address"
	elif doctype in ("ITM Trip", "Trip", "IT Service Report"):
		fields = "name, destination"
	else:
		fields = "name, `{0}`".format(address_field)

	try:
		rows = frappe.db.sql(
			"SELECT {fields} FROM `tab{doctype}` WHERE {where_sql}".format(
				fields=fields, doctype=doctype, where_sql=where_sql
			),
			as_dict=True,
		)
	except frappe.db.InternalError:
		frappe.throw(
			_("Could not load map coordinates for {0}").format(doctype),
			title=_("Map View"),
		)

	features = []
	for row in rows:
		address_name = resolve_address_for_doc(doctype, row)
		coords = _get_address_coords(address_name)
		if not coords:
			continue

		lat, lng, address = coords
		title = row.get("title") or row.get("itm_location_name") or row.name
		features.append(
			create_point_feature(
				name=row.name,
				latitude=lat,
				longitude=lng,
				title=title,
				address=address,
			)
		)

	return {"type": "FeatureCollection", "features": features}


def get_map_enabled_doctypes():
	"""DocTypes for which this app registers Map View via Address links."""
	return list(ADDRESS_LINK_FIELDS.keys())
