# Copyright (c) 2026, IT Management contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import unittest
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from it_management.it_management.utils.geocoding import (
	address_query_hash,
	apply_geocode_to_address,
	build_address_query,
	should_geocode,
)
from it_management.it_management.utils.map_view import (
	ADDRESS_LINK_FIELDS,
	create_point_feature,
	get_coords,
	resolve_itm_location_address,
)


class TestMapViewHelpers(FrappeTestCase):
	def test_create_point_feature_geojson_order(self):
		feature = create_point_feature("LOC-1", latitude=52.52, longitude=13.405, title="Berlin")
		self.assertEqual(feature["type"], "Feature")
		self.assertEqual(feature["geometry"]["type"], "Point")
		# GeoJSON is [longitude, latitude]
		self.assertEqual(feature["geometry"]["coordinates"], [13.405, 52.52])
		self.assertEqual(feature["properties"]["name"], "LOC-1")
		self.assertEqual(feature["properties"]["title"], "Berlin")

	def test_address_link_field_mapping(self):
		self.assertEqual(ADDRESS_LINK_FIELDS["ITM Location"], "itm_location_address")
		self.assertEqual(ADDRESS_LINK_FIELDS["Location"], "address")
		self.assertEqual(ADDRESS_LINK_FIELDS["ITM Trip"], "destination")

	def test_build_address_query(self):
		query = build_address_query(
			frappe._dict(
				{
					"address_line1": "Pariser Platz 1",
					"city": "Berlin",
					"pincode": "10117",
					"country": "Germany",
				}
			)
		)
		self.assertEqual(query, "Pariser Platz 1, Berlin, 10117, Germany")
		self.assertEqual(address_query_hash(query), address_query_hash(query))

	def test_should_geocode_respects_manual_flag_and_hash(self):
		query = "Berlin, Germany"
		address = frappe._dict(
			{
				"address_line1": "Berlin",
				"country": "Germany",
				"latitude": 52.52,
				"longitude": 13.4,
				"itm_geocode_hash": address_query_hash(query),
				"itm_manual_coordinates": 0,
			}
		)
		self.assertFalse(should_geocode(address))

		# Remembered miss (hash set, no coordinates) should not retry
		address.latitude = None
		address.longitude = None
		self.assertFalse(should_geocode(address))

		address.itm_manual_coordinates = 1
		self.assertFalse(should_geocode(address))
		self.assertTrue(should_geocode(address, force=True))

		address.itm_manual_coordinates = 0
		address.city = "Munich"
		self.assertTrue(should_geocode(address))

	@patch("it_management.it_management.utils.geocoding.geocode_query")
	def test_apply_geocode_sets_coordinates(self, mocked_geocode):
		mocked_geocode.return_value = (48.8566, 2.3522)
		address = frappe._dict(
			{
				"address_line1": "Paris",
				"country": "France",
				"latitude": None,
				"longitude": None,
				"itm_manual_coordinates": 0,
				"itm_geocode_hash": None,
			}
		)
		updated = apply_geocode_to_address(address, force=True)
		self.assertTrue(updated)
		self.assertEqual(address.latitude, 48.8566)
		self.assertEqual(address.longitude, 2.3522)
		self.assertTrue(address.itm_geocode_hash)


class TestMapViewCoordsIntegration(FrappeTestCase):
	def setUp(self):
		super().setUp()
		from it_management.it_management.utils.address_geo_fields import ensure_address_geo_fields

		ensure_address_geo_fields()

	def test_get_coords_for_itm_location(self):
		if not frappe.db.exists("Country", "Germany"):
			frappe.get_doc({"doctype": "Country", "country_name": "Germany", "code": "de"}).insert(
				ignore_permissions=True
			)

		address = frappe.get_doc(
			{
				"doctype": "Address",
				"address_title": "ITM Map Test Site",
				"address_type": "Office",
				"address_line1": "Teststrasse 1",
				"city": "Berlin",
				"country": "Germany",
				"latitude": 52.52,
				"longitude": 13.405,
				"itm_manual_coordinates": 1,
			}
		).insert(ignore_permissions=True)

		location = frappe.get_doc(
			{
				"doctype": "ITM Location",
				"itm_location_name": "ITM Map Test Site Loc",
				"location_type": "Site",
				"itm_location_address": address.name,
			}
		).insert(ignore_permissions=True)

		self.addCleanup(lambda: frappe.delete_doc("ITM Location", location.name, force=1))
		self.addCleanup(lambda: frappe.delete_doc("Address", address.name, force=1))

		result = get_coords("ITM Location", [["ITM Location", "name", "=", location.name]], None)
		self.assertEqual(result["type"], "FeatureCollection")
		self.assertEqual(len(result["features"]), 1)
		self.assertEqual(result["features"][0]["properties"]["name"], location.name)
		self.assertEqual(result["features"][0]["geometry"]["coordinates"], [13.405, 52.52])

	def test_resolve_address_from_parent_site(self):
		if not frappe.db.exists("Country", "Germany"):
			frappe.get_doc({"doctype": "Country", "country_name": "Germany", "code": "de"}).insert(
				ignore_permissions=True
			)

		address = frappe.get_doc(
			{
				"doctype": "Address",
				"address_title": "ITM Map Parent Addr",
				"address_type": "Office",
				"address_line1": "Parent 1",
				"city": "Hamburg",
				"country": "Germany",
				"latitude": 53.55,
				"longitude": 9.99,
				"itm_manual_coordinates": 1,
			}
		).insert(ignore_permissions=True)

		site = frappe.get_doc(
			{
				"doctype": "ITM Location",
				"itm_location_name": "ITM Map Parent Site",
				"location_type": "Site",
				"itm_location_address": address.name,
			}
		).insert(ignore_permissions=True)

		building = frappe.get_doc(
			{
				"doctype": "ITM Location",
				"itm_location_name": "ITM Map Child Building",
				"location_type": "Building",
				"itm_parent_location": site.name,
			}
		).insert(ignore_permissions=True)

		self.addCleanup(lambda: frappe.delete_doc("ITM Location", building.name, force=1))
		self.addCleanup(lambda: frappe.delete_doc("ITM Location", site.name, force=1))
		self.addCleanup(lambda: frappe.delete_doc("Address", address.name, force=1))

		self.assertEqual(resolve_itm_location_address(building.name), address.name)

		result = get_coords("ITM Location", [["ITM Location", "name", "=", building.name]], None)
		self.assertEqual(len(result["features"]), 1)
		self.assertEqual(result["features"][0]["geometry"]["coordinates"], [9.99, 53.55])


if __name__ == "__main__":
	unittest.main()
