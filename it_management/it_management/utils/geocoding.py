# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

"""Geocode Frappe Address documents via Nominatim (OpenStreetMap)."""

from __future__ import unicode_literals

import hashlib

import frappe
import requests
from frappe import _
from frappe.utils import cint, flt


ADDRESS_GEO_FIELDS = (
	"address_line1",
	"address_line2",
	"city",
	"county",
	"state",
	"pincode",
	"country",
)

DEFAULT_NOMINATIM_URL = "https://nominatim.openstreetmap.org"


def get_geocoding_settings():
	"""Return geocoding options from IT Management Settings (with defaults)."""
	settings = frappe.db.get_singles_dict("IT Management Settings") or {}
	return {
		"auto_geocode_addresses": cint(settings.get("auto_geocode_addresses", 1)),
		"nominatim_url": (settings.get("nominatim_url") or DEFAULT_NOMINATIM_URL).rstrip("/"),
	}


def cstr_strip(value):
	return str(value).strip()


def build_address_query(address):
	"""Build a Nominatim search string from Address fields."""
	parts = []
	for fieldname in ADDRESS_GEO_FIELDS:
		value = address.get(fieldname) if hasattr(address, "get") else getattr(address, fieldname, None)
		if value:
			parts.append(cstr_strip(value))
	return ", ".join(parts)


def address_query_hash(query):
	"""Stable hash used to skip re-geocoding unchanged addresses."""
	return hashlib.md5(query.encode("utf-8")).hexdigest()


def _get_coord(address, fieldname):
	value = address.get(fieldname) if hasattr(address, "get") else getattr(address, fieldname, None)
	return flt(value)


def has_coordinates(address):
	return bool(_get_coord(address, "latitude") or _get_coord(address, "longitude"))


def should_geocode(address, force=False):
	"""Decide whether an Address needs (re)geocoding."""
	if force:
		return True

	if cint(
		address.get("itm_manual_coordinates")
		if hasattr(address, "get")
		else getattr(address, "itm_manual_coordinates", 0)
	):
		return False

	query = build_address_query(address)
	if not query:
		return False

	current_hash = (
		address.get("itm_geocode_hash")
		if hasattr(address, "get")
		else getattr(address, "itm_geocode_hash", None)
	)
	# Matching hash means we already looked this address text up (hit or miss)
	if current_hash == address_query_hash(query):
		return False

	return True


def geocode_query(query, nominatim_url=None, raise_on_error=False):
	"""
	Forward-geocode a free-text query with Nominatim.

	Returns (latitude, longitude) or (None, None).
	"""
	if not query:
		return None, None

	settings = get_geocoding_settings()
	base_url = (nominatim_url or settings["nominatim_url"]).rstrip("/")
	url = "{0}/search".format(base_url)

	headers = {
		"User-Agent": "it_management-frappe/1.0 (+https://github.com/phamos-eu/it_management)",
		"Accept": "application/json",
	}
	params = {
		"q": query,
		"format": "json",
		"limit": 1,
	}

	try:
		response = requests.get(url, params=params, headers=headers, timeout=10)
		response.raise_for_status()
		results = response.json()
	except Exception as exc:
		frappe.log_error(
			title=_("Address Geocoding Failed"),
			message="{0}\n\nQuery: {1}".format(frappe.get_traceback(), query),
		)
		if raise_on_error:
			frappe.throw(
				_("Could not geocode address: {0}").format(str(exc)),
				title=_("Geocoding Error"),
			)
		return None, None

	if not results:
		return None, None

	return flt(results[0].get("lat")), flt(results[0].get("lon"))


def apply_geocode_to_address(address, force=False, raise_on_error=False, throw_on_miss=False):
	"""
	Populate latitude/longitude on an Address document (not saved).

	Returns True if coordinates were updated.
	"""
	if not should_geocode(address, force=force):
		return False

	query = build_address_query(address)
	if not query:
		return False

	lat, lng = geocode_query(query, raise_on_error=raise_on_error)

	if lat is None or lng is None:
		if throw_on_miss:
			frappe.throw(
				_("No coordinates found for: {0}").format(query),
				title=_("Geocoding Miss"),
			)
		# Remember the query so we do not hammer the geocoder on every save
		address.itm_geocode_hash = address_query_hash(query)
		return "miss"

	address.latitude = lat
	address.longitude = lng
	address.itm_geocode_hash = address_query_hash(query)
	return True


def geocode_address_on_update(doc, method=None):
	"""
	doc_events hook: queue auto-geocoding after Address save.

	Runs in the background so Nominatim latency does not block the form.
	"""
	settings = get_geocoding_settings()
	if not settings["auto_geocode_addresses"]:
		return

	# Custom fields may not exist yet during early migrate
	if not frappe.db.has_column("Address", "latitude"):
		return

	if cint(doc.get("itm_manual_coordinates")):
		return

	if not should_geocode(doc, force=False):
		return

	_enqueue_geocode(doc.name)


def _enqueue_geocode(address_name):
	"""Enqueue geocode job with kwargs compatible across Frappe v13–v15."""
	method = "it_management.it_management.utils.geocoding.geocode_address"
	kwargs = {
		"name": address_name,
		"force": 0,
		"queue": "short",
		"enqueue_after_commit": True,
	}
	try:
		frappe.enqueue(
			method,
			deduplicate=True,
			job_id="itm-geocode-{0}".format(address_name),
			**kwargs
		)
	except TypeError:
		# Older Frappe builds may not support deduplicate/job_id
		frappe.enqueue(method, **kwargs)


@frappe.whitelist()
def geocode_address(name, force=1):
	"""Whitelisted / background: geocode a saved Address and persist coordinates."""
	frappe.has_permission("Address", "write", throw=True)

	doc = frappe.get_doc("Address", name)
	result = apply_geocode_to_address(
		doc, force=cint(force), raise_on_error=cint(force), throw_on_miss=cint(force)
	)
	# Persist successful lookups and "miss" hashes (avoid repeat calls)
	if result:
		doc.flags.ignore_permissions = True
		doc.save()
	return {
		"name": doc.name,
		"latitude": getattr(doc, "latitude", None),
		"longitude": getattr(doc, "longitude", None),
		"updated": result is True,
	}
